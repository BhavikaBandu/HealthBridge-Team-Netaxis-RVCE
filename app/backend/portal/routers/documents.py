"""Document upload/download. Files live in a private folder, served only to their owner (and doctors with access).
After upload, text and printed values are extracted in the background (see portal/extraction.py)."""
import os
import re
import secrets
import unicodedata
import uuid
from datetime import date
from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from backend.config import MAX_UPLOAD_BYTES, UPLOAD_DIR
from backend.models import now
from ..deps import Auth, audit, current_patient, get_db
from ..models import Allergy, Condition, Document, DocumentLink, Medication, Procedure
from ..extraction import extract_by_id, extraction_payload, summary as extraction_summary
from ..reference import DOCUMENT_TYPES, RECORD_TYPES, clean

router = APIRouter(prefix='/api/documents', tags=['documents'])

ALLOWED = {  # detected type -> (mime, allowed extensions)
    'pdf': ('application/pdf', {'.pdf'}),
    'png': ('image/png', {'.png'}),
    'jpeg': ('image/jpeg', {'.jpg', '.jpeg'}),
}
RECORD_MODELS = {'medication': Medication, 'condition': Condition, 'procedure': Procedure, 'allergy': Allergy}


def sniff(head: bytes):
    if head.startswith(b'%PDF-'):
        return 'pdf'
    if head.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    if head.startswith(b'\xff\xd8\xff'):
        return 'jpeg'
    return None


def safe_filename(name):
    name = os.path.basename((name or '').replace('\\', '/'))
    name = unicodedata.normalize('NFKC', name)
    name = re.sub(r'[\x00-\x1f\x7f<>:"/\\|?*]', '_', name).strip(' .')
    return (name or 'document')[:200]


def _path(patient_id, key):
    return UPLOAD_DIR / patient_id.hex / key


def _record_label(db, patient_id, record_type, record_id):
    model = RECORD_MODELS[record_type]
    r = db.scalar(select(model).where(model.id == record_id, model.patient_id == patient_id))
    if not r:
        return None
    return {'name': r.allergen if record_type == 'allergy' else r.name, 'archived': r.archived_at is not None}


def doc_payload(db, d):
    links = []
    for link in db.scalars(select(DocumentLink).where(DocumentLink.document_id == d.id, DocumentLink.patient_id == d.patient_id)
                           .order_by(DocumentLink.created_at)):
        info = _record_label(db, d.patient_id, link.record_type, link.record_id)
        links.append({'link_id': str(link.id), 'record_type': link.record_type, 'record_id': str(link.record_id),
                      'label': info['name'] if info else '(record no longer available)',
                      'record_archived': bool(info and info['archived']), 'missing': info is None})
    return {'id': str(d.id), 'name': d.name, 'doc_type': d.doc_type, 'doc_type_label': DOCUMENT_TYPES.get(d.doc_type, d.doc_type),
            'document_date': d.document_date.isoformat() if d.document_date else None, 'notes': d.notes,
            'original_filename': d.original_filename, 'mime_type': d.mime_type, 'size_bytes': d.size_bytes,
            'uploaded_at': d.created_at.isoformat(), 'updated_at': d.updated_at.isoformat(),
            'archived': d.archived_at is not None, 'links': links, 'extraction': extraction_summary(db, d)}


def get_owned(db, auth, doc_id):
    d = db.scalar(select(Document).where(Document.id == doc_id, Document.patient_id == auth.patient_id))
    if not d:
        raise HTTPException(404, 'Document not found')
    return d


def _validate_link(db, auth, record_type, record_id):
    if record_type not in RECORD_TYPES:
        raise HTTPException(422, 'Unknown record type')
    model = RECORD_MODELS[record_type]
    if not db.scalar(select(model.id).where(model.id == record_id, model.patient_id == auth.patient_id)):
        raise HTTPException(404, 'Medical-history record not found')  # never link across patients


def _add_link(db, auth, d, record_type, record_id):
    _validate_link(db, auth, record_type, record_id)
    exists = db.scalar(select(DocumentLink.id).where(DocumentLink.document_id == d.id, DocumentLink.record_type == record_type,
                                                     DocumentLink.record_id == record_id))
    if not exists:
        db.add(DocumentLink(document_id=d.id, patient_id=auth.patient_id, record_type=record_type, record_id=record_id))


