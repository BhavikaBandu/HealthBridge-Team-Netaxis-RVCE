"""Policy & Jurisdiction agent: flags and quantity advice for the medicines carried on the trip.

Code decides every flag from retrieved source facts (controlled list, clause facets, conflicts) and from the facts
read from the patient's prescription (unverified). Carried = ongoing medications. One AI call then:
  - rewrites each flag as one or two plain sentences,
  - where official sources disagree, picks the stricter (safer) requirement and says why,
  - checks flags about the patient's documents (e.g. "no prescription on file") against the uploaded documents and
    drops a flag only when it quotes document text that contradicts it (code checks the quote).
Nothing here is a clearance or a refusal.
"""
import re

from sqlalchemy import select

from backend.portal.models import Document, DocumentFinding, DocumentText
from backend.retrieval.evidence import search_policy_clauses
from .common import ai_or_fallback, dedupe_sources, source_entry, squash
from . import llm

SYSTEM = (
    'You rewrite travel-medicine flags for a patient and their doctor. Each flag was decided by deterministic code '
    'from official sources. Rewrite each "draft" as 1-2 short, plain sentences (max 35 words) with the same meaning '
    'and the same next step. Do not add rules, numbers, authorities or medicines that are not in the draft, conflict '
    'or facts. Never say the patient is allowed, cleared or approved to travel or carry anything. '
    'CONFLICTS: a flag with "conflict" means official sources state different requirements. Choose the option that '
    'keeps the patient on the safer side (the stricter requirement, e.g. approval required rather than optional, the '
    'more demanding attestation). Return it in "conflict_choices" (flag_id, chosen_value copied exactly from the '
    'options, reason max 20 words) and write that flag so it tells the patient to follow the safer option and names '
    'the authority that states it. '
    'DOCUMENT CHECK: "documents" lists the patient\'s uploaded documents with their text. A flag with "doc_claim": '
    'true says something about those documents (no prescription on file, not attested, no treatment duration). If the '
    'document text clearly contradicts that flag, set keep=false and copy the exact contradicting words into "quote". '
    'Otherwise keep=true and quote="". Every other flag: keep=true. Return JSON only.')
SCHEMA = {'type': 'object', 'required': ['flags', 'conflict_choices'], 'properties': {
    'flags': {'type': 'array', 'items': {'type': 'object', 'required': ['id', 'text', 'keep', 'quote'], 'properties': {
        'id': {'type': 'integer'}, 'text': {'type': 'string'}, 'keep': {'type': 'boolean'}, 'quote': {'type': 'string'}}}},
    'conflict_choices': {'type': 'array', 'items': {'type': 'object', 'required': ['flag_id', 'chosen_value', 'reason'],
                         'properties': {'flag_id': {'type': 'integer'}, 'chosen_value': {'type': 'string'},
                                        'reason': {'type': 'string'}}}}}}
STRICTER = {'required', 'UAE embassy abroad'}   # values that, when chosen, make a review flag an action
DOC_CHARS = 2500


def _conflict(c, facet):
    """Compact conflict for the AI: the facet and each stated option with who states it."""
    return {'facet': facet, 'options': [{'value': v['value'], 'stated_by': [
        {'source': x['source_id'], 'authority': x['authority'], 'clause': x['clause_ref'], 'phrase': x['phrase'][:220]}
        for x in v['stated_by']]} for v in c['values']]}


def _documents(s, patient_id):
    """The patient's uploaded documents: name, type, medicines read from them, and text (for the document check)."""
    out = []
    for d in s.scalars(select(Document).where(Document.patient_id == patient_id, Document.archived_at.is_(None))):
        t = s.get(DocumentText, d.id)
        text = '\n'.join(p['text'] for p in (t.pages if t else []))[:DOC_CHARS]
        items = [f.data.get('medicine') for f in s.scalars(select(DocumentFinding).where(
            DocumentFinding.document_id == d.id, DocumentFinding.kind == 'prescription_item'))]
        out.append({'name': d.name, 'type': d.doc_type, 'medicines_read': [i for i in items if i], 'text': text})
    return out


def _src(source_id, record_id, label):
    return {'source_id': source_id, 'label': f'{source_id} {label}'.strip(), 'record_id': record_id,
            'url': f'/api/sources/{source_id}/file'}


