"""Medicine agent: one finding per medication (ongoing or stopped).

Code decides the destination candidate, the ingredient/strength comparison, match label and confidence (from the
medicine retriever). One AI call then reads the retrieved label passages and:
  - fills table cells code left as "Not stated" (only from the passages, with a quote that code checks),
  - gives its own match strength (shown next to code's confidence),
  - checks the medicine against the patient's allergies (drug-family knowledge; code's exact check stays),
  - writes the one-line "verify" advice.
"""
import re

from backend.ingestion import terminology as T
from backend.retrieval.evidence import search_medicines
from .common import (FILL_RULES, FILLS_SCHEMA, STRENGTH_RULES, STRENGTH_SCHEMA, ai_match, ai_or_fallback,
                     ai_status, apply_fills, blank_cells, dedupe_sources, source_entry)
from . import llm

STYLE = "Write for a doctor in plain words. Do not use system words such as 'ingested', 'sources', 'evidence', 'evidenced', 'record status' or 'match'. "
SYSTEM = (
    'You review a cross-border medicine comparison prepared by deterministic code from official/manufacturer sources, '
    'together with the label passages retrieved for each product. ' + FILL_RULES + STRENGTH_RULES +
    'ALLERGY: compare the medicine\'s active ingredients with the patient\'s recorded allergies using your '
    'pharmacology knowledge (same drug, same drug family, known cross-reactions). status = "direct" (same ingredient), '
    '"possible" (same family or a known cross-reaction) or "none"; note = one short sentence (max 20 words) for a '
    'doctor, e.g. "Ibuprofen allergy: paracetamol is not an NSAID; cross-reaction is uncommon." '
    'VERIFY: ONE short sentence (max 20 words) telling a doctor what still needs checking before relying on the '
    'match (cells still "Not stated" after your fills, local availability). Never say a medicine is safe, approved, '
    'substitutable or available. Do not introduce numbers that are not in the input. ' + STYLE + 'Return JSON only.')
SCHEMA = {'type': 'object', 'required': ['verify', 'strength', 'strength_reason', 'allergy', 'fills'], 'properties': {
    'verify': {'type': 'string'}, **STRENGTH_SCHEMA, 'fills': FILLS_SCHEMA,
    'allergy': {'type': 'object', 'required': ['status', 'note'], 'properties': {
        'status': {'type': 'string', 'enum': ['direct', 'possible', 'none']}, 'note': {'type': 'string'}}}}}
PASSAGE_CHARS = 2500


def _strength(med):
    if med.strength_value is None:
        return ''
    return f'{float(med.strength_value):g} {med.strength_unit or ""}'.strip()


def _ingredients(facts):
    return ' + '.join(f"{i['ingredient'].capitalize()} {i['strength']:g} {i['unit']}" if i['strength'] is not None
                      else i['ingredient'].capitalize() for i in facts['ingredients'])


_FORM = re.compile(r'(film[\s-]*coated|uncoated|chewable|effervescent|dispersible)?\s*'
                   r'(tablet|capsule|caplet|syrup|suspension|injection|cream|drops)', re.I)


def _form(facts):
    """Short dosage form ("Film-coated tablet") from the label wording."""
    m = _FORM.search(facts.get('form_detail') or '')
    if m:
        kind = (m.group(1) or '').replace(' ', '-').lower()
        return f'{kind} {m.group(2).lower()}'.strip().capitalize()
    return (facts.get('dosage_form') or 'Not stated').capitalize()


def _short_name(facts):
    """Product name, with the strength appended when the name has none ("Panadol Advance 500 mg")."""
    name = facts['product_name']
    if any(ch.isdigit() for ch in name):
        return name
    strengths = [f"{i['strength']:g} {i['unit']}" for i in facts['ingredients'] if i['strength'] is not None]
    return f"{name} {' + '.join(strengths)}".strip()


