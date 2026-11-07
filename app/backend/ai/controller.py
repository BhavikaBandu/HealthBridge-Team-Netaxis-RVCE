"""Dopamine-Cortisol controller: decides how much each finding can be trusted and how it is shown.

Dopamine (D, "go") and Cortisol (C, "caution") are engineered control signals computed by code from what the agents
recorded (table cells, checks, code-vs-AI agreement, risk). They are not clinical scores and never come from the AI's
own opinion of itself.

    D = 0.35*E + 0.25*K + 0.20*P + 0.20*V
    C = 0.35*G + 0.25*R + 0.25*X + 0.15*F

E evidence (importance-weighted share of confirmed fields)   G important gaps (share of important fields not confirmed)
K code-vs-AI agreement                                       R risk of the item
P comparison completed (a match exists)                      X contradiction between sources
V AI reply passed every check                                F share of failed checks / rejected quotes

Decision order (hard rules first, scores second):
    1. hard safety failure                                   -> BLOCKED
    2. core field not confirmed, allergy concern, high-risk item with an important gap, code and AI two steps apart
                                                             -> HUMAN_REVIEW
    3. C >= 0.5                                              -> HUMAN_REVIEW
    4. D >= 0.9 and C < 0.15                                 -> VALIDATED_FOR_DISPLAY
    5. otherwise                                             -> DISPLAY_WITH_LIMITATIONS
"""
from sqlalchemy import func, or_, select

from backend.models import ControlledSubstance, Source

VERSION = 'dc-1'
WEIGHTS_D = {'E': 0.35, 'K': 0.25, 'P': 0.20, 'V': 0.20}
WEIGHTS_C = {'G': 0.35, 'R': 0.25, 'X': 0.25, 'F': 0.15}
D_VALIDATED, C_VALIDATED, C_REVIEW = 0.9, 0.15, 0.5
TIER_WEIGHT = {'core': 3.0, 'important': 2.0, 'minor': 0.5}
LABELS = {'VALIDATED_FOR_DISPLAY': 'Validated', 'DISPLAY_WITH_LIMITATIONS': 'Shown with limitations',
          'HUMAN_REVIEW': 'Needs review', 'BLOCKED': 'Blocked'}

# How important each compared field is (rows of the comparison table).
TIERS = {
    'medicine': {'Ingredients': 'core', 'Route': 'important', 'Release': 'important', 'Form': 'minor'},
    'procedure': {'Scan': 'core', 'Body area': 'core', 'Side': 'important', 'Contrast': 'important',
                  'Protocol': 'important'},
}
NOT_CONFIRMED = ('not stated', 'not specified', '—', 'no match found', '')
PARTIAL = ('(general)',)          # e.g. "Joints (general)" for a knee request: half confirmed
CONF_RANK = {'High': 2, 'Medium': 1, 'Low': 0}
AI_RANK = {'Strong': 2, 'Moderate': 1, 'Weak': 0}


def _cell_state(value):
    v = str(value or '').strip().lower()
    if v in NOT_CONFIRMED:
        return 0.0
    if any(p in v for p in PARTIAL):
        return 0.5
    return 1.0


def _agreement(confidence, ai):
    """K: 1 when code and AI agree, 0.5 one step apart, 0 two steps apart; 0.75 when the AI gave no strength."""
    if not ai or confidence not in CONF_RANK or ai.get('strength') not in AI_RANK:
        return 0.75, None
    gap = abs(CONF_RANK[confidence] - AI_RANK[ai['strength']])
    return {0: 1.0, 1: 0.5}.get(gap, 0.0), gap


def _controlled(s, name):
    if not name:
        return False
    key = ''.join(ch if ch.isalnum() or ch == ' ' else ' ' for ch in name.lower()).strip()
    return bool(s.scalar(select(func.count()).select_from(ControlledSubstance)
                         .join(Source, Source.active_version_id == ControlledSubstance.version_pk)
                         .where(or_(ControlledSubstance.name_key == key, ControlledSubstance.name_key.contains(key)))))


def _short(column):
    return column.split(' (')[0]   # "India (referral)" -> "India"


def _table_features(agent, comp):
    """E, G and readable notes from the comparison table:
    core_missing (a core field not confirmed at all -> review), partial (a core field only broadly matched),
    gaps (important fields not stated, grouped by field)."""
    tiers = TIERS[agent]
    cols = comp.get('columns') or ['', '']
    total = missing = imp_total = imp_missing = 0.0
    core_missing, partial, gaps = [], [], {}
    for row in comp.get('rows') or []:
        tier = tiers.get(row[0], 'minor')
        w = TIER_WEIGHT[tier]
        for i, value in enumerate(row[1:3]):
            state = _cell_state(value)
            total += w
            missing += w * (1 - state)
            if tier == 'important':
                imp_total += 1
                imp_missing += 1 - state
            if state < 1:
                if tier == 'core':
                    (partial if state else core_missing).append(f'{_short(cols[i])} {row[0].lower()}')
                elif tier == 'important':
                    gaps.setdefault(row[0].lower(), []).append(_short(cols[i]))
    E = 1 - missing / total if total else 1.0
    G = imp_missing / imp_total if imp_total else 0.0
    gap_text = [f"{field} ({', '.join(where)})" for field, where in gaps.items()]
    return E, G, core_missing, partial, gap_text


