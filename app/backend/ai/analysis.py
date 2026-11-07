"""Trip analysis runner: runs the LangGraph pipeline (backend/ai/graph.py) for one trip.

Only what changed is re-run (input fingerprints); the Dopamine-Cortisol controller assesses every new finding.
Triggered when a trip is created or edited, from the patient's Refresh / "Reprocess now", or from the command line:
    python -m backend.ai.analysis --patient HC-DEMO0001          # changed parts of the next active trip
    python -m backend.ai.analysis --patient HC-DEMO0001 --full   # every agent again
    python -m backend.ai.analysis --trip <trip uuid>
Opening a page never runs this; pages only read the stored results.
"""
import argparse
import logging
import uuid
from datetime import date, timedelta

from sqlalchemy import select

from backend.database import SessionLocal
from backend.models import now
from backend.portal.models import AnalysisFinding, AnalysisFlag, Trip, TripAnalysis, User

log = logging.getLogger('uvicorn.error')
STUCK_AFTER = timedelta(minutes=15)


def run_trip_analysis(trip_id, force=False, full=False):
    """Run the graph for one trip. `force`: a manual refresh (runs everything if nothing is out of date);
    `full`: every agent regardless of what changed. Returns the analysis id."""
    with SessionLocal() as s:
        trip = s.get(Trip, trip_id)
        if trip is None or trip.archived_at is not None:
            return None
        a = s.scalar(select(TripAnalysis).where(TripAnalysis.trip_id == trip.id))
        if a is None:
            a = TripAnalysis(trip_id=trip.id, patient_id=trip.patient_id, origin=trip.origin_country,
                             destination=trip.destination_country)
            s.add(a)
        elif a.running and a.analyzed_at and now() - a.analyzed_at < STUCK_AFTER:
            return a.id   # a run is already in progress: join it instead of starting another
        a.running, a.origin, a.destination = True, trip.origin_country, trip.destination_country
        a.analyzed_at = a.analyzed_at or now()
        s.commit()
        analysis_id = a.id

    from . import graph   # imported here: building the graph imports every agent
    try:
        graph.run(trip_id, analysis_id, force=force, full=full)
    except Exception:
        log.exception('trip analysis failed')
        with SessionLocal() as s:
            a = s.get(TripAnalysis, analysis_id)
            if a:
                a.running, a.note = False, 'Analysis failed; previous results kept.'
                s.commit()
        raise
    with SessionLocal() as s:   # nothing to do: the graph ended at "plan"
        a = s.get(TripAnalysis, analysis_id)
        if a.running:
            a.running = False
            s.commit()
    return analysis_id


def run_in_background(trip_id, force=False):
    """Entry point for FastAPI BackgroundTasks (never raises)."""
    try:
        run_trip_analysis(trip_id, force=force)
    except Exception:
        pass


def active_trips(s, patient_id):
    """Upcoming or in-progress trips of a patient (the ones worth reprocessing)."""
    today = date.today()
    trips = s.scalars(select(Trip).where(Trip.patient_id == patient_id, Trip.archived_at.is_(None))).all()
    return [t for t in trips if (t.return_date or t.departure_date) >= today]


def main():
    ap = argparse.ArgumentParser(description='Run the trip analysis (LangGraph pipeline) now.')
    ap.add_argument('--trip')
    ap.add_argument('--patient', help='Patient ID, e.g. HC-DEMO0001 (uses the next active trip)')
    ap.add_argument('--full', action='store_true', help='Run every agent, not only what changed')
    args = ap.parse_args()
    trip_id = uuid.UUID(args.trip) if args.trip else None
    if not trip_id:
        with SessionLocal() as s:
            u = s.scalar(select(User).where(User.public_patient_id == args.patient))
            trip = s.scalar(select(Trip).where(Trip.patient_id == u.id, Trip.archived_at.is_(None))
                            .order_by(Trip.departure_date)) if u else None
            if not trip:
                raise SystemExit('No active trip found.')
            trip_id = trip.id
    run_trip_analysis(trip_id, full=args.full)
    with SessionLocal() as s:
        a = s.scalar(select(TripAnalysis).where(TripAnalysis.trip_id == trip_id))
        print(f'provider: {a.provider}\nnote: {a.note}')
        for f in s.scalars(select(AnalysisFinding).where(AnalysisFinding.analysis_id == a.id).order_by(AnalysisFinding.position)):
            x = f.assessment or {}
            print(f'[{f.agent}] {f.title} | {f.match_label} | {f.confidence}')
            print(f"       D={x.get('dopamine')} C={x.get('cortisol')} -> {x.get('label')}: {x.get('reason')}")
            print(f"       features: {x.get('features')}")
        for fl in s.scalars(select(AnalysisFlag).where(AnalysisFlag.analysis_id == a.id).order_by(AnalysisFlag.position)):
            print(f'<{fl.kind}/{fl.severity}> {fl.subject}: {fl.text}')


if __name__ == '__main__':
    main()
