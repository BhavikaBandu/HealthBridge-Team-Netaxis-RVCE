"""get_source_record: one record with full provenance and any structured facts extracted from it."""
from sqlalchemy import select

from backend.models import (ControlledSubstance, KnowledgeRecord, LabTestReference, MedProduct, PolicyClause,
                            ProcedureTerm)
from .common import record_result

_FACT_TABLES = {'med_products': MedProduct, 'lab_test_refs': LabTestReference, 'procedure_terms': ProcedureTerm,
                'policy_clauses': PolicyClause, 'controlled_substances': ControlledSubstance}


def _row(obj):
    out = {c.key: getattr(obj, c.key) for c in obj.__table__.columns if c.key not in ('record_pk', 'version_pk')}
    if isinstance(obj, MedProduct):
        out['ingredients'] = [{'ingredient': i.ingredient, 'as_written': i.as_written,
                               'strength': float(i.strength_value) if i.strength_value is not None else None,
                               'unit': i.strength_unit} for i in obj.ingredients]
    return {k: (float(v) if hasattr(v, 'as_integer_ratio') and not isinstance(v, (int, bool, float)) else v)
            for k, v in out.items()}


def get_source_record(session, record_id):
    if session.get(KnowledgeRecord, record_id) is None:
        return None
    result = record_result(session, record_id, matched_fields=['record id'], method='direct_lookup')
    facts = {}
    for name, model in _FACT_TABLES.items():
        rows = session.scalars(select(model).where(model.record_pk == record_id)).all()
        if rows:
            facts[name] = [_row(r) for r in rows]
    result['facts'] = facts
    return result
