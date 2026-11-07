"""Versioned, idempotent ingestion.

Usage:
    python -m backend.ingestion.pipeline                 # all registered sources
    python -m backend.ingestion.pipeline --source GL-UCUM
    python -m backend.ingestion.pipeline --source GL-UCUM --file path/to/new_snapshot.xml

Rules:
- Same SHA-256 as the active version  -> 'unchanged', nothing written except the run log.
- Same SHA-256 as an older version    -> that version is re-activated ('reactivated').
- New SHA-256                         -> new immutable version with its own records; the previous
                                         version is marked 'superseded' and kept with its records.
- Any fatal error                     -> transaction rolled back, run logged as 'failed'.
"""
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import insert, select, text
from sqlalchemy.exc import OperationalError, ProgrammingError

from backend.config import ROOT, SNAPSHOT_DIR
from backend.database import SessionLocal
from backend.models import IngestionRun, KnowledgeRecord, Source, SourceVersion, now
from .facts import materialize_facts
from .registry import DATASETS, NOT_INGESTED
from .safety import SourceFileError

BATCH_SIZE = 2000
MAX_LOGGED_ERRORS = 50


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def _rel(path):
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _snapshot(path, source_id, digest):
    """Keep an immutable copy of the raw bytes so older versions remain inspectable."""
    target = SNAPSHOT_DIR / source_id / f'{digest[:16]}_{Path(path).name}'
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    return _rel(target)


def _start_run(source_id):
    with SessionLocal() as s:
        run = IngestionRun(source_id=source_id, status='running', started_at=now())
        s.add(run)
        s.commit()
        return run.id


def _finish_run(run_id, **fields):
    with SessionLocal() as s:
        run = s.get(IngestionRun, run_id)
        for k, v in fields.items():
            setattr(run, k, v)
        run.finished_at = now()
        s.commit()


def _get_or_create_source(session, dataset):
    source = session.scalar(select(Source).where(Source.source_id == dataset['source_id']))
    if source is None:
        source = Source(source_id=dataset['source_id'], created_at=now())
        session.add(source)
    # Registry metadata (title, licence, ...) is descriptive and may be corrected; versions stay immutable.
    for field in ('title', 'workflow', 'jurisdiction', 'origin_url', 'licence_note', 'access_note'):
        setattr(source, field, dataset[field])
    source.catalogue_id = dataset.get('catalogue_id')
    source.publisher = dataset.get('publisher')
    source.limitations = dataset.get('limitations', [])
    source.ingestion_status = 'ingested'
    session.flush()
    return source


def register_not_ingested(entries=NOT_INGESTED):
    """Catalogued sources that could not be acquired: registered without a version so they show as gaps."""
    with SessionLocal() as session:
        for e in entries:
            source = session.scalar(select(Source).where(Source.source_id == e['source_id']))
            if source is None:
                source = Source(source_id=e['source_id'], created_at=now())
                session.add(source)
            for field in ('title', 'workflow', 'jurisdiction', 'origin_url', 'access_note', 'catalogue_id', 'publisher'):
                setattr(source, field, e.get(field))
            source.limitations = e.get('limitations', [])
            source.licence_note = None
            if source.active_version_id is None:
                source.ingestion_status = 'not_ingested'
        session.commit()
    return [{'source': e['source_id'], 'status': 'not_ingested', 'reason': e['access_note']} for e in entries]


def _activate(session, source, version):
    if source.active_version_id and source.active_version_id != version.id:
        previous = session.get(SourceVersion, source.active_version_id)
        previous.status = 'superseded'
    version.status = 'active'
    source.active_version_id = version.id


