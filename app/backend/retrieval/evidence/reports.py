"""Medical report evidence retrieval: analyte/unit references, UCUM unit definitions, deterministic conversion.

Original values are always preserved. Conversions use reviewed analyte-specific rules (terminology.CONVERSIONS);
UCUM is used to identify units, never to convert mass to molar concentration on its own. No interpretation or
diagnosis is produced.
"""
import re

from sqlalchemy import select

from backend.ingestion import terminology as T
from backend.models import KnowledgeRecord, LabTestReference, Source
from .common import active_join, missing_sources, passage_search, record_result, status

_VALUE_UNIT = re.compile(r'(\d+(?:\.\d+)?)\s*(mg/dl|mmol/l|g/dl|µmol/l|umol/l)\b', re.I)
_CANON_UNITS = {'mg/dl': 'mg/dL', 'mmol/l': 'mmol/L', 'g/dl': 'g/dL', 'µmol/l': 'µmol/L', 'umol/l': 'µmol/L'}


def _ucum_records(session):
    rows = session.execute(active_join(select(KnowledgeRecord.id, KnowledgeRecord.metadata_), KnowledgeRecord)
                           .where(Source.source_id == 'GL-UCUM')).all()
    return {(m.get('unit_type'), m.get('code')): rid for rid, m in rows}


def ucum_parse(session, unit):
    """'mg/dL' -> [{'part': 'mg', 'prefix': 'm', 'atom': 'g', records...}] using UCUM codes only."""
    index = _ucum_records(session)
    prefixes = sorted({code for (kind, code) in index if kind == 'prefix'}, key=len, reverse=True)
    atoms = {code for (kind, code) in index if kind in ('unit', 'base-unit')}
    out = []
    for part in unit.split('/'):
        entry = {'part': part, 'prefix': None, 'atom': None, 'record_ids': []}
        if part in atoms:
            entry['atom'] = part
        else:
            for p in prefixes:
                if part.startswith(p) and part[len(p):] in atoms:
                    entry['prefix'], entry['atom'] = p, part[len(p):]
                    break
        if entry['atom'] is None:
            entry['unresolved'] = True
        for kind, code in (('prefix', entry['prefix']), ('base-unit', entry['atom']), ('unit', entry['atom'])):
            if code and (kind, code) in index:
                entry['record_ids'].append(index[(kind, code)])
        out.append(entry)
    return out


def search_lab_evidence(session, query='', analyte=None, value=None, unit=None, countries=None, limit_passages=3):
    query = (query or '').strip()[:200]
    m = _VALUE_UNIT.search(query)
    if value is None and m:
        value = float(m.group(1))
    if unit is None and m:
        unit = _CANON_UNITS[m.group(2).lower()]
    name_part = _VALUE_UNIT.sub(' ', query).strip()
    analyte = analyte or T.normalise_analyte(name_part) or T.normalise_analyte(re.sub(r'\b(serum|plasma|test|level)\b', '', name_part, flags=re.I).strip())
    fasting = T.is_fasting(query)
    results, missing = [], []

    if not analyte:
        missing.append({'type': 'analyte_unresolved', 'detail': f'"{name_part}" does not match a reviewed analyte synonym.'})
        refs = []
    else:
        stmt = active_join(select(LabTestReference), LabTestReference).where(LabTestReference.analyte == analyte)
        if countries:
            stmt = stmt.where(LabTestReference.country.in_(countries))
        refs = session.scalars(stmt.order_by(LabTestReference.entry_type, LabTestReference.country, LabTestReference.id)).all()
    seen = set()
    units_seen = []
    for r in refs:
        matched = [f'analyte {analyte}']
        if fasting and r.fasting:
            matched.append('fasting')
        if unit and r.unit == unit:
            matched.append(f'unit {unit}')
        facts = {'entry_type': r.entry_type, 'test_name': r.test_name, 'analyte': r.analyte, 'synonyms': r.synonyms,
                 'specimen': r.specimen, 'fasting': r.fasting, 'unit': r.unit, 'unit_system': r.unit_system,
                 'reference_interval': r.ref_text, 'method': r.method, 'panel': r.panel, 'codes': r.codes}
        if r.entry_type == 'sample_observation':
            facts['observed_value_as_printed'] = r.observed_value
            facts['note'] = 'Observation printed on a public sample report (dummy patient); format evidence only.'
        if r.unit and r.unit not in units_seen:
            units_seen.append(r.unit)
        if r.record_pk not in seen:
            results.append(record_result(session, r.record_pk, matched_fields=matched, method='structured_sql', facts=facts))
            seen.add(r.record_pk)

    # UCUM unit definitions (DT05) for the units involved.
    units = [u for u in ([unit] if unit else []) + units_seen if u]
    ucum = {}
    for u in dict.fromkeys(units):
        parts = ucum_parse(session, u)
        ucum[u] = [{k: v for k, v in p.items() if k != 'record_ids'} for p in parts]
        for p in parts:
            for rid in p['record_ids']:
                if rid not in seen:
                    results.append(record_result(session, rid, matched_fields=[f'UCUM code in {u}'],
                                                 method='ucum_code_lookup'))
                    seen.add(rid)
            if p.get('unresolved'):
                missing.append({'type': 'ucum_unresolved', 'detail': f'Unit part "{p["part"]}" of {u} is not a UCUM code.'})

    # Deterministic conversion (original value kept).
    conversion = None
    if value is not None and unit and analyte:
        targets = [u for u in units_seen if u != unit] or (['mmol/L'] if unit == 'mg/dL' else ['mg/dL'] if unit == 'mmol/L' else [])
        for target in targets:
            converted = T.convert(analyte, value, unit, target)
            if converted:
                conversion = {'original': {'value': value, 'unit': unit}, 'derived': converted,
                              'note': 'Derived value for comparison only; the original value and report remain the record.'}
                break
        if conversion is None:
            missing.append({'type': 'no_reviewed_conversion',
                            'detail': f'No reviewed conversion rule for {analyte} from {unit}.'})

    for rid, score, method in passage_search(session, f'{name_part} {unit or ""}'.strip(), workflow='medical_reports',
                                             countries=countries, kinds=['report_passage', 'lab_test_reference'],
                                             limit=limit_passages, exclude=seen):
        results.append(record_result(session, rid, matched_fields=['passage text'], method=method, score=score))

    if analyte:
        countries_with_refs = {r.country for r in refs if r.entry_type == 'reference_test'}
        for c in (countries or []):
            if c not in countries_with_refs:
                missing.append({'type': 'no_reference_test', 'country': c,
                                'detail': f'No {c} laboratory reference entry for {analyte} is ingested.'})
        if any(r.entry_type == 'reference_test' and r.panel and not r.unit for r in refs):
            missing.append({'type': 'unit_not_stated', 'detail': 'A panel reference lists the analyte without a '
                            'per-analyte unit or interval (units stated only as a convention).'})
    missing.append({'type': 'scope', 'detail': 'Reference sources describe single laboratories; they do not establish '
                    'a national unit convention. No interpretation or diagnosis is provided.'})
    if value is not None:
        missing.append({'type': 'patient_document_not_in_knowledge_base',
                        'detail': 'The patient report itself is not part of the knowledge base; verify the original document.'})
    missing += missing_sources(session, 'medical_reports', countries)
    return {'domain': 'reports',
            'query': {'query': query, 'analyte': analyte, 'value': value, 'unit': unit, 'fasting': fasting,
                      'countries': countries},
            'retrieval_status': status(results, missing), 'conversion': conversion, 'ucum_units': ucum,
            'results': results, 'missing_evidence': missing}
