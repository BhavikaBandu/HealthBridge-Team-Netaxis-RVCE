"""Medical Reports agent: one finding per document.

The AI decides what matters in the document (any type): up to 4 short facts. For lab values, code first retrieves the
lab sources for each test (destination laboratory units and ranges, reviewed conversion rules, UCUM units); the AI then
picks the destination unit and does the conversion from what was retrieved. When nothing was retrieved for a test, the
AI chooses the unit itself and the value is marked as an AI estimate. Guardrail: every number in a fact's label/value
must appear in the document text; the converted value is not re-checked by code. Nothing is interpreted or diagnosed.
"""
import re

from sqlalchemy import select

from backend.ingestion import terminology as T
from backend.portal.models import DocumentFinding, DocumentText
from backend.portal.reference import DOCUMENT_TYPES
from backend.retrieval.evidence import search_lab_evidence
from .common import ai_or_fallback, ai_status, dedupe_sources, source_entry
from . import llm

SYSTEM = (
    'You read one patient document (synthetic test data) for a doctor in another country. Be brief. "kind" is a plain '
    'label: "Lab report", "Prescription", "Referral letter" or similar. '
    'LAB REPORT: one fact per result (max 4): label = test name; value = value and unit exactly as printed plus the lab '
    'flag in brackets if printed, e.g. "108 mg/dL (H)"; lab_id = the id of that result in "lab_retrieval"; '
    '"converted" = the value in the units used in the destination country. Use "lab_retrieval": when it gives '
    'destination laboratory units, convert to that unit; when it gives a conversion rule, use that factor and do the '
    'arithmetic yourself (2 significant decimals at most, e.g. "5.99 mmol/L"). When it gives nothing for a test, choose '
    'the unit commonly used in the destination from your own knowledge, or leave "converted" empty if the unit is '
    'already the same or no standard conversion exists; problem = false. context = one line (max 25 words): specimen, '
    'fasting, reference ranges as printed. '
    'PRESCRIPTION: one fact per medicine: label = name and strength; value = dose and quantity in max 12 words; '
    'problem = false. Then ONE extra fact labelled "Missing" listing what is missing or not stated (e.g. "No treatment '
    'duration; not attested") with problem = true, only if something is missing. context = prescriber and date only. '
    'REFERRAL / LETTER / OTHER: NO facts. context = exactly 2 lines separated by a newline, each max 18 words: line 1 = '
    'what is requested and its status; line 2 = the key history or finding. Do not list medicines or allergies. '
    'Copy numbers exactly from the document. Do not give travel, legal or import advice. Never interpret results, never '
    'diagnose, never use words like normal/abnormal/diabetes. JSON only.')
SCHEMA = {'type': 'object', 'required': ['kind', 'facts', 'context'], 'properties': {
    'kind': {'type': 'string'},
    'context': {'type': 'string'},
    'facts': {'type': 'array', 'maxItems': 4, 'items': {'type': 'object', 'required': ['label', 'value'], 'properties': {
        'label': {'type': 'string'}, 'value': {'type': 'string'}, 'converted': {'type': 'string'},
        'lab_id': {'type': 'integer'}, 'problem': {'type': 'boolean'}}}}}}


def _lab_retrieval(s, labs, ctx):
    """For each extracted lab value: destination lab units/ranges and reviewed conversion rules from the sources.
    Returns (items for the AI, sources used, {lab_id: True if something was retrieved})."""
    items, sources, found = [], [], {}
    for n, v in enumerate(labs):
        item = {'lab_id': n, 'test': v.get('test_name'), 'value': v.get('value'), 'unit': v.get('unit'), 'retrieved': None}
        found[n] = False
        if v.get('analyte') and v.get('unit'):
            r = search_lab_evidence(s, v.get('test_name') or v['analyte'], analyte=v['analyte'],
                                    value=v.get('value_numeric'), unit=v['unit'], countries=[ctx.destination, ctx.origin])
            dest = [x for x in r['results'] if x['country'] == ctx.destination and (x.get('facts') or {}).get('unit')
                    and x['facts'].get('entry_type') == 'reference_test']
            refs = [{'source': x['source_id'], 'test': x['facts']['test_name'], 'unit': x['facts']['unit'],
                     'reference_range': x['facts'].get('reference_interval')} for x in dest]
            rules = []
            for (analyte, a, b), rule in T.CONVERSIONS.items():
                if analyte == v['analyte'] and a == v['unit']:
                    rules.append({'from': a, 'to': b, **({'divide_by': rule['divide_by']} if 'divide_by' in rule
                                                          else {'multiply_by': rule['multiply_by']}),
                                  'basis': rule['basis']})
            if refs or rules:
                item['retrieved'] = {'destination_lab_references': refs, 'conversion_rules': rules}
                found[n] = True
                sources += [source_entry(x) for x in dest]
                if rules:
                    sources += [source_entry(x) for x in r['results'] if x['source_id'] == 'GL-UCUM'][:1]
        items.append(item)
    return items, sources, found


