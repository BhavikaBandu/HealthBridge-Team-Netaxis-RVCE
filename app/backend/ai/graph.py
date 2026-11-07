"""LangGraph orchestration of one trip analysis.

    START -> plan --(nothing changed)--> END
                 \--> medicines ---\
                  --> procedures ---+--> policy -> controller -> persist -> END
                  --> documents ---/

plan        compares input fingerprints with the stored findings and selects only what changed (everything when the
            trip route/dates, the knowledge base or the pipeline changed, or when a full run is forced)
medicines / procedures / documents
            the existing Phase 3 agents, run in parallel (each node has its own database session)
policy      runs after the others, only when its inputs changed (it reads medicines and documents)
controller  Dopamine-Cortisol assessment of every new finding
persist     replaces only the re-run findings (and flags, if policy ran) in one transaction

Pages never run this graph; they read the stored results. Graph state is checkpointed per run (in memory).
"""
import logging
import operator
import uuid
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from sqlalchemy import delete, select

from backend.database import SessionLocal
from backend.models import now
from backend.portal.models import (Allergy, AnalysisFinding, AnalysisFlag, Document, DocumentLink, DocumentText,
                                   Medication, Procedure, Trip, TripAnalysis)
from . import controller, fingerprints, llm, medicine_agent, policy_agent, procedure_agent, report_agent
from .common import TripContext

log = logging.getLogger('uvicorn.error')


class RunState(TypedDict, total=False):
    trip_id: str
    analysis_id: str
    force: bool                   # manual refresh: run everything if nothing is out of date
    force_full: bool              # run every agent regardless of fingerprints
    plan: dict                   # {'medication': [ids], 'procedure': [ids], 'document': [ids], 'policy': bool, 'drop': [ids], 'full': bool}
    fingerprints: dict            # {'base', 'policy', 'records': {record id: fingerprint}}
    findings: Annotated[list, operator.add]
    flags: list | None
    ai_used: Annotated[int, operator.add]
    notes: Annotated[list, operator.add]


# ------------------------------------------------------------------ helpers
def _jurisdiction(country):
    return 'AE-DU' if country == 'AE' else country   # UAE trips: federal rules + Dubai guidance


def _context(s, trip):
    stay = (trip.return_date - trip.departure_date).days + 1 if trip.return_date else None
    allergies = [x.allergen for x in s.scalars(select(Allergy).where(Allergy.patient_id == trip.patient_id,
                                                                     Allergy.archived_at.is_(None)))]
    return TripContext(trip.id, trip.patient_id, trip.origin_country, trip.destination_country,
                       _jurisdiction(trip.destination_country), stay, allergies)


def _referral_text(s, proc):
    ids = s.scalars(select(DocumentLink.document_id).where(DocumentLink.record_type == 'procedure',
                                                           DocumentLink.record_id == proc.id)).all()
    texts = [s.get(DocumentText, i) for i in ids]
    return '\n'.join(p['text'] for t in texts if t for p in t.pages)[:4000]


def _safe(fn, *args, record):
    try:
        return fn(*args)
    except Exception as exc:   # one record failing must not stop the trip analysis
        log.exception('agent failed for %s', record)
        rtype, rid, name = record
        return {'agent': {'medication': 'medicine', 'procedure': 'procedure', 'document': 'report'}[rtype],
                'record_type': rtype, 'record_id': rid, 'title': name, 'match_label': 'Could not analyse',
                'confidence': None, 'patient_line': None, 'comparison': {}, 'facts': [], 'context': str(exc)[:300],
                'verify': None, 'sources': [], '_ai': 'rejected'}


def _agent_node(rtype, model, run):
    """Graph node running one agent for the planned records of one type."""
    def node(state):
        ids = [uuid.UUID(i) for i in state['plan'].get(rtype, [])]
        if not ids:
            return {}
        out = []
        with SessionLocal() as s:
            trip = s.get(Trip, uuid.UUID(state['trip_id']))
            ctx = _context(s, trip)
            for rec in s.scalars(select(model).where(model.id.in_(ids))):
                out.append(_safe(run, s, rec, ctx, record=(rtype, rec.id, getattr(rec, 'brand', None) or rec.name)))
        for f in out:
            f['_fingerprint'] = state['fingerprints']['records'].get(str(f['record_id']))
        return {'findings': out, 'ai_used': ctx.ai_used, 'notes': ctx.ai_fallbacks}
    node.__name__ = f'{rtype}_node'
    return node


# ------------------------------------------------------------------ nodes
def plan(state):
    with SessionLocal() as s:
        trip = s.get(Trip, uuid.UUID(state['trip_id']))
        a = s.get(TripAnalysis, uuid.UUID(state['analysis_id']))
        fp = fingerprints.collect(s, trip)
        records = fp.pop('_records')
        stored = {f.record_id: f.fingerprint for f in s.scalars(select(AnalysisFinding).where(AnalysisFinding.analysis_id == a.id))}
        live = {r.id for recs in records.values() for r in recs}
        full = state.get('force_full') or a.base_fingerprint != fp['base']
        selected = {rtype: [str(r.id) for r in recs if full or stored.get(r.id) != fp[(rtype, r.id)]]
                    for rtype, recs in records.items()}
        policy = full or a.policy_fingerprint != fp['policy']
        drop = [str(rid) for rid in stored if rid not in live]
        if state.get('force') and not any(selected.values()) and not policy and not drop:
            # manual refresh with nothing out of date: run everything again
            selected = {rtype: [str(r.id) for r in recs] for rtype, recs in records.items()}
            policy, full = True, True
        fps = {'base': fp['base'], 'policy': fp['policy'],
               'records': {str(k[1]): v for k, v in fp.items() if isinstance(k, tuple)}}
    return {'plan': {**selected, 'policy': policy, 'drop': drop, 'full': full}, 'fingerprints': fps}


