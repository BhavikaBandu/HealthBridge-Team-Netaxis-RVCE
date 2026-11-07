"""Patient portal data model. Every patient-owned row carries patient_id and is always queried by it."""
import uuid
from datetime import date, datetime

from sqlalchemy import (Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, Uuid,
                        text)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models import now


def _id():
    return mapped_column(Uuid, primary_key=True, default=uuid.uuid4)


def _owner():
    return mapped_column(Uuid, ForeignKey('users.id', ondelete='CASCADE'), index=True)


class Timestamps:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Archivable(Timestamps):
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class Reported:
    """Who entered a medical-history record. Patients -> 'Self-reported'; doctors -> 'Doctor reported'."""
    reported_by_role: Mapped[str] = mapped_column(String(20), default='patient', server_default='patient')  # patient | doctor
    reported_by_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey('users.id', ondelete='SET NULL'))


class User(Timestamps, Base):
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = _id()
    public_patient_id: Mapped[str | None] = mapped_column(String(20), unique=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(20), default='patient')  # patient | doctor (doctor portal later)
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PatientProfile(Base):
    __tablename__ = 'patient_profiles'
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    origin_country: Mapped[str | None] = mapped_column(String(2))
    preferred_language: Mapped[str | None] = mapped_column(String(5))
    phone: Mapped[str | None] = mapped_column(String(20))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class UserSession(Base):
    __tablename__ = 'user_sessions'
    id: Mapped[uuid.UUID] = _id()
    user_id: Mapped[uuid.UUID] = _owner()
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)  # SHA-256 of the cookie token
    csrf_token: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    remember: Mapped[bool] = mapped_column(Boolean, default=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Trip(Archivable, Base):
    __tablename__ = 'trips'
    id: Mapped[uuid.UUID] = _id()
    patient_id: Mapped[uuid.UUID] = _owner()
    origin_country: Mapped[str] = mapped_column(String(2))
    destination_country: Mapped[str] = mapped_column(String(2))
    purpose_type: Mapped[str] = mapped_column(String(20))  # basic | specialised
    purpose_description: Mapped[str | None] = mapped_column(Text)
    departure_date: Mapped[date] = mapped_column(Date, index=True)
    return_date: Mapped[date | None] = mapped_column(Date)


class Medication(Reported, Archivable, Base):
    __tablename__ = 'medications'
    id: Mapped[uuid.UUID] = _id()
    patient_id: Mapped[uuid.UUID] = _owner()
    name: Mapped[str] = mapped_column(String(200))
    brand: Mapped[str | None] = mapped_column(String(200))
    manufacturer: Mapped[str | None] = mapped_column(String(200))
    strength_value: Mapped[float | None] = mapped_column(Numeric(12, 4))
    strength_unit: Mapped[str | None] = mapped_column(String(20))
    strength_label: Mapped[str | None] = mapped_column(String(100))
    dosage_form: Mapped[str | None] = mapped_column(String(20))
    dose: Mapped[str | None] = mapped_column(String(100))
    schedule: Mapped[dict] = mapped_column(JSONB, default=dict)
    start_date: Mapped[date | None] = mapped_column(Date)
    start_date_unknown: Mapped[bool] = mapped_column(Boolean, default=False)
    ongoing: Mapped[bool] = mapped_column(Boolean, default=True)
    stop_date: Mapped[date | None] = mapped_column(Date)
    instructions: Mapped[str | None] = mapped_column(Text)


class Condition(Reported, Archivable, Base):
    __tablename__ = 'conditions'
    id: Mapped[uuid.UUID] = _id()
    patient_id: Mapped[uuid.UUID] = _owner()
    name: Mapped[str] = mapped_column(String(200))
    diagnosis_date: Mapped[date | None] = mapped_column(Date)
    diagnosis_year: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default='active')  # active | resolved | unknown
    notes: Mapped[str | None] = mapped_column(Text)


class Procedure(Reported, Archivable, Base):
    __tablename__ = 'procedures'
    id: Mapped[uuid.UUID] = _id()
    patient_id: Mapped[uuid.UUID] = _owner()
    name: Mapped[str] = mapped_column(String(200))
    procedure_date: Mapped[date | None] = mapped_column(Date)
    country: Mapped[str | None] = mapped_column(String(2))
    hospital: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default='completed')  # planned | completed
    notes: Mapped[str | None] = mapped_column(Text)


