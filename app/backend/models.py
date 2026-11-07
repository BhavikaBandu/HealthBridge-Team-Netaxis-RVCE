"""Database models.

Source          stable identity of a reference source (one row per source ID).
SourceVersion   immutable snapshot of that source's raw file, identified by SHA-256. Old versions are kept.
KnowledgeRecord structured record extracted from one SourceVersion.
RecordEmbedding optional semantic vector for a record (one per embedding model).
IngestionRun    audit log of every ingestion attempt, including failures.
"""
from datetime import datetime, timezone

from sqlalchemy import (BigInteger, Boolean, Computed, DateTime, ForeignKey, Index, Integer, LargeBinary, Numeric,
                        String, Text, UniqueConstraint)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def now():
    return datetime.now(timezone.utc)


SEARCH_VECTOR_SQL = (
    "setweight(to_tsvector('simple', coalesce(title, '')), 'A') || "
    "setweight(to_tsvector('simple', coalesce(external_id, '')), 'A') || "
    "setweight(to_tsvector('simple', coalesce(content, '')), 'B')"
)


class Source(Base):
    __tablename__ = 'sources'
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[str] = mapped_column(String(80), unique=True)
    title: Mapped[str] = mapped_column(Text)
    workflow: Mapped[str] = mapped_column(String(40), index=True)
    jurisdiction: Mapped[str] = mapped_column(String(30))
    origin_url: Mapped[str | None] = mapped_column(Text)
    licence_note: Mapped[str | None] = mapped_column(Text)
    access_note: Mapped[str | None] = mapped_column(Text)
    # Catalogue ID from the data handoff (e.g. GL-UCUM is catalogue DT05), publisher, and whether the source is
    # actually ingested. 'not_ingested' sources are registered so retrieval can report them as missing evidence.
    catalogue_id: Mapped[str | None] = mapped_column(String(40))
    publisher: Mapped[str | None] = mapped_column(Text)
    ingestion_status: Mapped[str] = mapped_column(String(20), default='ingested', server_default='ingested')
    limitations: Mapped[list] = mapped_column(JSONB, default=list, server_default='[]')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    active_version_id: Mapped[int | None] = mapped_column(
        ForeignKey('source_versions.id', use_alter=True, name='fk_sources_active_version', ondelete='SET NULL'))
    versions: Mapped[list['SourceVersion']] = relationship(
        back_populates='source', foreign_keys='SourceVersion.source_pk', order_by='SourceVersion.id')


class SourceVersion(Base):
    __tablename__ = 'source_versions'
    id: Mapped[int] = mapped_column(primary_key=True)
    source_pk: Mapped[int] = mapped_column(ForeignKey('sources.id', ondelete='CASCADE'), index=True)
    version_label: Mapped[str] = mapped_column(String(80))
    sha256: Mapped[str] = mapped_column(String(64))
    raw_path: Mapped[str] = mapped_column(Text)
    snapshot_path: Mapped[str | None] = mapped_column(Text)
    file_size: Mapped[int] = mapped_column(BigInteger)
    parser_name: Mapped[str] = mapped_column(String(80))
    parser_version: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default='loading')  # loading | active | superseded
    record_count: Mapped[int] = mapped_column(Integer, default=0)
    acquired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    source: Mapped[Source] = relationship(back_populates='versions', foreign_keys=[source_pk])
    __table_args__ = (UniqueConstraint('source_pk', 'sha256', name='uq_version_source_sha'),)


class KnowledgeRecord(Base):
    __tablename__ = 'knowledge_records'
    id: Mapped[int] = mapped_column(primary_key=True)
    version_pk: Mapped[int] = mapped_column(ForeignKey('source_versions.id', ondelete='CASCADE'), index=True)
    external_id: Mapped[str] = mapped_column(String(250))
    kind: Mapped[str] = mapped_column(String(40), index=True)
    workflow: Mapped[str] = mapped_column(String(40), index=True)
    jurisdiction: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(15))
    source_link: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column('metadata', JSONB, default=dict)
    search_vector = mapped_column(TSVECTOR, Computed(SEARCH_VECTOR_SQL, persisted=True))
    __table_args__ = (
        UniqueConstraint('version_pk', 'external_id', name='uq_record_version_external'),
        Index('ix_records_search_vector', 'search_vector', postgresql_using='gin'),
    )


class RecordEmbedding(Base):
    __tablename__ = 'record_embeddings'
    record_pk: Mapped[int] = mapped_column(ForeignKey('knowledge_records.id', ondelete='CASCADE'), primary_key=True)
    model: Mapped[str] = mapped_column(String(120), primary_key=True)
    dim: Mapped[int] = mapped_column(Integer)
    vector: Mapped[bytes] = mapped_column(LargeBinary)  # float32 little-endian, L2-normalised


