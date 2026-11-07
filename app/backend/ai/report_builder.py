"""Printable travel health report: the patient's Travel Health Summary as a document, in English or Arabic.

English content is built by code from the stored trip analysis (same items and order as the summary page).
Arabic: one AI call translates all display strings; numbers/units must be preserved and medicine/product names
stay in Latin script (validated). Fixed labels (confidence, status, headings) use a reviewed glossary.
"""
import re
from datetime import datetime

from . import llm

SHORT = {'AE': 'UAE', 'GB': 'UK', 'US': 'USA'}
TAGS = {'stopped': 'stopped', 'completed': 'done', 'planned': 'planned'}
GLOSSARY_AR = {
    'Travel health report': 'تقرير الصحة أثناء السفر', 'Patient': 'المريض', 'Patient ID': 'رقم المريض',
    'Trip': 'الرحلة', 'Generated': 'تاريخ الإنشاء', 'Lab results': 'نتائج المختبر',
    'Flags to act on': 'تنبيهات تتطلب إجراء', 'Quantity advice': 'إرشادات الكمية',
    'High': 'عالية', 'Medium': 'متوسطة', 'Low': 'منخفضة',
    'stopped': 'متوقف', 'done': 'تم', 'planned': 'مخطط', 'Confidence': 'درجة الثقة',
    'Complete patient report': 'التقرير الكامل للمريض', 'Doctor': 'الطبيب', 'Summary': 'الملخص',
    'Findings': 'النتائج التفصيلية', 'Medications': 'الأدوية', 'Procedures': 'الإجراءات الطبية', 'Documents': 'المستندات',
    'Sources': 'المصادر',
}
TRANSLATE_SYSTEM = (
    'Translate each string of a patient travel-health report from English to Modern Standard Arabic for a patient. '
    'Keep the meaning exactly; do not add or remove advice. Keep every number, unit and symbol exactly as written '
    '(e.g. 108 mg/dL, 6.0 mmol/L, 16-day, 3 months -> keep digits as Western digits). Always write numbers as digits, '
    'including 1 (write "1 كبسولة", not "كبسولة واحدة"). Keep medicine, brand, product, '
    'hospital and organisation names in Latin script (e.g. Crocin Advance, Panadol Advance, Tramadol, Mediclinic). '
    'Keep arrows (→) and the order of items. Return JSON only: {"items": [{"id": n, "text": "..."}]} with every id.')
TRANSLATE_SCHEMA = {'type': 'object', 'required': ['items'], 'properties': {'items': {'type': 'array', 'items': {
    'type': 'object', 'required': ['id', 'text'], 'properties': {'id': {'type': 'integer'}, 'text': {'type': 'string'}}}}}}


def _place(code, name):
    return SHORT.get(code, name)


def _date(iso):
    return datetime.fromisoformat(iso).strftime('%d %b %Y') if iso else ''


def build_english(payload, patient_name, patient_code):
    """Report content (English) from analysis_payload(); mirrors the Travel Health Summary page."""
    t = payload['trip']
    dest = _place(t['destination_country'], t['destination_name'])
    trip_label = (f"{_place(t['origin_country'], t['origin_name'])} → {dest} · {_date(t['departure_date'])}"
                  + (f" – {_date(t['return_date'])}" if t.get('return_date') else ''))

    def rows(agent):
        return [{'main': f['title'].split(' → ')[0], 'sub': f['patient_line'] or '', 'tag': TAGS.get(f.get('record_status')),
                 'badge': f['confidence']} for f in payload['findings'] if f['agent'] == agent]

    labs = [{'main': f"{x['label']} {x['value']}", 'sub': f"≈ {x['converted']} ({dest} units)", 'tag': None, 'badge': None}
            for f in payload['findings'] if f['agent'] == 'report' for x in (f.get('facts') or []) if x.get('converted')]
    sections = [{'title': f'Medicines in the {dest}', 'rows': rows('medicine')},
                {'title': f'Procedures in the {dest}', 'rows': rows('procedure')}]
    if labs:
        sections.append({'title': 'Lab results', 'rows': labs})
    return {
        'language': 'en', 'dir': 'ltr', 'title': 'Travel health report',
        'meta': [['Patient', patient_name], ['Patient ID', patient_code], ['Trip', trip_label],
                 ['Generated', datetime.now().strftime('%d %b %Y, %H:%M')]],
        'sections': sections,
        'flags_title': 'Flags to act on',
        'flags': [{'severity': f['severity'], 'text': f['text']} for f in payload['flags'] if f['kind'] == 'flag'],
        'quantity_title': 'Quantity advice',
        'quantity': [{'subject': f['subject'], 'text': f['text']} for f in payload['flags'] if f['kind'] == 'quantity'],
        'disclaimer': 'Generated from your records and official sources. Not a medical decision or a travel clearance. '
                      'Check with your doctor.',
    }