def route_after_plan(state):
    p = state['plan']
    if not (p['medication'] or p['procedure'] or p['document'] or p['policy'] or p['drop']):
        return 'nothing'
    return 'run'


medicines = _agent_node('medication', Medication, medicine_agent.analyse)
documents = _agent_node('document', Document, report_agent.analyse)


def procedures(state):
    def run(s, proc, ctx):
        return procedure_agent.analyse(s, proc, ctx, _referral_text(s, proc))
    return _agent_node('procedure', Procedure, run)(state)


def policy(state):
    if not state['plan'].get('policy'):
        return {'flags': None}
    with SessionLocal() as s:
        trip = s.get(Trip, uuid.UUID(state['trip_id']))
        ctx = _context(s, trip)
        meds = s.scalars(select(Medication).where(Medication.patient_id == trip.patient_id, Medication.archived_at.is_(None))
                         .order_by(Medication.ongoing.desc(), Medication.created_at)).all()
        try:
            flags = policy_agent.analyse(s, meds, ctx)
        except Exception as exc:   # keep the other agents' results
            log.exception('policy agent failed')
            flags = [{'kind': 'flag', 'severity': 'review', 'subject': 'Policy check',
                      'text': 'The policy check could not be completed. Check medicine rules before travel.',
                      'origin': 'rules', 'sources': [], '_error': str(exc)}]
    return {'flags': flags, 'ai_used': ctx.ai_used, 'notes': ctx.ai_fallbacks}


def assess(state):
    with SessionLocal() as s:
        for f in state.get('findings') or []:
            f['assessment'] = controller.assess(s, f)
    return {}


def persist(state):
    order = {'medicine': 0, 'procedure': 1, 'report': 2}
    with SessionLocal() as s:
        a = s.get(TripAnalysis, uuid.UUID(state['analysis_id']))
        p = state['plan']
        new = state.get('findings') or []
        replaced = [uuid.UUID(i) for i in p['drop']] + [f['record_id'] for f in new]
        if p.get('full'):
            s.execute(delete(AnalysisFinding).where(AnalysisFinding.analysis_id == a.id))
        elif replaced:
            s.execute(delete(AnalysisFinding).where(AnalysisFinding.analysis_id == a.id,
                                                    AnalysisFinding.record_id.in_(replaced)))
        for f in sorted(new, key=lambda x: order.get(x['agent'], 3)):
            s.add(AnalysisFinding(analysis_id=a.id, patient_id=a.patient_id, fingerprint=f.get('_fingerprint'),
                                  **{k: v for k, v in f.items() if not k.startswith('_')}))
        s.flush()
        # keep a stable display order: medicines, procedures, documents
        rows = s.scalars(select(AnalysisFinding).where(AnalysisFinding.analysis_id == a.id)).all()
        for n, f in enumerate(sorted(rows, key=lambda x: (order.get(x.agent, 3), x.position if x.position is not None else 0))):
            f.position = n
        if state.get('flags') is not None:
            s.execute(delete(AnalysisFlag).where(AnalysisFlag.analysis_id == a.id))
            for n, f in enumerate(state['flags']):
                s.add(AnalysisFlag(analysis_id=a.id, patient_id=a.patient_id, position=n,
                                   **{k: v for k, v in f.items() if not k.startswith('_')}))
            a.policy_fingerprint = state['fingerprints']['policy']
        a.base_fingerprint = state['fingerprints']['base']
        a.running, a.analyzed_at = False, now()
        if state.get('ai_used'):
            a.provider = llm.provider_label()
        elif new or state.get('flags'):
            a.provider = 'template wording (AI unavailable)'
        ran = {k: len(v) for k, v in p.items() if isinstance(v, list) and v and k != 'drop'}
        summary = ('full run' if p.get('full') else 'changed only: ' + ', '.join(f'{v} {k}' for k, v in ran.items())
                   + (', policy' if p.get('policy') else ''))
        a.note = ('; '.join([summary] + (state.get('notes') or [])))[:2000]
        s.commit()
    return {}


def build():
    g = StateGraph(RunState)
    g.add_node('plan', plan)
    g.add_node('medicines', medicines)
    g.add_node('procedures', procedures)
    g.add_node('documents', documents)
    g.add_node('policy', policy)
    g.add_node('controller', assess)
    g.add_node('persist', persist)
    g.add_edge(START, 'plan')
    g.add_conditional_edges('plan', route_after_plan, {'nothing': END, 'run': 'fanout'})
    g.add_node('fanout', lambda state: {})
    for n in ('medicines', 'procedures', 'documents'):
        g.add_edge('fanout', n)
    g.add_edge(['medicines', 'procedures', 'documents'], 'policy')   # policy waits for all three
    g.add_edge('policy', 'controller')
    g.add_edge('controller', 'persist')
    g.add_edge('persist', END)
    return g.compile(checkpointer=InMemorySaver())


GRAPH = build()


def run(trip_id, analysis_id, force=False, full=False):
    """Run the graph for one trip; returns the final state."""
    run_id = str(uuid.uuid4())
    return GRAPH.invoke({'trip_id': str(trip_id), 'analysis_id': str(analysis_id), 'force': force, 'force_full': full,
                         'findings': [], 'ai_used': 0, 'notes': []},
                        config={'configurable': {'thread_id': run_id}})