def _fallback(doc, findings, text=""):
    """Template facts from the extractor when the AI is unavailable."""
    labs = [f.data for f in findings if f.kind == 'lab_result']
    if labs:
        facts = []
        for v in labs[:4]:
            conv = None
            if v.get('analyte') and v.get('unit') == 'mg/dL':
                c = T.convert(v['analyte'], v['value_numeric'], 'mg/dL', 'mmol/L')
                conv = f"{c['value']:.1f} mmol/L" if c else None
            facts.append({'label': v['test_name'], 'value': f"{v['value']} {v['unit']}" + (f" ({v['flag']})" if v.get('flag') else ''),
                          'converted': conv or '', 'problem': False})
        first = labs[0]
        ctx = ', '.join(filter(None, [(first.get('specimen') or '').capitalize(), first.get('fasting_note') and f"fasting {first['fasting_note']}",
                                      first.get('reference_interval') and f"lab range {first['reference_interval']} {first.get('unit') or ''}".strip()]))
        return {'kind': 'Lab report', 'facts': facts, 'context': ctx}
    items = [f.data for f in findings if f.kind == 'prescription_item']
    fields = next((f.data for f in findings if f.kind == 'prescription_fields'), {})
    if items:
        facts = [{'label': i['medicine'], 'value': '; '.join(filter(None, [i.get('dose_text'), i.get('quantity_text') and f"quantity {i['quantity_text']}"])),
                  'converted': '', 'problem': False} for i in items[:3]]
        problems = []
        if any(not i.get('duration_stated') for i in items):
            problems.append('No treatment duration')
        if not fields.get('attestation_wording_found'):
            problems.append('not attested')
        if problems:
            facts.append({'label': 'Missing', 'value': '; '.join(problems), 'converted': '', 'problem': True})
        return {'kind': 'Prescription', 'facts': facts[:4],
                'context': ' · '.join(filter(None, [fields.get('prescriber'), fields.get('issue_date')]))}
    return {'kind': DOCUMENT_TYPES.get(doc.doc_type, 'Document'), 'facts': [], 'context': _letter_summary(text)}


_SECTIONS = {'history', 'examination', 'imaging', 'request', 'reason', 'reason for referral', 'diagnosis', 'impression',
             'findings', 'plan', 'current medicines', 'past medicines', 'medicines', 'allergies', 'investigations',
             'recommendation', 'recommendations', 'conclusion'}
_FIRST_SENTENCE = re.compile(r'^(.+?[.!?])(\s|$)')


def _sections(text):
    """{heading: text} for letters laid out as 'Heading' lines followed by their text."""
    out, current = {}, None
    for line in [ln.strip() for ln in (text or '').split('\n') if ln.strip()]:
        key = line.rstrip(':').lower()
        if key in _SECTIONS:
            current = key
            out.setdefault(current, [])
        elif current:
            out[current].append(line)
    return {k: ' '.join(v) for k, v in out.items() if v}


def _letter_summary(text):
    """Two short lines from a letter/referral without AI: what is requested, then the key history."""
    sec = _sections(text)
    lines = []
    ask = sec.get('request') or sec.get('reason for referral') or sec.get('reason') or sec.get('plan')
    if ask:
        lines.append('Request: ' + re.sub(r'\s+', ' ', ask)[:200])
    story = sec.get('history') or sec.get('findings') or sec.get('impression') or sec.get('examination')
    if story:
        first = _FIRST_SENTENCE.match(story)
        extra = next((sen for sen in re.split(r'(?<=[.!?])\s+', story) if re.search(r'diagnos', sen, re.I)), '')
        line = (first.group(1) if first else story[:160])
        lines.append('History: ' + (f'{line} {extra}' if extra and extra not in line else line))
    if not lines:   # no recognisable sections: first two sentences of the body
        body = ' '.join(ln.strip() for ln in (text or '').split('\n')[10:] if ln.strip())
        lines = [sen for sen in re.split(r'(?<=[.!?])\s+', body) if len(sen) > 20][:2]
    return '\n'.join(lines[:2]) or 'No summary available.'


