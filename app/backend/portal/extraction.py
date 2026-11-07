"""Read uploaded patient documents and store their text and the values printed in them.

Runs after every upload (and for seeded documents). Deterministic, no AI:
- text: every PDF page's text layer is stored (images / scanned PDFs are marked 'no_text_layer', no OCR).
- lab results (Laboratory Report): test name, value as printed, flag, unit, reference interval, method,
  specimen, fasting, collection date, with page/line and the exact text.
- prescriptions (Prescription): each item (medicine, strength, dose text, duration text, quantity) and the
  prescription fields (prescriber, date, patient, stamp/signature, attestation wording).
Every finding starts 'unverified' until a doctor confirms it. Nothing is interpreted or diagnosed.

    python -m backend.portal.extraction            # (re)extract all documents
"""
import re

from sqlalchemy import delete, select

from backend.config import UPLOAD_DIR
from backend.database import SessionLocal
from backend.ingestion import terminology as T
from backend.models import now
from .models import Document, DocumentFinding, DocumentText, Medication

PARSER_VERSION = '1.0'

_VALUE = re.compile(r'^(?P<val>[<>]?\d+(?:\.\d+)?)\s*(?P<flag>HH|LL|H|L|\*)?$')
_UNIT = re.compile(r'^(?:%|[A-Za-zµ][A-Za-z0-9µ%/.^]*(?:/[A-Za-z0-9µ.^]+)*)$')
_REF = re.compile(r'^(?:[<>≤≥]\s*)?\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?$')
_ONE_LINE = re.compile(r'^(?P<name>[A-Za-z][A-Za-z0-9 ,()/%.-]*?)\s+(?P<val>[<>]?\d+(?:\.\d+)?)\s*(?P<flag>HH|LL|H|L|\*)?\s+'
                       r'(?P<unit>%|[A-Za-zµ][A-Za-z0-9µ%/.^]*)\s+(?P<ref>(?:[<>]\s*)?\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)'
                       r'(?:\s+(?P<method>[A-Za-z][A-Za-z ,()-]*))?$')
_HEADERS = {'test name', 'result', 'results', 'units', 'unit', 'bio. ref. interval', 'reference interval', 'method',
            'reference range', 'test', 'value'}
_UNIT_WORDS = {'%', 'mg', 'g', 'mcg', 'iu', 'u', 'fl', 'pg', 'ratio', 'cells', 'mm', 'sec', 'seconds', 'index'}
# "1.00Creatinine" / "(Modified Jaffe,Kinetic)" / "0.70 - 1.30 mg/dL"  (value printed before the name)
_PRE_VALUE = re.compile(r'^(?P<val>[<>]?\d+(?:\.\d+)?)(?P<name>[A-Za-z].*)$')
_METHOD_ONLY = re.compile(r'^\((?P<method>[^)]*)\)$')
_REF_UNIT = re.compile(r'^(?P<ref>(?:[<>≤≥]\s*)?\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)\s+(?P<unit>\S+)$')
_SECTION = re.compile(r"^[A-Z][A-Z0-9 ,&/()'\-]{3,}$")
_SPECIMEN = re.compile(r'\b(serum|plasma|whole blood|blood|urine)\b', re.I)


def _is_unit(u):
    return bool(u) and ('/' in u or u.lower() in _UNIT_WORDS or u.lower().endswith(('/l', '/dl', '/ml')))


def read_pdf_text(path):
    from pypdf import PdfReader   # cryptography is installed for AES-encrypted PDFs
    reader = PdfReader(str(path))
    return [{'page': i + 1, 'text': (p.extract_text() or '').replace('\xa0', ' ')} for i, p in enumerate(reader.pages)]


def _lines(text):
    return [re.sub(r'\s+', ' ', ln).strip() for ln in text.split('\n') if ln.strip()]


def _label_value(text, label):
    """'Collected\\n: 12/12/2026 08:10 AM' or 'Collected : ...' -> value text."""
    m = re.search(rf'(?mi)^\s*{label}\s*(?:\n\s*)?:\s*([^\n]+)', text)
    return m.group(1).strip() if m else None


