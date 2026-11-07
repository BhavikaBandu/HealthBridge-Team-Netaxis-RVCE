"""Procedure agent: one finding per procedure (planned or completed).

Code compares the patient's procedure (record + linked referral notes) with the best destination service from the
procedure retriever: scan type, body area, contrast, protocol. One AI call then reads the referral text and the
retrieved provider passages and fills cells code left as "Not stated" (with a quote that code checks), gives its own
match strength, and writes the one-line "verify" advice.
"""
import re

from backend.ingestion import terminology as T
from backend.retrieval.evidence import search_procedures
from .common import (FILL_RULES, FILLS_SCHEMA, STRENGTH_RULES, STRENGTH_SCHEMA, ai_match, ai_or_fallback,
                     ai_status, apply_fills, blank_cells, dedupe_sources, source_entry)
from . import llm

STYLE = "Write for a doctor in plain words. Do not use system words such as 'ingested', 'sources', 'evidence', 'evidenced', 'record status' or 'match'. "
SYSTEM = (
    'You review a cross-border procedure comparison prepared by deterministic code from provider/official sources, '
    'together with the patient\'s referral/record text (first column) and the retrieved provider passages (second '
    'column). ' + FILL_RULES + STRENGTH_RULES +
    'VERIFY: ONE short sentence (max 20 words) telling a doctor what must be confirmed with the destination provider '
    '(e.g. protocol, contrast, side, availability). Never claim equivalence, availability or approval. '
    'Do not introduce numbers that are not in the input. ' + STYLE + 'Return JSON only.')
SCHEMA = {'type': 'object', 'required': ['verify', 'strength', 'strength_reason', 'fills'], 'properties': {
    'verify': {'type': 'string'}, **STRENGTH_SCHEMA, 'fills': FILLS_SCHEMA}}
PASSAGE_CHARS = 2500
_RANK = {'exact': 0}


def _rank(match):
    return _RANK.get(match, 1 if str(match).startswith('broader') else 2)


def _contrast_from(text):
    t = (text or '').lower()
    if 'contrast' not in t:
        return 'Not stated'
    if re.search(r'contrast[^.]*not specified|not specified[^.]*contrast', t):
        return 'Not specified'
    if re.search(r'without contrast|non-contrast|no contrast', t):
        return 'Without contrast'
    if re.search(r'with contrast|contrast-enhanced', t):
        return 'With contrast'
    return 'Mentioned'


