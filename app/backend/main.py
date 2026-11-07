import logging
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from backend.api.knowledge import router as knowledge_router
from backend.api.retrieval import router as retrieval_router
from backend.config import APP_TITLE, ROOT, UPLOAD_DIR
from backend.database import SessionLocal
from backend.portal import pages
from backend.portal.routers import access, analysis, auth, dashboard, doctor, documents, history, profile, trips

log = logging.getLogger('uvicorn.error')


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start even if PostgreSQL is down; requests then return 503 instead of the server crashing.
    try:
        with SessionLocal() as s:
            s.execute(text('SELECT version_num FROM alembic_version'))
    except OperationalError as exc:
        log.warning('Database unavailable at startup: %s', exc.orig)
    except ProgrammingError:
        log.warning('Database schema missing. Run: python -m alembic upgrade head')
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title='HealthBridge', lifespan=lifespan,
              description='HealthBridge patient and doctor portals and reference knowledge API. Not clinical decision support.')
for r in (auth.router, profile.router, trips.router, history.router, documents.router, dashboard.router,
          access.router, doctor.router, analysis.router, knowledge_router, retrieval_router, pages.router):
    app.include_router(r)
app.mount('/static', StaticFiles(directory=ROOT / 'frontend/static'), name='static')


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    """Consistent error payload: {'detail': {'message', 'errors': {field: message}}}."""
    errors = {}
    for e in exc.errors():
        loc = [str(x) for x in e.get('loc', []) if x not in ('body', 'query', 'path', 'form')]
        msg = re.sub(r'^(Value|Assertion) error, ', '', e.get('msg', 'Invalid value'))
        m = re.match(r'^([a-z_]+): (.+)$', msg)  # model-level errors are written as "field: message"
        field = m.group(1) if m else (loc[0] if loc else '_')
        errors.setdefault(field, m.group(2) if m else msg)
    return JSONResponse(status_code=422, content={'detail': {'message': 'Please fix the highlighted fields.', 'errors': errors}})


@app.exception_handler(OperationalError)
async def database_unavailable(request: Request, exc: OperationalError):
    log.error('Database error: %s', exc.orig)
    return JSONResponse(status_code=503, content={'detail': 'Database unavailable. Check that PostgreSQL is running and DATABASE_URL is correct.'})


@app.exception_handler(ProgrammingError)
async def schema_missing(request: Request, exc: ProgrammingError):
    log.error('Database schema error: %s', exc.orig)
    return JSONResponse(status_code=503, content={'detail': 'Database schema missing or out of date. Run: python -m alembic upgrade head'})
