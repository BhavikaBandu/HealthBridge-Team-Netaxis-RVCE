"""Read stored trip analyses (patient + doctor) and request a refresh. Reading never runs the AI."""
import uuid
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy import select
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.ai import fingerprints, llm, report_builder
from backend.ai.analysis import active_trips, run_in_background
from backend.models import now
from ..deps import Auth, audit, current_patient, get_db, verified_doctor
from backend.models import Source
from ..models import (AnalysisFinding, AnalysisFlag, Document, DoctorProfile, Medication, PatientProfile, Procedure,
                      Trip, TripAnalysis, TripReport)
from .doctor import granted_patient
from .trips import trip_payload

router = APIRouter(tags=['trip analysis'])


def analysis_payload(db, trip):
    a = db.scalar(select(TripAnalysis).where(TripAnalysis.trip_id == trip.id))
    out = {'trip': trip_payload(trip), 'available': a is not None and a.analyzed_at is not None and not (a.running and not
           db.scalar(select(AnalysisFinding.id).where(AnalysisFinding.analysis_id == a.id).limit(1))),
           'running': bool(a and a.running), 'analyzed_at': a.analyzed_at.isoformat() if a and a.analyzed_at else None,
           'findings': [], 'flags': [], 'freshness': {'stale': 0, 'new_records': 0, 'flags_stale': False}}
    if not a:
        return out
    # Freshness: compare stored input fingerprints with the inputs now (no agent runs).
    fp = fingerprints.collect(db, trip)
    records = fp.pop('_records')
    all_stale = a.base_fingerprint != fp['base']
    seen = set()
    for f in db.scalars(select(AnalysisFinding).where(AnalysisFinding.analysis_id == a.id).order_by(AnalysisFinding.position)):
        rec = db.get({'medication': Medication, 'procedure': Procedure, 'document': Document}[f.record_type], f.record_id)
        if rec is None or rec.archived_at is not None:
            continue   # record removed since the analysis ran
        seen.add(f.record_id)
        if f.record_type == 'medication':
            status = 'ongoing' if rec.ongoing else 'stopped'
        else:
            status = rec.status if f.record_type == 'procedure' else None
        stale = all_stale or f.fingerprint != fp.get((f.record_type, f.record_id))
        out['freshness']['stale'] += stale
        out['findings'].append({'record_status': status, 'id': str(f.id), 'agent': f.agent, 'record_type': f.record_type,
                                'record_id': str(f.record_id),
                                'title': f.title, 'match_label': f.match_label, 'confidence': f.confidence,
                                'patient_line': f.patient_line, 'comparison': f.comparison, 'facts': f.facts,
                                'context': f.context, 'verify': f.verify, 'sources': f.sources,
                                'assessment': f.assessment or {}, 'freshness': 'stale' if stale else 'current'})
    out['freshness']['new_records'] = sum(1 for recs in records.values() for r in recs if r.id not in seen)
    out['freshness']['flags_stale'] = all_stale or a.policy_fingerprint != fp['policy']
    for fl in db.scalars(select(AnalysisFlag).where(AnalysisFlag.analysis_id == a.id).order_by(AnalysisFlag.position)):
        out['flags'].append({'id': str(fl.id), 'kind': fl.kind, 'severity': fl.severity, 'subject': fl.subject,
                             'text': fl.text, 'origin': fl.origin, 'sources': fl.sources})
    return out


def _own_trip(db, auth, trip_id):
    t = db.scalar(select(Trip).where(Trip.id == trip_id, Trip.patient_id == auth.patient_id, Trip.archived_at.is_(None)))
    if not t:
        raise HTTPException(404, 'Trip not found')
    return t