def analyse(s, proc, ctx, referral_text=''):
    text = f'{proc.name}. {proc.notes or ""}. {referral_text}'
    modality = (T.modalities_in(proc.name) or T.modalities_in(text) or [None])[0]
    anatomy = next((a for a in T.anatomy_in(proc.name) if a != 'joints'), None) or (T.anatomy_in(proc.name) or [None])[0]
    side = T.laterality_in(proc.name)
    r = search_procedures(s, proc.name, countries=[ctx.destination], modality=modality, anatomy=anatomy)
    terms = [x for x in r['results'] if x['retrieval_method'] == 'structured_terminology' and x['country'] == ctx.destination]
    terms.sort(key=lambda x: _rank(x['facts']['anatomy_match']))
    best = terms[0] if terms else None
    origin_hits = search_procedures(s, proc.name, countries=[ctx.origin], modality=modality, anatomy=anatomy)['results']
    origin_hits = [x for x in origin_hits if x['retrieval_method'] == 'structured_terminology'
                   and x['facts']['anatomy_match'] == 'exact']

    body = ' '.join(filter(None, [(side or '').replace('single (left or right)', '').strip(), anatomy])).capitalize() or 'Not stated'
    o_col = {'Scan': modality or 'Not stated', 'Body area': body, 'Contrast': _contrast_from(text), 'Protocol': 'Not stated'}
    status = 'planned' if proc.status == 'planned' else 'done'
    if best:
        f = best['facts']
        scan = f['modality'] + (', 3 Tesla' if re.search(r'\b3\s*T\b', f['term']) else '')
        match = f['anatomy_match']
        area = anatomy.capitalize() if match == 'exact' else ('Joints (general)' if 'joints' in match else ', '.join(f['anatomy']).capitalize() or 'Not stated')
        d_col = {'Scan': scan, 'Body area': area, 'Contrast': 'Stated' if f.get('contrast_statement') else 'Not stated',
                 'Protocol': f.get('protocol') or 'Not stated'}
        if match == 'exact':
            label, confidence = 'Exact match', 'High'
        else:
            label, confidence = 'Partial match', 'Medium'
        provider = (f.get('provider') or '').split(',')[0]
        term = f['term'] if f['term'] != f['term'].upper() else f['term'].title().replace('Mri', 'MRI').replace('Ct', 'CT')
        title = f'{proc.name} → {term}, {provider}'.rstrip(', ')
        patient_line = f'→ {term}, {provider}'.rstrip(', ')
        if f.get('laterality'):
            o_col['Side'], d_col['Side'] = (side or 'Not stated'), f['laterality']
    else:
        d_col = {k: '—' for k in o_col}
        d_col['Scan'] = 'No match found'
        label, confidence = f'No {ctx.destination_short} match found', 'Low'
        title, patient_line = f'{proc.name} → No {ctx.destination_short} match found', f'No {ctx.destination_short} match found'
    rows = [[k, o_col[k], d_col.get(k, 'Not stated')] for k in o_col]
    cols = [f'{ctx.origin_name} ({"referral" if referral_text else "record"})', ctx.destination_short]
    sources = dedupe_sources(([source_entry(best)] if best else []) + [source_entry(x) for x in origin_hits[:1]])
    missing = [row[0].lower() for row in rows if row[2] in ('Not stated', '—') or row[1] in ('Not stated', 'Not specified')]
    fallback = (f'Confirm {", ".join(dict.fromkeys(missing)) or "details"} and availability with the '
                f'{ctx.destination_short} provider.' if best else
                f'No matching service is in the {ctx.destination_short} sources; confirm with a local provider.')
    # Text the AI may fill from: the patient's record/referral (first column), the provider's pages (second column).
    passages = {cols[0]: [{'source': 'Patient referral' if referral_text else 'Patient record',
                           'text': f'{proc.name}. {proc.notes or ""}\n{referral_text}'.strip()[:PASSAGE_CHARS]}]}
    if best:
        items = [{'source': best['source_id'], 'text': best['evidence_text']}]
        items += [{'source': x['source_id'], 'text': x['evidence_text']} for x in r['results']
                  if x['source_id'] == best['source_id'] and x['retrieval_method'] in ('keyword', 'semantic')]
        out, size = [], 0
        for it in items:
            if size + len(it['text']) > PASSAGE_CHARS and out:
                break
            out.append(it)
            size += len(it['text'])
        passages[cols[1]] = out
    blanks = [b for b in blank_cells(rows, cols) if passages.get(b['column'])]

    payload = {'procedure': {'name': proc.name, 'status': status, 'notes': proc.notes}, 'comparison': {'columns': cols, 'rows': rows},
               'match': label, 'confidence': confidence,
               'blank_cells': [{k: v for k, v in b.items() if k != '_pos'} for b in blanks],
               'passages': {col: [p['text'] for p in items] for col, items in passages.items()},
               'missing_evidence': [m['detail'] for m in r['missing_evidence']]}
    allowed = llm.numbers_in(str(payload))
    data = ai_or_fallback(ctx, f'procedure {proc.name}', SYSTEM, payload, SCHEMA, {'verify': fallback},
                          lambda d: (llm.check_text(d.get('verify'), allowed, 'verify'), llm.check_length(d.get('verify'), 28, 'verify')))
    fill_stats = {}
    filled = apply_fills(rows, blanks, data.get('fills'), passages, fill_stats)
    return {'agent': 'procedure', 'record_type': 'procedure', 'record_id': proc.id, 'title': title,
            'match_label': label, 'confidence': confidence, 'patient_line': patient_line,
            'comparison': {'columns': cols, 'rows': rows, 'filled': filled, 'ai_match': ai_match(data)},
            'facts': [], 'context': None, 'verify': data['verify'], 'sources': sources,
            # for the controller only (not stored)
            '_ai': ai_status(data), '_fills': fill_stats, '_planned': status == 'planned'}
