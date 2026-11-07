"""Doctor portal API. Patient data is only reachable through an accepted access grant, checked on every call."""
import re
import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ValidationError, field_validator
from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models import now
from ..deps import Auth, audit, current_doctor, get_db, verified_doctor
from .. import extraction
from ..models import (AccessRequest, AllergyDeclaration, Document, DocumentFinding, DoctorProfile, PatientProfile,
                      Trip, User)
from ..reference import COUNTRIES, LANGUAGES, check_country, clean, normalise_email, normalise_phone
from ..security import Throttle
from . import documents as docs_api
from .history import KINDS, create_record, list_records
from .trips import trip_payload

router = APIRouter(prefix='/api/doctor', tags=['doctor portal'])
PATIENT_CODE_RE = re.compile(r'^HC-[A-Z0-9]{4,12}$')
REQUEST_TTL = timedelta(days=30)
request_throttle = Throttle(limit=30, window_seconds=60 * 60)
NOT_GRANTED = 'Patient not found, or you do not have access to this patient.'


# ---------- helpers ----------------------------------------------------------------------------
def expire_stale(db):
    """Pending requests older than 30 days expire (lazy, on read)."""
    db.execute(update(AccessRequest).where(AccessRequest.status == 'pending', AccessRequest.created_at < now() - REQUEST_TTL)
               .values(status='expired', decided_at=now()))


def granted_patient(db, auth, code):
    """The patient behind an ACCEPTED grant for this doctor, else 404 (no hint whether the ID exists)."""
    code = (code or '').strip().upper()
    grant = db.scalar(select(AccessRequest).where(AccessRequest.doctor_id == auth.user.id, AccessRequest.status == 'accepted',
                                                  AccessRequest.requested_patient_code == code,
                                                  AccessRequest.patient_id.is_not(None)))
    if not grant:
        raise HTTPException(404, NOT_GRANTED)
    user = db.get(User, grant.patient_id)
    if not user or user.role != 'patient':
        raise HTTPException(404, NOT_GRANTED)
    return user


def doctor_payload(user, d):
    return {'doctor_id': d.public_doctor_id, 'full_name': d.full_name, 'email': user.email, 'email_verified': user.email_verified,
            'phone': d.phone, 'origin_country': d.origin_country, 'origin_country_name': COUNTRIES.get(d.origin_country),
            'preferred_language': d.preferred_language, 'preferred_language_name': LANGUAGES.get(d.preferred_language),
            'registration_number': d.registration_number, 'hospital': d.hospital, 'speciality': d.speciality,
            'verification_status': d.verification_status, 'member_since': user.created_at.isoformat()}


# ---------- profile ----------------------------------------------------------------------------
class DoctorProfilePatch(BaseModel):
    full_name: str | None = Field(None, max_length=120)
    email: str | None = Field(None, max_length=254)
    phone: str | None = Field(None, max_length=30)
    origin_country: str | None = None
    preferred_language: str | None = None
    hospital: str | None = Field(None, max_length=200)
    speciality: str | None = Field(None, max_length=120)

    @field_validator('full_name')
    @classmethod
    def _name(cls, v):
        if v is None:
            return v
        v = clean(v, 120)
        if not v:
            raise ValueError('Full name is required')
        return v

    @field_validator('email')
    @classmethod
    def _email(cls, v):
        return None if v is None else normalise_email(v)

    @field_validator('phone')
    @classmethod
    def _phone(cls, v):
        return normalise_phone(v)

    @field_validator('origin_country')
    @classmethod
    def _country(cls, v):
        return None if v in (None, '') else check_country(v)

    @field_validator('preferred_language')
    @classmethod
    def _lang(cls, v):
        if v in (None, ''):
            return None
        if v not in LANGUAGES:
            raise ValueError('Choose English or Arabic')
        return v

    @field_validator('hospital', 'speciality')
    @classmethod
    def _opt(cls, v):
        return clean(v)