class AllergyDeclaration(Base):
    __tablename__ = 'allergy_declarations'
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    declaration: Mapped[str] = mapped_column(String(10), default='unknown')  # unknown | none | known
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Allergy(Reported, Archivable, Base):
    __tablename__ = 'allergies'
    id: Mapped[uuid.UUID] = _id()
    patient_id: Mapped[uuid.UUID] = _owner()
    allergen: Mapped[str] = mapped_column(String(200))
    reaction: Mapped[str | None] = mapped_column(String(300))
    severity: Mapped[str] = mapped_column(String(20), default='unknown')  # mild | moderate | severe | unknown
    notes: Mapped[str | None] = mapped_column(Text)


class Document(Archivable, Base):
    __tablename__ = 'documents'
    id: Mapped[uuid.UUID] = _id()
    patient_id: Mapped[uuid.UUID] = _owner()
    name: Mapped[str] = mapped_column(String(200))
    doc_type: Mapped[str] = mapped_column(String(30), index=True)
    document_date: Mapped[date | None] = mapped_column(Date)
    storage_key: Mapped[str] = mapped_column(String(64), unique=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(50))
    size_bytes: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)


class DocumentLink(Base):
    """Many-to-many link between a document and a medical-history record of the same patient."""
    __tablename__ = 'document_links'
    id: Mapped[uuid.UUID] = _id()
    document_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('documents.id', ondelete='CASCADE'), index=True)
    patient_id: Mapped[uuid.UUID] = _owner()
    record_type: Mapped[str] = mapped_column(String(20))  # medication | condition | procedure | allergy
    record_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__ = (UniqueConstraint('document_id', 'record_type', 'record_id', name='uq_document_link'),)


class DocumentText(Base):
    """Text read from an uploaded document (one row per document), kept so it can be searched and re-parsed."""
    __tablename__ = 'document_texts'
    document_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('documents.id', ondelete='CASCADE'), primary_key=True)
    patient_id: Mapped[uuid.UUID] = _owner()
    status: Mapped[str] = mapped_column(String(20))   # extracted | no_text_layer | failed
    method: Mapped[str] = mapped_column(String(40))   # e.g. "pypdf text layer"
    parser_version: Mapped[str] = mapped_column(String(20))
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    pages: Mapped[list] = mapped_column(JSONB, default=list)   # [{"page": 1, "text": "..."}]
    error: Mapped[str | None] = mapped_column(Text)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DocumentFinding(Base):
    """A value read from a document (lab result, prescription item, ...). Always starts 'unverified'."""
    __tablename__ = 'document_findings'
    id: Mapped[uuid.UUID] = _id()
    document_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('documents.id', ondelete='CASCADE'), index=True)
    patient_id: Mapped[uuid.UUID] = _owner()
    kind: Mapped[str] = mapped_column(String(30), index=True)   # lab_result | prescription_item | prescription_fields
    data: Mapped[dict] = mapped_column(JSONB, default=dict)
    evidence_text: Mapped[str] = mapped_column(Text)            # the exact text the value was read from
    page: Mapped[int | None] = mapped_column(Integer)
    line: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default='unverified')   # unverified | confirmed | rejected
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey('users.id', ondelete='SET NULL'))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class TripAnalysis(Base):
    """The latest AI cross-border analysis of one trip (replaced on every run). Read by both portals."""
    __tablename__ = 'trip_analyses'
    id: Mapped[uuid.UUID] = _id()
    trip_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('trips.id', ondelete='CASCADE'), unique=True)
    patient_id: Mapped[uuid.UUID] = _owner()
    origin: Mapped[str] = mapped_column(String(2))
    destination: Mapped[str] = mapped_column(String(2))
    running: Mapped[bool] = mapped_column(Boolean, default=False)   # true while a run is in progress
    provider: Mapped[str | None] = mapped_column(String(80))         # e.g. "ollama:qwen3:30b-a3b"
    note: Mapped[str | None] = mapped_column(Text)                   # e.g. AI unavailable -> template wording used
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    base_fingerprint: Mapped[str | None] = mapped_column(String(64))    # trip route/dates + knowledge base + pipeline version
    policy_fingerprint: Mapped[str | None] = mapped_column(String(64))  # inputs of the policy flags (medicines, documents)


