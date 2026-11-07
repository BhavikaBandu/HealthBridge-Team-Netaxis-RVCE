from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..deps import Auth, current_patient, get_db
from ..models import AuditEvent, Condition, Document, Medication, PatientProfile, Procedure, Trip
from .trips import trip_payload

router = APIRouter(prefix='/api', tags=['dashboard'])

# Security/access events are recorded but not shown as "recent activity" on the dashboard.
HIDDEN_ACTIONS = ('login', 'logout', 'login_failed', 'document_viewed', 'document_downloaded')
ICONS = {'trip': 'airplane', 'medication': 'capsule', 'condition': 'heart-pulse', 'procedure': 'bandaid',
         'allergy': 'exclamation-triangle', 'allergy_declaration': 'exclamation-triangle', 'document': 'file-earmark-text',
         'profile': 'person', 'user': 'shield-check'}


def _count(db, model, patient_id, *extra):
    return db.scalar(select(func.count()).select_from(model).where(model.patient_id == patient_id,
                                                                     model.archived_at.is_(None), *extra))


def activity(db, patient_id, limit):
    rows = db.scalars(select(AuditEvent).where(AuditEvent.patient_id == patient_id, AuditEvent.action.not_in(HIDDEN_ACTIONS),
                                               AuditEvent.summary.is_not(None))
                      .order_by(AuditEvent.created_at.desc()).limit(limit))
    return [{'summary': e.summary, 'action': e.action, 'icon': ICONS.get(e.entity_type, 'clock-history'),
             'at': e.created_at.isoformat()} for e in rows]


@router.get('/dashboard/summary')
def summary(auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    pid = auth.patient_id
    today = date.today()
    # Next relevant trip: ongoing first, else the nearest planned one.
    active = list(db.scalars(select(Trip).where(Trip.patient_id == pid, Trip.archived_at.is_(None),
                                               (Trip.return_date.is_(None)) | (Trip.return_date >= today))
                             .order_by(Trip.departure_date)))
    ongoing = [t for t in active if t.departure_date <= today]
    upcoming = ongoing[0] if ongoing else (active[0] if active else None)
    p = db.get(PatientProfile, pid)
    return {
        'first_name': p.full_name.split()[0] if p and p.full_name else None,
        'patient_id': auth.user.public_patient_id,
        'profile_complete': bool(p and p.origin_country and p.preferred_language),
        'upcoming_trip': trip_payload(upcoming) if upcoming else None,
        'counts': {'medications': _count(db, Medication, pid, Medication.ongoing.is_(True)),
                   'medications_total': _count(db, Medication, pid),
                   'conditions': _count(db, Condition, pid), 'procedures': _count(db, Procedure, pid),
                   'documents': _count(db, Document, pid),
                   'trips': _count(db, Trip, pid)},
        'recent_activity': activity(db, pid, 6),
    }


@router.get('/activity')
def activity_list(limit: int = Query(50, ge=1, le=200), auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    return activity(db, auth.patient_id, limit)