@router.get('/profile')
def get_profile(auth: Auth = Depends(current_doctor), db: Session = Depends(get_db)):
    return doctor_payload(auth.user, db.get(DoctorProfile, auth.user.id))


@router.patch('/profile')
def patch_profile(data: DoctorProfilePatch, request: Request, auth: Auth = Depends(current_doctor), db: Session = Depends(get_db)):
    d = db.get(DoctorProfile, auth.user.id)
    fields = data.model_dump(exclude_unset=True)
    if fields.get('email') and fields['email'] != auth.user.email:
        if db.scalar(select(User.id).where(User.email == fields['email'], User.id != auth.user.id)):
            raise HTTPException(409, {'message': 'That email is already used by another account.', 'errors': {'email': 'Already in use'}})
        auth.user.email = fields['email']
        auth.user.email_verified = False
    for key in ('full_name', 'phone', 'origin_country', 'preferred_language', 'hospital', 'speciality'):
        if key in fields and not (key == 'full_name' and not fields[key]):
            setattr(d, key, fields[key])
    audit(db, request, 'doctor_profile_updated', actor_id=auth.user.id, entity_type='doctor', entity_id=auth.user.id,
          summary='Doctor profile updated')
    db.commit()
    return doctor_payload(auth.user, d)


# ---------- dashboard & access requests --------------------------------------------------------
@router.get('/dashboard')
def dashboard(auth: Auth = Depends(current_doctor), db: Session = Depends(get_db)):
    expire_stale(db)
    db.commit()
    d = db.get(DoctorProfile, auth.user.id)
    count = lambda *c: db.scalar(select(func.count()).select_from(AccessRequest).where(AccessRequest.doctor_id == auth.user.id, *c))
    # Upcoming arrivals: trips of patients who granted access, under way now or starting in the next 60 days.
    today = date.today()
    granted = select(AccessRequest.patient_id).where(AccessRequest.doctor_id == auth.user.id, AccessRequest.status == 'accepted',
                                                     AccessRequest.patient_id.is_not(None))
    arrivals = db.scalar(select(func.count()).select_from(Trip).where(
        Trip.patient_id.in_(granted), Trip.archived_at.is_(None), Trip.departure_date <= today + timedelta(days=60),
        or_(Trip.return_date >= today, Trip.return_date.is_(None) & (Trip.departure_date >= today))))
    return {'first_name': d.full_name.split()[0] if d.full_name else None, 'full_name': d.full_name,
            'doctor_id': d.public_doctor_id, 'verification_status': d.verification_status,
            'assigned_patients': count(AccessRequest.status == 'accepted', AccessRequest.patient_id.is_not(None)),
            'pending_invitations': count(AccessRequest.status == 'pending'), 'upcoming_arrivals': arrivals}


class AccessRequestIn(BaseModel):
    patient_id: str = Field(max_length=20)


lookup_throttle = Throttle(limit=120, window_seconds=60 * 60)


@router.get('/patient-lookup')
def patient_lookup(q: str = Query('', max_length=20), auth: Auth = Depends(verified_doctor), db: Session = Depends(get_db)):
    """Basic details (name, country) of patients whose ID starts with what the doctor typed (min. 5 characters).
    Records stay locked until the patient accepts a request."""
    code = q.strip().upper()
    if len(code) < 5 or not re.match(r'^[A-Z0-9-]+$', code):
        return []
    key = str(auth.user.id)
    if lookup_throttle.blocked(key):
        raise HTTPException(429, 'Too many lookups. Please try again later.')
    lookup_throttle.hit(key)
    rows = db.execute(select(User.public_patient_id, PatientProfile.full_name, PatientProfile.origin_country)
                      .join(PatientProfile, PatientProfile.user_id == User.id)
                      .where(User.role == 'patient', User.public_patient_id.like(code.replace('%', '').replace('_', '\\_') + '%', escape='\\'))
                      .order_by(User.public_patient_id).limit(5)).all()
    return [{'patient_id': pid, 'full_name': name, 'country': COUNTRIES.get(cc)} for pid, name, cc in rows]


