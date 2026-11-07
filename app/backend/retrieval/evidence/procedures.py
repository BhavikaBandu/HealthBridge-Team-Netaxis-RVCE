"""Procedure evidence retrieval: terminology-aware matching on modality, anatomy and laterality, then passages.

Only attributes stated by a source are compared. A general "MRI of joints" service is reported as a *broader*
anatomy match for a knee request, never as a knee-specific protocol. Other modalities (e.g. CT) are listed as
not equivalent.
"""
from sqlalchemy import select

from backend.ingestion import terminology as T
from backend.models import ProcedureTerm
from .common import active_join, missing_sources, passage_search, record_result, status


def _anatomy_match(requested, stated):
    if not requested:
        return 'not requested'
    if requested in stated:
        return 'exact'
    parent = T.ANATOMY_PARENTS.get(requested)
    if parent and parent in stated:
        return f'broader ({parent})'
    return 'none'


def _laterality_match(requested, stated):
    if not requested:
        return 'not requested'
    if not stated:
        return 'not stated'
    if stated == requested or (stated == 'single (left or right)' and requested in ('right', 'left')):
        return f'stated: {stated}'
    return f'different: {stated}'


def search_procedures(session, query, countries=None, modality=None, anatomy=None, laterality=None, limit_passages=4):
    query = (query or '').strip()[:200]
    modality = modality or (T.modalities_in(query) or [None])[0]
    anatomy = anatomy or next((a for a in T.anatomy_in(query) if a != 'joints'), None) or (T.anatomy_in(query) or [None])[0]
    laterality = laterality or T.laterality_in(query)
    results, missing, by_country, not_equivalent = [], [], {}, []

    stmt = active_join(select(ProcedureTerm), ProcedureTerm)
    if countries:
        stmt = stmt.where(ProcedureTerm.country.in_(countries))
    terms = session.scalars(stmt.order_by(ProcedureTerm.country, ProcedureTerm.id)).all()
    seen = set()
    for t in terms:
        if modality and t.modality != modality:
            if anatomy and _anatomy_match(anatomy, t.anatomy or []) != 'none' and t.modality:
                not_equivalent.append({'source_id': t.source_id, 'country': t.country, 'term': t.term,
                                       'modality': t.modality, 'note': f'{t.modality} is not {modality}; not used as a match.'})
            continue
        a_match = _anatomy_match(anatomy, t.anatomy or [])
        if anatomy and a_match == 'none':
            continue
        l_match = _laterality_match(laterality, t.laterality)
        matched = [f'modality {t.modality}'] + ([f'anatomy {a_match}'] if anatomy else []) + \
                  ([f'laterality {l_match}'] if laterality else [])
        facts = {'term': t.term, 'provider': t.provider, 'modality': t.modality, 'anatomy': t.anatomy,
                 'anatomy_match': a_match, 'laterality': t.laterality, 'laterality_match': l_match,
                 'contrast_statement': t.contrast, 'protocol': t.protocol}
        c = by_country.setdefault(t.country, {'country': t.country, 'modality_found': False, 'best_anatomy_match': None,
                                              'laterality_statements': [], 'contrast_statements': [], 'protocol_stated': False,
                                              'sources': []})
        c['modality_found'] = True
        rank = {'exact': 0}.get(a_match, 1 if a_match.startswith('broader') else 2)
        best = c['best_anatomy_match']
        if best is None or rank < {'exact': 0}.get(best, 1 if str(best).startswith('broader') else 2):
            c['best_anatomy_match'] = a_match
        if t.laterality and t.laterality not in c['laterality_statements']:
            c['laterality_statements'].append(t.laterality)
        if t.contrast and t.contrast not in c['contrast_statements']:
            c['contrast_statements'].append(t.contrast)
        c['protocol_stated'] = c['protocol_stated'] or bool(t.protocol)
        if t.source_id not in c['sources']:
            c['sources'].append(t.source_id)
        if t.record_pk not in seen:
            results.append(record_result(session, t.record_pk, matched_fields=matched, method='structured_terminology',
                                         facts=facts))
            seen.add(t.record_pk)

    for rid, score, method in passage_search(session, query, workflow='procedures', countries=countries,
                                             limit=limit_passages, exclude=seen):
        results.append(record_result(session, rid, matched_fields=['passage text'], method=method, score=score))

    for country in (countries or sorted(by_country)):
        c = by_country.get(country)
        if not c:
            missing.append({'type': 'no_matching_service', 'country': country,
                            'detail': f'No ingested {country} source states a {modality or "matching"} service'
                                      + (f' for {anatomy}' if anatomy else '') + '.'})
            continue
        if anatomy and c['best_anatomy_match'] != 'exact':
            missing.append({'type': 'anatomy_not_specific', 'country': country,
                            'detail': f'{country} sources describe {modality} for {c["best_anatomy_match"]}, not a '
                                      f'{anatomy}-specific service or protocol.'})
        if laterality and not c['laterality_statements']:
            missing.append({'type': 'laterality_not_stated', 'country': country,
                            'detail': f'No {country} source states laterality support ({laterality}).'})
        if not c['protocol_stated']:
            missing.append({'type': 'protocol_not_stated', 'country': country,
                            'detail': f'No {country} source states an imaging protocol/sequence'
                                      + (f' for {laterality} {anatomy}' if anatomy else '') + '; protocol unresolved.'})
        if not c['contrast_statements']:
            missing.append({'type': 'contrast_not_stated', 'country': country,
                            'detail': f'No {country} source states contrast use for this service.'})
    missing.append({'type': 'out_of_scope_evidence', 'detail': 'No billing/procedure code, price or appointment '
                    'availability evidence is in the ingested sources.'})
    missing += missing_sources(session, 'procedures', countries)
    return {'domain': 'procedures',
            'query': {'query': query, 'countries': countries, 'modality': modality, 'anatomy': anatomy,
                      'laterality': laterality},
            'retrieval_status': status(results, missing), 'by_country': list(by_country.values()),
            'not_equivalent': not_equivalent, 'results': results, 'missing_evidence': missing}
