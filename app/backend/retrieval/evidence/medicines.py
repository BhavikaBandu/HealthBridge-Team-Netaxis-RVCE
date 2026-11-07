"""Medicine evidence retrieval: structured ingredient/strength matching first, label passages second.

A "candidate" in the target country is a product with the same set of active ingredients. Strength agreement is
checked per ingredient. A candidate is documented correspondence only: it does not establish substitution,
registration, availability or stock in the target country.
"""
import re

from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from backend.ingestion import terminology as T
from backend.models import KnowledgeRecord, MedIngredient, MedProduct
from .common import active_join, missing_sources, passage_search, record_result, status

_STRENGTH = re.compile(r'(\d+(?:\.\d+)?)\s*(mg|g|mcg)\b', re.I)


def _strength_tokens(query):
    """'Augmentin DUO 1 g' -> [(1000.0, 'mg', '1 g')]"""
    return [(*T.normalise_strength(v, u), f'{v} {u}') for v, u in _STRENGTH.findall(query or '')]


def _product_facts(p):
    return {'product_name': p.product_name, 'brand': p.brand, 'country': p.country, 'generic_name': p.generic_name,
            'dosage_form': p.dosage_form, 'form_detail': p.form_detail, 'route': p.route,
            'release_profile': p.release_profile, 'manufacturer': p.manufacturer,
            'ingredients': [{'ingredient': i.ingredient, 'as_written': i.as_written,
                             'strength': float(i.strength_value) if i.strength_value is not None else None,
                             'unit': i.strength_unit, 'evidence_text': i.evidence_text} for i in p.ingredients]}


def _strength_match(p, tokens):
    """Which requested strength(s) this product matches: an ingredient strength or the strength in its name."""
    hits = []
    name = re.sub(r'\s+', '', p.product_name.lower())
    for value, unit, written in tokens:
        if any(i.strength_value is not None and float(i.strength_value) == value and i.strength_unit == unit
               for i in p.ingredients):
            hits.append(f'ingredient strength {written}')
        elif re.sub(r'\s+', '', written.lower()) in name:
            hits.append(f'product name strength {written}')
    return hits


def _compare(origin, cand):
    o = {i.ingredient: i for i in origin.ingredients}
    c = {i.ingredient: i for i in cand.ingredients}
    per = []
    for ing in sorted(o):
        a, b = o[ing], c.get(ing)
        same = b is not None and a.strength_value == b.strength_value and a.strength_unit == b.strength_unit
        per.append({'ingredient': ing,
                    'origin': f'{float(a.strength_value):g} {a.strength_unit}' if a.strength_value is not None else None,
                    'candidate': f'{float(b.strength_value):g} {b.strength_unit}' if b and b.strength_value is not None else None,
                    'same_strength': same})
    all_same = all(x['same_strength'] for x in per)
    form = ('same' if origin.dosage_form and origin.dosage_form == cand.dosage_form else
            'not stated in one or both sources' if not (origin.dosage_form and cand.dosage_form) else 'different')
    return {'relationship': 'same_ingredients_same_strengths' if all_same else 'same_ingredients_different_strengths',
            'per_ingredient': per, 'dosage_form': form,
            'note': 'Documented ingredient/strength correspondence only. Not a substitution, registration, '
                    'availability or stock claim.'}