def _join(items):
    items = list(dict.fromkeys(items))
    return ', '.join(items[:-1]) + (' and ' if len(items) > 1 else '') + items[-1] if items else ''


def assess(s, f):
    """Assessment dict for one finding (agent output, including its private "_" keys)."""
    agent = f['agent']
    ai = f.get('_ai', 'ok')
    V = 0.0 if ai == 'rejected' else 1.0
    fills = f.get('_fills') or {}
    F = min(1.0, (fills.get('rejected', 0) / fills['offered'] if fills.get('offered') else 0.0) + (1.0 if ai == 'rejected' else 0.0))
    X = 0.0
    reasons, review, blocked = [], [], []

    if agent in ('medicine', 'procedure'):
        comp = f.get('comparison') or {}
        E, G, core_missing, partial, gaps = _table_features(agent, comp)
        K, gap = _agreement(f.get('confidence'), comp.get('ai_match'))
        P = 0.0 if str(f.get('match_label') or '').startswith('No ') else 1.0
        if agent == 'medicine':
            controlled = _controlled(s, f.get('_medicine_name'))
            allergy = (comp.get('allergy') or {}).get('status')
            R = 1.0 if controlled or allergy in ('direct', 'possible') else (0.3 if f.get('_ongoing') else 0.1)
            if allergy in ('direct', 'possible'):
                review.append('possible allergy concern' if allergy == 'possible' else 'same ingredient as a recorded allergy')
            if controlled:
                reasons.append('controlled medicine in the destination')
            if 'different strength' in str(f.get('match_label') or ''):
                reasons.append('strength differs from the destination product')
        else:
            R = 0.5 if f.get('_planned') else 0.2
        if not P:
            review.append(f"no {_short((comp.get('columns') or ['', 'destination'])[1])} match found")
        elif core_missing:
            review.append(f'{_join(core_missing)} not confirmed')
        if R >= 1.0 and G > 0:
            review.append('high-risk item with missing details')
        if gap == 2:
            review.append('code and AI strongly disagree on the match')
        if partial:
            reasons.append(f'{_join(partial)} only matched in general')
        if gaps and P:
            reasons.append(f'not stated: {_join(gaps)}')
        if gap == 1:
            reasons.append(f"code says {f.get('confidence')}, AI says {comp['ai_match']['strength']}")
        if P and not f.get('sources'):
            blocked.append('match shown without a source')
    else:   # report (patient document)
        has_text = f.get('_has_text', True)
        estimates = sum(1 for x in f.get('facts') or [] if x.get('basis') == 'ai')
        labs = sum(1 for x in f.get('facts') or [] if x.get('converted'))
        total = labs * (TIER_WEIGHT['core'] + TIER_WEIGHT['minor'])
        E = 1 - (estimates * TIER_WEIGHT['minor']) / total if total else 1.0
        G = 0.0
        K = f.get('_conversion_agreement', 1.0)
        P = 1.0 if has_text else 0.0
        R = 0.5 if f.get('_flagged') else 0.2
        if not has_text:
            review.append('document text could not be read')
        if K < 1.0:
            reasons.append('a converted value does not match the reviewed rule')
        if estimates:
            reasons.append(f'{estimates} conversion{"s" if estimates > 1 else ""} by AI estimate')
        if f.get('_flagged'):
            reasons.append('a result is flagged by the laboratory')

    feats = {'E': E, 'K': K, 'P': P, 'V': V, 'G': G, 'R': R, 'X': X, 'F': F}
    D = sum(WEIGHTS_D[k] * feats[k] for k in WEIGHTS_D)
    C = sum(WEIGHTS_C[k] * feats[k] for k in WEIGHTS_C)
    if ai == 'rejected':
        reasons.append('AI reply failed a check (template wording used)')

    if blocked:
        disposition, why = 'BLOCKED', blocked
    elif review:
        disposition, why = 'HUMAN_REVIEW', review + reasons
    elif C >= C_REVIEW:
        disposition, why = 'HUMAN_REVIEW', reasons or ['high caution score']
    elif D >= D_VALIDATED and C < C_VALIDATED:
        disposition, why = 'VALIDATED_FOR_DISPLAY', ['key details confirmed'] + [r for r in reasons if 'AI estimate' in r or 'flagged' in r]
    else:
        disposition, why = 'DISPLAY_WITH_LIMITATIONS', reasons or ['some details could not be confirmed']
    reason = '; '.join(dict.fromkeys(why))
    return {'version': VERSION, 'dopamine': round(D, 2), 'cortisol': round(C, 2), 'disposition': disposition,
            'label': LABELS[disposition], 'reason': reason[:1].upper() + reason[1:],
            'features': {k: round(v, 3) for k, v in feats.items()},
            'thresholds': {'validated': [D_VALIDATED, C_VALIDATED], 'review': C_REVIEW}}