def _ref_bounds(ref):
    if ref and '-' in ref and not ref.lstrip().startswith(('<', '>')):
        nums = re.findall(r'\d+(?:\.\d+)?', ref)
        if len(nums) >= 2:
            return float(nums[0]), float(nums[1])
    return None, None


def lab_results(pages):
    full = '\n'.join(p['text'] for p in pages)
    doc_specimen = _label_value(full, r'(?:Sample Type|Specimen)')
    fasting_note = _label_value(full, r'Fasting')
    collected = _label_value(full, r'Collected')
    collected = collected if collected and re.search(r'\d', collected) else None
    out = []
    for p in pages:
        lines = _lines(p['text'])
        section = None
        i = 0
        while i < len(lines):
            line = lines[i]
            row = None
            m = _ONE_LINE.match(line)
            pm = _PRE_VALUE.match(line)
            if m and m.group('name').lower() not in _HEADERS and _is_unit(m.group('unit')):
                row = {**m.groupdict(), 'span': 1}
            elif (pm and i + 2 < len(lines) and _METHOD_ONLY.match(lines[i + 1]) and _REF_UNIT.match(lines[i + 2])
                  and _is_unit(_REF_UNIT.match(lines[i + 2]).group('unit'))):
                rm = _REF_UNIT.match(lines[i + 2])
                row = {'name': pm.group('name'), 'val': pm.group('val'), 'flag': None, 'unit': rm.group('unit'),
                       'ref': rm.group('ref'), 'method': _METHOD_ONLY.match(lines[i + 1]).group('method'), 'span': 3}
            elif (i + 3 < len(lines) and line.lower() not in _HEADERS and not _VALUE.match(line)
                  and _VALUE.match(lines[i + 1]) and _UNIT.match(lines[i + 2]) and _is_unit(lines[i + 2])
                  and _REF.match(lines[i + 3])):
                v = _VALUE.match(lines[i + 1])
                row = {'name': line, 'val': v.group('val'), 'flag': v.group('flag'), 'unit': lines[i + 2],
                       'ref': lines[i + 3], 'method': None, 'span': 4}
                # optional method cell: the next line, unless it starts the next result row or a section
                nxt = lines[i + 4] if i + 4 < len(lines) else None
                after = lines[i + 5] if i + 5 < len(lines) else ''
                if nxt and not _SECTION.match(nxt) and not _VALUE.match(after) and len(nxt) < 40 \
                        and re.match(r'^[A-Za-z][A-Za-z ,()-]*$', nxt):
                    row['method'], row['span'] = nxt, 5
            if row:
                name = row['name'].strip()
                lo, hi = _ref_bounds(row['ref'])
                specimen = (_SPECIMEN.search(section or '') or _SPECIMEN.search(name) or
                            _SPECIMEN.search(doc_specimen or ''))
                fasting = bool(re.search(r'fast', f'{section or ""} {name}', re.I)) or None
                out.append({'page': p['page'], 'line': i + 1, 'evidence': '\n'.join(lines[i:i + row['span']]), 'data': {
                    'test_name': name, 'analyte': T.normalise_analyte(name), 'value': row['val'],
                    'value_numeric': float(row['val'].lstrip('<>')), 'flag': row['flag'], 'unit': row['unit'],
                    'unit_system': T.UNIT_SYSTEMS.get(row['unit'].lower()), 'reference_interval': row['ref'],
                    'ref_low': lo, 'ref_high': hi, 'method': row.get('method'), 'section': section,
                    'specimen': specimen.group(1).lower() if specimen else None, 'fasting': fasting,
                    'fasting_note': fasting_note if fasting else None, 'collected': collected}})
                i += row['span']
                continue
            if _SECTION.match(line) and line.lower() not in _HEADERS:
                section = line
            i += 1
    return out


