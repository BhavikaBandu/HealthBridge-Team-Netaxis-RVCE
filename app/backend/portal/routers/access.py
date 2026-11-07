"""Patient side of doctor access: see requests, accept/reject, revoke. Access is never granted automatically."""
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import now
from ..deps import Auth, audit, current_patient, get_db
from ..models import AccessRequest, DoctorProfile
from ..reference import COUNTRIES
from .doctor import expire_stale

router = APIRouter(prefix='/api', tags=['doctor access (patient)'])


class DecisionIn(BaseModel):
    decision: Literal['accept', 'reject']


def _payload(r, d):
    return {'id': str(r.id), 'status': r.status, 'requested_at': r.created_at.isoformat(),
            'decided_at': r.decided_at.isoformat() if r.decided_at else None,
            'doctor': {'doctor_id': d.public_doctor_id, 'full_name': d.full_name, 'hospital': d.hospital,
                       'speciality': d.speciality, 'country': COUNTRIES.get(d.origin_country),
                       'verified': d.verification_status == 'approved'} if d else None}


def _owned(db, auth, request_id):
    r = db.scalar(select(AccessRequest).where(AccessRequest.id == request_id, AccessRequest.patient_id == auth.patient_id))
    if not r:
        raise HTTPException(404, 'Request not found')
    return r


@router.get('/access-requests')
def my_access(auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    expire_stale(db)
    db.commit()
    rows = db.execute(select(AccessRequest, DoctorProfile).join(DoctorProfile, DoctorProfile.user_id == AccessRequest.doctor_id)
                      .where(AccessRequest.patient_id == auth.patient_id, AccessRequest.status.in_(('pending', 'accepted')))
                      .order_by(AccessRequest.created_at.desc())).all()
    return {'pending': [_payload(r, d) for r, d in rows if r.status == 'pending'],
            'granted': [_payload(r, d) for r, d in rows if r.status == 'accepted']}


@router.post('/access-requests/{request_id}/decision')
def decide(request_id: uuid.UUID, data: DecisionIn, request: Request, auth: Auth = Depends(current_patient),
           db: Session = Depends(get_db)):
    r = _owned(db, auth, request_id)
    if r.status != 'pending':
        raise HTTPException(409, 'This request has already been handled.')
    r.status = 'accepted' if data.decision == 'accept' else 'rejected'
    r.decided_at = now()
    audit(db, request, f'access_{r.status}', actor_id=auth.user.id, patient_id=auth.patient_id, entity_type='access_request',
          entity_id=r.id, summary=f"Doctor access {'granted' if r.status == 'accepted' else 'declined'}")
    db.commit()
    return {'ok': True, 'status': r.status}


@router.post('/access-grants/{request_id}/revoke')
def revoke(request_id: uuid.UUID, request: Request, auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    r = _owned(db, auth, request_id)
    if r.status != 'accepted':
        raise HTTPException(409, 'This doctor does not currently have access.')
    r.status, r.revoked_at = 'revoked', now()  # takes effect immediately: every doctor call re-checks the grant
    audit(db, request, 'access_revoked', actor_id=auth.user.id, patient_id=auth.patient_id, entity_type='access_request',
          entity_id=r.id, summary='Doctor access revoked')
    db.commit()
    return {'ok': True, 'status': r.status}