def _clause_mentioning(s, phrase):
    """A clause of an active policy source whose text contains `phrase` (used to cite a specific requirement)."""
    from backend.models import KnowledgeRecord, Source
    row = s.execute(select(KnowledgeRecord.id, Source.source_id, KnowledgeRecord.metadata_)
                    .join(Source, Source.active_version_id == KnowledgeRecord.version_pk)
                    .where(KnowledgeRecord.workflow == 'policies', KnowledgeRecord.content.ilike(f'%{phrase}%'))
                    .order_by(KnowledgeRecord.id).limit(1)).first()
    return [_src(row.source_id, row.id, (row.metadata_ or {}).get('location_label') or '')] if row else []


def _prescription_facts(s, med):
    """Latest prescription item read from a document for this medication, and that document's fields."""
    items = s.scalars(select(DocumentFinding).where(DocumentFinding.patient_id == med.patient_id,
                                                    DocumentFinding.kind == 'prescription_item',
                                                    DocumentFinding.status != 'rejected')
                      .order_by(DocumentFinding.created_at.desc())).all()
    item = next((f for f in items if f.data.get('matched_medication_id') == str(med.id)), None)
    if not item:
        return None, None
    fields = s.scalar(select(DocumentFinding).where(DocumentFinding.document_id == item.document_id,
                                                    DocumentFinding.kind == 'prescription_fields'))
    return item, fields