def search_medicines(session, query, origin_country=None, target_country=None, limit_passages=3):
    query = (query or '').strip()[:200]
    tokens = _strength_tokens(query)
    words = re.sub(_STRENGTH, ' ', query).strip()
    ingredient_terms = {T.normalise_ingredient(w) for w in re.split(r'[,+/]| and ', words) if w.strip()}

    base = active_join(select(MedProduct), MedProduct).options(selectinload(MedProduct.ingredients))
    name_match = or_(func.lower(query).contains(func.lower(MedProduct.brand)),
                     func.similarity(MedProduct.product_name, words) > 0.3)
    ing_match = MedProduct.id.in_(select(MedIngredient.product_id).where(MedIngredient.ingredient.in_(ingredient_terms)))
    stmt = base.where(or_(name_match, ing_match))
    if origin_country:
        stmt = stmt.where(MedProduct.country == origin_country)
    found = list(session.scalars(stmt.order_by(MedProduct.id)).unique())
    origins = []
    for p in found:
        matched = []
        if p.brand.lower() in query.lower():
            matched.append(f'brand "{p.brand}"')
        if {i.ingredient for i in p.ingredients} & ingredient_terms:
            matched.append('ingredient name')
        s_hits = _strength_match(p, tokens)
        if tokens and not s_hits:
            continue   # a strength was requested and this product does not have it
        origins.append((p, matched + s_hits))

    results, comparisons, missing = [], [], []
    if not origins:
        missing.append({'type': 'no_product_match', 'detail': f'No ingested product matches "{query}"'
                        + (f' in {origin_country}' if origin_country else '') + '.'})
    seen_records = set()
    for p, matched in origins:
        results.append(record_result(session, p.record_pk, matched_fields=matched, method='structured_sql',
                                     facts={'role': 'queried_product', **_product_facts(p)}))
        seen_records.add(p.record_pk)
        if not target_country:
            continue
        cands = session.scalars(active_join(select(MedProduct), MedProduct)
                                .options(selectinload(MedProduct.ingredients))
                                .where(MedProduct.ingredient_key == p.ingredient_key, MedProduct.country == target_country,
                                       MedProduct.id != p.id).order_by(MedProduct.id)).unique().all()
        if not cands:
            missing.append({'type': 'no_target_candidate', 'detail':
                            f'No ingested {target_country} product with the same active ingredients as {p.product_name}.'})
        for c in cands:
            cmp = _compare(p, c)
            comparisons.append({'queried_product': p.product_name, 'queried_source': p.source_id,
                                'candidate_product': c.product_name, 'candidate_source': c.source_id,
                                'candidate_country': c.country, **cmp})
            if c.record_pk not in seen_records:
                results.append(record_result(session, c.record_pk, matched_fields=[f'same active ingredients ({c.ingredient_key})'],
                                             method='structured_sql', facts={'role': 'target_candidate', **_product_facts(c)}))
                seen_records.add(c.record_pk)
            for field, value in (('dosage form', c.dosage_form), ('route', c.route)):
                if not value:
                    missing.append({'type': 'field_not_stated', 'source_id': c.source_id,
                                    'detail': f'{field.capitalize()} of {c.product_name} is not stated in {c.source_id}.'})

    # Label passages that explain the structured facts: the passage(s) at the composition location of each product,
    # then other passages of the same sources by keyword / similar meaning.
    product_records = [r for r in results if r['retrieval_method'] == 'structured_sql']
    for r in product_records:
        loc = r['source_location']
        cond = [KnowledgeRecord.version_pk == r['source_version']['version_id'], KnowledgeRecord.kind == 'label_passage']
        if loc.get('page'):
            cond.append(KnowledgeRecord.metadata_['location']['page'].as_integer() == int(loc['page']))
        elif loc.get('block') is not None:
            cond.append(KnowledgeRecord.metadata_['location']['block'].as_integer() == int(loc['block']))
        else:
            continue
        squash = lambda s: re.sub(r'\s+', '', s or '').lower()  # noqa: E731
        evidence = [squash(i['evidence_text']) for i in r['facts']['ingredients']]
        passages = session.execute(select(KnowledgeRecord.id, KnowledgeRecord.content).where(*cond)
                                   .order_by(KnowledgeRecord.id)).all()
        # the passage(s) on that page/section that contain the composition wording; else the first one
        chosen = [rid for rid, content in passages if any(e and e in squash(content) for e in evidence)] \
            or [rid for rid, _ in passages[:1]]
        for rid in chosen:
            if rid not in seen_records:
                results.append(record_result(session, rid, matched_fields=[f'composition location of {r["facts"]["product_name"]}'],
                                             method='same_location'))
                seen_records.add(rid)
    sources = sorted({r['source_id'] for r in product_records})
    ing_query = ' OR '.join(sorted({i['ingredient'] for r in product_records for i in r['facts']['ingredients']}))
    for rid, score, method in passage_search(session, ing_query, workflow='medicines', source_ids=sources,
                                             kinds=['label_passage'], limit=limit_passages, exclude=seen_records):
        results.append(record_result(session, rid, matched_fields=['label passage'], method=method, score=score))

    if comparisons or origins:
        missing.append({'type': 'out_of_scope_evidence', 'detail': 'No registration, availability, price or stock '
                        'evidence for any country is in the ingested sources; manufacturer labels do not prove these.'})
    missing += missing_sources(session, 'medicines')
    return {'domain': 'medicines',
            'query': {'query': query, 'origin_country': origin_country, 'target_country': target_country},
            'retrieval_status': status(results, missing), 'comparisons': comparisons,
            'results': results, 'missing_evidence': missing}