@router.post('/access-requests', status_code=201)
def request_access(data: AccessRequestIn, request: Request, auth: Auth = Depends(verified_doctor), db: Session = Depends(get_db)):
    code = data.patient_id.strip().upper()
    if not PATIENT_CODE_RE.match(code):
        raise HTTPException(422, {'message': 'Enter a valid Patient ID, e.g. HC-8F3A92C1.',
                                  'errors': {'patient_id': 'Enter a valid Patient ID, e.g. HC-8F3A92C1'}})
    key = str(auth.user.id)
    if request_throttle.blocked(key):
        raise HTTPException(429, 'Too many requests. Please try again later.')
    request_throttle.hit(key)
    expire_stale(db)
    existing = db.scalar(select(AccessRequest).where(AccessRequest.doctor_id == auth.user.id,
                                                     AccessRequest.requested_patient_code == code,
                                                     AccessRequest.status.in_(('pending', 'accepted'))))
    if existing:
        msg = 'You already have access to this patient.' if existing.status == 'accepted' else 'A request for this Patient ID is already pending.'
        raise HTTPException(409, {'message': msg, 'errors': {'patient_id': msg}})
    patient = db.scalar(select(User).where(User.public_patient_id == code, User.role == 'patient'))
    if not patient:
        raise HTTPException(404, {'message': 'No patient found with this ID.', 'errors': {'patient_id': 'No patient found with this ID'}})
    req = AccessRequest(doctor_id=auth.user.id, requested_patient_code=code, patient_id=patient.id, status='pending')
    db.add(req)
    try:
        db.flush()
    except IntegrityError:  # concurrent duplicate
        db.rollback()
        raise HTTPException(409, {'message': 'A request for this Patient ID is already pending.',
                                  'errors': {'patient_id': 'A request for this Patient ID is already pending.'}})
    audit(db, request, 'access_requested', actor_id=auth.user.id, patient_id=req.patient_id, entity_type='access_request',
          entity_id=req.id, summary='Doctor requested access')
    db.commit()
    return {'id': str(req.id), 'patient_code': code, 'status': 'pending',
            'message': 'Request sent. The patient will be asked to approve it.'}


@router.get('/access-requests')
def list_requests(status: str = Query('pending', max_length=20), auth: Auth = Depends(current_doctor), db: Session = Depends(get_db)):
    expire_stale(db)
    db.commit()
    rows = db.execute(select(AccessRequest, User.email, PatientProfile.full_name, PatientProfile.origin_country)
                      .outerjoin(User, User.id == AccessRequest.patient_id)
                      .outerjoin(PatientProfile, PatientProfile.user_id == AccessRequest.patient_id)
                      .where(AccessRequest.doctor_id == auth.user.id, AccessRequest.status == status)
                      .order_by(AccessRequest.created_at.desc())).all()
    return [{'id': str(r.id), 'patient_code': r.requested_patient_code, 'status': r.status,
             'requested_at': r.created_at.isoformat(), 'name': name, 'email': email, 'country': COUNTRIES.get(cc)}
            for r, email, name, cc in rows]


@router.post('/access-requests/{request_id}/cancel')
def cancel_request(request_id: uuid.UUID, request: Request, auth: Auth = Depends(current_doctor), db: Session = Depends(get_db)):
    r = db.scalar(select(AccessRequest).where(AccessRequest.id == request_id, AccessRequest.doctor_id == auth.user.id))
    if not r or r.status != 'pending':
        raise HTTPException(404, 'Pending request not found.')
    r.status, r.decided_at = 'cancelled', now()
    audit(db, request, 'access_request_cancelled', actor_id=auth.user.id, patient_id=r.patient_id,
          entity_type='access_request', entity_id=r.id, summary='Doctor cancelled access request')
    db.commit()
    return {'ok': True}


