from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import Auth, audit, current_patient, get_db
from ..models import PatientProfile, User
from ..reference import (COUNTRIES, COUNTRY_OPTIONS, DOCUMENT_TYPES, DOSAGE_FORMS, LANGUAGES, STRENGTH_UNITS,
                         TRIP_PURPOSES, check_country, clean, normalise_email, normalise_phone)
from ..security import PASSWORD_RULES

router = APIRouter(prefix='/api', tags=['profile'])


class ProfilePatch(BaseModel):
    full_name: str | None = Field(None, max_length=120)
    email: str | None = Field(None, max_length=254)
    origin_country: str | None = None
    preferred_language: str | None = None
    phone: str | None = Field(None, max_length=30)

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

    @field_validator('phone')
    @classmethod
    def _phone(cls, v):
        return normalise_phone(v)


def profile_payload(user, p):
    missing = [label for label, value in (('origin country', p.origin_country), ('preferred language', p.preferred_language))
               if not value]
    return {'patient_id': user.public_patient_id, 'full_name': p.full_name, 'email': user.email,
            'email_verified': user.email_verified, 'origin_country': p.origin_country,
            'origin_country_name': COUNTRIES.get(p.origin_country), 'preferred_language': p.preferred_language,
            'preferred_language_name': LANGUAGES.get(p.preferred_language), 'phone': p.phone,
            'member_since': user.created_at.isoformat(), 'profile_complete': not missing, 'missing_fields': missing}


@router.get('/profile')
def get_profile(auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    return profile_payload(auth.user, db.get(PatientProfile, auth.patient_id))


@router.patch('/profile')
def patch_profile(data: ProfilePatch, request: Request, auth: Auth = Depends(current_patient),
                  db: Session = Depends(get_db)):
    p = db.get(PatientProfile, auth.patient_id)
    fields = data.model_dump(exclude_unset=True)
    changed = []
    if 'email' in fields and fields['email'] and fields['email'] != auth.user.email:
        if db.scalar(select(User.id).where(User.email == fields['email'], User.id != auth.user.id)):
            raise HTTPException(409, {'message': 'That email is already used by another account.',
                                      'errors': {'email': 'Already in use'}})
        auth.user.email = fields['email']
        auth.user.email_verified = False  # no verification mechanism yet; never claim verified
        changed.append('email')
    for key in ('full_name', 'origin_country', 'preferred_language', 'phone'):
        if key in fields:
            if key == 'full_name' and not fields[key]:
                continue
            setattr(p, key, fields[key])
            changed.append(key)
    if changed:
        audit(db, request, 'profile_updated', actor_id=auth.user.id, patient_id=auth.patient_id,
              entity_type='profile', entity_id=auth.user.id, summary='Profile updated')
    db.commit()
    return profile_payload(auth.user, p)


@router.get('/portal/reference')
def reference_lists():
    """Static option lists for portal forms (no patient data)."""
    return {'countries': COUNTRY_OPTIONS, 'languages': [{'code': k, 'name': v} for k, v in LANGUAGES.items()],
            'trip_purposes': TRIP_PURPOSES, 'dosage_forms': DOSAGE_FORMS, 'strength_units': STRENGTH_UNITS,
            'document_types': DOCUMENT_TYPES,
            'password_rules': [{'key': k, 'label': label} for k, label, _ in PASSWORD_RULES]}