def ingest_dataset(dataset, file_path=None):
    path = Path(file_path) if file_path else ROOT / dataset['path']
    run_id = _start_run(dataset['source_id'])
    loaded = skipped = 0
    errors = []
    try:
        if not path.is_file():
            raise SourceFileError(f'Raw source file not found: {_rel(path)}')
        digest = sha256_file(path)
        with SessionLocal() as session:
            source = _get_or_create_source(session, dataset)
            existing = session.scalar(select(SourceVersion).where(
                SourceVersion.source_pk == source.id, SourceVersion.sha256 == digest))
            if existing is not None:
                status = 'unchanged' if existing.status == 'active' else 'reactivated'
                _activate(session, source, existing)
                session.commit()
                result = {'source': dataset['source_id'], 'status': status, 'version_id': existing.id,
                          'records': existing.record_count}
                _finish_run(run_id, status=status, sha256=digest, version_pk=existing.id,
                            message=f'Hash matches version {existing.id} ({existing.version_label}).')
                return result

            version = SourceVersion(
                source_pk=source.id, version_label=dataset['version_label'] if not file_path else f"{dataset['version_label']} + {path.name}",
                sha256=digest, raw_path=_rel(path), file_size=path.stat().st_size,
                parser_name=dataset['parser_name'], parser_version=dataset['parser_version'], status='loading',
                acquired_at=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc), ingested_at=now())
            session.add(version)
            session.flush()

            seen = set()
            batch = []
            for item in dataset['parser'](path):
                problem = item.pop('_problem', None)
                valid = item.pop('_valid', True)
                if not valid or not item.get('external_id') or not item.get('title'):
                    skipped += 1
                    if len(errors) < MAX_LOGGED_ERRORS:
                        errors.append({'external_id': item.get('external_id'), 'reason': problem or 'missing id or title'})
                    continue
                if item['external_id'] in seen:
                    skipped += 1
                    if len(errors) < MAX_LOGGED_ERRORS:
                        errors.append({'external_id': item['external_id'], 'reason': 'duplicate external_id in snapshot'})
                    continue
                seen.add(item['external_id'])
                batch.append({'version_pk': version.id, 'workflow': dataset['workflow'],
                              'jurisdiction': dataset['jurisdiction'], 'external_id': item['external_id'][:250],
                              'kind': item['kind'], 'title': item['title'], 'content': item['content'],
                              'language': item['language'], 'source_link': item['source_link'],
                              'metadata_': item['metadata']})
                if len(batch) >= BATCH_SIZE:
                    session.execute(insert(KnowledgeRecord), batch)
                    loaded += len(batch)
                    batch.clear()
            if batch:
                session.execute(insert(KnowledgeRecord), batch)
                loaded += len(batch)
            if loaded == 0:
                raise SourceFileError('Parser produced no valid records; refusing to activate an empty version.')
            facts = materialize_facts(session, version.id, dataset['source_id'])

            version.record_count = loaded
            version.snapshot_path = _snapshot(path, dataset['source_id'], digest)
            _activate(session, source, version)
            session.commit()
            version_id = version.id
            session.execute(text('ANALYZE knowledge_records'))  # keep planner statistics fresh for search
            session.commit()
        fact_note = ', '.join(f'{n} {t}' for t, n in facts.items()) or 'no structured facts'
        _finish_run(run_id, status='ingested', sha256=digest, version_pk=version_id, records_loaded=loaded,
                    records_skipped=skipped, errors=errors,
                    message=f'Loaded {loaded} records into new version {version_id}; skipped {skipped}; facts: {fact_note}.')
        return {'source': dataset['source_id'], 'status': 'ingested', 'version_id': version_id,
                'records': loaded, 'skipped': skipped, 'facts': facts}
    except (OperationalError, ProgrammingError):
        raise  # database problems are reported by main()
    except Exception as exc:  # parser / file errors: record the failure, keep going with other sources
        _finish_run(run_id, status='failed', records_loaded=0, records_skipped=skipped,
                    errors=errors + [{'reason': f'{type(exc).__name__}: {exc}'}], message=str(exc))
        return {'source': dataset['source_id'], 'status': 'failed', 'error': str(exc)}


def check_schema():
    with SessionLocal() as s:
        s.execute(text('SELECT 1 FROM source_versions LIMIT 1'))


def main(argv=None):
    parser = argparse.ArgumentParser(description='Ingest registered knowledge sources into PostgreSQL.')
    parser.add_argument('--source', help='Only ingest this source ID')
    parser.add_argument('--file', help='Ingest this file as a new snapshot of --source (for version updates)')
    args = parser.parse_args(argv)
    datasets = [d for d in DATASETS if not args.source or d['source_id'] == args.source]
    if args.source and not datasets:
        sys.exit(f"ERROR: unknown source '{args.source}'. Known: {', '.join(d['source_id'] for d in DATASETS)}")
    if args.file and not args.source:
        sys.exit('ERROR: --file requires --source')
    try:
        check_schema()
        results = [ingest_dataset(d, args.file) for d in datasets]
        if not args.source:
            results += register_not_ingested()
    except OperationalError as exc:
        print(f'ERROR: cannot reach PostgreSQL. Check the service is running and DATABASE_URL in .env.\n{exc.orig}',
              file=sys.stderr)
        sys.exit(1)
    except ProgrammingError as exc:
        print(f'ERROR: database schema missing or out of date. Run: python -m alembic upgrade head\n{exc.orig}',
              file=sys.stderr)
        sys.exit(1)
    for r in results:
        print(json.dumps(r))
    if any(r['status'] == 'failed' for r in results):
        sys.exit(2)


if __name__ == '__main__':
    main()