def build_doctor(payload, patient_name, patient_code, doctor_name, source_titles):
    """Complete report for the doctor: the patient summary + every finding box + flags with sources + source list."""
    content = build_english(payload, patient_name, patient_code)
    content['title'] = 'Complete patient report'
    content['meta'].insert(3, ['Doctor', doctor_name])
    content['summary_title'], content['details_title'], content['sources_title'] = 'Summary', 'Findings', 'Sources'
    by_source = {f['id']: f for f in payload['findings']}
    groups = []
    for agent, heading in (('medicine', 'Medications'), ('procedure', 'Procedures'), ('report', 'Documents')):
        blocks = []
        for f in (x for x in by_source.values() if x['agent'] == agent):
            comp = f.get('comparison') or {}
            al = comp.get('allergy') or {}
            allergy = None
            if al.get('note'):
                allergy = al['note'] + (' (AI check – confirm with prescriber)' if al.get('by') == 'ai' else '')
            blocks.append({'title': f['title'], 'label': f.get('match_label'), 'badge': f.get('confidence'),
                           'allergy': allergy, 'allergy_status': al.get('status'),
                           'columns': comp.get('columns') or [], 'rows': comp.get('rows') or [],
                           'facts': [{'label': x.get('label'), 'value': x.get('value'), 'converted': x.get('converted') or '',
                                      'problem': bool(x.get('problem'))} for x in f.get('facts') or []],
                           'context': f.get('context'), 'verify': f.get('verify'),
                           'sources': [s['label'] for s in f.get('sources') or []]})
        if blocks:
            groups.append({'heading': heading, 'blocks': blocks})
    content['details'] = groups
    labels = {f['id']: f for f in payload['flags']}
    content['flags'] = [{'severity': f['severity'], 'text': f['text'], 'sources': [s['label'] for s in f.get('sources') or []]}
                        for f in labels.values() if f['kind'] == 'flag']
    content['quantity'] = [{'subject': f['subject'], 'text': f['text'], 'sources': [s['label'] for s in f.get('sources') or []]}
                           for f in labels.values() if f['kind'] == 'quantity']
    used = sorted({s['source_id'] for f in payload['findings'] + payload['flags'] for s in f.get('sources') or []})
    content['source_list'] = [{'id': sid, 'title': source_titles.get(sid, '')} for sid in used]
    content['disclaimer'] = ('Generated from the patient’s records and official sources for review by a clinician. '
                             'Not a clinical decision, prescribing advice or a travel clearance.')
    return content


