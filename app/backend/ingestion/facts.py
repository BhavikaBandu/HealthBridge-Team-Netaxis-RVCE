"""Write the structured facts carried by a version's records into the domain evidence tables.

Called inside the ingestion transaction, right after the records are inserted, so a version and its facts are
activated together (or not at all). Facts are linked to the record they were extracted from.
"""
from sqlalchemy import select

from backend.models import (ControlledSubstance, KnowledgeRecord, LabTestReference, MedIngredient, MedProduct,
                            PolicyClause, ProcedureTerm)

_SIMPLE = {'lab_test_refs': LabTestReference, 'procedure_terms': ProcedureTerm, 'policy_clauses': PolicyClause,
           'controlled_substances': ControlledSubstance}


def _columns(model):
    return {c.key for c in model.__table__.columns} - {'id', 'record_pk', 'version_pk', 'source_id'}


def materialize_facts(session, version_id, source_id):
    counts = {}
    rows = session.execute(select(KnowledgeRecord.id, KnowledgeRecord.metadata_)
                           .where(KnowledgeRecord.version_pk == version_id,
                                  KnowledgeRecord.metadata_.has_key('facts'))).all()
    for record_id, meta in rows:
        for table, items in (meta.get('facts') or {}).items():
            for item in items:
                if table == 'med_products':
                    cols = _columns(MedProduct)
                    product = MedProduct(record_pk=record_id, version_pk=version_id, source_id=source_id,
                                         ingredient_key='+'.join(sorted(i['ingredient'] for i in item['ingredients'])),
                                         **{k: v for k, v in item.items() if k in cols and k != 'ingredient_key'})
                    product.ingredients = [MedIngredient(position=n, **{k: i[k] for k in (
                        'ingredient', 'as_written', 'strength_value', 'strength_unit', 'evidence_text')})
                        for n, i in enumerate(item['ingredients'], 1)]
                    session.add(product)
                elif table in _SIMPLE:
                    model = _SIMPLE[table]
                    cols = _columns(model)
                    session.add(model(record_pk=record_id, version_pk=version_id, source_id=source_id,
                                      **{k: v for k, v in item.items() if k in cols}))
                else:
                    raise ValueError(f'Unknown fact table {table!r}')
                counts[table] = counts.get(table, 0) + 1
    session.flush()
    return counts