class IngestionRun(Base):
    __tablename__ = 'ingestion_runs'
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[str] = mapped_column(String(80), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default='running')  # running | ingested | unchanged | reactivated | failed
    sha256: Mapped[str | None] = mapped_column(String(64))
    version_pk: Mapped[int | None] = mapped_column(ForeignKey('source_versions.id', ondelete='SET NULL'))
    records_loaded: Mapped[int] = mapped_column(Integer, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str | None] = mapped_column(Text)
    errors: Mapped[list] = mapped_column(JSONB, default=list)


# ---------------------------------------------------------------------------------------------------------------
# Domain evidence tables. Each row is a structured fact extracted from one KnowledgeRecord (a passage of an
# ingested source version). Rows are rebuilt with their version and never edited; retrieval reads only rows whose
# version is the source's active version. Values are copied from source text; nothing is inferred.
# ---------------------------------------------------------------------------------------------------------------

def _record_fk():
    return mapped_column(ForeignKey('knowledge_records.id', ondelete='CASCADE'), index=True)


def _version_fk():
    return mapped_column(ForeignKey('source_versions.id', ondelete='CASCADE'), index=True)


class MedProduct(Base):
    """A medicinal product as described on a label / product page."""
    __tablename__ = 'med_products'
    id: Mapped[int] = mapped_column(primary_key=True)
    record_pk: Mapped[int] = _record_fk()
    version_pk: Mapped[int] = _version_fk()
    source_id: Mapped[str] = mapped_column(String(80))
    country: Mapped[str] = mapped_column(String(10), index=True)
    brand: Mapped[str] = mapped_column(Text)
    product_name: Mapped[str] = mapped_column(Text)          # as written, e.g. "AUGMENTIN 1g DUO"
    generic_name: Mapped[str | None] = mapped_column(Text)
    dosage_form: Mapped[str | None] = mapped_column(String(40))   # normalised: tablet, capsule, ...
    form_detail: Mapped[str | None] = mapped_column(Text)         # as written: "film-coated tablet"
    route: Mapped[str | None] = mapped_column(String(40))
    release_profile: Mapped[str | None] = mapped_column(Text)
    manufacturer: Mapped[str | None] = mapped_column(Text)
    ingredient_key: Mapped[str] = mapped_column(Text, index=True)  # sorted normalised ingredients joined by '+'
    ingredients: Mapped[list['MedIngredient']] = relationship(order_by='MedIngredient.position',
                                                              cascade='all, delete-orphan')
    __table_args__ = (Index('ix_med_products_brand_trgm', 'brand', postgresql_using='gin',
                            postgresql_ops={'brand': 'gin_trgm_ops'}),)


class MedIngredient(Base):
    """One active ingredient of a product, kept separately for combination products."""
    __tablename__ = 'med_ingredients'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('med_products.id', ondelete='CASCADE'), index=True)
    position: Mapped[int] = mapped_column(Integer)
    ingredient: Mapped[str] = mapped_column(String(120))          # normalised, e.g. "amoxicillin"
    as_written: Mapped[str] = mapped_column(Text)                 # e.g. "Amoxycillin Trihydrate IP equivalent to Amoxycillin"
    strength_value: Mapped[float | None] = mapped_column(Numeric(12, 4))
    strength_unit: Mapped[str | None] = mapped_column(String(20))
    evidence_text: Mapped[str] = mapped_column(Text)
    __table_args__ = (Index('ix_med_ingredients_ing_strength', 'ingredient', 'strength_value', 'strength_unit'),)


class LabTestReference(Base):
    """A lab test reference (test catalogue entry) or an observation printed on a sample report."""
    __tablename__ = 'lab_test_refs'
    id: Mapped[int] = mapped_column(primary_key=True)
    record_pk: Mapped[int] = _record_fk()
    version_pk: Mapped[int] = _version_fk()
    source_id: Mapped[str] = mapped_column(String(80))
    country: Mapped[str] = mapped_column(String(10), index=True)
    entry_type: Mapped[str] = mapped_column(String(30))           # reference_test | sample_observation
    test_name: Mapped[str] = mapped_column(Text)
    analyte: Mapped[str | None] = mapped_column(String(80))        # normalised analyte, e.g. "glucose"
    synonyms: Mapped[list] = mapped_column(JSONB, default=list)
    specimen: Mapped[str | None] = mapped_column(Text)
    fasting: Mapped[bool | None] = mapped_column(Boolean)
    unit: Mapped[str | None] = mapped_column(String(40))
    unit_system: Mapped[str | None] = mapped_column(String(20))    # conventional | SI
    ref_low: Mapped[float | None] = mapped_column(Numeric(14, 4))
    ref_high: Mapped[float | None] = mapped_column(Numeric(14, 4))
    ref_text: Mapped[str | None] = mapped_column(Text)
    method: Mapped[str | None] = mapped_column(Text)
    observed_value: Mapped[str | None] = mapped_column(String(40))  # only for sample_observation, as printed
    panel: Mapped[str | None] = mapped_column(Text)
    codes: Mapped[dict] = mapped_column(JSONB, default=dict)         # order code, CPT, ... as printed
    __table_args__ = (Index('ix_lab_refs_analyte_unit', 'analyte', 'unit'),)


