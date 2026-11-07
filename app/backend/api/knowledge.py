import csv
from collections import Counter
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from backend.config import ROOT
from backend.database import SessionLocal
from backend.ingestion.registry import WORKFLOWS
from backend.models import IngestionRun, KnowledgeRecord, Source, SourceVersion
from backend.retrieval import embeddings
from backend.retrieval.search import MAX_QUERY_LENGTH, search
from backend.portal.deps import current_doctor

# Knowledge search is part of the doctor portal: any signed-in doctor may use it.
DOCTORS_ONLY = [Depends(current_doctor)]

router = APIRouter(prefix='/api', tags=['knowledge'])
Workflow = Literal['medicines', 'procedures', 'medical_reports', 'policies']
CATALOGUE = ROOT / 'data/manifests/source_catalogue_216.csv'


def db():
    with SessionLocal() as session:
        yield session


def _dt(value):
    return value.isoformat() if value else None


def _version(v):
    return {'version_id': v.id, 'version_label': v.version_label, 'status': v.status, 'sha256': v.sha256,
            'record_count': v.record_count, 'raw_path': v.raw_path, 'snapshot_path': v.snapshot_path,
            'file_size': v.file_size, 'parser': f'{v.parser_name} {v.parser_version}',
            'acquired_at': _dt(v.acquired_at), 'ingested_at': _dt(v.ingested_at)}


def _source(s, active):
    return {'source_id': s.source_id, 'catalogue_id': s.catalogue_id, 'title': s.title, 'workflow': s.workflow,
            'jurisdiction': s.jurisdiction, 'publisher': s.publisher, 'ingestion_status': s.ingestion_status,
            'origin_url': s.origin_url, 'licence_note': s.licence_note, 'access_note': s.access_note,
            'limitations': s.limitations or [], 'version_count': len(s.versions),
            'active_version': _version(active) if active else None,
            'stored_file_url': f'/api/sources/{s.source_id}/file' if active else None}


@router.get('/health', summary='Liveness: the web process is running')
def health():
    return {'status': 'ok'}


@router.get('/ready', summary='Readiness: database, schema, data and semantic search status')
def ready():
    checks = {}
    try:
        with SessionLocal() as s:
            s.execute(text('SELECT 1'))
            checks['database'] = 'ok'
            checks['migration'] = s.scalar(text('SELECT version_num FROM alembic_version'))
            checks['pg_trgm'] = bool(s.scalar(text("SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm'")))
            checks['active_sources'] = s.scalar(select(func.count()).select_from(Source).where(Source.active_version_id.is_not(None)))
            checks['semantic'] = embeddings.status(s)
    except Exception as exc:  # report, never crash
        checks.setdefault('database', f'error: {type(exc).__name__}')
        return JSONResponse(status_code=503, content={'status': 'not ready', 'checks': checks,
                                                      'detail': 'Database or schema unavailable. Check PostgreSQL and run: python -m alembic upgrade head'})
    ok = checks['database'] == 'ok' and checks['migration'] and checks['active_sources'] > 0
    return JSONResponse(status_code=200 if ok else 503,
                        content={'status': 'ready' if ok else 'not ready', 'checks': checks})


@router.get('/workflows', dependencies=DOCTORS_ONLY, summary='Per-workflow source and record counts (active versions)')
def workflows(session: Session = Depends(db)):
    counts = dict(session.execute(
        select(KnowledgeRecord.workflow, func.count()).join(Source, Source.active_version_id == KnowledgeRecord.version_pk)
        .group_by(KnowledgeRecord.workflow)).all())
    sources = Counter(session.scalars(select(Source.workflow).where(Source.active_version_id.is_not(None))))
    return [{'workflow': w, 'sources': sources.get(w, 0), 'records': counts.get(w, 0)} for w in WORKFLOWS]


@router.get('/sources', dependencies=DOCTORS_ONLY, summary='Registered sources with their active version')
def sources(session: Session = Depends(db)):
    out = []
    for s in session.scalars(select(Source).order_by(Source.source_id)):
        out.append(_source(s, session.get(SourceVersion, s.active_version_id) if s.active_version_id else None))
    return out


@router.get('/sources/{source_id}', dependencies=DOCTORS_ONLY, summary='One source with its full version history')
def source_detail(source_id: str, session: Session = Depends(db)):
    s = session.scalar(select(Source).where(Source.source_id == source_id))
    if not s:
        raise HTTPException(404, f'Source {source_id!r} not found')
    result = _source(s, session.get(SourceVersion, s.active_version_id) if s.active_version_id else None)
    result['versions'] = [_version(v) for v in reversed(s.versions)]
    return result


_FILE_TYPES = {'.pdf': 'application/pdf', '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8',
               '.txt': 'text/plain; charset=utf-8', '.json': 'application/json', '.xml': 'application/xml',
               '.zip': 'application/zip'}