def translate_arabic(content):
    """Arabic copy of `content`. Raises llm.LLMError if the AI is unavailable or a translation fails the checks."""
    strings, setters = [], []

    def add(text, setter):
        if text:
            strings.append(text)
            setters.append(setter)

    ar = {**content, 'language': 'ar', 'dir': 'rtl', 'title': GLOSSARY_AR.get(content['title'], content['title']),
          'meta': [[GLOSSARY_AR.get(k, k), v] for k, v in content['meta']],
          'flags_title': GLOSSARY_AR['Flags to act on'], 'quantity_title': GLOSSARY_AR['Quantity advice'],
          'sections': [{**sec, 'rows': [dict(r) for r in sec['rows']]} for sec in content['sections']],
          'flags': [dict(f) for f in content['flags']], 'quantity': [dict(q) for q in content['quantity']]}
    trip = next((i for i, (k, _) in enumerate(content['meta']) if k == 'Trip'), None)
    if trip is not None:
        add(content['meta'][trip][1], lambda v, i=trip: ar['meta'][i].__setitem__(1, v))
    for sec in ar['sections']:
        title = sec['title']
        if title in GLOSSARY_AR:
            sec['title'] = GLOSSARY_AR[title]
        else:
            add(title, lambda v, s=sec: s.__setitem__('title', v))
        for r in sec['rows']:
            add(r['main'], lambda v, r=r: r.__setitem__('main', v))
            add(r['sub'], lambda v, r=r: r.__setitem__('sub', v))
            r['tag'] = GLOSSARY_AR.get(r['tag'], r['tag']) if r.get('tag') else None
            r['badge'] = GLOSSARY_AR.get(r['badge'], r['badge']) if r.get('badge') else None
    for f in ar['flags']:
        add(f['text'], lambda v, f=f: f.__setitem__('text', v))
    for q in ar['quantity']:
        add(q['text'], lambda v, q=q: q.__setitem__('text', v))
    # Doctor report parts (detailed findings; source names stay as they are).
    for f in ar['flags'] + ar['quantity']:
        f['sources'] = list(f.get('sources') or [])
    if content.get('details'):
        ar['details_title'] = GLOSSARY_AR.get(content['details_title'], content['details_title'])
        ar['sources_title'] = GLOSSARY_AR.get(content['sources_title'], content['sources_title'])
        ar['summary_title'] = GLOSSARY_AR.get(content['summary_title'], content['summary_title'])
        ar['details'] = []
        for g in content['details']:
            group = {'heading': GLOSSARY_AR.get(g['heading'], g['heading']), 'blocks': []}
            for b in g['blocks']:
                nb = {**b, 'columns': list(b.get('columns') or []), 'rows': [list(r) for r in b.get('rows') or []],
                      'facts': [dict(x) for x in b.get('facts') or []], 'sources': list(b.get('sources') or [])}
                nb['badge'] = GLOSSARY_AR.get(b.get('badge'), b.get('badge')) if b.get('badge') else None
                for key in ('title', 'label', 'allergy', 'context', 'verify'):
                    add(b.get(key), lambda v, nb=nb, key=key: nb.__setitem__(key, v))
                for i, col in enumerate(nb['columns']):
                    add(col, lambda v, nb=nb, i=i: nb['columns'].__setitem__(i, v))
                for r in nb['rows']:
                    for i, cell in enumerate(r):
                        add(cell, lambda v, r=r, i=i: r.__setitem__(i, v))
                for x in nb['facts']:
                    for key in ('label', 'value', 'converted'):
                        add(x.get(key), lambda v, x=x, key=key: x.__setitem__(key, v))
                group['blocks'].append(nb)
            ar['details'].append(group)
        ar['source_list'] = [dict(x) for x in content.get('source_list') or []]
    add(content['disclaimer'], lambda v: ar.__setitem__('disclaimer', v))

    last_error = None
    for _attempt in range(2):   # one retry: translations occasionally drop a digit
        try:
            got = _translate(strings)
            break
        except llm.LLMError as exc:
            last_error = exc
    else:
        raise last_error
    for i, out in got.items():
        setters[i](out)
    return ar


_AR_DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
_AR_ONE = re.compile(r'(واحد|واحدة|مرة واحدة)')


def _numbers_match(src, out):
    """Same numbers before and after translation. Arabic-script digits count as digits, and the Arabic word for
    'one' may stand for the digit 1 (natural Arabic grammar); any other difference fails."""
    a, b = llm.numbers_in(src), llm.numbers_in(out.translate(_AR_DIGITS))
    if a == b:
        return True
    return a - b == {'1'} and not (b - a) and bool(_AR_ONE.search(out))


def _translate(strings):
    data = llm.generate(TRANSLATE_SYSTEM, {'items': [{'id': i, 'text': s} for i, s in enumerate(strings)]}, TRANSLATE_SCHEMA)
    got = {int(x['id']): (x['text'] or '').strip() for x in data.get('items', [])}
    if set(got) != set(range(len(strings))):
        raise llm.LLMError('translation is missing items')
    for i, src in enumerate(strings):
        if not got[i]:
            raise llm.LLMError(f'empty translation for item {i}')
        if not _numbers_match(src, got[i]):
            raise llm.LLMError(f'numbers changed in translation of item {i}')
    return got