class DocumentPatch(BaseModel):
    name: str = Field(max_length=200)
    doc_type: str
    document_date: date | None = None
    notes: str | None = Field(None, max_length=2000)

    @model_validator(mode='after')
    def _rules(self):
        self.name = clean(self.name, 200)
        if not self.name:
            raise ValueError('name: Document name is required')
        if self.doc_type not in DOCUMENT_TYPES:
            raise ValueError('doc_type: Choose a document type')
        self.notes = clean(self.notes)
        return self


class LinkIn(BaseModel):
    record_type: str
    record_id: uuid.UUID


@router.get('')
def list_documents(archived: bool = False, doc_type: str | None = Query(None, max_length=30),
                   q: str | None = Query(None, max_length=100), limit: int = Query(100, ge=1, le=500),
                   offset: int = Query(0, ge=0), auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    cond = [Document.patient_id == auth.patient_id,
            Document.archived_at.is_not(None) if archived else Document.archived_at.is_(None)]
    if doc_type:
        cond.append(Document.doc_type == doc_type)
    if q and q.strip():
        pattern = '%' + q.strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
        cond.append(or_(Document.name.ilike(pattern, escape='\\'), Document.notes.ilike(pattern, escape='\\'),
                        Document.original_filename.ilike(pattern, escape='\\')))
    total = db.scalar(select(func.count()).select_from(Document).where(*cond))
    rows = db.scalars(select(Document).where(*cond).order_by(Document.created_at.desc()).offset(offset).limit(limit))
    return {'items': [doc_payload(db, d) for d in rows], 'total': total}


@router.post('', status_code=201)
async def upload_document(request: Request, background: BackgroundTasks, file: UploadFile = File(...), name: str = Form(..., max_length=200),
                          doc_type: str = Form(...), document_date: date | None = Form(None),
                          notes: str | None = Form(None, max_length=2000), record_type: str | None = Form(None),
                          record_id: uuid.UUID | None = Form(None), auth: Auth = Depends(current_patient),
                          db: Session = Depends(get_db)):
    meta = DocumentPatch(name=name, doc_type=doc_type, document_date=document_date or None, notes=notes)
    if record_type and record_id:
        _validate_link(db, auth, record_type, record_id)
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f'File is larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.')
    if not data:
        raise HTTPException(422, {'message': 'The file is empty.', 'errors': {'file': 'The file is empty'}})
    kind = sniff(data[:16])
    filename = safe_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()
    if not kind or ext not in ALLOWED[kind][1]:
        raise HTTPException(415, {'message': 'Only PDF, JPG and PNG files are accepted.',
                                  'errors': {'file': 'Only PDF, JPG and PNG files are accepted'}})
    key = secrets.token_hex(16)
    path = _path(auth.patient_id, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.part')
    tmp.write_bytes(data)
    os.replace(tmp, path)
    d = Document(patient_id=auth.patient_id, name=meta.name, doc_type=meta.doc_type, document_date=meta.document_date,
                 notes=meta.notes, storage_key=key, original_filename=filename, mime_type=ALLOWED[kind][0],
                 size_bytes=len(data))
    db.add(d)
    db.flush()
    if record_type and record_id:
        _add_link(db, auth, d, record_type, record_id)
    audit(db, request, 'document_uploaded', actor_id=auth.user.id, patient_id=auth.patient_id, entity_type='document',
          entity_id=d.id, summary=f'Document uploaded: {meta.name}')
    try:
        db.commit()
    except Exception:
        path.unlink(missing_ok=True)
        raise
    background.add_task(extract_by_id, d.id)   # read text + printed values after the response is sent
    return doc_payload(db, d)


@router.get('/{doc_id}')
def get_document(doc_id: uuid.UUID, auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    return doc_payload(db, get_owned(db, auth, doc_id))


@router.get('/{doc_id}/extraction')
def get_extraction(doc_id: uuid.UUID, auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    """Text and values read from the patient's own document (read-only for patients)."""
    return extraction_payload(db, get_owned(db, auth, doc_id))


@router.patch('/{doc_id}')
def update_document(doc_id: uuid.UUID, data: DocumentPatch, request: Request, auth: Auth = Depends(current_patient),
                    db: Session = Depends(get_db)):
    d = get_owned(db, auth, doc_id)
    for k, v in data.model_dump().items():
        setattr(d, k, v)
    audit(db, request, 'document_updated', actor_id=auth.user.id, patient_id=auth.patient_id, entity_type='document',
          entity_id=d.id, summary=f'Document details updated: {d.name}')
    db.commit()
    return doc_payload(db, d)


@router.get('/{doc_id}/download')
def download_document(doc_id: uuid.UUID, request: Request, inline: bool = False, auth: Auth = Depends(current_patient),
                      db: Session = Depends(get_db)):
    d = get_owned(db, auth, doc_id)
    path = _path(auth.patient_id, d.storage_key)
    if not path.is_file():
        raise HTTPException(410, 'The stored file is missing.')
    audit(db, request, 'document_viewed' if inline else 'document_downloaded', actor_id=auth.user.id,
          patient_id=auth.patient_id, entity_type='document', entity_id=d.id)
    db.commit()
    return file_response(d, path, inline)


def file_response(d, path, inline):
    disposition = 'inline' if inline else 'attachment'
    ascii_name = d.original_filename.encode('ascii', 'replace').decode().replace('"', '')
    return FileResponse(path, media_type=d.mime_type, headers={
        'Content-Disposition': f"{disposition}; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(d.original_filename)}",
        'X-Content-Type-Options': 'nosniff', 'Cache-Control': 'private, no-store'})


@router.post('/{doc_id}/archive')
def archive_document(doc_id: uuid.UUID, request: Request, auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    d = get_owned(db, auth, doc_id)
    if d.archived_at is None:
        d.archived_at = now()
        audit(db, request, 'document_archived', actor_id=auth.user.id, patient_id=auth.patient_id, entity_type='document',
              entity_id=d.id, summary=f'Document archived: {d.name}')
        db.commit()
    return doc_payload(db, d)


@router.post('/{doc_id}/restore')
def restore_document(doc_id: uuid.UUID, request: Request, auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    d = get_owned(db, auth, doc_id)
    if d.archived_at is not None:
        d.archived_at = None
        audit(db, request, 'document_restored', actor_id=auth.user.id, patient_id=auth.patient_id, entity_type='document',
              entity_id=d.id, summary=f'Document restored: {d.name}')
        db.commit()
    return doc_payload(db, d)


@router.delete('/{doc_id}')
def delete_document(doc_id: uuid.UUID, request: Request, auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    d = get_owned(db, auth, doc_id)
    path = _path(auth.patient_id, d.storage_key)
    name = d.name
    db.execute(delete(DocumentLink).where(DocumentLink.document_id == d.id, DocumentLink.patient_id == auth.patient_id))
    db.delete(d)
    audit(db, request, 'document_deleted', actor_id=auth.user.id, patient_id=auth.patient_id, entity_type='document',
          entity_id=doc_id, summary=f'Document deleted: {name}')
    db.commit()
    path.unlink(missing_ok=True)
    return {'ok': True}


@router.post('/{doc_id}/links', status_code=201)
def add_link(doc_id: uuid.UUID, data: LinkIn, request: Request, auth: Auth = Depends(current_patient),
             db: Session = Depends(get_db)):
    d = get_owned(db, auth, doc_id)
    _add_link(db, auth, d, data.record_type, data.record_id)
    audit(db, request, 'document_linked', actor_id=auth.user.id, patient_id=auth.patient_id, entity_type='document',
          entity_id=d.id, summary=f'Document linked: {d.name}')
    db.commit()
    return doc_payload(db, d)


@router.delete('/{doc_id}/links/{link_id}')
def remove_link(doc_id: uuid.UUID, link_id: uuid.UUID, request: Request, auth: Auth = Depends(current_patient),
                db: Session = Depends(get_db)):
    d = get_owned(db, auth, doc_id)
    link = db.scalar(select(DocumentLink).where(DocumentLink.id == link_id, DocumentLink.document_id == d.id,
                                                DocumentLink.patient_id == auth.patient_id))
    if not link:
        raise HTTPException(404, 'Link not found')
    db.delete(link)
    audit(db, request, 'document_unlinked', actor_id=auth.user.id, patient_id=auth.patient_id, entity_type='document',
          entity_id=d.id, summary=f'Document unlinked: {d.name}')
    db.commit()
    return doc_payload(db, d)
