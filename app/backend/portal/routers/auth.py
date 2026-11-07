import secrets
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.config import COOKIE_SECURE
from backend.models import now
from ..deps import Auth, audit, client_ip, current_user, get_db, load_session
from ..models import AllergyDeclaration, DoctorProfile, PatientProfile, User, UserSession
from ..reference import LANGUAGES, check_country, clean, normalise_email, normalise_phone
from ..security import (CSRF_COOKIE, PASSWORD_MAX, SESSION_COOKIE, burn_verify, hash_password, login_throttle,
                        new_session_values, password_problems, password_throttle, signup_throttle, token_hash,
                        verify_password)

router = APIRouter(prefix='/api/auth', tags=['auth'])


class SignupIn(BaseModel):
    full_name: str = Field(max_length=120)
    email: str = Field(max_length=254)
    phone: str | None = Field(None, max_length=30)
    origin_country: str | None = None
    preferred_language: str | None = None
    password: str = Field(max_length=PASSWORD_MAX)
    confirm_password: str = Field(max_length=PASSWORD_MAX)

    @field_validator('full_name')
    @classmethod
    def _name(cls, v):
        v = clean(v, 120)
        if not v:
            raise ValueError('Enter your full name')
        return v

    _email = field_validator('email')(lambda cls, v: normalise_email(v))
    _phone = field_validator('phone')(lambda cls, v: normalise_phone(v))
    _country = field_validator('origin_country')(lambda cls, v: check_country(v, required=False))

    @field_validator('preferred_language')
    @classmethod
    def _lang(cls, v):
        if v in (None, ''):
            return None
        if v not in LANGUAGES:
            raise ValueError('Choose English or Arabic')
        return v

    @field_validator('password')
    @classmethod
    def _password(cls, v):
        problems = password_problems(v)
        if problems:
            raise ValueError('Password needs: ' + ', '.join(problems).lower())
        return v

    @model_validator(mode='after')
    def _match(self):
        if self.password != self.confirm_password:
            raise ValueError('confirm_password: Passwords do not match')
        return self


class DoctorSignupIn(SignupIn):
    registration_number: str | None = Field(None, max_length=60)
    hospital: str | None = Field(None, max_length=200)
    speciality: str | None = Field(None, max_length=120)

    @field_validator('registration_number', 'hospital', 'speciality')
    @classmethod
    def _optional_text(cls, v):
        return clean(v)


class LoginIn(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=PASSWORD_MAX)
    role: Literal['patient', 'doctor'] = 'patient'
    remember: bool = False


class ChangePasswordIn(BaseModel):
    current_password: str = Field(max_length=PASSWORD_MAX)
    new_password: str = Field(max_length=PASSWORD_MAX)
    confirm_new_password: str = Field(max_length=PASSWORD_MAX)


def _new_patient_id(db):
    while True:
        pid = 'HC-' + secrets.token_hex(4).upper()
        if not db.scalar(select(User.id).where(User.public_patient_id == pid)):
            return pid


def new_doctor_id(db):
    while True:
        did = 'DR-' + secrets.token_hex(4).upper()
        if not db.scalar(select(DoctorProfile.user_id).where(DoctorProfile.public_doctor_id == did)):
            return did


def _start_session(db, response, user, remember):
    token, csrf, expires, lifetime = new_session_values(remember)
    db.add(UserSession(user_id=user.id, token_hash=token_hash(token), csrf_token=csrf, expires_at=expires, remember=remember))
    max_age = int(lifetime.total_seconds()) if remember else None
    response.set_cookie(SESSION_COOKIE, token, max_age=max_age, httponly=True, secure=COOKIE_SECURE, samesite='lax', path='/')
    response.set_cookie(CSRF_COOKIE, csrf, max_age=max_age, httponly=False, secure=COOKIE_SECURE, samesite='lax', path='/')


def _clear_cookies(response):
    response.delete_cookie(SESSION_COOKIE, path='/')
    response.delete_cookie(CSRF_COOKIE, path='/')


def me_payload(db, user):
    if user.role == 'doctor':
        d = db.get(DoctorProfile, user.id)
        return {'role': 'doctor', 'doctor_id': d.public_doctor_id if d else None, 'email': user.email,
                'email_verified': user.email_verified, 'full_name': d.full_name if d else None,
                'verification_status': d.verification_status if d else 'pending'}
    p = db.get(PatientProfile, user.id)
    return {'patient_id': user.public_patient_id, 'email': user.email, 'email_verified': user.email_verified,
            'role': user.role, 'full_name': p.full_name if p else None,
            'first_name': (p.full_name.split()[0] if p and p.full_name else None),
            'profile_complete': bool(p and p.full_name and p.origin_country and p.preferred_language)}