class ProcedureTerm(Base):
    """A procedure / imaging service term with only the attributes the source text states."""
    __tablename__ = 'procedure_terms'
    id: Mapped[int] = mapped_column(primary_key=True)
    record_pk: Mapped[int] = _record_fk()
    version_pk: Mapped[int] = _version_fk()
    source_id: Mapped[str] = mapped_column(String(80))
    country: Mapped[str] = mapped_column(String(10), index=True)
    provider: Mapped[str | None] = mapped_column(Text)
    term: Mapped[str] = mapped_column(Text)                         # as written, e.g. "MRI (3T)"
    modality: Mapped[str | None] = mapped_column(String(40), index=True)   # MRI | CT | X-ray | ultrasound | ...
    anatomy: Mapped[list] = mapped_column(JSONB, default=list)      # e.g. ["brain", "spine", "joints"]
    laterality: Mapped[str | None] = mapped_column(String(40))      # e.g. "single (R/L)", "both"; None = not stated
    contrast: Mapped[str | None] = mapped_column(Text)              # statement about contrast, as written
    protocol: Mapped[str | None] = mapped_column(Text)              # only if stated
    evidence_text: Mapped[str] = mapped_column(Text)


class PolicyClause(Base):
    """A clause of a law / guidance page with its hierarchy and the facets stated in its text."""
    __tablename__ = 'policy_clauses'
    id: Mapped[int] = mapped_column(primary_key=True)
    record_pk: Mapped[int] = _record_fk()
    version_pk: Mapped[int] = _version_fk()
    source_id: Mapped[str] = mapped_column(String(80))
    jurisdiction: Mapped[str] = mapped_column(String(20), index=True)   # AE (federal) | AE-DU (Dubai)
    authority: Mapped[str | None] = mapped_column(Text)
    document_title: Mapped[str] = mapped_column(Text)
    document_type: Mapped[str | None] = mapped_column(String(40))       # law | regulator_service | guidance | circular | list
    hierarchy: Mapped[list] = mapped_column(JSONB, default=list)        # ["Part Two ...", "Article (35) ..."]
    clause_ref: Mapped[str | None] = mapped_column(Text)
    actions: Mapped[list] = mapped_column(JSONB, default=list)          # e.g. ["traveller_medicine_import"]
    medicine_classes: Mapped[list] = mapped_column(JSONB, default=list)  # e.g. ["controlled", "narcotic"]
    facets: Mapped[dict] = mapped_column(JSONB, default=dict)           # stated rules, e.g. {"max_supply": "three months"}
    date_text: Mapped[str | None] = mapped_column(Text)                 # dates as stated (publication / update)
    status_note: Mapped[str | None] = mapped_column(Text)               # e.g. "attachment not acquired"
    __table_args__ = (Index('ix_policy_actions', 'actions', postgresql_using='gin'),
                      Index('ix_policy_classes', 'medicine_classes', postgresql_using='gin'))


class ControlledSubstance(Base):
    """One row of a controlled-medicine list (e.g. EDE list) with its category and carry rule as written."""
    __tablename__ = 'controlled_substances'
    id: Mapped[int] = mapped_column(primary_key=True)
    record_pk: Mapped[int] = _record_fk()
    version_pk: Mapped[int] = _version_fk()
    source_id: Mapped[str] = mapped_column(String(80))
    jurisdiction: Mapped[str] = mapped_column(String(20))
    list_number: Mapped[int | None] = mapped_column(Integer)
    generic_name: Mapped[str] = mapped_column(Text)
    name_key: Mapped[str] = mapped_column(Text, index=True)     # lower-case, punctuation-free
    category: Mapped[str | None] = mapped_column(Text)
    carry_rule: Mapped[str | None] = mapped_column(Text)
    prohibited: Mapped[bool | None] = mapped_column(Boolean)
    __table_args__ = (Index('ix_controlled_name_trgm', 'name_key', postgresql_using='gin',
                            postgresql_ops={'name_key': 'gin_trgm_ops'}),)
