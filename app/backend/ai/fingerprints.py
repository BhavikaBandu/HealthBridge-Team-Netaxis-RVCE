"""Input fingerprints: which stored findings are still current.

Each finding stores a hash of exactly the inputs it was made from. Comparing it with the hash of the inputs now tells
whether the finding is current or out of date, without running any agent:

    base      trip route and dates + knowledge-base versions + pipeline version (a change makes everything out of date)
    medicine  the medication record + the patient's allergies (allergy check)
    procedure the procedure record + documents linked to it (referral text)
    document  the document record and its stored file
    policy    every ongoing medication + every document (prescription facts and the document check)
"""
import hashlib
import json

from sqlalchemy import select

from backend.models import Source
from backend.portal.models import Allergy, Document, DocumentLink, Medication, Procedure

PIPELINE_VERSION = 'p4-6.1'   # bump when agent logic changes in a way that should mark old findings out of date


def _h(*parts):
    return hashlib.sha256(json.dumps(parts, default=str, sort_keys=True).encode()).hexdigest()


def _stamp(rec):
    return [str(rec.id), rec.updated_at.isoformat() if getattr(rec, 'updated_at', None) else None]


def base(s, trip):
    kb = sorted(s.scalars(select(Source.active_version_id).where(Source.active_version_id.is_not(None))))
    return _h(PIPELINE_VERSION, trip.origin_country, trip.destination_country, trip.departure_date, trip.return_date, kb)


def collect(s, trip):
    """Current fingerprints: {'base': .., 'policy': .., ('medication', id): .., ('procedure', id): .., ('document', id): ..}
    plus the live records under '_records'."""
    pid = trip.patient_id
    b = base(s, trip)
    meds = s.scalars(select(Medication).where(Medication.patient_id == pid, Medication.archived_at.is_(None))).all()
    procs = s.scalars(select(Procedure).where(Procedure.patient_id == pid, Procedure.archived_at.is_(None))).all()
    docs = s.scalars(select(Document).where(Document.patient_id == pid, Document.archived_at.is_(None))).all()
    allergies = sorted(a.allergen.lower() for a in s.scalars(select(Allergy).where(Allergy.patient_id == pid,
                                                                                  Allergy.archived_at.is_(None))))
    doc_stamp = {d.id: _stamp(d) + [d.storage_key] for d in docs}
    links = {}
    for link in s.scalars(select(DocumentLink).where(DocumentLink.patient_id == pid, DocumentLink.record_type == 'procedure')):
        links.setdefault(link.record_id, []).append(doc_stamp.get(link.document_id))
    out = {'base': b, '_records': {'medication': meds, 'procedure': procs, 'document': docs}}
    for m in meds:
        out[('medication', m.id)] = _h(b, _stamp(m), allergies)
    for p in procs:
        out[('procedure', p.id)] = _h(b, _stamp(p), sorted(map(str, links.get(p.id, []))))
    for d in docs:
        out[('document', d.id)] = _h(b, doc_stamp[d.id])
    out['policy'] = _h(b, sorted(_stamp(m) for m in meds if m.ongoing), sorted(map(str, doc_stamp.values())))
    return out
