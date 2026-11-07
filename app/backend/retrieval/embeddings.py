"""Optional semantic layer: local embeddings stored in PostgreSQL, cosine similarity computed in NumPy.

pgvector is not used because it is not bundled with the Windows PostgreSQL installer and building it
needs Visual Studio C++ tools. Vectors are stored as float32 bytes in `record_embeddings`; at query time
the active vectors are loaded once into memory (about 45 MB for ~30k records at 384 dimensions).

Build or update embeddings (only missing ones are computed):
    python -m backend.retrieval.embeddings
"""
import sys
import threading

from sqlalchemy import func, select

from backend.config import EMBEDDING_CACHE_DIR, EMBEDDING_MODEL
from backend.database import SessionLocal
from backend.models import KnowledgeRecord, RecordEmbedding, Source

try:
    import numpy as np
    from fastembed import TextEmbedding
    LIBRARIES_AVAILABLE = True
except ImportError:  # optional dependency (requirements-semantic.txt)
    np = TextEmbedding = None
    LIBRARIES_AVAILABLE = False

_model = None
_model_lock = threading.Lock()
_index = None
_index_lock = threading.Lock()


def embedding_text(rec_title, rec_kind, metadata, content=None):
    """Text that describes a record's meaning (identifiers and dates are left to keyword search)."""
    m = metadata or {}
    if rec_kind == 'medicine_document':
        doc = {'SmPC': 'summary of product characteristics (prescribing information)',
               'PIL': 'patient information leaflet'}.get(m.get('document_type'), m.get('document_type', ''))
        return f"{rec_title}. {doc}. {m.get('domain', '')} medicine. {m.get('holder', '')}"
    if rec_kind == 'unit':
        return f"{m.get('name') or rec_title}. unit of {m.get('property') or 'measure'}. symbol {m.get('code', '')}"
    if content:   # evidence passages: the passage text carries the meaning (model reads ~128 tokens)
        return f'{rec_title}. {content}'[:1000]
    return rec_title


def get_model():
    global _model
    if not LIBRARIES_AVAILABLE:
        raise RuntimeError('Semantic search libraries are not installed (pip install -r requirements-semantic.txt).')
    with _model_lock:
        if _model is None:
            _model = TextEmbedding(EMBEDDING_MODEL, cache_dir=str(EMBEDDING_CACHE_DIR))
        return _model


def embed_texts(texts, batch_size=256):
    vecs = np.asarray(list(get_model().embed(texts, batch_size=batch_size)), dtype=np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12
    return vecs


def _active_filter(stmt):
    return stmt.join(Source, Source.active_version_id == KnowledgeRecord.version_pk)


def coverage(session):
    """(active records, active records with an embedding for the configured model)."""
    total = session.scalar(_active_filter(select(func.count()).select_from(KnowledgeRecord)))
    embedded = session.scalar(_active_filter(select(func.count()).select_from(KnowledgeRecord)
                                             .join(RecordEmbedding, RecordEmbedding.record_pk == KnowledgeRecord.id))
                              .where(RecordEmbedding.model == EMBEDDING_MODEL))
    return total or 0, embedded or 0


def status(session):
    total, embedded = coverage(session)
    if not LIBRARIES_AVAILABLE:
        return {'available': False, 'reason': 'fastembed/numpy not installed', 'model': EMBEDDING_MODEL,
                'records': total, 'embedded': embedded}
    if embedded == 0:
        return {'available': False, 'reason': 'no embeddings built; run python -m backend.retrieval.embeddings',
                'model': EMBEDDING_MODEL, 'records': total, 'embedded': 0}
    return {'available': True, 'reason': None if embedded == total else f'{total - embedded} active records lack embeddings',
            'model': EMBEDDING_MODEL, 'records': total, 'embedded': embedded, 'backend': 'numpy cosine (pgvector not installed)'}


class _Index:
    def __init__(self, session):
        rows = session.execute(_active_filter(
            select(KnowledgeRecord.id, KnowledgeRecord.workflow, KnowledgeRecord.kind, RecordEmbedding.vector)
            .join(RecordEmbedding, RecordEmbedding.record_pk == KnowledgeRecord.id))
            .where(RecordEmbedding.model == EMBEDDING_MODEL).order_by(KnowledgeRecord.id)).all()
        self.ids = np.array([r[0] for r in rows], dtype=np.int64)
        self.workflow = np.array([r[1] for r in rows])
        self.kind = np.array([r[2] for r in rows])
        self.matrix = np.frombuffer(b''.join(r[3] for r in rows), dtype=np.float32).reshape(len(rows), -1) \
            if rows else np.zeros((0, 384), dtype=np.float32)
        self.signature = _signature(session)


def _signature(session):
    return tuple(session.execute(_active_filter(
        select(func.count(), func.max(RecordEmbedding.record_pk)).select_from(KnowledgeRecord)
        .join(RecordEmbedding, RecordEmbedding.record_pk == KnowledgeRecord.id))
        .where(RecordEmbedding.model == EMBEDDING_MODEL)).one())


def semantic_search(session, query, workflow=None, kind=None, top_k=50):
    """Return [(record_id, cosine_similarity)] best first. Reloads the in-memory index when data changes."""
    global _index
    with _index_lock:
        if _index is None or _index.signature != _signature(session):
            _index = _Index(session)
        index = _index
    if len(index.ids) == 0:
        return []
    qv = embed_texts([query])[0]
    scores = index.matrix @ qv
    mask = np.ones(len(scores), dtype=bool)
    if workflow:
        mask &= index.workflow == workflow
    if kind:
        mask &= index.kind == kind
    candidates = np.flatnonzero(mask)
    if len(candidates) == 0:
        return []
    k = min(top_k, len(candidates))
    top = candidates[np.argpartition(-scores[candidates], k - 1)[:k]]
    top = top[np.argsort(-scores[top], kind='stable')]
    return [(int(index.ids[i]), float(scores[i])) for i in top]


def build(batch_size=512):
    if not LIBRARIES_AVAILABLE:
        sys.exit('ERROR: install optional semantic dependencies first: python -m pip install -r requirements-semantic.txt')
    with SessionLocal() as session:
        missing = session.execute(_active_filter(
            select(KnowledgeRecord.id, KnowledgeRecord.title, KnowledgeRecord.kind, KnowledgeRecord.metadata_,
                   KnowledgeRecord.content))
            .outerjoin(RecordEmbedding, (RecordEmbedding.record_pk == KnowledgeRecord.id) & (RecordEmbedding.model == EMBEDDING_MODEL))
            .where(RecordEmbedding.record_pk.is_(None)).order_by(KnowledgeRecord.id)).all()
        print(f'{len(missing)} active records need embeddings (model {EMBEDDING_MODEL}).', flush=True)
        for start in range(0, len(missing), batch_size):
            chunk = missing[start:start + batch_size]
            vecs = embed_texts([embedding_text(r.title, r.kind, r.metadata_, r.content) for r in chunk])
            session.add_all(RecordEmbedding(record_pk=r.id, model=EMBEDDING_MODEL, dim=vecs.shape[1],
                                            vector=v.astype('<f4').tobytes()) for r, v in zip(chunk, vecs))
            session.commit()
            print(f'  embedded {min(start + batch_size, len(missing))}/{len(missing)}', flush=True)
        print(status(session))


if __name__ == '__main__':
    build()