_ITEM = re.compile(r'^(?:\d+\s+)?(?P<form>Cap|Caps|Tab|Tabs|Syp|Syr|Inj|Oint|Drops?)\.?\s+(?P<name>.+)$', re.I)
_STRENGTH = re.compile(r'(\d+(?:\.\d+)?)\s*(mg|g|mcg|ml|iu)\b', re.I)
_DURATION = re.compile(r'^(as needed|sos|prn|stat|\d+\s*(?:day|week|month)s?|for\s+\d+\s*(?:day|week|month)s?.*|x\s*\d+\s*(?:day|week|month)s?|continue.*)$', re.I)
_QTY = re.compile(r'^(\d+\s*(?:\([a-z ]+\))?|\d+\s*(?:tablets?|capsules?|tabs?|caps?)|\d*\s*strips?\s*(?:\(\d+\))?.*)$', re.I)
_STOP = re.compile(r'^(advice|review|follow[- ]?up|signature|investigations?|note)\b', re.I)


def prescription(pages, patient_meds):
    full = '\n'.join(p['text'] for p in pages)
    out = []
    for p in pages:
        lines = _lines(p['text'])
        i = 0
        while i < len(lines):
            m = _ITEM.match(lines[i])
            if not m:
                i += 1
                continue
            start = i
            name = m.group('name')
            j = i + 1
            if j < len(lines) and lines[j].startswith('('):          # "(Paracetamol 500 mg)"
                name = f'{name} {lines[j]}'
                j += 1
            body = []
            while j < len(lines) and not _ITEM.match(lines[j]) and not _STOP.match(lines[j]) and not re.fullmatch(r'\d+', lines[j]):
                body.append(lines[j])
                j += 1
            duration = next((b for b in body if _DURATION.match(b)), None)
            qty = next((b for b in reversed(body) if _QTY.match(b) and b != duration), None)
            dose = ' '.join(b for b in body if b not in (duration, qty)) or None
            strength = _STRENGTH.search(name)
            words = re.sub(r'[^a-z ]', ' ', name.lower()).split()
            matched = next((mid for mid, label in patient_meds if any(w in label for w in words if len(w) > 3)), None)
            out.append({'page': p['page'], 'line': start + 1, 'evidence': '\n'.join(lines[start:j]), 'data': {
                'form': m.group('form').capitalize(), 'medicine': name,
                'strength': f'{strength.group(1)} {strength.group(2)}' if strength else None,
                'dose_text': dose, 'duration_text': duration,
                'duration_stated': bool(duration and re.search(r'\d+\s*(day|week|month)', duration, re.I)),
                'quantity_text': qty, 'matched_medication_id': str(matched) if matched else None}})
            i = j
    fields = {
        'prescriber': next((ln for ln in _lines(full) if re.match(r'^Dr\.?\s', ln)), None),
        'issue_date': (re.search(r'(?i)\bDate\s*:\s*([^\n]+)', full) or [None, None])[1],
        'patient_name': (re.search(r'(?i)\bPatient(?: Name)?\s*:\s*([^\n]+)', full) or [None, None])[1],
        'registration_number': (re.search(r'(?i)Reg\.?\s*No\.?\s*:?\s*([A-Z0-9-]+)', full) or [None, None])[1],
        'signature_or_stamp_mentioned': bool(re.search(r'(?i)signature|stamp', full)),
        'attestation_wording_found': bool(re.search(r'(?i)attest|apostille|legali[sz]|embassy|consulate|MOFA', full)),
        'items': len(out),
    }
    evidence = '\n'.join(v for v in (fields['prescriber'], fields['issue_date'] and f"Date: {fields['issue_date']}",
                                      fields['patient_name'] and f"Patient: {fields['patient_name']}") if v)
    out.append({'page': 1, 'line': None, 'evidence': evidence or '(document header)', 'kind': 'prescription_fields',
                'data': fields})
    return out


