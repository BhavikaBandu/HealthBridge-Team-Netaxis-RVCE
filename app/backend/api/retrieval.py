"""Evidence retrieval API (doctor portal authentication). Retrieval only: no generation, no clinical advice.

POST /api/retrieval/medicines   {query, origin_country?, target_country?}
POST /api/retrieval/procedures  {query, countries?, modality?, anatomy?, laterality?}
POST /api/retrieval/reports     {query?, analyte?, value?, unit?, countries?}
POST /api/retrieval/policies    {query?, destination?, origin_country?, action?, medicine_name?, supply_days?}
GET  /api/retrieval/records/{record_id}   one source record with provenance and extracted facts
"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.portal.deps import current_doctor, get_db
from backend.retrieval.evidence import (get_source_record, search_lab_evidence, search_medicines,
                                        search_policy_clauses, search_procedures)

router = APIRouter(prefix='/api/retrieval', tags=['evidence retrieval'], dependencies=[Depends(current_doctor)])
Country = Literal['IN', 'AE', 'CH']


class MedicineQuery(BaseModel):
    query: str = Field(..., min_length=2, max_length=200, examples=['Crocin Advance 500 mg'])
    origin_country: Country | None = None
    target_country: Country | None = None


class ProcedureQuery(BaseModel):
    query: str = Field(..., min_length=2, max_length=200, examples=['right knee MRI'])
    countries: list[Country] | None = None
    modality: str | None = Field(None, max_length=40)
    anatomy: str | None = Field(None, max_length=60)
    laterality: Literal['right', 'left', 'both'] | None = None


class ReportQuery(BaseModel):
    query: str = Field('', max_length=200, examples=['fasting glucose 108 mg/dL'])
    analyte: str | None = Field(None, max_length=60)
    value: float | None = None
    unit: str | None = Field(None, max_length=20)
    countries: list[Country] | None = None


class PolicyQuery(BaseModel):
    query: str = Field('', max_length=300)
    destination: Literal['AE', 'AE-DU'] = 'AE-DU'
    origin_country: Country | None = None
    action: Literal['traveller_medicine_import', 'controlled_medicine', 'import_permit',
                    'prescription_requirement', 'customs_declaration'] | None = 'traveller_medicine_import'
    medicine_name: str | None = Field(None, max_length=120)
    supply_days: int | None = Field(None, ge=1, le=3650)


@router.post('/medicines', summary='Medicine evidence: structured ingredient/strength match + label passages')
def medicines(body: MedicineQuery, db: Session = Depends(get_db)):
    return search_medicines(db, body.query, body.origin_country, body.target_country)


@router.post('/procedures', summary='Procedure evidence: modality/anatomy/laterality terminology + passages')
def procedures(body: ProcedureQuery, db: Session = Depends(get_db)):
    return search_procedures(db, body.query, body.countries, body.modality, body.anatomy, body.laterality)


@router.post('/reports', summary='Lab report evidence: analyte/unit references, UCUM units, deterministic conversion')
def reports(body: ReportQuery, db: Session = Depends(get_db)):
    return search_lab_evidence(db, body.query, body.analyte, body.value, body.unit, body.countries)


@router.post('/policies', summary='Policy evidence: jurisdiction/action-filtered clauses, conflicts, review required')
def policies(body: PolicyQuery, db: Session = Depends(get_db)):
    return search_policy_clauses(db, body.query, body.destination, body.origin_country, body.action,
                                 body.medicine_name, body.supply_days)


@router.get('/records/{record_id}', summary='get_source_record: one record with provenance and extracted facts')
def record(record_id: int, db: Session = Depends(get_db)):
    out = get_source_record(db, record_id)
    if out is None:
        raise HTTPException(404, 'Record not found')
    return out