@router.get('/sources/{source_id}/file', dependencies=DOCTORS_ONLY, summary='Stored copy of the source file (active version)')
def source_file(source_id: str, session: Session = Depends(db)):
    s = session.scalar(select(Source).where(Source.source_id == source_id))
    if not s or not s.active_version_id:
        raise HTTPException(404, 'No stored file for this source (not ingested)')
    v = session.get(SourceVersion, s.active_version_id)
    path = (ROOT / (v.snapshot_path or v.raw_path)).resolve()
    if ROOT.resolve() not in path.parents or not path.is_file():
        raise HTTPException(404, 'Stored file not found')
    suffix = path.suffix.lower()
    media = _FILE_TYPES.get(suffix, 'application/octet-stream')
    # Saved third-party pages are shown sandboxed: their scripts never run on this site.
    headers = {'X-Content-Type-Options': 'nosniff'}
    if suffix in ('.html', '.htm', '.xml', '.txt', '.json'):   # (Chrome's PDF viewer does not run under a sandbox CSP)
        headers['Content-Security-Policy'] = "sandbox; default-src 'none'; img-src data:; style-src 'unsafe-inline'"
    inline = suffix in ('.pdf', '.html', '.htm', '.txt', '.json', '.xml')
    return FileResponse(path, media_type=media, headers=headers, filename=f'{source_id}{suffix}',
                        content_disposition_type='inline' if inline else 'attachment')


@router.get('/sources/{source_id}/versions', dependencies=DOCTORS_ONLY, summary='Version history of one source (newest first)')
def source_versions(source_id: str, session: Session = Depends(db)):
    return source_detail(source_id, session)['versions']


@router.get('/ingestion/runs', dependencies=DOCTORS_ONLY, summary='Ingestion audit log (newest first)')
def ingestion_runs(source_id: str | None = Query(None, max_length=80), limit: int = Query(20, ge=1, le=200),
                   session: Session = Depends(db)):
    stmt = select(IngestionRun).order_by(IngestionRun.id.desc()).limit(limit)
    if source_id:
        stmt = stmt.where(IngestionRun.source_id == source_id)
    return [{'run_id': r.id, 'source_id': r.source_id, 'status': r.status, 'started_at': _dt(r.started_at),
             'finished_at': _dt(r.finished_at), 'version_id': r.version_pk, 'sha256': r.sha256,
             'records_loaded': r.records_loaded, 'records_skipped': r.records_skipped, 'message': r.message,
             'errors': r.errors} for r in session.scalars(stmt)]


@router.get('/catalogue/summary', dependencies=DOCTORS_ONLY, summary='Acquisition planning catalogue (references, not acquired files)')
def catalogue_summary():
    if not CATALOGUE.exists():
        raise HTTPException(404, 'Catalogue file not found')
    with open(CATALOGUE, encoding='utf-8-sig', newline='') as fh:
        rows = list(csv.DictReader(fh))
    return {'file': CATALOGUE.relative_to(ROOT).as_posix(), 'references': len(rows),
            'by_domain': Counter(r.get('domain', '') for r in rows).most_common(),
            'by_download_status': Counter(r.get('download_status', '') for r in rows).most_common(),
            'note': 'Planning references only. Ingested sources are listed by /api/sources.'}


@router.get('/search', dependencies=DOCTORS_ONLY, summary='Search active records: all keyword matches first, then top 50 similar-meaning matches')
def search_records(q: str = Query('', max_length=MAX_QUERY_LENGTH), workflow: Workflow | None = None,
                   kind: str | None = Query(None, max_length=40),
                   limit: int = Query(30, ge=1, le=100), offset: int = Query(0, ge=0),
                   session: Session = Depends(db)):
    return {**search(session, q, workflow, kind, limit, offset), 'limit': limit, 'offset': offset}


@router.get('/records/{record_id}', dependencies=DOCTORS_ONLY, summary='One record with full provenance')
def record(record_id: int, session: Session = Depends(db)):
    rec = session.get(KnowledgeRecord, record_id)
    if not rec:
        raise HTTPException(404, 'Record not found')
    v = session.get(SourceVersion, rec.version_pk)
    s = session.get(Source, v.source_pk)
    return {'id': rec.id, 'title': rec.title, 'content': rec.content, 'kind': rec.kind, 'external_id': rec.external_id,
            'workflow': rec.workflow, 'jurisdiction': rec.jurisdiction, 'language': rec.language,
            'source_link': rec.source_link, 'metadata': rec.metadata_,
            'is_active_version': s.active_version_id == v.id,
            'source': {'source_id': s.source_id, 'catalogue_id': s.catalogue_id, 'title': s.title,
                       'publisher': s.publisher, 'origin_url': s.origin_url, 'licence_note': s.licence_note,
                       'access_note': s.access_note, 'limitations': s.limitations or [],
                       'stored_file_url': f'/api/sources/{s.source_id}/file' if s.active_version_id == v.id else None},
            'version': _version(v)}
