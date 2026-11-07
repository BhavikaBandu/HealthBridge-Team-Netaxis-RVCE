"""Medical history: medications, conditions, procedures, allergies (+ allergy declaration).

All entries are patient-entered and labelled self-reported / unverified. No validation, coding or inference.
"""
import uuid
from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.models import now
from ..deps import Auth, audit, current_patient, get_db
from ..models import (Allergy, AllergyDeclaration, Condition, Document, DocumentLink, DoctorProfile, Medication, Procedure,
                      User)
from ..reference import COUNTRIES, DOSAGE_FORMS, STRENGTH_UNITS, check_country, clean

router = APIRouter(prefix='/api', tags=['medical history'])
REPORTED_LABELS = {'patient': 'Self-reported', 'doctor': 'Doctor reported'}


# ---- schemas ---------------------------------------------------------------------------------
class Schedule(BaseModel):
    morning: bool = False
    afternoon: bool = False
    night: bool = False
    as_needed: bool = False
    custom: str | None = Field(None, max_length=200)


class MedicationIn(BaseModel):
    name: str = Field(max_length=200)
    brand: str | None = Field(None, max_length=200)
    manufacturer: str | None = Field(None, max_length=200)
    strength_value: Decimal | None = Field(None, gt=0, max_digits=12, decimal_places=4)
    strength_unit: str | None = None
    strength_label: str | None = Field(None, max_length=100)
    dosage_form: str | None = None
    dose: str | None = Field(None, max_length=100)
    schedule: Schedule = Schedule()
    start_date: date | None = None
    start_date_unknown: bool = False
    ongoing: bool = True
    stop_date: date | None = None
    instructions: str | None = Field(None, max_length=1000)

    @model_validator(mode='after')
    def _rules(self):
        self.name = clean(self.name, 200)  # preserve the patient's spelling; only trim whitespace
        if not self.name:
            raise ValueError('name: Medicine name is required')
        for f in ('brand', 'manufacturer', 'strength_label', 'dose', 'instructions'):
            setattr(self, f, clean(getattr(self, f)))
        self.schedule.custom = clean(self.schedule.custom)
        if self.strength_unit in ('', None):
            self.strength_unit = None
        elif self.strength_unit not in STRENGTH_UNITS:
            raise ValueError('strength_unit: Choose a unit from the list')
        if self.strength_value is not None and not self.strength_unit:
            raise ValueError('strength_unit: Choose a unit for the strength')
        if self.dosage_form in ('', None):
            self.dosage_form = None
        elif self.dosage_form not in DOSAGE_FORMS:
            raise ValueError('dosage_form: Choose a dosage form from the list')
        if self.start_date_unknown:
            self.start_date = None
        elif self.start_date is None:
            raise ValueError("start_date: Enter the start date, or tick 'Start date unknown'")
        if self.ongoing:
            self.stop_date = None  # clear any stale stop date
        else:
            if self.stop_date is None:
                raise ValueError('stop_date: Enter the stop date (or switch Ongoing on)')
            if self.start_date and self.stop_date < self.start_date:
                raise ValueError('stop_date: Stop date cannot be before the start date')
        return self


class ConditionIn(BaseModel):
    name: str = Field(max_length=200)
    diagnosis_date: date | None = None
    diagnosis_year: int | None = Field(None, ge=1900, le=2100)
    status: Literal['active', 'resolved', 'unknown'] = 'unknown'
    notes: str | None = Field(None, max_length=2000)

    @model_validator(mode='after')
    def _rules(self):
        self.name = clean(self.name, 200)
        if not self.name:
            raise ValueError('name: Condition name is required')
        self.notes = clean(self.notes)
        if self.diagnosis_date:
            self.diagnosis_year = self.diagnosis_date.year
        if self.diagnosis_year and self.diagnosis_year > date.today().year:
            raise ValueError('diagnosis_year: Year cannot be in the future')
        return self


class ProcedureIn(BaseModel):
    name: str = Field(max_length=200)
    procedure_date: date | None = None
    country: str | None = None
    hospital: str | None = Field(None, max_length=200)
    status: Literal['planned', 'completed'] = 'completed'
    notes: str | None = Field(None, max_length=2000)

    @model_validator(mode='after')
    def _rules(self):
        self.name = clean(self.name, 200)
        if not self.name:
            raise ValueError('name: Procedure name is required')
        self.country = check_country(self.country, required=False)
        self.hospital, self.notes = clean(self.hospital), clean(self.notes)
        return self


