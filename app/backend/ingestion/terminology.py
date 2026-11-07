"""Deterministic normalisation rules shared by ingestion and retrieval.

Every rule here is a reviewed, explicit mapping. Nothing is learned or inferred: a term that is not listed stays
as written (normalised only for case and spacing) and is reported as unresolved by retrieval.
"""
import re

# ---------------------------------------------------------------- medicines
# Spelling variants and pharmacopoeia suffixes for active ingredients. Salt forms are stripped only when the
# label states the strength "as" / "equivalent to" the base (handled in the parser, not here).
INGREDIENT_SYNONYMS = {
    'amoxycillin': 'amoxicillin',
    'amoxicillin': 'amoxicillin',
    'clavulanic acid': 'clavulanic acid',
    'clavulanate': 'clavulanic acid',
    'paracetamol': 'paracetamol',
    'acetaminophen': 'paracetamol',
}
_PHARMACOPOEIA = re.compile(r'\b(i\.?p\.?|b\.?p\.?|u\.?s\.?p\.?|ph\.?\s?eur\.?)(?=\s|$|[,;:])', re.I)
_SALTS = re.compile(r'\b(trihydrate|sodium|potassium|hydrochloride|diluted)\b', re.I)


def normalise_ingredient(text):
    """'Amoxycillin Trihydrate IP' -> 'amoxicillin'; unknown names are returned lower-cased and tidied."""
    t = _PHARMACOPOEIA.sub(' ', text or '')
    t = re.sub(r'[®™*]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip(' .,;:-').lower()
    if t in INGREDIENT_SYNONYMS:
        return INGREDIENT_SYNONYMS[t]
    bare = re.sub(r'\s+', ' ', _SALTS.sub(' ', t)).strip()
    if bare in INGREDIENT_SYNONYMS:
        return INGREDIENT_SYNONYMS[bare]
    if 'clavulan' in t:
        return 'clavulanic acid'
    return bare or t


STRENGTH_UNITS = {'mg': 'mg', 'g': 'g', 'mcg': 'mcg', 'µg': 'mcg', 'ug': 'mcg', 'ml': 'ml', 'iu': 'IU'}


def normalise_strength(value, unit):
    """('1', 'g') -> (1000.0, 'mg'); only exact metric scaling, nothing clinical."""
    v = float(value)
    u = STRENGTH_UNITS.get(unit.lower(), unit)
    if u == 'g':
        return v * 1000, 'mg'
    if u == 'mcg':
        return v / 1000, 'mg'
    return v, u


DOSAGE_FORMS = [  # (pattern, normalised form); first match wins
    (r'film[\s-]*coated tablet', 'tablet'),
    (r'uncoated tablet', 'tablet'),
    (r'\btablets?\b', 'tablet'),
    (r'\bcaplets?\b', 'tablet'),
    (r'\bcapsules?\b', 'capsule'),
    (r'\bsyrup\b', 'syrup'),
    (r'\bsuspension\b', 'suspension'),
    (r'\binjection\b', 'injection'),
]


def normalise_form(text):
    for pattern, form in DOSAGE_FORMS:
        if re.search(pattern, text or '', re.I):
            return form
    return None


# ---------------------------------------------------------------- lab analytes
ANALYTE_SYNONYMS = {
    'glucose': ['glucose', 'fasting glucose', 'glucose fasting', 'glucose (fasting)', 'fasting blood sugar',
                'fasting plasma glucose', 'fbs', 'fpg', 'blood sugar', 'plasma glucose', 'glucose, fasting'],
    'creatinine': ['creatinine'],
    'urea': ['urea'],
    'sodium': ['sodium'],
    'potassium': ['potassium'],
    'chloride': ['chloride'],
    'calcium': ['calcium', 'total calcium', 'calcium, total'],
    'bicarbonate': ['bicarbonate', 'total co2', 'bicarbonate (total co2)'],
    'hba1c': ['hba1c', 'glycosylated hemoglobin', 'glycated haemoglobin'],
    'cholesterol': ['cholesterol', 'total cholesterol', 'cholesterol, total'],
    'triglycerides': ['triglycerides'],
}
_ANALYTE_LOOKUP = {s: a for a, syns in ANALYTE_SYNONYMS.items() for s in syns}


def normalise_analyte(text):
    """Map a test name to a normalised analyte, or None if no reviewed synonym matches."""
    t = re.sub(r'\s+', ' ', (text or '').lower()).strip(' .,:;')
    if t in _ANALYTE_LOOKUP:
        return _ANALYTE_LOOKUP[t]
    # Exact match only, after removing bracketed qualifiers and trailing unit-system/specimen words.
    # ("Glucose (Fasting), SI" -> "glucose"; "Urea Nitrogen Blood" stays unmapped: BUN is not urea.)
    fasting = '(fasting)' in t
    t = re.sub(r'\([^)]*\)', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip(' ,')
    t = re.sub(r'(\s*,?\s*\b(si|serum|plasma)\b)+$', '', t).strip(' ,')
    if fasting and f'fasting {t}' in _ANALYTE_LOOKUP:
        return _ANALYTE_LOOKUP[f'fasting {t}']
    return _ANALYTE_LOOKUP.get(t)


def is_fasting(text):
    return bool(re.search(r'\bfast(ing|ed)\b|\(f\)', text or '', re.I)) or None


# Reviewed analyte-specific conversion rules. UCUM alone cannot convert mass to molar concentration; it needs the
# molar mass of the analyte. Factor for glucose taken from the project specification (Four RAG Retrieval brief, s5).
CONVERSIONS = {
    ('glucose', 'mg/dL', 'mmol/L'): {
        'rule_id': 'glucose-mgdl-to-mmoll-v1', 'divide_by': 18.0182,
        'basis': 'glucose molar mass ~180.16 g/mol; factor 18.0182 as specified in the HealthBridge retrieval brief',
        'reviewed': True},
    ('glucose', 'mmol/L', 'mg/dL'): {
        'rule_id': 'glucose-mmoll-to-mgdl-v1', 'multiply_by': 18.0182,
        'basis': 'inverse of glucose-mgdl-to-mmoll-v1', 'reviewed': True},
}


def convert(analyte, value, from_unit, to_unit):
    """Deterministic analyte-specific conversion, or None if no reviewed rule exists."""
    rule = CONVERSIONS.get((analyte, from_unit, to_unit))
    if not rule:
        return None
    v = float(value)
    result = v / rule['divide_by'] if 'divide_by' in rule else v * rule['multiply_by']
    return {'value': round(result, 2), 'unit': to_unit, 'rule_id': rule['rule_id'], 'basis': rule['basis'],
            'reviewed': rule['reviewed'], 'approximate': True}


UNIT_SYSTEMS = {'mg/dl': 'conventional', 'mmol/l': 'SI', 'g/dl': 'conventional', 'u/l': 'enzyme activity',
                'pg/ml': 'conventional', 'ng/ml': 'conventional', '%': 'percent'}

# ---------------------------------------------------------------- procedures
MODALITIES = [  # (pattern, modality)
    (r'\bmagnetic resonance angiograph|\bMRA\b', 'MRA'),
    (r'\bMRI\b|\bmagnetic resonance\b|\bMR\b(?=\s)', 'MRI'),
    (r'\bCT\b|\bcomputed tomography\b|\bCAT scan\b', 'CT'),
    (r'\bx[\s-]?ray\b|\bradiograph', 'X-ray'),
    (r'\bultrasound\b|\bsonograph|\bdoppler\b', 'ultrasound'),
    (r'\bmammogra', 'mammography'),
    (r'\bPET\b', 'PET'),
]
ANATOMY_TERMS = ['knee', 'joints', 'joint', 'brain', 'spine', 'liver', 'biliary tree', 'pelvic organs', 'breast',
                 'heart', 'coronary arteries', 'blood vessels', 'abdomen', 'kidney', 'shoulder', 'hip', 'wrist',
                 'elbow', 'ankle', 'soft tissue', 'ligament', 'cartilage']
# A term that implies a broader one. Used only to *explain* a partial match (knee is a joint), never to claim
# that a general "joints" service covers a specific knee protocol.
ANATOMY_PARENTS = {'knee': 'joints', 'shoulder': 'joints', 'hip': 'joints', 'wrist': 'joints', 'elbow': 'joints',
                   'ankle': 'joints', 'joint': 'joints'}


def modalities_in(text):
    found = []
    for pattern, modality in MODALITIES:
        if re.search(pattern, text or '', re.I) and modality not in found:
            found.append(modality)
    return found


def anatomy_in(text):
    found = []
    for term in ANATOMY_TERMS:
        if re.search(rf'\b{re.escape(term)}s?\b', text or '', re.I):
            norm = 'joints' if term == 'joint' else term
            if norm not in found:
                found.append(norm)
    return found


def laterality_in(text):
    """Laterality only when the text states it."""
    t = text or ''
    if re.search(r'\bsingle\s*\(\s*R\s*/\s*L\s*\)|\beither left/right\b|\bleft/right\b|\bleft or right\b', t, re.I):
        return 'single (left or right)'
    if re.search(r'\bboth\b.*\b(knees?|sides?)\b|\bbilateral\b|–\s*Both\b', t, re.I):
        return 'both'
    if re.search(r'\bright\b', t, re.I) and not re.search(r'\bleft\b', t, re.I):
        return 'right'
    if re.search(r'\bleft\b', t, re.I) and not re.search(r'\bright\b', t, re.I):
        return 'left'
    return None


def contrast_statement(text):
    """The sentence that mentions contrast, as written, or None."""
    for sentence in re.split(r'(?<=[.!?])\s+|\n', text or ''):
        if re.search(r'\bcontrast (dye|media|medium|agent)|\bgadolinium\b|\bcontrast\b', sentence, re.I) \
                and not re.search(r'superior contrast between soft tissues', sentence, re.I):
            return sentence.strip()
    return None


# ---------------------------------------------------------------- policy
POLICY_ACTIONS = {  # action -> patterns (any)
    'traveller_medicine_import': [r'travell?ers?\b.*\bmedic', r'medic\w*\b.*\btravell?ers?', r'passengers?\b.*\bmedic',
                                  r'personal use', r'bring in (narcotics|medication)', r'accompanying medical products'],
    'controlled_medicine': [r'\bcontrolled\b', r'\bnarcotic', r'\bpsychotropic', r'semi-controlled'],
    'import_permit': [r'\bpermit\b', r'\bprior approval\b', r'\bapproval\b.*\bimport', r'\bimport\b.*\bapproval'],
    'prescription_requirement': [r'\bprescription\b', r'medical report'],
    'customs_declaration': [r'\bcustoms\b', r'\bdeclare\b', r'\bconfiscat'],
}
MEDICINE_CLASSES = {
    'narcotic': r'\bnarcotic',
    'psychotropic': r'\bpsychotropic',
    'controlled': r'\bcontrolled\b',
    'semi_controlled': r'semi-controlled',
    'neuropathic_psychiatric': r'neuropathic|psychiatric',
}


def policy_actions(text):
    return [a for a, pats in POLICY_ACTIONS.items() if any(re.search(p, text or '', re.I | re.S) for p in pats)]


def medicine_classes(text):
    return [c for c, p in MEDICINE_CLASSES.items() if re.search(p, text or '', re.I)]


def policy_facets(text):
    """Rule facets stated in a clause, each with the exact phrase that supports it."""
    t = text or ''
    facets = {}

    def phrase(m):
        p = m.group(0)
        if m.start() > 0 and t[m.start() - 1].isalnum():   # window began mid-word: drop the partial word
            p = re.sub(r'^\S*\s+', '', p)
        if m.end() < len(t) and t[m.end()].isalnum():
            p = re.sub(r'\s+\S*$', '', p)
        return re.sub(r'\s+', ' ', p).strip()

    for m in re.finditer(r'(no more than|maximum( period)? of|not exceed[^.]{0,60}?|maximum)\s+(\(3\)\s*)?(three|3)[\s-]+months?', t, re.I):
        sentence_start = max(t.rfind('.', 0, m.start()), t.rfind('\n', 0, m.start())) + 1
        sentence = t[sentence_start: m.end() + 80]
        if re.search(r'quantit|supply|need|medic|personal use', sentence, re.I):   # a medicine-supply limit, not a penalty
            facets['max_supply'] = {'value': '3 months', 'days': 90, 'phrase': phrase(m)}
            break
    m = re.search(r'[^.]{0,200}Executive Regulations[^.]{0,40}specify[^.]{0,200}', t, re.I)
    if m:
        facets['delegated_rules'] = {'value': 'conditions delegated to the Executive Regulations (not in this source)',
                                     'phrase': phrase(m)}
    m = re.search(r'[^.]{0,80}\boptional\b[^.]{0,120}', t, re.I)
    if m and re.search(r'approv|permit|service', m.group(0), re.I):
        facets['prior_approval'] = {'value': 'optional', 'phrase': phrase(m)}
    m = re.search(r'[^.]{0,60}\bmust (have|obtain) (a )?prior approval[^.]{0,80}', t, re.I)
    if m:
        facets['prior_approval'] = {'value': 'required', 'phrase': phrase(m)}
    m = re.search(r'[^.]{0,80}authenticated by the UAE embass\w*[^.]{0,40}', t, re.I)
    if m:
        facets['document_authentication'] = {'value': 'UAE embassy abroad', 'phrase': phrase(m)}
    m = re.search(r'[^.]{0,80}authenticated by the health authority[^.]{0,80}', t, re.I)
    if m:
        facets['document_authentication'] = {'value': 'treating health authority', 'phrase': phrase(m)}
    m = re.search(r'[^.]{0,120}without the authori[sz]ation of the Ministry of Health[^.]{0,80}', t, re.I)
    if m:
        facets['ministry_authorisation'] = {'value': 'required for neuropathic/psychiatric medicines', 'phrase': phrase(m)}
    m = re.search(r'[^.]{0,40}(original )?(signed )?prescription[^.]{0,160}', t, re.I)
    if m:
        facets['prescription'] = {'value': 'stated', 'phrase': phrase(m)}
    return facets
