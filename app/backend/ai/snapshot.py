"""Save / restore a named copy of a trip's analysis (findings + flags), e.g. the template version before AI runs.

    python -m backend.ai.snapshot save template --patient HC-DEMO0001
    python -m backend.ai.snapshot restore template --patient HC-DEMO0001
    python -m backend.ai.snapshot list

Copies live in data/analysis_snapshots/<name>.json. Findings are matched back to records by type + name, so a copy
still restores after the demo case is rebuilt (records get new IDs).
"""
import argparse
import json
from pathlib import Path

from sqlalchemy import delete, select

from backend.config import ROOT
from backend.database import SessionLocal
from backend.models import now
from backend.portal.models import (AnalysisFinding, AnalysisFlag, Document, Medication, Procedure, Trip, TripAnalysis,
                                   User)

FOLDER = ROOT / 'data' / 'analysis_snapshots'
MODELS = {'medication': Medication, 'procedure': Procedure, 'document': Document}
FINDING_FIELDS = ('agent', 'record_type', 'title', 'match_label', 'confidence', 'patient_line', 'comparison', 'facts', 'assessment', 'fingerprint',
                  'context', 'verify', 'sources', 'position')
FLAG_FIELDS = ('kind', 'severity', 'subject', 'text', 'origin', 'sources', 'position')


def _record_key(rec, rtype):
    if rtype == 'medication':
        return f'{rec.brand or ""}|{rec.name}'
    return rec.name


def _trip(s, patient_code):
    u = s.scalar(select(User).where(User.public_patient_id == patient_code))
    trip = s.scalar(select(Trip).where(Trip.patient_id == u.id, Trip.archived_at.is_(None)).order_by(Trip.departure_date)) if u else None
    if not trip:
        raise SystemExit(f'No active trip for {patient_code}')
    return trip


def save(name, patient_code):
    with SessionLocal() as s:
        trip = _trip(s, patient_code)
        a = s.scalar(select(TripAnalysis).where(TripAnalysis.trip_id == trip.id))
        if not a:
            raise SystemExit('No analysis to save yet.')
        findings = []
        for f in s.scalars(select(AnalysisFinding).where(AnalysisFinding.analysis_id == a.id).order_by(AnalysisFinding.position)):
            rec = s.get(MODELS[f.record_type], f.record_id)
            if rec is None:
                continue
            findings.append({**{k: getattr(f, k) for k in FINDING_FIELDS}, 'record_key': _record_key(rec, f.record_type)})
        flags = [{k: getattr(fl, k) for k in FLAG_FIELDS} for fl in
                 s.scalars(select(AnalysisFlag).where(AnalysisFlag.analysis_id == a.id).order_by(AnalysisFlag.position))]
        data = {'name': name, 'patient': patient_code, 'saved_at': now().isoformat(), 'provider': a.provider,
                'analyzed_at': a.analyzed_at.isoformat() if a.analyzed_at else None, 'findings': findings, 'flags': flags}
    FOLDER.mkdir(parents=True, exist_ok=True)
    path = FOLDER / f'{name}.json'
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'saved {len(findings)} findings and {len(flags)} flags to {path.relative_to(ROOT)}')


def restore(name, patient_code):
    path = FOLDER / f'{name}.json'
    if not path.exists():
        raise SystemExit(f'No copy named {name!r} ({path})')
    data = json.loads(path.read_text(encoding='utf-8'))
    with SessionLocal() as s:
        trip = _trip(s, patient_code)
        pid = trip.patient_id
        a = s.scalar(select(TripAnalysis).where(TripAnalysis.trip_id == trip.id))
        if not a:
            a = TripAnalysis(trip_id=trip.id, patient_id=pid, origin=trip.origin_country, destination=trip.destination_country)
            s.add(a)
            s.flush()
        records = {}
        for rtype, model in MODELS.items():
            for rec in s.scalars(select(model).where(model.patient_id == pid, model.archived_at.is_(None))):
                records[(rtype, _record_key(rec, rtype))] = rec.id
        s.execute(delete(AnalysisFinding).where(AnalysisFinding.analysis_id == a.id))
        s.execute(delete(AnalysisFlag).where(AnalysisFlag.analysis_id == a.id))
        restored = skipped = 0
        for f in data['findings']:
            rid = records.get((f['record_type'], f['record_key']))
            if rid is None:
                skipped += 1
                continue
            s.add(AnalysisFinding(analysis_id=a.id, patient_id=pid, record_id=rid, **{k: f.get(k) for k in FINDING_FIELDS if k in f}))
            restored += 1
        for fl in data['flags']:
            s.add(AnalysisFlag(analysis_id=a.id, patient_id=pid, **{k: fl[k] for k in FLAG_FIELDS}))
        a.running, a.analyzed_at = False, now()
        a.provider, a.note = f"copy '{name}' ({data.get('provider')})", None
        s.commit()
    print(f'restored copy {name!r}: {restored} findings, {len(data["flags"])} flags' + (f'; {skipped} skipped (record not found)' if skipped else ''))


def main():
    ap = argparse.ArgumentParser(description='Save or restore a named copy of a trip analysis.')
    ap.add_argument('action', choices=['save', 'restore', 'list'])
    ap.add_argument('name', nargs='?', default='template')
    ap.add_argument('--patient', default='HC-DEMO0001')
    args = ap.parse_args()
    if args.action == 'list':
        for p in sorted(FOLDER.glob('*.json')):
            d = json.loads(p.read_text(encoding='utf-8'))
            print(f"{p.stem}: {d['patient']}, {len(d['findings'])} findings, {len(d['flags'])} flags, saved {d['saved_at']} ({d['provider']})")
        return
    (save if args.action == 'save' else restore)(args.name, args.patient)


if __name__ == '__main__':
    main()
