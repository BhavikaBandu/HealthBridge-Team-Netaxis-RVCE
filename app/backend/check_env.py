"""Check the local environment and print actionable fixes.

    python -m backend.check_env
"""
import importlib.util
import sys

from backend.config import DATABASE_URL, ROOT

OK, WARN, FAIL = '[ OK ]', '[WARN]', '[FAIL]'
problems = 0


def report(level, msg, fix=None):
    global problems
    if level == FAIL:
        problems += 1
    print(f'{level} {msg}')
    if fix and level != OK:
        print(f'       -> {fix}')


def main():
    v = sys.version_info
    report(OK if v >= (3, 11) else FAIL, f'Python {v.major}.{v.minor}.{v.micro}', 'Install Python 3.11+ and recreate .venv: py -3.11 -m venv .venv')
    missing = [m for m in ('fastapi', 'uvicorn', 'sqlalchemy', 'psycopg', 'alembic', 'defusedxml', 'dotenv', 'jinja2')
               if importlib.util.find_spec(m) is None]
    report(FAIL if missing else OK, f"Core packages{': missing ' + ', '.join(missing) if missing else ''}",
           'python -m pip install -r requirements.txt')
    sem_missing = [m for m in ('numpy', 'fastembed') if importlib.util.find_spec(m) is None]
    report(WARN if sem_missing else OK, f"Semantic packages{' (optional) missing: ' + ', '.join(sem_missing) if sem_missing else ''}",
           'python -m pip install -r requirements-semantic.txt')
    report(OK if (ROOT / '.env').exists() else WARN, '.env file', 'Copy-Item .env.example .env  (defaults are used until then)')
    safe_url = DATABASE_URL.split('@')[-1]
    for path in ('data/raw/medicines/AIPS_20261101_original.zip', 'data/raw/medical_reports/ucum-essence.xml'):
        report(OK if (ROOT / path).exists() else FAIL, f'Raw source {path}', 'Restore the file from the project archive')

    try:
        from sqlalchemy import text
        from backend.database import engine
        with engine.connect() as c:
            server = c.execute(text('SHOW server_version')).scalar()
            report(OK, f'PostgreSQL {server} reachable at {safe_url}')
            try:
                rev = c.execute(text('SELECT version_num FROM alembic_version')).scalar()
            except Exception:
                rev = None
            report(OK if rev else FAIL, f'Schema migration: {rev or "not applied"}', 'python -m alembic upgrade head')
            if rev:
                trgm = c.execute(text("SELECT 1 FROM pg_extension WHERE extname='pg_trgm'")).scalar()
                report(OK if trgm else FAIL, 'pg_trgm extension', 'python -m alembic upgrade head (creates it)')
                active = c.execute(text('SELECT count(*) FROM sources WHERE active_version_id IS NOT NULL')).scalar()
                report(OK if active else WARN, f'Active sources: {active}', 'python -m backend.ingestion.pipeline')
                emb = c.execute(text('SELECT count(*) FROM record_embeddings')).scalar()
                report(OK if emb else WARN, f'Embeddings stored: {emb}', 'python -m backend.retrieval.embeddings  (optional, for semantic/hybrid)')
            vec = c.execute(text("SELECT 1 FROM pg_available_extensions WHERE name='vector'")).scalar()
            report(OK if vec else WARN, 'pgvector ' + ('available' if vec else 'not installed (optional; NumPy fallback is used)'))
    except Exception as exc:
        report(FAIL, f'Cannot connect to PostgreSQL at {safe_url}: {type(exc).__name__}',
               'Start the "postgresql-x64-17" Windows service and check DATABASE_URL in .env; see docs/LOCAL_POSTGRESQL_SETUP.md')

    print('\nAll required checks passed.' if not problems else f'\n{problems} required check(s) failed.')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