def _kind_label(kind):
    """'lab_report' -> 'Lab report'."""
    k = re.sub(r'[_-]+', ' ', (kind or '').strip())
    return k[:1].upper() + k[1:].lower() if k else ''


def analyse(s, doc, ctx):
    text_row = s.get(DocumentText, doc.id)
    text = '\n'.join(p['text'] for p in (text_row.pages if text_row else []))[:9000]
    findings = s.scalars(select(DocumentFinding).where(DocumentFinding.document_id == doc.id)).all()
    fallback = _fallback(doc, findings, text)
    doc_numbers = llm.numbers_in(text) | llm.numbers_in(doc.name)

    def validate(d):
        for f in d.get('facts', []):
            llm.check_text(f.get('label', '') + ' ' + f.get('value', ''), doc_numbers, 'fact')
            if f.get('converted') and llm.BANNED.search(f['converted']):
                raise llm.LLMError('converted: wording not allowed')
        conv_numbers = set().union(*[llm.numbers_in(f.get('converted', '')) for f in d.get('facts', [])] or [set()])
        llm.check_text(d.get('context', ''), doc_numbers | conv_numbers, 'context')
        for f in d.get('facts', []):
            llm.check_length(f.get('value', ''), 20, 'fact value')
        lines = [ln for ln in (d.get('context') or '').split('\n') if ln.strip()]
        if d.get('facts'):
            llm.check_length(d.get('context', ''), 40, 'context')
        else:   # narrative documents: a 2-line summary
            if len(lines) > 2:
                raise llm.LLMError('summary has more than 2 lines')
            for ln in lines:
                llm.check_length(ln, 26, 'summary line')

    labs = [f.data for f in findings if f.kind == 'lab_result']
    lab_items, lab_sources, retrieved = _lab_retrieval(s, labs, ctx) if labs else ([], [], {})
    payload = {'document': {'name': doc.name, 'type': DOCUMENT_TYPES.get(doc.doc_type, doc.doc_type),
                            'date': doc.document_date.isoformat() if doc.document_date else None},
               'source_country': ctx.origin_name, 'destination_country': ctx.destination_name,
               'extracted_values': [{'kind': f.kind, **f.data} for f in findings], 'document_text': text}
    if lab_items:
        payload['lab_retrieval'] = lab_items
    data = ai_or_fallback(ctx, f'document {doc.name}', SYSTEM, payload, SCHEMA, fallback, validate) if text else fallback

    def basis(f):
        """Where the converted value's unit/factor came from: the retrieved lab sources, or the AI's own choice."""
        if not f.get('converted'):
            return ''
        if data is fallback or data.get('_fallback'):
            return 'rule'
        return 'sources' if retrieved.get(f.get('lab_id')) else 'ai'

    facts = [{'label': f.get('label', ''), 'value': f.get('value', ''), 'converted': f.get('converted') or '',
              'basis': basis(f), 'problem': bool(f.get('problem'))} for f in data.get('facts', [])][:4]
    date = doc.document_date.strftime('%d %b %Y') if doc.document_date else ''
    return {'agent': 'report', 'record_type': 'document', 'record_id': doc.id, 'title': doc.name,
            'match_label': ' · '.join(filter(None, [_kind_label(data.get('kind')), date])), 'confidence': None,
            'patient_line': None, 'comparison': {}, 'facts': facts, 'context': data.get('context'),
            'verify': None, 'sources': dedupe_sources(lab_sources),
            # for the controller only (not stored)
            '_ai': ai_status(data) if text else 'unavailable', '_has_text': bool(text),
            '_conversion_agreement': _conversion_agreement(data.get('facts', []), labs),
            '_flagged': any(v.get('flag') for v in labs)}


_NUMBER = re.compile(r'\d+(?:\.\d+)?')


def _conversion_agreement(ai_facts, labs):
    """Share of AI conversions that match the reviewed rule, where a rule exists (1.0 when nothing to compare).
    Used only as the controller's consistency signal; the value shown is still the AI's."""
    checked = agreed = 0
    for f in ai_facts:
        n = f.get('lab_id')
        if not f.get('converted') or n is None or not (0 <= n < len(labs)):
            continue
        lab = labs[n]
        m = _NUMBER.search(f['converted'])
        unit = f['converted'][m.end():].strip() if m else ''
        rule = T.convert(lab.get('analyte'), lab.get('value_numeric'), lab.get('unit'), unit) if m and lab.get('analyte') else None
        if not rule:
            continue
        checked += 1
        if abs(float(m.group(0)) - rule['value']) <= max(0.02 * rule['value'], 0.05):
            agreed += 1
    return agreed / checked if checked else 1.0
