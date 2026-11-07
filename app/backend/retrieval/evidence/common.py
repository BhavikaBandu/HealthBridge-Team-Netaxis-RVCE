"""Shared pieces of the four evidence retrievers: output contract, active-version filtering, passage search.

Output contract (every domain):
    {domain, query, retrieval_status, results[], missing_evidence[], ...domain blocks}
Each result:
    {source_id, catalogue_id, country, title, matched_fields, retrieval_method, source_location,
     evidence_text, record_id, record_ref, source_version, facts?, score?}
Scores are only reported where a real ranking value exists (keyword rank / cosine similarity); never invented.
"""
from sqlalchemy import Float, cast, func, select

from backend.models import KnowledgeRecord, Source, SourceVersion
from backend.retrieval import embeddings
from backend.retrieval.search import _keyword_parts

SEMANTIC_MIN = 0.50


def active_join(stmt, model):
    """Restrict a fact/record query to rows of each source's active version."""
    return stmt.join(Source, Source.active_version_id == model.version_pk)


def record_result(session, record_id, *, matched_fields, method, facts=None, score=None):
    rec, version, source = session.execute(
        select(KnowledgeRecord, SourceVersion, Source)
        .join(SourceVersion, SourceVersion.id == KnowledgeRecord.version_pk)
        .join(Source, Source.id == SourceVersion.source_pk)
        .where(KnowledgeRecord.id == record_id)).one()
    out = {'source_id': source.source_id, 'catalogue_id': source.catalogue_id, 'country': rec.jurisdiction,
           'publisher': source.publisher, 'title': rec.title, 'matched_fields': matched_fields,
           'retrieval_method': method,
           'source_location': {'label': (rec.metadata_ or {}).get('location_label') or f'record {rec.external_id}',
                               **((rec.metadata_ or {}).get('location') or {}),
                               'url': rec.source_link, 'stored_file': version.snapshot_path or version.raw_path},
           'evidence_text': rec.content, 'record_id': rec.id, 'record_ref': rec.external_id,
           'source_version': {'version_id': version.id, 'label': version.version_label, 'sha256': version.sha256,
                              'active': source.active_version_id == version.id},
           'source_limitations': source.limitations or []}
    if facts is not None:
        out['facts'] = facts
    if score is not None:
        out['score'] = round(float(score), 4)
    return out


def passage_search(session, query, *, workflow, countries=None, kinds=None, source_ids=None, limit=5, exclude=()):
    """Keyword matches first, then similar-meaning matches (cosine >= 0.50), restricted by country/kind/source."""
    if not (query or '').strip():
        return []
    q = query.strip()[:200]

    def filtered(stmt):
        stmt = active_join(stmt, KnowledgeRecord).where(KnowledgeRecord.workflow == workflow)
        if countries:
            stmt = stmt.where(KnowledgeRecord.jurisdiction.in_(countries))
        if kinds:
            stmt = stmt.where(KnowledgeRecord.kind.in_(kinds))
        if source_ids:
            stmt = stmt.where(Source.source_id.in_(source_ids))
        if exclude:
            stmt = stmt.where(KnowledgeRecord.id.not_in(list(exclude)))
        return stmt

    match, score = _keyword_parts(q)
    kw = session.execute(filtered(select(KnowledgeRecord.id, score.label('s')).select_from(KnowledgeRecord))
                         .where(match).order_by(score.desc(), KnowledgeRecord.id).limit(limit)).all()
    out = [(r.id, float(r.s), 'keyword') for r in kw]
    if len(out) < limit and embeddings.status(session)['available']:
        seen = {r[0] for r in out} | set(exclude)
        ranked = [(rid, s) for rid, s in embeddings.semantic_search(session, q, workflow, None, top_k=300)
                  if s >= SEMANTIC_MIN and rid not in seen]
        if ranked:
            allowed = set(session.scalars(filtered(select(KnowledgeRecord.id).select_from(KnowledgeRecord))
                                          .where(KnowledgeRecord.id.in_([rid for rid, _ in ranked]))))
            out += [(rid, s, 'semantic') for rid, s in ranked if rid in allowed][:limit - len(out)]
    return out


def missing_sources(session, workflow, countries=None):
    """Catalogued sources registered as not ingested for this workflow (reported, never searched)."""
    stmt = select(Source).where(Source.workflow == workflow, Source.ingestion_status == 'not_ingested')
    if countries:
        stmt = stmt.where(Source.jurisdiction.in_(countries))
    return [{'type': 'source_not_ingested', 'source_id': s.source_id, 'country': s.jurisdiction,
             'detail': s.access_note} for s in session.scalars(stmt)]


def status(results, missing):
    if not results:
        return 'no_evidence'
    return 'partial' if missing else 'ok'


def trigram(a, b):
    return cast(func.similarity(a, b), Float)