def analyse(s, med, ctx):
    strength = _strength(med)
    display = ' '.join(filter(None, [med.brand or med.name, strength]))
    query = ' '.join(filter(None, [med.brand, med.name, strength]))
    r = search_medicines(s, query, origin_country=ctx.origin, target_country=ctx.destination)
    queried = [x for x in r['results'] if (x.get('facts') or {}).get('role') == 'queried_product']
    queried.sort(key=lambda x: not any('brand' in m for m in x['matched_fields']))
    origin = queried[0] if queried else None
    cand = None
    if origin:
        comp = next((c for c in r['comparisons'] if c['queried_source'] == origin['source_id']
                     and c['queried_product'] == origin['facts']['product_name']), None)
        if comp:
            cand = next((x for x in r['results'] if (x.get('facts') or {}).get('role') == 'target_candidate'
                         and x['facts']['product_name'] == comp['candidate_product']), None)
    else:
        comp = None

    o_name = ctx.origin_name
    d_name = ctx.destination_short
    cols = [o_name, d_name]
    if origin and cand:
        of, cf = origin['facts'], cand['facts']
        rows = [['Ingredients', _ingredients(of), _ingredients(cf)], ['Form', _form(of), _form(cf)],
                ['Route', (of.get('route') or 'Not stated').capitalize(), (cf.get('route') or 'Not stated').capitalize()]]
        if of.get('release_profile') or cf.get('release_profile'):
            rows.append(['Release', (of.get('release_profile') or 'Not stated').capitalize(), (cf.get('release_profile') or 'Not stated').capitalize()])
        same = comp['relationship'] == 'same_ingredients_same_strengths'
        label, confidence = ('Same ingredients and strength', 'High') if same else ('Same ingredients, different strength', 'Medium')
        cand_name = _short_name(cf)
        title, patient_line = f'{display} → {cand_name} ({ctx.destination_short})', f'→ {cand_name}'
    else:
        rows = [['Ingredients', _ingredients(origin['facts']) if origin else f'{med.name} {strength}'.strip(), 'No match found'],
                ['Form', _form(origin['facts']) if origin else (med.dosage_form or 'Not stated').capitalize(), '—']]
        label = 'No product information in sources' if not origin else f'No {ctx.destination_short} match found'
        confidence = 'Low'
        title, patient_line = f'{display} → No {ctx.destination_short} match found', f'No {ctx.destination_short} match found'

    # Allergy check at ingredient level only (no drug-class inference).
    allergens = {T.normalise_ingredient(a) for a in ctx.allergies}
    ingredients = {i['ingredient'] for x in (origin, cand) if x for i in x['facts']['ingredients']}
    overlap = sorted(allergens & ingredients)
    not_stated = sorted({row[0].lower() for row in rows if 'Not stated' in row[1:]})
    sources = dedupe_sources([source_entry(x) for x in (origin, cand) if x] +
                             [source_entry(x) for x in r['results'] if x['retrieval_method'] == 'same_location'])

    if origin and cand:
        fallback = 'Confirm ' + (', '.join(not_stated) + ' and ' if not_stated else '') + \
                   f'availability in the {d_name}. Not a substitution approval.'
    elif origin:
        fallback = f'No {d_name} product with the same ingredients is in the sources; confirm an equivalent locally.'
    else:
        fallback = f'No product information for this medicine is in the sources; confirm an equivalent in the {d_name}.'
    if overlap:
        fallback = f"Ingredient matches a recorded allergy ({', '.join(overlap)}). " + fallback

    # Label passages retrieved for each product, by table column (origin product / destination candidate).
    passages = {}
    for col, prod in ((cols[0], origin), (cols[1], cand)):
        if not prod:
            continue
        items = [{'source': prod['source_id'], 'text': prod['evidence_text']}]
        items += [{'source': x['source_id'], 'text': x['evidence_text']} for x in r['results']
                  if x['source_id'] == prod['source_id'] and x['retrieval_method'] != 'structured_sql']
        out, size = [], 0
        for it in items:
            if size + len(it['text']) > PASSAGE_CHARS and out:
                break
            out.append(it)
            size += len(it['text'])
        passages[col] = out
    blanks = [b for b in blank_cells(rows, cols) if passages.get(b['column'])]

    payload = {'medicine_record': {'display': display, 'status': 'ongoing' if med.ongoing else 'stopped'},
               'comparison': {'columns': cols, 'rows': rows}, 'match': label, 'confidence': confidence,
               'blank_cells': [{k: v for k, v in b.items() if k != '_pos'} for b in blanks],
               'passages': {col: [p['text'] for p in items] for col, items in passages.items()},
               'patient_allergies': ctx.allergies or [], 'exact_allergy_overlap': overlap,
               'missing_evidence': [m['detail'] for m in r['missing_evidence']]}
    allowed = llm.numbers_in(str(payload))

    def validate(d):
        llm.check_text(d.get('verify'), allowed, 'verify')
        llm.check_length(d.get('verify'), 28, 'verify')
        note = (d.get('allergy') or {}).get('note')
        llm.check_text(note, allowed, 'allergy note')
        llm.check_length(note, 28, 'allergy note')

    data = ai_or_fallback(ctx, f'medicine {display}', SYSTEM, payload, SCHEMA, {'verify': fallback}, validate)
    fill_stats = {}
    filled = apply_fills(rows, blanks, data.get('fills'), passages, fill_stats)
    allergy = _allergy(ctx.allergies, overlap, data.get('allergy'))
    return {'agent': 'medicine', 'record_type': 'medication', 'record_id': med.id, 'title': title,
            'match_label': label, 'confidence': confidence, 'patient_line': patient_line,
            'comparison': {'columns': cols, 'rows': rows, 'filled': filled, 'ai_match': ai_match(data),
                           'allergy': allergy},
            'facts': [], 'context': None, 'verify': data['verify'], 'sources': sources,
            # for the controller only (not stored)
            '_ai': ai_status(data), '_fills': fill_stats, '_ongoing': bool(med.ongoing), '_medicine_name': med.name}


def _allergy(allergies, overlap, ai):
    """Allergy line under the table. Code's exact ingredient match always wins; the AI adds drug-family checks."""
    if not allergies:
        return {'status': 'none', 'note': 'No allergies recorded.', 'by': 'code'}
    if overlap:
        note = (ai or {}).get('note') or f"Same ingredient as a recorded allergy ({', '.join(overlap)})."
        return {'status': 'direct', 'note': note, 'by': 'code'}
    if ai and ai.get('status') in ('possible', 'none') and ai.get('note'):
        return {'status': ai['status'], 'note': ai['note'], 'by': 'ai'}
    return {'status': 'unchecked', 'note': f"No exact ingredient match with recorded allergies ({', '.join(allergies)}); "
            'drug-family check not available.', 'by': 'code'}