def analyse(s, meds, ctx):
    """Returns flag dicts (kind, severity, subject, text, origin, sources)."""
    drafts = []
    extra = {}   # (subject, draft text) -> {'conflict': ..., 'doc_claim': True}
    for med in [m for m in meds if m.ongoing]:
        label = med.brand or med.name
        res = search_policy_clauses(s, f'{med.name} traveller personal use medicines', destination=ctx.jurisdiction,
                                    origin_country=ctx.origin, medicine_name=med.name)
        cls = res['classification']
        entry = (cls.get('entries') or [None])[0] if cls['status'] == 'listed' else None
        listed_rec = next((r for r in res['results'] if r['matched_fields'] == ['controlled list name']), None)
        clauses = [r for r in res['results'] if r['retrieval_method'] == 'metadata_filter']
        conflicts = {c['facet']: c for c in res['conflicts']}
        item, fields = _prescription_facts(s, med)
        doc_origin = 'document (unverified)'

        def facet_sources(key):
            out = []
            for c in clauses:
                if key in (c['facts'].get('facets') or {}):
                    out.append(source_entry(c))
            return dedupe_sources(out)

        if entry:   # controlled medicine
            row_src = [source_entry(listed_rec)] if listed_rec else []
            if entry.get('prohibited'):
                drafts.append(('flag', 'action', label, f"{label} is listed as prohibited for travellers in the UAE "
                               f"controlled-medicine list. Do not carry it without checking with the Emirates Drug Establishment.",
                               'rules', row_src))
                continue
            drafts.append(('flag', 'action', label, f"{label} is a controlled medicine in the UAE ({entry['category']}). "
                           'Carry your prescription or an attested medical report with it.', 'rules', row_src))
            if 'prior_approval' in conflicts:
                text = (f'UAE sources disagree on whether {label} needs approval before you travel. Check with the '
                        'Emirates Drug Establishment before your trip.')
                drafts.append(('flag', 'review', label, text, 'rules', facet_sources('prior_approval')))
                extra[(label, text)] = {'conflict': _conflict(conflicts['prior_approval'], 'prior_approval')}
            if item is None:
                text = f'No prescription for {label} is on file. Carry a prescription or an attested medical report.'
                drafts.append(('flag', 'action', label, text, 'rules', row_src))
                extra[(label, text)] = {'doc_claim': True}
            else:
                if fields and not fields.data.get('attestation_wording_found') and 'document_authentication' in conflicts:
                    text = (f"Your prescription for {label} isn't attested. UAE guidance asks for attestation by a "
                            'health authority or a UAE embassy.')
                    drafts.append(('flag', 'action', label, text, doc_origin, facet_sources('document_authentication')))
                    extra[(label, text)] = {'doc_claim': True, 'conflict': _conflict(
                        conflicts['document_authentication'], 'document_authentication')}
                if not item.data.get('duration_stated'):
                    text = (f"Your prescription doesn't say how long to take {label}. Ask your doctor to add the "
                            'treatment duration.')
                    drafts.append(('flag', 'action', label, text, doc_origin, _clause_mentioning(s, 'duration of treatment')))
                    extra[(label, text)] = {'doc_claim': True}
            stay = re.search(r'period of stay', entry.get('carry_rule') or '', re.I)
            if stay and ctx.stay_days:
                qty = (f'Carry enough {label} for your {ctx.stay_days}-day stay only, and never more than '
                       '3 months, as the controlled list says.')
            else:
                qty = f'Carry no more than a 3-month supply of {label}.'
            drafts.append(('quantity', 'advice', label, qty, 'rules', row_src + facet_sources('max_supply')[:2]))
        else:      # not on the controlled list
            embassy = [c for c in clauses if (c['facts'].get('facets') or {}).get('document_authentication', {}).get('value') == 'UAE embassy abroad']
            if embassy:
                drafts.append(('flag', 'review', label, f'Dubai Customs asks for an attested prescription for all '
                               f'medicines, including {label}. Keep the prescription with you.', 'rules',
                               dedupe_sources([source_entry(c) for c in embassy])))
            supply = [c for c in clauses if 'max_supply' in (c['facts'].get('facets') or {}) and c['source_id'] == 'AE33']
            drafts.append(('quantity', 'advice', label, f"Carry up to a 3-month supply of {label}, in the original packs.",
                           'rules', dedupe_sources([source_entry(c) for c in supply])))

    # Actions first, then items to review, then quantity advice (stable within each group).
    order = {('flag', 'action'): 0, ('flag', 'review'): 1}
    drafts.sort(key=lambda d: order.get((d[0], d[1]), 2))
    # One AI call rewrites all drafts, resolves conflicts to the safer side and checks document claims.
    docs = _documents(s, ctx.patient_id)
    payload = {'trip': {'from': ctx.origin_name, 'to': ctx.destination_name, 'stay_days': ctx.stay_days},
               'flags': [{'id': i, 'kind': d[0], 'severity': d[1], 'medicine': d[2], 'draft': d[3],
                          **extra.get((d[2], d[3]), {})} for i, d in enumerate(drafts)],
               'documents': docs}
    allowed = llm.numbers_in(str(payload))

    def validate(data):
        ids = {f['id'] for f in data.get('flags', [])}
        if ids != set(range(len(drafts))):
            raise llm.LLMError('flags missing or extra')
        for f in data['flags']:
            llm.check_text(f['text'], allowed, 'flag')
            llm.check_length(f['text'], 45, 'flag')

    fallback = {'flags': [{'id': i, 'text': d[3], 'keep': True, 'quote': ''} for i, d in enumerate(drafts)],
                'conflict_choices': []}
    data = ai_or_fallback(ctx, 'policy flags', SYSTEM, payload, SCHEMA, fallback, validate) if drafts else fallback
    replies = {f['id']: f for f in data['flags']}
    doc_text = squash(' '.join(d['text'] for d in docs))
    choices = {}
    for c in data.get('conflict_choices') or []:
        d = drafts[c['flag_id']] if 0 <= c.get('flag_id', -1) < len(drafts) else None
        conflict = extra.get((d[2], d[3]), {}).get('conflict') if d else None
        if conflict and c.get('chosen_value') in [o['value'] for o in conflict['options']]:
            choices[c['flag_id']] = c

    out = []
    for i, d in enumerate(drafts):
        reply = replies.get(i, {})
        meta = extra.get((d[2], d[3]), {})
        quote = (reply.get('quote') or '').strip()
        if meta.get('doc_claim') and reply.get('keep') is False and len(squash(quote)) >= 8 and squash(quote) in doc_text:
            ctx.ai_fallbacks.append(f'policy: dropped "{d[3][:60]}" (documents say: "{quote[:80]}")')
            continue   # the documents contradict this flag
        severity = d[1]
        if i in choices and choices[i]['chosen_value'] in STRICTER:
            severity = 'action'
        out.append({'kind': d[0], 'severity': severity, 'subject': d[2], 'text': reply.get('text') or d[3],
                    'origin': d[4] + (' · safer option' if i in choices else ''), 'sources': d[5]})
    return out