class AllergyIn(BaseModel):
    allergen: str = Field(max_length=200)
    reaction: str | None = Field(None, max_length=300)
    severity: Literal['mild', 'moderate', 'severe', 'unknown'] = 'unknown'
    notes: str | None = Field(None, max_length=2000)

    @model_validator(mode='after')
    def _rules(self):
        self.allergen = clean(self.allergen, 200)
        if not self.allergen:
            raise ValueError('allergen: Allergen is required')
        self.reaction, self.notes = clean(self.reaction), clean(self.notes)
        return self


class DeclarationIn(BaseModel):
    declaration: Literal['unknown', 'none', 'known']


# ---- payloads --------------------------------------------------------------------------------
def _d(v):
    return v.isoformat() if v else None


def _common(r):
    return {'id': str(r.id), 'archived': r.archived_at is not None, 'created_at': _d(r.created_at),
            'updated_at': _d(r.updated_at), 'reported_by_role': r.reported_by_role,
            'reported_by_label': REPORTED_LABELS.get(r.reported_by_role, r.reported_by_role)}


def _reporter_ids(db, rows):
    """{user_id: public ID} of the people who entered these records (patient ID now; doctor ID later)."""
    ids = {r.reported_by_user_id for r in rows if r.reported_by_user_id}
    if not ids:
        return {}
    rows = db.execute(select(User.id, func.coalesce(DoctorProfile.public_doctor_id, User.public_patient_id))
                      .outerjoin(DoctorProfile, DoctorProfile.user_id == User.id).where(User.id.in_(ids))).all()
    return dict(rows)


def med_payload(m):
    strength = None
    if m.strength_value is not None:
        strength = f'{Decimal(m.strength_value).normalize():f} {m.strength_unit or ""}'.strip()
    return {**_common(m), 'name': m.name, 'brand': m.brand, 'manufacturer': m.manufacturer,
            'strength_value': float(m.strength_value) if m.strength_value is not None else None,
            'strength_unit': m.strength_unit, 'strength_label': m.strength_label, 'strength': strength or m.strength_label,
            'dosage_form': m.dosage_form, 'dose': m.dose, 'schedule': m.schedule or {}, 'start_date': _d(m.start_date),
            'start_date_unknown': m.start_date_unknown, 'ongoing': m.ongoing, 'stop_date': _d(m.stop_date),
            'instructions': m.instructions, 'status': 'ongoing' if m.ongoing else 'stopped'}


def cond_payload(c):
    return {**_common(c), 'name': c.name, 'diagnosis_date': _d(c.diagnosis_date), 'diagnosis_year': c.diagnosis_year,
            'status': c.status, 'notes': c.notes}


def proc_payload(p):
    return {**_common(p), 'name': p.name, 'procedure_date': _d(p.procedure_date), 'country': p.country,
            'country_name': COUNTRIES.get(p.country), 'hospital': p.hospital, 'status': p.status, 'notes': p.notes}


def allergy_payload(a):
    return {**_common(a), 'allergen': a.allergen, 'reaction': a.reaction, 'severity': a.severity, 'notes': a.notes}


KINDS = {
    'medications': dict(model=Medication, schema=MedicationIn, payload=med_payload, record_type='medication',
                        label='Medication', search=[Medication.name, Medication.brand, Medication.manufacturer],
                        status=None, order=[Medication.ongoing.desc(), Medication.start_date.desc().nulls_last()]),
    'conditions': dict(model=Condition, schema=ConditionIn, payload=cond_payload, record_type='condition',
                       label='Condition', search=[Condition.name, Condition.notes], status=Condition.status,
                       order=[Condition.created_at.desc()]),
    'procedures': dict(model=Procedure, schema=ProcedureIn, payload=proc_payload, record_type='procedure',
                       label='Procedure', search=[Procedure.name, Procedure.hospital], status=Procedure.status,
                       order=[Procedure.procedure_date.desc().nulls_last()]),
    'allergies': dict(model=Allergy, schema=AllergyIn, payload=allergy_payload, record_type='allergy',
                      label='Allergy', search=[Allergy.allergen, Allergy.reaction], status=Allergy.severity,
                      order=[Allergy.created_at.desc()]),
}