class AnalysisFinding(Base):
    """One finding for one medication / procedure / document of the analysed trip."""
    __tablename__ = 'analysis_findings'
    id: Mapped[uuid.UUID] = _id()
    analysis_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('trip_analyses.id', ondelete='CASCADE'), index=True)
    patient_id: Mapped[uuid.UUID] = _owner()
    agent: Mapped[str] = mapped_column(String(20))          # medicine | procedure | report
    record_type: Mapped[str] = mapped_column(String(20))    # medication | procedure | document
    record_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    title: Mapped[str] = mapped_column(Text)                # "Augmentin DUO 1 g -> Augmentin 1 g (UAE)"
    match_label: Mapped[str | None] = mapped_column(String(80))   # "Same ingredients and strength"
    confidence: Mapped[str | None] = mapped_column(String(10))    # High | Medium | Low
    patient_line: Mapped[str | None] = mapped_column(Text)        # short line for the patient summary
    comparison: Mapped[dict] = mapped_column(JSONB, default=dict)  # {"columns": [...], "rows": [[label, a, b], ...]}
    facts: Mapped[list] = mapped_column(JSONB, default=list)        # documents: [{"label", "value", "converted", "problem"}]
    context: Mapped[str | None] = mapped_column(Text)
    verify: Mapped[str | None] = mapped_column(Text)
    sources: Mapped[list] = mapped_column(JSONB, default=list)      # [{"source_id", "label", "record_id", "url"}]
    position: Mapped[int] = mapped_column(Integer, default=0)
    # Dopamine-Cortisol controller result: {"version", "dopamine", "cortisol", "disposition", "label", "reasons", "features"}
    assessment: Mapped[dict] = mapped_column(JSONB, default=dict)
    fingerprint: Mapped[str | None] = mapped_column(String(64))      # hash of the inputs this finding was made from


class AnalysisFlag(Base):
    """A jurisdiction flag or quantity advice for the analysed trip."""
    __tablename__ = 'analysis_flags'
    id: Mapped[uuid.UUID] = _id()
    analysis_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('trip_analyses.id', ondelete='CASCADE'), index=True)
    patient_id: Mapped[uuid.UUID] = _owner()
    kind: Mapped[str] = mapped_column(String(20))           # flag | quantity
    severity: Mapped[str] = mapped_column(String(20))       # action | review | advice
    subject: Mapped[str] = mapped_column(Text)              # medicine the flag is about
    text: Mapped[str] = mapped_column(Text)                 # 1-2 plain sentences (patient + doctor)
    origin: Mapped[str] = mapped_column(String(40))         # rules | document (unverified)
    sources: Mapped[list] = mapped_column(JSONB, default=list)
    position: Mapped[int] = mapped_column(Integer, default=0)


class TripReport(Base):
    """A generated travel health report (printable), saved per trip, language and audience so it can be reused."""
    __tablename__ = 'trip_reports'
    id: Mapped[uuid.UUID] = _id()
    trip_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('trips.id', ondelete='CASCADE'), index=True)
    patient_id: Mapped[uuid.UUID] = _owner()
    audience: Mapped[str] = mapped_column(String(10), default='patient')   # patient | doctor
    language: Mapped[str] = mapped_column(String(5))                       # en | ar
    analysis_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))   # analysis the report was built from
    content: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__ = (UniqueConstraint('trip_id', 'audience', 'language', name='uq_trip_report'),)


class AuditEvent(Base):
    __tablename__ = 'audit_events'
    id: Mapped[uuid.UUID] = _id()
    actor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey('users.id', ondelete='SET NULL'))
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    action: Mapped[str] = mapped_column(String(40))
    entity_type: Mapped[str | None] = mapped_column(String(30))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    summary: Mapped[str | None] = mapped_column(String(200))  # short, no medical detail or secrets
    ip: Mapped[str | None] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)


class DoctorProfile(Base):
    """Doctor account details. A typed registration number is stored, never treated as verified."""
    __tablename__ = 'doctor_profiles'
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    public_doctor_id: Mapped[str] = mapped_column(String(20), unique=True)
    full_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str | None] = mapped_column(String(20))
    origin_country: Mapped[str | None] = mapped_column(String(2))
    preferred_language: Mapped[str | None] = mapped_column(String(5))
    registration_number: Mapped[str | None] = mapped_column(String(60))
    hospital: Mapped[str | None] = mapped_column(String(200))
    speciality: Mapped[str | None] = mapped_column(String(120))
    verification_status: Mapped[str] = mapped_column(String(20), default='pending', server_default='pending')  # pending | approved | rejected
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class AccessRequest(Base):
    """A doctor's request to access one patient's records.

    The typed patient ID is stored as entered; patient_id is only set when it matches a real patient, so the
    doctor never learns whether an ID exists. Lifecycle: pending -> accepted | rejected | cancelled | expired;
    accepted -> revoked.
    """
    __tablename__ = 'access_requests'
    id: Mapped[uuid.UUID] = _id()
    doctor_id: Mapped[uuid.UUID] = _owner()
    requested_patient_code: Mapped[str] = mapped_column(String(20))
    patient_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    status: Mapped[str] = mapped_column(String(20), default='pending', index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        # At most one open (pending or accepted) request per doctor and patient ID.
        Index('uq_access_open_pair', 'doctor_id', 'requested_patient_code', unique=True,
              postgresql_where=text("status IN ('pending', 'accepted')")),
    )
