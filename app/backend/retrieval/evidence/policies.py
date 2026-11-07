"""Policy / jurisdiction evidence retrieval with metadata filters, conflict reporting and no automatic verdicts.

Filters are applied first (jurisdiction hierarchy, action, medicine class), then clauses are ranked by how many
rule facets they state, then passages are added by keyword/semantic search. Conflicts are reported when two
sources state different values for the same facet. Precedence between authorities is never inferred, and the
result always requires review.
"""
from collections import defaultdict

from sqlalchemy import func, or_, select

from backend.models import ControlledSubstance, PolicyClause, Source
from .common import active_join, missing_sources, passage_search, record_result

JURISDICTIONS = {'AE-DU': ['AE', 'AE-DU'], 'AE': ['AE']}
TRAVEL_ACTION = 'traveller_medicine_import'


def _classify(session, medicine_name):
    if not medicine_name:
        return {'status': 'unknown', 'detail': 'No medicine named; controlled-status classification cannot be determined.'}, []
    key = ''.join(ch if ch.isalnum() or ch == ' ' else ' ' for ch in medicine_name.lower()).strip()
    rows = session.scalars(active_join(select(ControlledSubstance), ControlledSubstance)
                           .where(or_(ControlledSubstance.name_key == key, ControlledSubstance.name_key.contains(key),
                                      func.similarity(ControlledSubstance.name_key, key) > 0.6))
                           .order_by(func.similarity(ControlledSubstance.name_key, key).desc()).limit(5)).all()
    if not rows:
        return {'status': 'not_found_in_list', 'detail': f'"{medicine_name}" is not on the ingested controlled list '
                'by name; the list notes non-inclusion does not mean a material is not covered.'}, []
    return {'status': 'listed', 'entries': [{'generic_name': r.generic_name, 'category': r.category,
                                              'carry_rule': r.carry_rule, 'prohibited': r.prohibited,
                                              'source_id': r.source_id} for r in rows]}, rows


def search_policy_clauses(session, query='', destination='AE-DU', origin_country=None, action=TRAVEL_ACTION,
                          medicine_name=None, supply_days=None, limit_passages=5):
    query = (query or '').strip()[:300]
    jurisdictions = JURISDICTIONS.get(destination, [destination])
    results, missing, seen = [], [], set()

    stmt = active_join(select(PolicyClause), PolicyClause).where(PolicyClause.jurisdiction.in_(jurisdictions))
    if action:
        stmt = stmt.where(PolicyClause.actions.contains([action]))
    clauses = session.scalars(stmt.order_by(PolicyClause.id)).all()
    clauses = sorted(clauses, key=lambda c: (-len(c.facets or {}), c.id))

    facet_values = defaultdict(lambda: defaultdict(list))
    for c in clauses:
        matched = [f'jurisdiction {c.jurisdiction}'] + ([f'action {action}'] if action else []) + \
                  [f'facet {k}' for k in (c.facets or {})]
        facts = {'authority': c.authority, 'jurisdiction': c.jurisdiction, 'document_type': c.document_type,
                 'hierarchy': c.hierarchy, 'clause_ref': c.clause_ref, 'actions': c.actions,
                 'medicine_classes': c.medicine_classes, 'facets': c.facets, 'date_text': c.date_text,
                 'status_note': c.status_note}
        results.append(record_result(session, c.record_pk, matched_fields=matched, method='metadata_filter', facts=facts))
        seen.add(c.record_pk)
        for key, f in (c.facets or {}).items():
            facet_values[key][f['value']].append({'source_id': c.source_id, 'clause_ref': c.clause_ref,
                                                  'authority': c.authority, 'phrase': f['phrase'], 'record_id': c.record_pk})

    classification, entries = _classify(session, medicine_name)
    for e in entries:
        if e.record_pk not in seen:
            results.append(record_result(session, e.record_pk, matched_fields=['controlled list name'],
                                         method='structured_sql', facts={'generic_name': e.generic_name,
                                                                         'category': e.category, 'carry_rule': e.carry_rule}))
            seen.add(e.record_pk)

    # Clause passages; individual controlled-list rows only come from the name lookup above.
    for rid, score, method in passage_search(session, query or 'traveller personal use medicines controlled',
                                             workflow='policies', countries=jurisdictions,
                                             kinds=['policy_clause', 'law_clause'], limit=limit_passages, exclude=seen):
        results.append(record_result(session, rid, matched_fields=['passage text'], method=method, score=score))

    conflicts = [{'facet': key, 'values': [{'value': v, 'stated_by': refs} for v, refs in vals.items()],
                  'note': 'Sources state different requirements; precedence is not inferred.'}
                 for key, vals in facet_values.items() if len(vals) > 1]
    stated_limits = [{'facet': 'max_supply', 'value': v, 'stated_by': refs}
                     for v, refs in facet_values.get('max_supply', {}).items()]
    supply_check = None
    stated_days = sorted({c.facets['max_supply']['days'] for c in clauses if 'max_supply' in (c.facets or {})})
    if supply_days is not None and stated_days:
        supply_check = {'requested_days': supply_days,
                        'stated_maximum_days': stated_days,
                        'within_stated_maximum': supply_days <= min(stated_days),
                        'note': 'Comparison with the stated quantity limit only. It is not a clearance: classification, '
                                'documents and approvals still need review.'}

    if classification['status'] != 'listed':
        missing.append({'type': 'classification_unknown', 'detail': classification['detail']})
    for c in clauses:
        if c.status_note:
            missing.append({'type': 'source_partially_ingested', 'source_id': c.source_id, 'detail': c.status_note})
        if 'delegated_rules' in (c.facets or {}):
            missing.append({'type': 'delegated_rules_not_ingested', 'source_id': c.source_id,
                            'detail': f'{c.clause_ref}: {c.facets["delegated_rules"]["phrase"][:220]} — '
                                      'the Executive Regulations are not in the knowledge base.'})
    dated = session.scalars(select(Source).where(Source.workflow == 'policies', Source.active_version_id.is_not(None),
                                                 Source.jurisdiction.in_(jurisdictions))).all()
    for s in dated:
        for lim in s.limitations or []:
            if 'updated' in lim.lower() or 'newer version' in lim.lower():
                missing.append({'type': 'possibly_stale', 'source_id': s.source_id, 'detail': lim})
    if origin_country:
        has_origin = session.scalar(select(func.count()).select_from(Source).where(
            Source.workflow == 'policies', Source.jurisdiction.like(f'{origin_country}%'),
            Source.active_version_id.is_not(None)))
        if not has_origin:
            missing.append({'type': 'no_origin_country_rules', 'country': origin_country,
                            'detail': f'No {origin_country} outbound rules are ingested; no departure ruling can be given.'})
    missing += missing_sources(session, 'policies', jurisdictions)
    # de-duplicate missing entries
    uniq, keys = [], set()
    for m in missing:
        k = (m['type'], m.get('source_id'), m['detail'])
        if k not in keys:
            keys.add(k)
            uniq.append(m)
    return {'domain': 'policies',
            'query': {'query': query, 'destination': destination, 'jurisdictions_searched': jurisdictions,
                      'origin_country': origin_country, 'action': action, 'medicine_name': medicine_name,
                      'supply_days': supply_days},
            'retrieval_status': 'review_required' if results else 'no_evidence',
            'review_required': True, 'classification': classification, 'conflicts': conflicts,
            'stated_limits': stated_limits, 'supply_check': supply_check,
            'results': results, 'missing_evidence': uniq}