def _linked_docs(db, patient_id, record_type, ids):
    """{record_id: [{id, name, archived}]} for the given records (same patient only)."""
    if not ids:
        return {}
    rows = db.execute(select(DocumentLink.record_id, Document.id, Document.name, Document.archived_at)
                      .join(Document, Document.id == DocumentLink.document_id)
                      .where(DocumentLink.patient_id == patient_id, Document.patient_id == patient_id,
                             DocumentLink.record_type == record_type, DocumentLink.record_id.in_(ids))).all()
    out = {}
    for rid, did, name, arch in rows:
        out.setdefault(rid, []).append({'id': str(did), 'name': name, 'archived': arch is not None})
    return out


def _get_owned(db, auth, kind, record_id):
    model = KINDS[kind]['model']
    r = db.scalar(select(model).where(model.id == record_id, model.patient_id == auth.patient_id))
    if not r:
        raise HTTPException(404, f"{KINDS[kind]['label']} not found")
    return r


def _declaration(db, patient_id):
    d = db.get(AllergyDeclaration, patient_id)
    if not d:
        d = AllergyDeclaration(patient_id=patient_id, declaration='unknown')
        db.add(d)
        db.flush()
    return d


def serialize(db, kind, patient_id, rows):
    """Records as API payloads, with linked documents and the reporter's public ID."""
    cfg = KINDS[kind]
    links = _linked_docs(db, patient_id, cfg['record_type'], [r.id for r in rows])
    reporters = _reporter_ids(db, rows)
    return [{**cfg['payload'](r), 'reported_by_id': reporters.get(r.reported_by_user_id), 'documents': links.get(r.id, [])}
            for r in rows]


def list_records(db, kind, patient_id, archived=False, q=None, status=None, limit=100, offset=0):
    cfg = KINDS[kind]
    model = cfg['model']
    cond = [model.patient_id == patient_id, model.archived_at.is_not(None) if archived else model.archived_at.is_(None)]
    if q and q.strip():
        pattern = '%' + q.strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
        cond.append(or_(*[c.ilike(pattern, escape='\\') for c in cfg['search']]))
    if status:
        if kind == 'medications':
            cond.append(model.ongoing.is_(status == 'ongoing'))
        elif cfg['status'] is not None:
            cond.append(cfg['status'] == status)
    total = db.scalar(select(func.count()).select_from(model).where(*cond))
    rows = list(db.scalars(select(model).where(*cond).order_by(*cfg['order'], model.id).offset(offset).limit(limit)))
    return {'items': serialize(db, kind, patient_id, rows), 'total': total}


def _possible_duplicate(db, kind, patient_id, values):
    """True if an active record with the same name already exists (shown as a notice, never merged)."""
    cfg = KINDS[kind]
    model = cfg['model']
    name_col, name = (model.allergen, values['allergen']) if kind == 'allergies' else (model.name, values['name'])
    return bool(db.scalar(select(func.count()).select_from(model).where(
        model.patient_id == patient_id, model.archived_at.is_(None), func.lower(name_col) == name.lower())))


def create_record(db, request, kind, data, patient_id, actor):
    """Create a history record for a patient. The reporter is the signed-in account (patient or doctor)."""
    cfg = KINDS[kind]
    values = data.model_dump()
    duplicate = _possible_duplicate(db, kind, patient_id, values)
    r = cfg['model'](patient_id=patient_id, reported_by_role=actor.role, reported_by_user_id=actor.id, **values)
    db.add(r)
    db.flush()
    who = 'by doctor' if actor.role == 'doctor' else ''
    audit(db, request, f"{cfg['record_type']}_created", actor_id=actor.id, patient_id=patient_id,
          entity_type=cfg['record_type'], entity_id=r.id, summary=f"{cfg['label']} added {who}".strip())
    db.commit()
    return {**serialize(db, kind, patient_id, [r])[0], 'possible_duplicate': duplicate}