@router.get('/api/trips/{trip_id}/analysis')
def patient_analysis(trip_id: uuid.UUID, auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    return analysis_payload(db, _own_trip(db, auth, trip_id))


@router.post('/api/trips/{trip_id}/analysis/refresh', status_code=202)
def refresh_analysis(trip_id: uuid.UUID, request: Request, background: BackgroundTasks,
                     auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    t = _own_trip(db, auth, trip_id)
    audit(db, request, 'trip_analysis_requested', actor_id=auth.user.id, patient_id=auth.patient_id,
          entity_type='trip', entity_id=t.id, summary='Travel health summary refresh requested')
    db.commit()
    background.add_task(run_in_background, t.id, True)   # manual refresh: changed parts, or everything if none
    return {'queued': True}


@router.post('/api/trips/reprocess', status_code=202)
def reprocess_active(request: Request, background: BackgroundTasks, auth: Auth = Depends(current_patient),
                     db: Session = Depends(get_db)):
    """"Reprocess now" after editing medical history: re-run only the out-of-date parts of upcoming/in-progress trips."""
    trips = active_trips(db, auth.patient_id)
    for t in trips:
        background.add_task(run_in_background, t.id)
    if trips:
        audit(db, request, 'trip_analysis_requested', actor_id=auth.user.id, patient_id=auth.patient_id,
              entity_type='trip', entity_id=trips[0].id, summary=f'Reprocess requested for {len(trips)} trip(s)')
        db.commit()
    return {'queued': len(trips)}


@router.get('/api/doctor/patients/{code}/analysis')
def doctor_analysis(code: str, trip_id: uuid.UUID | None = Query(None), auth: Auth = Depends(verified_doctor),
                    db: Session = Depends(get_db)):
    """Stored analysis for one of the patient's trips (default: the next/current active trip)."""
    u = granted_patient(db, auth, code)
    trips = db.scalars(select(Trip).where(Trip.patient_id == u.id, Trip.archived_at.is_(None))
                       .order_by(Trip.departure_date)).all()
    if not trips:
        return {'trips': [], 'trip': None, 'available': False, 'running': False, 'findings': [], 'flags': []}
    trip = next((t for t in trips if t.id == trip_id), None) if trip_id else None
    if trip_id and not trip:
        raise HTTPException(404, 'Trip not found')
    trip = trip or trips[0]
    return {'trips': [trip_payload(t) for t in trips], **analysis_payload(db, trip)}


# ------------------------------------------------------------------ printable report (patient)
class ReportRequest(BaseModel):
    language: Literal['en', 'ar'] = 'en'


def _saved_report(db, trip_id, language, audience='patient'):
    return db.scalar(select(TripReport).where(TripReport.trip_id == trip_id, TripReport.audience == audience,
                                              TripReport.language == language))


@router.get('/api/trips/{trip_id}/report')
def report_status(trip_id: uuid.UUID, language: Literal['en', 'ar'] = 'en', auth: Auth = Depends(current_patient),
                  db: Session = Depends(get_db)):
    t = _own_trip(db, auth, trip_id)
    a = db.scalar(select(TripAnalysis).where(TripAnalysis.trip_id == t.id))
    r = _saved_report(db, t.id, language)
    current = bool(r and a and r.analysis_at == a.analyzed_at)
    return {'exists': r is not None, 'current': current, 'report_url': f'/travel-summary/report/{r.id}' if r else None}


@router.post('/api/trips/{trip_id}/report')
def generate_report(trip_id: uuid.UUID, body: ReportRequest, request: Request, auth: Auth = Depends(current_patient),
                    db: Session = Depends(get_db)):
    """Return the saved report for this trip + language, or build it (Arabic is translated once by the AI)."""
    t = _own_trip(db, auth, trip_id)
    a = db.scalar(select(TripAnalysis).where(TripAnalysis.trip_id == t.id))
    if not a or a.analyzed_at is None or a.running and not db.scalar(
            select(AnalysisFinding.id).where(AnalysisFinding.analysis_id == a.id).limit(1)):
        raise HTTPException(409, 'Your travel health summary is not ready yet. Try again once it has finished.')
    r = _saved_report(db, t.id, body.language)
    if r and r.analysis_at == a.analyzed_at:
        return {'report_url': f'/travel-summary/report/{r.id}', 'reused': True}
    profile = db.get(PatientProfile, auth.patient_id)
    content = report_builder.build_english(analysis_payload(db, t), profile.full_name if profile else '',
                                           auth.user.public_patient_id)
    if body.language == 'ar':
        try:
            content = report_builder.translate_arabic(content)
        except llm.LLMError as exc:
            raise HTTPException(503, 'The Arabic version could not be prepared right now. The English report is '
                                     f'still available. ({exc})') from exc
    if r is None:
        r = TripReport(trip_id=t.id, patient_id=auth.patient_id, audience='patient', language=body.language)
        db.add(r)
    r.content, r.analysis_at, r.created_at = content, a.analyzed_at, now()
    db.flush()
    audit(db, request, 'travel_report_generated', actor_id=auth.user.id, patient_id=auth.patient_id,
          entity_type='trip', entity_id=t.id, summary=f'Travel health report generated ({body.language})')
    db.commit()
    return {'report_url': f'/travel-summary/report/{r.id}', 'reused': False}


# ------------------------------------------------------------------ complete report (doctor)
class DoctorReportRequest(BaseModel):
    trip_id: uuid.UUID
    language: Literal['en', 'ar'] = 'en'


def _doctor_trip(db, auth, code, trip_id):
    u = granted_patient(db, auth, code)
    t = db.scalar(select(Trip).where(Trip.id == trip_id, Trip.patient_id == u.id, Trip.archived_at.is_(None)))
    if not t:
        raise HTTPException(404, 'Trip not found')
    return u, t


@router.get('/api/doctor/patients/{code}/report')
def doctor_report_status(code: str, trip_id: uuid.UUID, language: Literal['en', 'ar'] = 'en',
                         auth: Auth = Depends(verified_doctor), db: Session = Depends(get_db)):
    _, t = _doctor_trip(db, auth, code, trip_id)
    a = db.scalar(select(TripAnalysis).where(TripAnalysis.trip_id == t.id))
    r = _saved_report(db, t.id, language, audience='doctor')
    mine = bool(r and r.content.get('_doctor_id') == str(auth.user.id))
    current = bool(mine and a and r.analysis_at == a.analyzed_at)
    return {'exists': mine, 'current': current, 'report_url': f'/doctor/patients/{code}/report/{r.id}' if mine else None}


@router.post('/api/doctor/patients/{code}/report')
def doctor_generate_report(code: str, body: DoctorReportRequest, request: Request, auth: Auth = Depends(verified_doctor),
                           db: Session = Depends(get_db)):
    """Complete patient report for this trip (summary + all findings + flags with sources). Saved and reused."""
    u, t = _doctor_trip(db, auth, code, body.trip_id)
    a = db.scalar(select(TripAnalysis).where(TripAnalysis.trip_id == t.id))
    if not a or a.analyzed_at is None or a.running and not db.scalar(
            select(AnalysisFinding.id).where(AnalysisFinding.analysis_id == a.id).limit(1)):
        raise HTTPException(409, 'The analysis for this trip is not ready yet.')
    r = _saved_report(db, t.id, body.language, audience='doctor')
    if r and r.analysis_at == a.analyzed_at and r.content.get('_doctor_id') == str(auth.user.id):
        return {'report_url': f'/doctor/patients/{code}/report/{r.id}', 'reused': True}
    profile = db.get(PatientProfile, u.id)
    doctor = db.get(DoctorProfile, auth.user.id)
    titles = dict(db.execute(select(Source.source_id, Source.title)).all())
    content = report_builder.build_doctor(analysis_payload(db, t), profile.full_name if profile else '', u.public_patient_id,
                                          doctor.full_name if doctor else '', titles)
    if body.language == 'ar':
        try:
            content = report_builder.translate_arabic(content)
        except llm.LLMError as exc:
            raise HTTPException(503, 'The Arabic version could not be prepared right now. The English report is '
                                     f'still available. ({exc})') from exc
    content['_doctor_id'] = str(auth.user.id)
    if r is None:
        r = TripReport(trip_id=t.id, patient_id=u.id, audience='doctor', language=body.language)
        db.add(r)
    r.content, r.analysis_at, r.created_at = content, a.analyzed_at, now()
    db.flush()
    audit(db, request, 'doctor_report_generated', actor_id=auth.user.id, patient_id=u.id, entity_type='trip',
          entity_id=t.id, summary=f'Complete patient report generated ({body.language})')
    db.commit()
    return {'report_url': f'/doctor/patients/{code}/report/{r.id}', 'reused': False}
