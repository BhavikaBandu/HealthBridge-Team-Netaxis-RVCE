"""Retrieval over the active version of each source.

Every search returns one combined list:
1. Keyword matches (all of them), best first. PostgreSQL full-text search ('simple' configuration,
   language-neutral) plus exact identifier and case-insensitive partial matching.
   Score = 10 (exact identifier) + ts_rank_cd + 0.5 (title starts with query) + trigram similarity(title, query).
2. Then up to 50 semantic matches (cosine similarity of local multilingual embeddings, >= 0.50) that are
   not already in the keyword list.

Empty query: all active records in stable order, no ranking.
If semantic search is unavailable, only keyword matches are returned, with a notice.
"""
from sqlalchemy import Float, case, cast, func, or_, select

from backend.models import KnowledgeRecord, Source, SourceVersion
from . import embeddings

MAX_QUERY_LENGTH = 200
SEMANTIC_TOP_K = 50
SEMANTIC_CANDIDATES = 300  # semantic pool searched before removing keyword matches
# Minimum cosine similarity for a "similar meaning" result. Measured on this data: nonsense queries
# (e.g. 'zzzqqq', 'asdf qwer', bare numbers) never exceed ~0.47; useful matches score 0.50+.
SEMANTIC_MIN_SIMILARITY = 0.50


def escape_like(text):
    """Make %, _ and \\ match literally in an ILIKE pattern."""
    return text.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def _base(columns, workflow, kind):
    stmt = (select(*columns).select_from(KnowledgeRecord)
            .join(Source, Source.active_version_id == KnowledgeRecord.version_pk))
    if workflow:
        stmt = stmt.where(KnowledgeRecord.workflow == workflow)
    if kind:
        stmt = stmt.where(KnowledgeRecord.kind == kind)
    return stmt


def _keyword_parts(query):
    tsq = func.websearch_to_tsquery('simple', query)
    pattern = f'%{escape_like(query)}%'
    exact = or_(func.lower(KnowledgeRecord.external_id) == query.lower(),
                KnowledgeRecord.metadata_['authorisation'].astext == query,
                KnowledgeRecord.metadata_['code'].astext == query)
    # Every branch is index-backed (GIN tsvector, GIN trigram, expression indexes). Identifier parts
    # (authorisation numbers, unit codes) also appear in content, so partial ID matches are covered there.
    match = or_(KnowledgeRecord.search_vector.op('@@')(tsq),
                KnowledgeRecord.title.ilike(pattern, escape='\\'),
                KnowledgeRecord.content.ilike(pattern, escape='\\'),
                exact)
    score = (case((exact, 10.0), else_=0.0)
             + cast(func.ts_rank_cd(KnowledgeRecord.search_vector, tsq), Float)
             + case((KnowledgeRecord.title.ilike(f'{escape_like(query)}%', escape='\\'), 0.5), else_=0.0)
             + cast(func.similarity(KnowledgeRecord.title, query), Float))
    return match, score


def keyword_ids(session, query, workflow, kind, limit, offset):
    match, score = _keyword_parts(query)
    total = session.scalar(_base([func.count()], workflow, kind).where(match))
    rows = session.execute(_base([KnowledgeRecord.id, score.label('score')], workflow, kind)
                           .where(match).order_by(score.desc(), KnowledgeRecord.id).offset(offset).limit(limit)).all()
    return [(r.id, float(r.score)) for r in rows], total


def browse_ids(session, workflow, kind, limit, offset):
    total = session.scalar(_base([func.count()], workflow, kind))
    rows = session.execute(_base([KnowledgeRecord.id], workflow, kind)
                           .order_by(KnowledgeRecord.id).offset(offset).limit(limit)).all()
    return [(r.id, None) for r in rows], total


def semantic_extras(session, query, workflow, kind):
    """Top semantic matches that are NOT keyword matches, best first, at most SEMANTIC_TOP_K."""
    ranked = [(rid, s) for rid, s in embeddings.semantic_search(session, query, workflow, kind, top_k=SEMANTIC_CANDIDATES)
              if s >= SEMANTIC_MIN_SIMILARITY]
    if not ranked:
        return []
    match, _ = _keyword_parts(query)
    ids = [rid for rid, _ in ranked]
    keyword_hits = set(session.scalars(select(KnowledgeRecord.id).where(KnowledgeRecord.id.in_(ids), match)))
    return [(rid, s) for rid, s in ranked if rid not in keyword_hits][:SEMANTIC_TOP_K]


def hydrate(session, scored, match_type):
    """Fetch full records for [(id, score)] keeping order, with provenance fields."""
    if not scored:
        return []
    ids = [rid for rid, _ in scored]
    rows = session.execute(
        select(KnowledgeRecord, Source.source_id, SourceVersion.version_label, SourceVersion.id)
        .join(SourceVersion, SourceVersion.id == KnowledgeRecord.version_pk)
        .join(Source, Source.id == SourceVersion.source_pk)
        .where(KnowledgeRecord.id.in_(ids))).all()
    by_id = {r[0].id: r for r in rows}
    out = []
    for rid, score in scored:
        if rid not in by_id:
            continue
        rec, source_id, version_label, version_id = by_id[rid]
        out.append({'id': rec.id, 'title': rec.title, 'kind': rec.kind, 'external_id': rec.external_id,
                    'content': rec.content, 'language': rec.language, 'source_link': rec.source_link,
                    'source_id': source_id, 'version': version_label, 'version_id': version_id,
                    'workflow': rec.workflow, 'jurisdiction': rec.jurisdiction, 'match_type': match_type,
                    'score': None if score is None else round(score, 4)})
    return out


def search(session, query='', workflow=None, kind=None, limit=30, offset=0):
    """Returns dict: results, total, keyword_total, semantic_total, notice."""
    query = (query or '').strip()[:MAX_QUERY_LENGTH]
    limit = min(max(limit, 1), 100)
    offset = max(offset, 0)
    if not query:
        scored, total = browse_ids(session, workflow, kind, limit, offset)
        return {'results': hydrate(session, scored, None), 'total': total, 'keyword_total': total,
                'semantic_total': 0, 'notice': None}

    notice = None
    sem_status = embeddings.status(session)
    extras = []
    if sem_status['available']:
        extras = semantic_extras(session, query, workflow, kind)
    else:
        notice = f"Similar-meaning matches unavailable ({sem_status['reason']}); showing keyword matches only."

    # Keyword matches fill the first pages; semantic extras follow after the last keyword match.
    kw_page, kw_total = keyword_ids(session, query, workflow, kind, limit, offset)
    results = hydrate(session, kw_page, 'keyword')
    remaining = limit - len(results)
    if remaining > 0:
        start = max(offset - kw_total, 0)
        results += hydrate(session, extras[start:start + remaining], 'semantic')
    return {'results': results, 'total': kw_total + len(extras), 'keyword_total': kw_total,
            'semantic_total': len(extras), 'notice': notice}
