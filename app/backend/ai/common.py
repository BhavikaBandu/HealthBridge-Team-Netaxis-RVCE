"""Shared pieces for the agents: trip context, source links, and an AI call with a template fallback."""
from dataclasses import dataclass, field

from backend.portal.reference import COUNTRIES
from . import llm


SHORT_NAMES = {'AE': 'UAE', 'GB': 'UK', 'US': 'USA'}


def country_name(code):
    return COUNTRIES.get(code or '')


@dataclass
class TripContext:
    trip_id: object
    patient_id: object
    origin: str            # trip origin country (used as record source country, marked as assumed)
    destination: str       # trip destination country
    jurisdiction: str      # policy jurisdiction searched (UAE trips -> federal + Dubai)
    stay_days: int | None
    allergies: list = field(default_factory=list)
    ai_used: int = 0
    ai_fallbacks: list = field(default_factory=list)

    @property
    def origin_name(self):
        return country_name(self.origin) or self.origin

    @property
    def destination_short(self):
        return SHORT_NAMES.get(self.destination, self.destination_name)

    @property
    def destination_name(self):
        return country_name(self.destination) or self.destination


def source_entry(result):
    """Compact source link for a retrieval result."""
    loc = (result.get('source_location') or {}).get('label') or ''
    return {'source_id': result['source_id'], 'label': f"{result['source_id']} {loc}".strip(),
            'record_id': result['record_id'], 'url': f"/api/sources/{result['source_id']}/file"}


def dedupe_sources(items, limit=4):
    out, seen = [], set()
    for s in items:
        if s['source_id'] in seen:
            continue
        seen.add(s['source_id'])
        out.append(s)
    return out[:limit]


STRENGTHS = ('Strong', 'Moderate', 'Weak')
STRENGTH_SCHEMA = {'strength': {'type': 'string', 'enum': list(STRENGTHS)}, 'strength_reason': {'type': 'string'}}
FILLS_SCHEMA = {'type': 'array', 'items': {'type': 'object', 'required': ['cell', 'value', 'quote'], 'properties': {
    'cell': {'type': 'integer'}, 'value': {'type': 'string'}, 'quote': {'type': 'string'}}}}
FILL_RULES = (
    'FILL: "blank_cells" lists table cells that code could not fill ("Not stated"). For each one, look ONLY in the '
    'passages given for that column. If a passage states the value, return {cell, value (max 5 words), quote (the '
    'exact words copied from the passage that state it)}. If the passages do not state it, do not return that cell. '
    'Never fill from general knowledge. ')
STRENGTH_RULES = (
    'STRENGTH: give your own strength of the match ("Strong", "Moderate" or "Weak") after reading the table and the '
    'passages, and "strength_reason" (max 15 words) saying why. ')


def squash(text):
    """Lower-case text without spaces or punctuation, for checking that a quote appears in a passage."""
    return ''.join(ch for ch in (text or '').lower() if ch.isalnum())


def blank_cells(rows, columns):
    """Cells of a comparison table that code left as "Not stated" (the only cells the AI may fill)."""
    out = []
    for r, row in enumerate(rows):
        for c in (1, 2):
            if str(row[c]).strip().lower() in ('not stated', 'not specified'):
                out.append({'cell': len(out), 'row': row[0], 'column': columns[c - 1], '_pos': (r, c)})
    return out


def apply_fills(rows, blanks, fills, passages_by_column, stats=None):
    """Put AI values into blank cells, only when the quote really appears in that column's passages.
    Returns the list of filled cells with their quote and source. `stats` (optional dict) receives
    'offered' and 'rejected' counts for the controller."""
    by_id = {b['cell']: b for b in blanks}
    filled = []
    offered = rejected = 0
    for f in fills or []:
        b = by_id.pop(f.get('cell'), None)
        if b is None:
            continue
        offered += 1
        value, quote = (f.get('value') or '').strip(), (f.get('quote') or '').strip()
        if not value or not quote or len(value.split()) > 6 or llm.BANNED.search(value):
            rejected += 1
            continue
        hit = next((p for p in passages_by_column.get(b['column'], []) if squash(quote) and squash(quote) in squash(p['text'])), None)
        if not hit:
            rejected += 1
            continue
        r, c = b['_pos']
        rows[r][c] = value[:1].upper() + value[1:]
        filled.append({'row': b['row'], 'column': b['column'], 'value': rows[r][c], 'quote': quote[:300],
                       'source': hit['source']})
    if stats is not None:
        stats.update(offered=offered, rejected=rejected)
    return filled


def ai_match(data):
    """The AI's own match strength, if it gave a valid one."""
    s = (data or {}).get('strength')
    if s not in STRENGTHS:
        return None
    reason = ' '.join(str(data.get('strength_reason') or '').split()[:18])
    return {'strength': s, 'reason': reason}


_UNAVAILABLE = ('mock provider', 'not found', 'timed out', 'Unreadable CLI output', 'Unknown LLM_PROVIDER',
                'not reachable', 'Unreadable Ollama output')


def ai_or_fallback(ctx, task, system_prompt, payload, schema, fallback, validate):
    """Ask the AI; validate the reply; on any problem use the template result and remember why.
    A fallback result carries "_fallback": "unavailable" (no AI) or "rejected" (the AI reply failed a check)."""
    try:
        data = llm.generate(system_prompt, payload, schema)
        validate(data)
        ctx.ai_used += 1
        return data
    except llm.LLMError as exc:
        ctx.ai_fallbacks.append(f'{task}: {exc}')
        kind = 'unavailable' if any(m in str(exc) for m in _UNAVAILABLE) else 'rejected'
        return {**fallback, '_fallback': kind}


def ai_status(data):
    """'ok' (AI reply used), 'unavailable' (template wording, no AI) or 'rejected' (AI reply failed a check)."""
    return (data or {}).get('_fallback') or 'ok'