def _register(kind):
    cfg = KINDS[kind]
    model, schema, label = cfg['model'], cfg['schema'], cfg['label']

    def with_links(db, auth, rows):
        return serialize(db, kind, auth.patient_id, rows)

    @router.get(f'/{kind}', name=f'list_{kind}')
    def list_items(archived: bool = False, q: str | None = Query(None, max_length=100), status: str | None = Query(None, max_length=20),
                   limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0),
                   auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
        return list_records(db, kind, auth.patient_id, archived, q, status, limit, offset)

    @router.post(f'/{kind}', status_code=201, name=f'create_{kind}')
    def create_item(data: schema, request: Request, auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
        if kind == 'allergies' and _declaration(db, auth.patient_id).declaration != 'known':
            raise HTTPException(409, "Set your allergy status to 'Known allergies' before adding an allergy.")
        return create_record(db, request, kind, data, auth.patient_id, auth.user)

    @router.get(f'/{kind}/{{record_id}}', name=f'get_{kind}')
    def get_item(record_id: uuid.UUID, auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
        return with_links(db, auth, [_get_owned(db, auth, kind, record_id)])[0]

    @router.patch(f'/{kind}/{{record_id}}', name=f'update_{kind}')
    def update_item(record_id: uuid.UUID, data: schema, request: Request, auth: Auth = Depends(current_patient),
                    db: Session = Depends(get_db)):
        r = _get_owned(db, auth, kind, record_id)
        if r.reported_by_role == 'doctor':
            raise HTTPException(403, f'This {label.lower()} was added by a doctor and cannot be edited. You can archive it instead.')
        for k, v in data.model_dump().items():
            setattr(r, k, v)
        audit(db, request, f"{cfg['record_type']}_updated", actor_id=auth.user.id, patient_id=auth.patient_id,
              entity_type=cfg['record_type'], entity_id=r.id, summary=f'{label} updated')
        db.commit()
        return with_links(db, auth, [r])[0]

    @router.post(f'/{kind}/{{record_id}}/archive', name=f'archive_{kind}')
    def archive_item(record_id: uuid.UUID, request: Request, auth: Auth = Depends(current_patient),
                     db: Session = Depends(get_db)):
        r = _get_owned(db, auth, kind, record_id)
        if r.archived_at is None:
            r.archived_at = now()  # linked documents and links are kept
            audit(db, request, f"{cfg['record_type']}_archived", actor_id=auth.user.id, patient_id=auth.patient_id,
                  entity_type=cfg['record_type'], entity_id=r.id, summary=f'{label} archived')
            db.commit()
        return with_links(db, auth, [r])[0]

    @router.post(f'/{kind}/{{record_id}}/restore', name=f'restore_{kind}')
    def restore_item(record_id: uuid.UUID, request: Request, auth: Auth = Depends(current_patient),
                     db: Session = Depends(get_db)):
        r = _get_owned(db, auth, kind, record_id)
        if kind == 'allergies' and _declaration(db, auth.patient_id).declaration != 'known':
            raise HTTPException(409, "Set your allergy status to 'Known allergies' before restoring an allergy.")
        if r.archived_at is not None:
            r.archived_at = None
            audit(db, request, f"{cfg['record_type']}_restored", actor_id=auth.user.id, patient_id=auth.patient_id,
                  entity_type=cfg['record_type'], entity_id=r.id, summary=f'{label} restored')
            db.commit()
        return with_links(db, auth, [r])[0]


for _kind in KINDS:
    _register(_kind)


@router.get('/allergy-declaration')
def get_declaration(auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    d = _declaration(db, auth.patient_id)
    db.commit()
    return {'declaration': d.declaration, 'updated_at': _d(d.updated_at)}


@router.put('/allergy-declaration')
def put_declaration(data: DeclarationIn, request: Request, auth: Auth = Depends(current_patient),
                    db: Session = Depends(get_db)):
    d = _declaration(db, auth.patient_id)
    if data.declaration != 'known':
        active = db.scalar(select(func.count()).select_from(Allergy).where(
            Allergy.patient_id == auth.patient_id, Allergy.archived_at.is_(None)))
        if active:
            raise HTTPException(409, f'You have {active} allergy record(s) listed. Archive them before choosing this status.')
    if d.declaration != data.declaration:
        d.declaration = data.declaration
        audit(db, request, 'allergy_status_updated', actor_id=auth.user.id, patient_id=auth.patient_id,
              entity_type='allergy_declaration', entity_id=auth.patient_id, summary='Allergy status updated')
    db.commit()
    return {'declaration': d.declaration, 'updated_at': _d(d.updated_at)}


def history_options(db, patient_id):
    """All of a patient's history records (incl. archived) for document-link pickers."""
    out = []
    for kind, cfg in KINDS.items():
        model = cfg['model']
        name_col = model.allergen if kind == 'allergies' else model.name
        for rid, name, arch in db.execute(select(model.id, name_col, model.archived_at)
                                          .where(model.patient_id == patient_id).order_by(name_col)):
            out.append({'record_type': cfg['record_type'], 'record_id': str(rid), 'label': name,
                        'archived': arch is not None})
    return out


@router.get('/history-records')
def history_records(auth: Auth = Depends(current_patient), db: Session = Depends(get_db)):
    return history_options(db, auth.patient_id)
