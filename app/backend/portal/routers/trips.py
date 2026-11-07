import uuid
from datetime import date
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models import now
from ..deps import Auth, audit, current_patient, get_db
from ..models import Trip
from ..reference import COUNTRIES, TRIP_PURPOSES, check_country, clean

router = APIRouter(prefix='/api/trips', tags=['trips'])


class TripIn(BaseModel):
    purpose_type: Literal['basic', 'specialised']
    purpose_description: str | None = Field(None, max_length=1000)
    origin_country: str
    destination_country: str
    departure_date: date
    return_date: date | None = None

    @model_validator(mode='after')
    def _rules(self):
        check_country(self.origin_country)
        check_country(self.destination_country)
        if self.origin_country == self.destination_country:
            raise ValueError('destination_country: Destination must be different from origin')
        if self.return_date and self.return_date < self.departure_date:
            raise ValueError('return_date: Return date cannot be before departure')
        self.purpose_description = clean(self.purpose_description, 1000)
        if self.purpose_type == 'specialised':
            if not self.purpose_description or len(self.purpose_description) < 3:
                raise ValueError('purpose_description: Briefly describe the specialised care')
        else:
            self.purpose_description = None  # only specialised care carries a description
        return self


def trip_status(t, today=None):
    today = today or date.today()
    if today < t.departure_date:
        return 'planned'
    if t.return_date is None or today <= t.return_date:
        return 'ongoing'
    return 'completed'


def trip_payload(t):
    return {'id': str(t.id), 'origin_country': t.origin_country, 'origin_name': COUNTRIES.get(t.origin_country),
            'destination_country': t.destination_country, 'destination_name': COUNTRIES.get(t.destination_country),
            'purpose_type': t.purpose_type, 'purpose_label': TRIP_PURPOSES[t.purpose_type],
            'purpose_description': t.purpose_description, 'departure_date': t.departure_date.isoformat(),
            'return_date': t.return_date.isoformat() if t.return_date else None, 'status': trip_status(t),
            'archived': t.archived_at is not None, 'created_at': t.created_at.isoformat()}


def _summary(t):
    return f'{COUNTRIES.get(t.origin_country, t.origin_country)} → {COUNTRIES.get(t.destination_country, t.destination_country)}'


def get_owned(db, auth, trip_id):
    t = db.scalar(select(Trip).where(Trip.id == trip_id, Trip.patient_id == auth.patient_id))
    if not t:
        raise HTTPException(404, 'Trip not found')
    return t


@router.get('')
def list_trips(archived: bool = False, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
               auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    cond = [Trip.patient_id == auth.patient_id,
            Trip.archived_at.is_not(None) if archived else Trip.archived_at.is_(None)]
    total = db.scalar(select(func.count()).select_from(Trip).where(*cond))
    rows = db.scalars(select(Trip).where(*cond).order_by(Trip.departure_date.desc(), Trip.created_at.desc())
                      .offset(offset).limit(limit))
    return {'items': [trip_payload(t) for t in rows], 'total': total}


def _analyse(trip_id):
    from backend.ai.analysis import run_in_background   # imported lazily: the AI package imports this module's models
    run_in_background(trip_id)


@router.post('', status_code=201)
def create_trip(data: TripIn, request: Request, background: BackgroundTasks, auth: Auth = Depends(current_patient),
                db: Session = Depends(get_db)):
    t = Trip(patient_id=auth.patient_id, **data.model_dump())
    db.add(t)
    db.flush()
    audit(db, request, 'trip_created', actor_id=auth.user.id, patient_id=auth.patient_id, entity_type='trip',
          entity_id=t.id, summary=f'Trip created: {_summary(t)}')
    db.commit()
    background.add_task(_analyse, t.id)   # travel health summary for the new trip
    return trip_payload(t)


@router.get('/{trip_id}')
def get_trip(trip_id: uuid.UUID, auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    return trip_payload(get_owned(db, auth, trip_id))


@router.patch('/{trip_id}')
def update_trip(trip_id: uuid.UUID, data: TripIn, request: Request, background: BackgroundTasks,
                auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    t = get_owned(db, auth, trip_id)
    for k, v in data.model_dump().items():
        setattr(t, k, v)
    audit(db, request, 'trip_updated', actor_id=auth.user.id, patient_id=auth.patient_id, entity_type='trip',
          entity_id=t.id, summary=f'Trip updated: {_summary(t)}')
    db.commit()
    background.add_task(_analyse, t.id)   # destination/dates may have changed
    return trip_payload(t)


@router.post('/{trip_id}/archive')
def archive_trip(trip_id: uuid.UUID, request: Request, auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    t = get_owned(db, auth, trip_id)
    if t.archived_at is None:
        t.archived_at = now()
        audit(db, request, 'trip_archived', actor_id=auth.user.id, patient_id=auth.patient_id, entity_type='trip',
              entity_id=t.id, summary=f'Trip archived: {_summary(t)}')
        db.commit()
    return trip_payload(t)


@router.post('/{trip_id}/restore')
def restore_trip(trip_id: uuid.UUID, request: Request, auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    t = get_owned(db, auth, trip_id)
    if t.archived_at is not None:
        t.archived_at = None
        audit(db, request, 'trip_restored', actor_id=auth.user.id, patient_id=auth.patient_id, entity_type='trip',
              entity_id=t.id, summary=f'Trip restored: {_summary(t)}')
        db.commit()
    return trip_payload(t)