def _create_user(db, request, data, role):
    ip = client_ip(request) or 'unknown'
    if signup_throttle.blocked(ip):
        raise HTTPException(429, 'Too many sign-up attempts. Please try again later.')
    signup_throttle.hit(ip)
    if db.scalar(select(User.id).where(User.email == data.email)):
        raise HTTPException(409, 'An account with this email already exists. Try signing in.')
    user = User(email=data.email, password_hash=hash_password(data.password), role=role,
                public_patient_id=_new_patient_id(db) if role == 'patient' else None,
                password_changed_at=now(), last_login_at=now())
    db.add(user)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'An account with this email already exists. Try signing in.')
    return user


@router.post('/doctor-signup', status_code=201)
def doctor_signup(data: DoctorSignupIn, request: Request, response: Response, db: Session = Depends(get_db)):
    user = _create_user(db, request, data, 'doctor')
    db.add(DoctorProfile(user_id=user.id, public_doctor_id=new_doctor_id(db), full_name=data.full_name, phone=data.phone,
                         origin_country=data.origin_country, preferred_language=data.preferred_language,
                         registration_number=data.registration_number, hospital=data.hospital,
                         speciality=data.speciality, verification_status='pending'))
    audit(db, request, 'doctor_account_created', actor_id=user.id, entity_type='user', entity_id=user.id,
          summary='Doctor account created (awaiting verification)')
    _start_session(db, response, user, remember=False)
    db.commit()
    return me_payload(db, user)


@router.post('/signup', status_code=201)
def signup(data: SignupIn, request: Request, response: Response, db: Session = Depends(get_db)):
    user = _create_user(db, request, data, 'patient')
    db.add(PatientProfile(user_id=user.id, full_name=data.full_name, origin_country=data.origin_country,
                          preferred_language=data.preferred_language, phone=data.phone))
    db.add(AllergyDeclaration(patient_id=user.id, declaration='unknown'))
    audit(db, request, 'account_created', actor_id=user.id, patient_id=user.id, entity_type='user',
          entity_id=user.id, summary='Account created')
    _start_session(db, response, user, remember=False)
    db.commit()
    return me_payload(db, user)


@router.post('/login')
def login(data: LoginIn, request: Request, response: Response, db: Session = Depends(get_db)):
    email = (data.email or '').strip().lower()
    key = f'{email}|{client_ip(request)}'
    if login_throttle.blocked(key):
        raise HTTPException(429, f'Too many failed attempts. Try again in {login_throttle.retry_after(key) // 60 + 1} minutes.')
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        burn_verify(data.password)
    if not user or not verify_password(user.password_hash, data.password) or user.role != data.role:
        login_throttle.hit(key)
        if user:
            audit(db, request, 'login_failed', patient_id=user.id, entity_type='user', entity_id=user.id)
            db.commit()
        raise HTTPException(401, 'Incorrect email or password.')
    login_throttle.reset(key)
    user.last_login_at = now()
    _start_session(db, response, user, data.remember)
    audit(db, request, 'login', actor_id=user.id, patient_id=user.id, entity_type='user', entity_id=user.id, summary='Signed in')
    db.commit()
    return me_payload(db, user)


@router.post('/logout')
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    auth = load_session(db, request)
    if auth:
        auth.session.revoked_at = now()
        audit(db, request, 'logout', actor_id=auth.user.id, patient_id=auth.user.id, entity_type='user',
              entity_id=auth.user.id, summary='Signed out')
        db.commit()
    _clear_cookies(response)
    return {'ok': True}


@router.get('/me')
def me(auth: Auth = Depends(current_user), db: Session = Depends(get_db)):
    return me_payload(db, auth.user)


@router.post('/change-password')
def change_password(data: ChangePasswordIn, request: Request, auth: Auth = Depends(current_user),
                    db: Session = Depends(get_db)):
    key = str(auth.user.id)
    if password_throttle.blocked(key):
        raise HTTPException(429, 'Too many attempts. Please wait 15 minutes and try again.')
    errors = {}
    if not verify_password(auth.user.password_hash, data.current_password):
        password_throttle.hit(key)
        errors['current_password'] = 'Current password is incorrect'
    problems = password_problems(data.new_password)
    if problems:
        errors['new_password'] = 'Password needs: ' + ', '.join(problems).lower()
    elif data.new_password == data.current_password:
        errors['new_password'] = 'New password must be different from the current one'
    if data.new_password != data.confirm_new_password:
        errors['confirm_new_password'] = 'Passwords do not match'
    if errors:
        raise HTTPException(422, {'message': 'Please fix the highlighted fields.', 'errors': errors})
    password_throttle.reset(key)
    auth.user.password_hash = hash_password(data.new_password)
    auth.user.password_changed_at = now()
    # Sign out every other session of this user.
    db.execute(update(UserSession).where(UserSession.user_id == auth.user.id, UserSession.id != auth.session.id,
                                         UserSession.revoked_at.is_(None)).values(revoked_at=now()))
    audit(db, request, 'password_changed', actor_id=auth.user.id, patient_id=auth.user.id, entity_type='user',
          entity_id=auth.user.id, summary='Password changed')
    db.commit()
    return {'ok': True, 'message': 'Password updated. Other devices have been signed out.'}