def extract_document(s, d):
    """(Re)extract one document. Replaces its stored text and unreviewed findings; keeps reviewed ones."""
    path = UPLOAD_DIR / d.patient_id.hex / d.storage_key
    s.execute(delete(DocumentText).where(DocumentText.document_id == d.id))
    s.execute(delete(DocumentFinding).where(DocumentFinding.document_id == d.id, DocumentFinding.status == 'unverified'))
    if d.mime_type != 'application/pdf':
        s.add(DocumentText(document_id=d.id, patient_id=d.patient_id, status='no_text_layer', method='image (no OCR)',
                           parser_version=PARSER_VERSION, page_count=0, pages=[], extracted_at=now()))
        return {'status': 'no_text_layer', 'findings': 0}
    try:
        pages = read_pdf_text(path)
    except Exception as exc:   # unreadable / damaged file: record, never break the upload
        s.add(DocumentText(document_id=d.id, patient_id=d.patient_id, status='failed', method='pypdf text layer',
                           parser_version=PARSER_VERSION, page_count=0, pages=[], error=f'{type(exc).__name__}: {exc}'[:500],
                           extracted_at=now()))
        return {'status': 'failed', 'findings': 0}
    has_text = sum(len(p['text'].strip()) for p in pages) >= 20
    s.add(DocumentText(document_id=d.id, patient_id=d.patient_id, status='extracted' if has_text else 'no_text_layer',
                       method='pypdf text layer', parser_version=PARSER_VERSION, page_count=len(pages), pages=pages,
                       extracted_at=now()))
    findings = []
    if has_text and d.doc_type == 'laboratory':
        findings = [{**f, 'kind': 'lab_result'} for f in lab_results(pages)]
    elif has_text and d.doc_type == 'prescription':
        meds = [(m.id, ' '.join(filter(None, [m.name, m.brand])).lower())
                for m in s.scalars(select(Medication).where(Medication.patient_id == d.patient_id,
                                                            Medication.archived_at.is_(None)))]
        findings = [{'kind': 'prescription_item', **f} if 'kind' not in f else f for f in prescription(pages, meds)]
    for f in findings:
        s.add(DocumentFinding(document_id=d.id, patient_id=d.patient_id, kind=f['kind'], data=f['data'],
                              evidence_text=f['evidence'], page=f['page'], line=f['line']))
    s.flush()
    return {'status': 'extracted' if has_text else 'no_text_layer', 'findings': len(findings)}


def extract_by_id(document_id):
    """Background-task entry point (own session)."""
    with SessionLocal() as s:
        d = s.get(Document, document_id)
        if d is not None:
            extract_document(s, d)
            s.commit()


def main():
    with SessionLocal() as s:
        docs = s.scalars(select(Document).where(Document.archived_at.is_(None))).all()
        for d in docs:
            r = extract_document(s, d)
            print(f'{d.name[:60]:60} {d.doc_type:20} {r}')
        s.commit()


if __name__ == '__main__':
    main()


# ------------------------------------------------------------------ API payloads
REVIEW_STATUSES = ('confirmed', 'rejected', 'unverified')


def summary(s, d):
    """Short status for document lists."""
    t = s.get(DocumentText, d.id)
    findings = s.scalars(select(DocumentFinding).where(DocumentFinding.document_id == d.id)).all()
    return {'status': t.status if t else 'pending', 'pages': t.page_count if t else 0,
            'findings': len(findings), 'unverified': sum(f.status == 'unverified' for f in findings)}


def finding_payload(f):
    return {'id': str(f.id), 'kind': f.kind, 'data': f.data, 'evidence_text': f.evidence_text, 'page': f.page,
            'line': f.line, 'status': f.status, 'reviewed_at': f.reviewed_at.isoformat() if f.reviewed_at else None}


def extraction_payload(s, d):
    t = s.get(DocumentText, d.id)
    findings = s.scalars(select(DocumentFinding).where(DocumentFinding.document_id == d.id)
                         .order_by(DocumentFinding.kind, DocumentFinding.page, DocumentFinding.line)).all()
    return {'document_id': str(d.id), 'status': t.status if t else 'pending', 'method': t.method if t else None,
            'parser_version': t.parser_version if t else None, 'error': t.error if t else None,
            'extracted_at': t.extracted_at.isoformat() if t else None, 'pages': t.pages if t else [],
            'findings': [finding_payload(f) for f in findings],
            'note': 'Values read automatically from the document text. Unverified until a doctor confirms them; '
                    'the original document remains the record.'}