# ---------- authorised patients ----------------------------------------------------------------
@router.get('/patients')
def my_patients(q: str | None = Query(None, max_length=100), auth: Auth = Depends(verified_doctor), db: Session = Depends(get_db)):
    """Only patients who accepted this doctor's request. Never searches the global patient directory."""
    stmt = (select(User, PatientProfile, AccessRequest.decided_at)
            .join(AccessRequest, AccessRequest.patient_id == User.id)
            .join(PatientProfile, PatientProfile.user_id == User.id)
            .where(AccessRequest.doctor_id == auth.user.id, AccessRequest.status == 'accepted')
            .order_by(PatientProfile.full_name))
    if q and q.strip():
        pattern = '%' + q.strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
        stmt = stmt.where(or_(PatientProfile.full_name.ilike(pattern, escape='\\'), User.public_patient_id.ilike(pattern, escape='\\')))
    return [{'patient_id': u.public_patient_id, 'full_name': p.full_name, 'origin_country': p.origin_country,
             'origin_country_name': COUNTRIES.get(p.origin_country), 'preferred_language_name': LANGUAGES.get(p.preferred_language),
             'access_since': decided.isoformat() if decided else None} for u, p, decided in db.execute(stmt)]


@router.get('/patients/{code}')
def patient_summary(code: str, auth: Auth = Depends(verified_doctor), db: Session = Depends(get_db)):
    u = granted_patient(db, auth, code)
    p = db.get(PatientProfile, u.id)
    decl = db.get(AllergyDeclaration, u.id)
    return {'patient_id': u.public_patient_id, 'full_name': p.full_name, 'origin_country_name': COUNTRIES.get(p.origin_country),
            'preferred_language_name': LANGUAGES.get(p.preferred_language),
            'allergy_declaration': decl.declaration if decl else 'unknown'}


@router.get('/patients/{code}/trips')
def patient_trips(code: str, auth: Auth = Depends(verified_doctor), db: Session = Depends(get_db)):
    u = granted_patient(db, auth, code)
    rows = db.scalars(select(Trip).where(Trip.patient_id == u.id, Trip.archived_at.is_(None)).order_by(Trip.departure_date.desc()))
    return [trip_payload(t) for t in rows]


@router.get('/patients/{code}/history/{kind}')
def patient_history(code: str, kind: str, q: str | None = Query(None, max_length=100), status: str | None = Query(None, max_length=30),
                    auth: Auth = Depends(verified_doctor), db: Session = Depends(get_db)):
    if kind not in KINDS:
        raise HTTPException(404, 'Unknown record type')
    u = granted_patient(db, auth, code)
    return list_records(db, kind, u.id, q=q, status=status or None, limit=500)


@router.post('/patients/{code}/history/{kind}', status_code=201)
def add_history(code: str, kind: str, request: Request, body: dict = Body(...), auth: Auth = Depends(verified_doctor),
                db: Session = Depends(get_db)):
    """Doctors may ADD medications, conditions, procedures and allergies; never edit or delete."""
    if kind not in KINDS:
        raise HTTPException(404, 'Unknown record type')
    u = granted_patient(db, auth, code)
    try:
        data = KINDS[kind]['schema'].model_validate(body)  # same rules as the patient form
    except ValidationError as exc:
        raise RequestValidationError(exc.errors())
    if kind == 'allergies':
        decl = db.get(AllergyDeclaration, u.id) or AllergyDeclaration(patient_id=u.id, declaration='unknown')
        if decl.declaration == 'none':
            raise HTTPException(409, 'The patient has declared no known allergies. The allergy was not added; '
                                     'please confirm with the patient so they can update their allergy status.')
        if decl.declaration == 'unknown':
            decl.declaration = 'known'  # a documented allergy makes the status "known"
            db.merge(decl)
            audit(db, request, 'allergy_status_updated', actor_id=auth.user.id, patient_id=u.id,
                  entity_type='allergy_declaration', entity_id=u.id, summary='Allergy status set to known by doctor')
    return create_record(db, request, kind, data, u.id, auth.user)


