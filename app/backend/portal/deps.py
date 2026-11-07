"""Request dependencies: DB session, authenticated patient, CSRF check, audit helper."""
import hmac
import uuid
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import now
from .models import AuditEvent, PatientProfile, User, UserSession
from .security import CSRF_HEADER, SESSION_COOKIE, token_hash

SAFE_METHODS = {'GET', 'HEAD', 'OPTIONS'}


def get_db():
    with SessionLocal() as session:
        yield session


@dataclass
class Auth:
    user: User
    session: UserSession

    @property
    def patient_id(self) -> uuid.UUID:
        return self.user.id


def load_session(db: Session, request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    s = db.scalar(select(UserSession).where(UserSession.token_hash == token_hash(token)))
    if not s or s.revoked_at is not None or s.expires_at <= now():
        return None
    user = db.get(User, s.user_id)
    return Auth(user=user, session=s) if user else None


def _authenticated(request, db, role=None):
    auth = load_session(db, request)
    if not auth:
        raise HTTPException(401, 'Please sign in to continue.')
    if role and auth.user.role != role:
        raise HTTPException(403, 'This area is not available for your account type.')
    if request.method not in SAFE_METHODS:
        sent = request.headers.get(CSRF_HEADER, '')
        if not sent or not hmac.compare_digest(sent, auth.session.csrf_token):
            raise HTTPException(403, 'Security check failed. Please reload the page and try again.')
    return auth


def current_user(request: Request, db: Session = Depends(get_db)) -> Auth:
    """Any signed-in account (patient or doctor)."""
    return _authenticated(request, db)


def current_patient(request: Request, db: Session = Depends(get_db)) -> Auth:
    return _authenticated(request, db, 'patient')


def current_doctor(request: Request, db: Session = Depends(get_db)) -> Auth:
    """Any signed-in doctor, including ones still awaiting verification (own profile, knowledge search)."""
    return _authenticated(request, db, 'doctor')


def verified_doctor(request: Request, db: Session = Depends(get_db)) -> Auth:
    """Doctors approved by an administrator. Required for anything touching patient data."""
    from .models import DoctorProfile
    auth = _authenticated(request, db, 'doctor')
    profile = db.get(DoctorProfile, auth.user.id)
    if not profile or profile.verification_status != 'approved':
        raise HTTPException(403, 'Your doctor account is awaiting verification. Patient features unlock once it is approved.')
    return auth


def client_ip(request: Request):
    return request.client.host if request.client else None


def audit(db: Session, request: Request, action, *, actor_id=None, patient_id=None, entity_type=None,
          entity_id=None, summary=None):
    """Record an audit event. Keep summaries free of medication details, passwords or file contents."""
    db.add(AuditEvent(actor_id=actor_id, patient_id=patient_id, action=action, entity_type=entity_type,
                      entity_id=entity_id, summary=summary[:200] if summary else None, ip=client_ip(request)))


def profile_of(db: Session, user_id):
    return db.get(PatientProfile, user_id)