@router.get('/patients/{code}/allergy-declaration')
def patient_allergy_status(code: str, auth: Auth = Depends(verified_doctor), db: Session = Depends(get_db)):
    u = granted_patient(db, auth, code)
    decl = db.get(AllergyDeclaration, u.id)
    return {'declaration': decl.declaration if decl else 'unknown'}


@router.get('/patients/{code}/documents')
def patient_documents(code: str, q: str | None = Query(None, max_length=100), doc_type: str | None = Query(None, max_length=30),
                      auth: Auth = Depends(verified_doctor), db: Session = Depends(get_db)):
    u = granted_patient(db, auth, code)
    cond = [Document.patient_id == u.id, Document.archived_at.is_(None)]
    if doc_type:
        cond.append(Document.doc_type == doc_type)
    if q and q.strip():
        pattern = '%' + q.strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
        cond.append(or_(Document.name.ilike(pattern, escape='\\'), Document.notes.ilike(pattern, escape='\\'),
                        Document.original_filename.ilike(pattern, escape='\\')))
    rows = db.scalars(select(Document).where(*cond).order_by(Document.created_at.desc()))
    return [docs_api.doc_payload(db, d) for d in rows]


class FindingReview(BaseModel):
    status: str = Field(pattern='^(confirmed|rejected|unverified)$')


def _granted_document(db, auth, code, doc_id):
    u = granted_patient(db, auth, code)
    d = db.scalar(select(Document).where(Document.id == doc_id, Document.patient_id == u.id, Document.archived_at.is_(None)))
    if not d:
        raise HTTPException(404, 'Document not found')
    return u, d


@router.get('/patients/{code}/documents/{doc_id}/extraction')
def patient_document_extraction(code: str, doc_id: uuid.UUID, auth: Auth = Depends(verified_doctor),
                                db: Session = Depends(get_db)):
    _, d = _granted_document(db, auth, code, doc_id)
    return extraction.extraction_payload(db, d)


@router.post('/patients/{code}/findings/{finding_id}/review')
def review_finding(code: str, finding_id: uuid.UUID, body: FindingReview, request: Request,
                   auth: Auth = Depends(verified_doctor), db: Session = Depends(get_db)):
    """Doctor confirms or rejects a value read from a document (or resets it to unverified)."""
    u = granted_patient(db, auth, code)
    f = db.scalar(select(DocumentFinding).where(DocumentFinding.id == finding_id, DocumentFinding.patient_id == u.id))
    if not f:
        raise HTTPException(404, 'Finding not found')
    f.status = body.status
    f.reviewed_by, f.reviewed_at = (None, None) if body.status == 'unverified' else (auth.user.id, now())
    audit(db, request, f'document_finding_{body.status}', actor_id=auth.user.id, patient_id=u.id,
          entity_type='document_finding', entity_id=f.id, summary=f'Extracted value {body.status} by doctor')
    db.commit()
    return extraction.finding_payload(f)


@router.get('/patients/{code}/documents/{doc_id}/download')
def patient_document_download(code: str, doc_id: uuid.UUID, request: Request, inline: bool = False,
                              auth: Auth = Depends(verified_doctor), db: Session = Depends(get_db)):
    u = granted_patient(db, auth, code)
    d = db.scalar(select(Document).where(Document.id == doc_id, Document.patient_id == u.id, Document.archived_at.is_(None)))
    if not d:
        raise HTTPException(404, 'Document not found')
    path = docs_api._path(u.id, d.storage_key)
    if not path.is_file():
        raise HTTPException(410, 'The stored file is missing.')
    audit(db, request, 'document_viewed_by_doctor', actor_id=auth.user.id, patient_id=u.id, entity_type='document', entity_id=d.id)
    db.commit()
    return docs_api.file_response(d, path, inline)
