"""Parsers for the HealthBridge demo evidence sources (medicine labels, lab references, procedure pages, policy).

Each parser yields KnowledgeRecord dicts (see pipeline.py). Records are passages with an exact location; records
that state structured facts carry them in metadata['facts'] = {table: [rows]}, which the pipeline materialises
into the domain tables (med_products, lab_test_refs, procedure_terms, policy_clauses, controlled_substances).

Parsing is deterministic. Facts are only produced from text the source states; anything not stated stays empty.
`profile` (from the registry) gives source-level context (country, provider, publisher) and structural hints such
as where the main content starts; it never contains expected answers.
"""
import re

from . import terminology as T
from .documents import (MAX_PASSAGE_CHARS, clean, find_start, html_blocks, html_sections, load_sidecar, pdf_pages,
                        read_json, split_passages)
from .safety import SourceFileError

PARSER_VERSION = '1.0'


def _record(profile, ext, kind, title, content, location, facts=None, extra=None):
    loc_label = location.get('label') or ''
    meta = {'source_id': profile['source_id'], 'country': profile['country'], 'location': location,
            'location_label': loc_label, 'publisher': profile.get('publisher')}
    if facts:
        meta['facts'] = facts
    if extra:
        meta.update(extra)
    link = profile.get('url')
    if link and location.get('page') and link.lower().split('?')[0].endswith('.pdf'):
        link = f"{link}#page={location['page']}"
    return {'external_id': f"{profile['source_id']}:{ext}", 'kind': kind, 'title': title[:500],
            'content': content, 'language': profile.get('language', 'en'), 'source_link': link, 'metadata': meta,
            '_valid': bool(content and content.strip()), '_problem': None if content else 'empty passage'}


def _page_passages(profile, pages, kind):
    for page, text in pages:
        for i, chunk in enumerate(split_passages(text)):
            yield _record(profile, f'p{page}:{i + 1}', kind, f"{profile['title']} — page {page}" + (f' (part {i + 1})' if i else ''),
                          chunk, {'page': page, 'part': i + 1, 'label': f'page {page}'})


def _section_passages(profile, sections, kind, facts_for=None):
    for s_idx, s in enumerate(sections):
        heading = ' > '.join(s['path']) if s['path'] else (s['heading'] or 'Introduction')
        body = s['text']
        if not body.strip():
            continue
        for i, chunk in enumerate(split_passages(body)):
            loc = {'section': s['path'] or [s['heading'] or 'Introduction'], 'block': s['block_index'], 'part': i + 1,
                   'label': f'section "{heading}"' + (f' part {i + 1}' if i else '')}
            facts = facts_for(s, chunk) if facts_for else None
            yield _record(profile, f's{s_idx + 1}:{i + 1}', kind, f"{profile['title']} — {heading}", chunk, loc, facts)


# =============================================================================================== medicines
_ING_PATTERNS = [
    # "Amoxycillin Trihydrate IP equivalent to Amoxycillin 875 mg"
    re.compile(r'(?P<written>[A-Z][A-Za-z ]{2,60}?)\s+(?:I\.?P\.?|B\.?P\.?)?\s*equivalent to\s+(?P<ing>[A-Za-z][A-Za-z ]{2,40}?)'
               r'\s+(?P<v>\d+(?:\.\d+)?)\s*(?P<u>mg|g|mcg)\b'),
    # "contains Paracetamol I.P. 500 mg"
    re.compile(r'contains?\s+(?P<ing>[A-Za-z][A-Za-z ]{2,40}?)\s+(?:I\.?P\.?|B\.?P\.?)?\s*(?P<v>\d+(?:\.\d+)?)\s*(?P<u>mg|g|mcg)\b'),
    # "paracetamol (500mg)", "amoxicillin trihydrate(875 mg)"
    re.compile(r'(?P<ing>(?:[A-Za-z]+\s+){0,3}[A-Za-z]+)\s*\(\s*(?P<v>\d+(?:\.\d+)?)\s*(?P<u>mg|g|mcg)\s*\)'),
]
_LEAD = re.compile(r'^.*\b(contains?|and|of|with)\s+', re.I)


def _ingredients(segment):
    found, taken = [], []
    for pattern in _ING_PATTERNS:
        for m in pattern.finditer(segment):
            if any(m.start() < e and m.end() > s for s, e in taken):
                continue
            ing_text = _LEAD.sub('', m.group('ing')).strip()
            norm = T.normalise_ingredient(ing_text)
            if not norm or any(f['ingredient'] == norm for f in found):
                continue
            value, unit = T.normalise_strength(m.group('v'), m.group('u'))
            written = (m.groupdict().get('written') or '').strip()
            found.append({'ingredient': norm, 'as_written': f'{written} equivalent to {ing_text}' if written else ing_text,
                          'strength_value': value, 'strength_unit': unit,
                          'evidence_text': re.sub(r'\s+', ' ', m.group(0)).strip()})
            taken.append((m.start(), m.end()))
    return found


def _first(pattern, text, group=1, flags=re.I):
    m = re.search(pattern, text or '', flags)
    return clean(m.group(group)) if m else None


def parse_medicine_label(path, profile):
    """Medicine label / product page -> page or section passages + one product record per product described."""
    if path.suffix.lower() == '.pdf':
        pages = pdf_pages(path)
        units = [(f'page {p}', {'page': p, 'label': f'page {p}'}, t) for p, t in pages]
        yield from _page_passages(profile, pages, 'label_passage')
    else:
        sections = html_sections(path, profile.get('start'), profile.get('stop'))
        units = [(s['heading'] or 'Introduction', {'section': s['path'], 'block': s['block_index'],
                                                    'label': f'section "{s["heading"] or "Introduction"}"'}, s['text'])
                 for s in sections]
        units = [(h, loc, (h + '\n' + t) if h else t) for h, loc, t in units]
        yield from _section_passages(profile, sections, 'label_passage')
    full = '\n'.join(t for _, _, t in units)

    # Composition block: from the composition heading to the next heading named in the profile.
    comp_re = re.compile(profile['composition_start'], re.I | re.M)
    m = None
    comp_loc = None
    for _, loc, t in units:
        m = comp_re.search(t)
        if m:
            comp_loc, unit_text = loc, t
            break
    if not m:
        raise SourceFileError(f"{profile['source_id']}: composition section not found")
    comp = unit_text[m.start():]
    end = re.search(profile['composition_end'], comp[len(m.group(0)):], re.I | re.M) if profile.get('composition_end') else None
    if end:
        comp = comp[:len(m.group(0)) + end.start()]

    # Products: split on product headings when a label describes several strengths.
    segments = [(profile.get('product_name') or profile['brand'], comp)]
    if profile.get('product_heading'):
        heads = list(re.finditer(profile['product_heading'], comp, re.M))
        if heads:
            segments = [(clean(h.group(0)), comp[h.start(): heads[i + 1].start() if i + 1 < len(heads) else len(comp)])
                        for i, h in enumerate(heads)]

    generic = _first(profile['generic_regex'], full) if profile.get('generic_regex') else None
    form_text = _first(r'(film[\s-]*coated tablets?|uncoated tablets?|oral tablets?|\btablets?\b|capsules?|caplets?)', comp) \
        or (_first(profile['form_regex'], full) if profile.get('form_regex') else None)
    route = 'oral' if re.search(r'\boral\b', full, re.I) else None
    route_evidence = _first(r'([^\n]{0,60}\boral\b[^\n]{0,60})', full) if route else None
    release = _first(r'\b((?:fast|immediate|modified|extended|sustained|prolonged)[ -]release)\b', full)
    manufacturer = _first(r'(?:manufactured|marketed)\s+by\s*:?\s*([^\n]{3,120})', full)

    for idx, (name, segment) in enumerate(segments):
        ings = _ingredients(segment)
        if not ings:
            continue
        evidence = clean(segment)
        product = {'country': profile['country'], 'brand': profile['brand'], 'product_name': name,
                   'generic_name': generic, 'dosage_form': T.normalise_form(form_text) if form_text else None,
                   'form_detail': form_text, 'route': route, 'release_profile': release, 'manufacturer': manufacturer,
                   'ingredients': ings,
                   'not_stated': [f for f, v in (('dosage form', form_text), ('route', route), ('manufacturer', manufacturer)) if not v],
                   'route_evidence': route_evidence}
        strengths = ' + '.join(f"{i['ingredient']} {i['strength_value']:g} {i['strength_unit']}" for i in ings)
        content = f"{name}: {strengths}.\nAs written: {evidence}"
        yield _record(profile, f'product:{idx + 1}', 'medicine_product', f"{name} ({profile['country']}) — {strengths}",
                      content, {**comp_loc, 'label': comp_loc['label'] + ' (composition)'},
                      facts={'med_products': [product]})


# =============================================================================================== lab references
_NRL_LABELS = ['Order Code', 'CPT', 'Synonyms', 'TAT', 'Methodology', 'Reference Interval', 'Remarks',
               'Performing Location', 'Testing Frequency', 'Test Overview', 'Specimen Type', 'Volume',
               'Specimen Container', 'Patient Preparation', 'Collection', 'Specimen Stability']
_NRL_SKIP = {'Test Details', 'Sample Requirements', 'Temperature', 'Period'}


def parse_lab_test_page(path, profile):
    """Lab test catalogue page (label/value layout) -> one test record (+ per-analyte facts for panels)."""
    blocks = html_blocks(path)
    start = next((i for i, (lvl, _) in enumerate(blocks) if lvl == 1), None)
    if start is None:
        raise SourceFileError('Test name heading (h1) not found')
    stop = next((i for i, (_, t) in enumerate(blocks) if i > start and t.startswith('©')), len(blocks))
    test_name = blocks[start][1]
    fields, current, stability = {}, None, []
    for _, text in blocks[start + 1: stop]:
        if text in _NRL_SKIP:
            continue
        if text in _NRL_LABELS:
            current = text
            continue
        if current == 'Specimen Stability':
            stability.append(text)
        elif current and current not in fields:
            fields[current] = text
    if stability:
        fields['Specimen Stability'] = '; '.join(f'{a}: {b}' for a, b in zip(stability[::2], stability[1::2]))
    lines = [test_name] + [f'{k}: {v}' for k, v in fields.items()]
    content = '\n'.join(lines)

    ref = fields.get('Reference Interval', '')
    rm = re.match(r'\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(\S+)', ref)
    remarks = fields.get('Remarks', '')
    system = 'SI' if re.search(r'\bSI\b', test_name + ' ' + remarks) else \
        'conventional' if re.search(r'conventional', test_name + ' ' + remarks, re.I) else None
    synonyms = [s.strip() for s in fields.get('Synonyms', '').split(',') if s.strip()]
    codes = {k: fields[k] for k in ('Order Code', 'CPT') if k in fields}
    base = {'country': profile['country'], 'specimen': fields.get('Specimen Type'), 'unit_system': system,
            'method': fields.get('Methodology'), 'codes': codes, 'panel': None, 'entry_type': 'reference_test'}
    rows = []
    components = re.search(r'Panel includes:\s*(.+?)\.?$', remarks) or re.search(r'Test Includes:\s*(.+?)\.?$', remarks)
    if components:   # panel: one fact row per component analyte; units are not stated per analyte
        for comp in [c.strip() for c in re.split(r',\s*(?![^()]*\))', components.group(1)) if c.strip()]:
            rows.append({**base, 'test_name': comp, 'analyte': T.normalise_analyte(comp), 'synonyms': [],
                         'fasting': T.is_fasting(comp), 'unit': None, 'ref_low': None, 'ref_high': None,
                         'ref_text': None, 'panel': test_name})
    else:
        fasting = T.is_fasting(test_name + ' ' + fields.get('Patient Preparation', '') + ' ' + ' '.join(synonyms))
        rows.append({**base, 'test_name': test_name, 'analyte': T.normalise_analyte(test_name), 'synonyms': synonyms,
                     'fasting': fasting, 'unit': rm.group(3) if rm else None,
                     'ref_low': float(rm.group(1)) if rm else None, 'ref_high': float(rm.group(2)) if rm else None,
                     'ref_text': ref or None})
    yield _record(profile, 'test', 'lab_test_reference', f"{test_name} — {profile['publisher']}", content,
                  {'section': [test_name], 'label': 'test details'}, facts={'lab_test_refs': rows})


_OBS_LINE = re.compile(r'^(?P<val>[<>]?\d+(?:\.\d+)?|[A-Z]\d)(?P<name>[A-Za-z(][^\n]*)$')
_METHOD_LINE = re.compile(r'^\((?P<method>[^)]*)\)$')
_REF_LINE = re.compile(r'^\s*(?P<ref>(?:[<>≥≤]\s*)?\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)?\s*(?P<unit>[A-Za-z%µ/][\w%µ/.^]*)?\s*$')
_PANEL_LINE = re.compile(r"^[A-Z][A-Z0-9 ,&/()'\-;.]{3,}$")


def parse_lab_sample_report(path, profile):
    """Sample lab report PDF -> page passages + one record per printed observation (kept separate from references)."""
    pages = pdf_pages(path)
    yield from _page_passages(profile, pages, 'report_passage')
    first = pages[0][1]
    dates = re.findall(r'\b(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}:\d{2}\s*[AP]M)', first)
    header = {'sample_report': True, 'patient_label': _first(r'(Mr\.?\s+DUMMY|DUMMY)', first),
              'dates_as_printed': [' '.join(d) for d in dates], 'lab': _first(r'(LPL-[A-Z ()-]+LAB\)?)', first)}
    n = 0
    for page, text in pages:
        lines = [ln.strip() for ln in text.split('\n')]
        panel = None
        for i, line in enumerate(lines):
            if _PANEL_LINE.match(line) and not _OBS_LINE.match(line):
                panel = line
                continue
            m = _OBS_LINE.match(line)
            if not m or i + 2 >= len(lines):
                continue
            mm = _METHOD_LINE.match(lines[i + 1])
            rm = _REF_LINE.match(lines[i + 2]) if mm else None
            if not (mm and rm):
                continue
            n += 1
            name = clean(m.group('name'))
            ref = (rm.group('ref') or '').strip() or None
            unit = rm.group('unit')
            lo = hi = None
            if ref and '-' in ref and not ref.startswith(('<', '>')):
                lo, hi = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', ref)[:2]]
            specimen = _first(r',\s*(SERUM|PLASMA|BLOOD|URINE|WHOLE BLOOD)\b', panel or '')
            evidence = '\n'.join(lines[i: i + 3])
            row = {'country': profile['country'], 'entry_type': 'sample_observation', 'test_name': name,
                   'analyte': T.normalise_analyte(name), 'synonyms': [], 'specimen': specimen.lower() if specimen else None,
                   'fasting': T.is_fasting(f'{panel or ""} {name}'), 'unit': unit,
                   'unit_system': T.UNIT_SYSTEMS.get((unit or '').lower()), 'ref_low': lo, 'ref_high': hi,
                   'ref_text': f'{ref} {unit}' if ref and unit else ref, 'method': mm.group('method'),
                   'observed_value': m.group('val'), 'panel': panel, 'codes': {}}
            content = (f"{name}: {m.group('val')} {unit or ''} (reference {row['ref_text'] or 'not printed'}; "
                       f"method {mm.group('method')}; panel {panel or 'not printed'}).\nAs printed: {evidence}\n"
                       'Sample report observation (dummy patient), not a patient record.')
            yield _record(profile, f'obs:{n}', 'lab_report_observation', f'{name} — sample report (page {page})',
                          content, {'page': page, 'line': i + 1, 'label': f'page {page}, line {i + 1}'},
                          facts={'lab_test_refs': [row]}, extra={'report_header': header})


# =============================================================================================== procedures
_TITLE_BLOCK = re.compile(r"^[A-Z0-9][A-Z0-9 /()&'+.-]{1,40}$")


def _procedure_facts(profile, term, text, provider):
    mods = T.modalities_in(term) or T.modalities_in(text)
    if not mods:
        return None
    rows = []
    for mod in mods[:1]:   # the first (most specific) modality named
        rows.append({'country': profile['country'], 'provider': provider, 'term': term, 'modality': mod,
                     'anatomy': T.anatomy_in(f'{term}\n{text}'), 'laterality': T.laterality_in(f'{term}\n{text}'),
                     'contrast': T.contrast_statement(text), 'protocol': None,
                     'evidence_text': re.sub(r'\s+', ' ', f'{term}: {text}').strip()[:2000]})
    return {'procedure_terms': rows}


def parse_procedure_page(path, profile):
    """Provider radiology / service page. Sub-services are title-like lines inside the main content."""
    blocks = html_blocks(path)
    start = find_start(blocks, profile['start'])
    stop = next((i for i, (_, t) in enumerate(blocks) if i > start and profile['stop'] in t), len(blocks))
    sections, current = [], {'term': 'Overview', 'lines': [], 'block': start}
    for i in range(start + 1, stop):
        text = blocks[i][1]
        if _TITLE_BLOCK.match(text) and not text.startswith('•'):
            sections.append(current)
            current = {'term': text, 'lines': [], 'block': i}
        else:
            current['lines'].append(text)
    sections.append(current)
    provider = profile.get('provider')
    for n, s in enumerate(sections):
        body = '\n'.join(s['lines']).strip()
        if not body:
            continue
        for k, chunk in enumerate(split_passages(body)):
            facts = _procedure_facts(profile, s['term'], chunk, provider) if s['term'] != 'Overview' else None
            yield _record(profile, f's{n + 1}:{k + 1}', 'procedure_service', f"{s['term']} — {provider}",
                          f"{s['term']}\n{chunk}", {'section': [blocks[start][1], s['term']], 'block': s['block'],
                                                    'label': f'section "{s["term"]}"'}, facts)


def parse_procedure_text(path, profile):
    """Captured page text (manual capture). Sections start at heading-like lines; package items become terms."""
    text = path.read_text(encoding='utf-8')
    lines = [ln.rstrip() for ln in text.split('\n')]
    heading_re = re.compile(profile['heading_regex'], re.M)
    sections, current = [], {'heading': 'Introduction', 'lines': [], 'line': 1}
    for i, line in enumerate(lines):
        if heading_re.match(line):
            sections.append(current)
            current = {'heading': line.strip(), 'lines': [], 'line': i + 1}
        elif line.strip():
            current['lines'].append(line.strip())
    sections.append(current)
    provider = profile.get('provider')
    for n, s in enumerate(sections):
        body = '\n'.join(s['lines'])
        if not body:
            continue
        for k, chunk in enumerate(split_passages(body)):
            rows = []
            if profile.get('item_terms'):   # package pages: each listed item naming a modality is one term
                if s['heading'] != 'Introduction':   # the intro paragraph mixes several items; kept as passage only
                    for ln in chunk.split('\n'):
                        f = _procedure_facts(profile, ln, ln, provider) if T.modalities_in(ln) else None
                        if f:
                            rows += f['procedure_terms']
            else:
                f = _procedure_facts(profile, profile.get('term') or s['heading'], chunk, provider)
                if f and (f['procedure_terms'][0]['anatomy'] or f['procedure_terms'][0]['contrast']):
                    rows += f['procedure_terms']
            yield _record(profile, f's{n + 1}:{k + 1}', 'procedure_service', f"{profile['title']} — {s['heading']}",
                          f"{s['heading']}\n{chunk}", {'section': [s['heading']], 'line': s['line'],
                                                       'label': f'section "{s["heading"]}" (line {s["line"]})'},
                          {'procedure_terms': rows} if rows else None)


# =============================================================================================== policy
def _clause_facts(profile, hierarchy, clause_ref, text, status_note=None):
    actions = T.policy_actions(text)
    facets = T.policy_facets(text)
    if 'traveller_medicine_import' not in actions:   # generic prescription wording is only a facet for traveller rules
        facets.pop('prescription', None)
    return {'policy_clauses': [{
        'jurisdiction': profile['jurisdiction'], 'authority': profile.get('authority'),
        'document_title': profile['title'], 'document_type': profile.get('document_type'),
        'hierarchy': hierarchy, 'clause_ref': clause_ref, 'actions': actions,
        'medicine_classes': T.medicine_classes(text), 'facets': facets,
        'date_text': profile.get('date_text'), 'status_note': status_note or profile.get('status_note')}]}


def parse_policy_page(path, profile):
    """Regulator / government page. Clause = paragraph (FAQ: question + answer) under its section heading."""
    blocks = html_blocks(path)
    start = find_start(blocks, profile['start'])
    stop = next((i for i, (_, t) in enumerate(blocks) if i > start and profile['stop'] in t), len(blocks)) \
        if profile.get('stop') else len(blocks)
    root = blocks[start][1]
    section, clauses = [root], []
    for i in range(start + 1, stop):
        level, text = blocks[i]
        # Sub-section titles: real headings, or (on pages that style them as plain text) short unpunctuated lines.
        is_title = level in (2, 3, 4) or bool(profile.get('title_blocks') and len(text) < 45
                                              and not text.endswith(('.', ':', '?')) and '\n' not in text)
        if is_title:
            section = [root, text]
            continue
        if len(text) < profile.get('min_clause_chars', 25) or text in profile.get('ignore', [])                 or (profile.get('ignore_regex') and re.search(profile['ignore_regex'], text)):
            continue
        clauses.append({'section': list(section), 'text': text, 'block': i})
    if profile.get('faq_section'):      # pair question + answer inside the FAQ section
        merged, pending = [], None
        for c in clauses:
            if c['section'][-1] == profile['faq_section']:
                if pending is None:
                    pending = c
                    continue
                pending = {**pending, 'text': f"Q: {pending['text']}\nA: {c['text']}"}
                merged.append(pending)
                pending = None
            else:
                merged.append(c)
        if pending:
            merged.append(pending)
        clauses = merged
    counters = {}
    for c in clauses:
        key = ' > '.join(c['section'])
        counters[key] = counters.get(key, 0) + 1
        ref = f"{c['section'][-1]} ¶{counters[key]}"
        yield _record(profile, f"b{c['block']}", 'policy_clause', f"{profile['title']} — {c['section'][-1]}",
                      c['text'], {'section': c['section'], 'block': c['block'], 'paragraph': counters[key],
                                  'label': f'section "{c["section"][-1]}", paragraph {counters[key]}'},
                      _clause_facts(profile, c['section'], ref, c['text']))


def parse_policy_law_json(path, profile):
    """Legislation payload (Part > Article > paragraphs). Long articles are split into clause groups."""
    data = read_json(path)
    html_data = data.get('html_data') or ''
    if not html_data:
        raise SourceFileError('No html_data in legislation payload')
    part = None
    pieces = re.split(r'(<h3[^>]*>.*?</h3>|<div class="content_"\s+id="item\d+")', html_data, flags=re.S)
    current_item = None
    for piece in pieces:
        if not piece:
            continue
        h3 = re.match(r'<h3[^>]*>(.*?)</h3>', piece, re.S)
        if h3:
            part = clean(re.sub('<[^>]+>', ' ', h3.group(1)))
            continue
        item = re.match(r'<div class="content_"\s+id="(item\d+)"', piece)
        if item:
            current_item = item.group(1)
            continue
        h4 = re.search(r'<h4>(.*?)</h4>', piece, re.S)
        if not h4 or not current_item:
            continue
        article = clean(re.sub('<[^>]+>', ' ', h4.group(1)))
        body_html = piece[h4.end():]
        body_html = re.sub(r'<br\s*/?>|</p>|</li>', '\n', body_html)
        paragraphs = [clean(re.sub('<[^>]+>', ' ', p)) for p in body_html.split('\n')]
        paragraphs = [p for p in paragraphs if p]
        groups, cur, start_idx = [], [], 1
        for idx, p in enumerate(paragraphs, 1):
            if cur and sum(len(x) for x in cur) + len(p) > MAX_PASSAGE_CHARS:
                groups.append((start_idx, idx - 1, cur))
                cur, start_idx = [], idx
            cur.append(p)
        if cur:
            groups.append((start_idx, len(paragraphs), cur))
        art_no = _first(r'Article \((\d+)\)', article)
        for a, b, paras in groups:
            text = '\n'.join(paras)
            ref = f"Article ({art_no})" + (f' ¶{a}' if a == b else f' ¶{a}-{b}') if art_no else article
            loc = {'part': part, 'article': article, 'anchor': current_item, 'paragraphs': f'{a}-{b}',
                   'label': f'{part} > {article}, paragraphs {a}-{b}'}
            ext = f"{current_item}:{a}"
            yield _record(profile, ext, 'law_clause', f"{profile['short_title']} — {article}" + (f' (¶{a}-{b})' if len(groups) > 1 else ''),
                          text, loc, _clause_facts(profile, [part, article], ref, text))


def parse_controlled_list(path, profile):
    """Controlled-medicine list PDF -> intro/notes clauses + one record per listed substance."""
    pages = pdf_pages(path)
    header_re = re.compile(profile['repeated_header'], re.S)
    rows, notes, intro = [], [], None
    for page, text in pages:
        hm = header_re.search(text)
        if hm and intro is None:
            intro = (page, clean(hm.group(0)))
        body = header_re.sub('\n', text)
        body = re.sub(r'^\s*\d+/\d+\s*$', '', body, flags=re.M)
        lines = [ln.strip() for ln in body.split('\n') if ln.strip()]
        i = 0
        while i < len(lines):
            expected = (rows[-1]['list_number'] + 1) if rows else 1
            if lines[i] == str(expected) and i + 2 < len(lines):
                name, category = lines[i + 1], lines[i + 2]
                j = i + 3
                rule = []
                while j < len(lines) and lines[j] != str(expected + 1):
                    rule.append(lines[j])
                    j += 1
                rule_text = ' '.join(rule)
                note = None
                nm = re.search(r'(The list is intended.*)$', rule_text)
                if nm:
                    note, rule_text = nm.group(1), rule_text[:nm.start()].strip()
                    notes.append((page, note))
                rows.append({'list_number': expected, 'generic_name': name, 'category': category,
                             'carry_rule': rule_text or None, 'page': page})
                i = j
            else:
                i += 1
    if not rows:
        raise SourceFileError('No list rows parsed')
    if intro:
        page, text = intro
        yield _record(profile, 'intro', 'policy_clause', f"{profile['title']} — scope and update date", text,
                      {'page': page, 'label': f'page {page}, list header'},
                      _clause_facts(profile, [profile['title'], 'List header'], 'List header', text))
    for k, (page, note) in enumerate(notes):
        yield _record(profile, f'note{k + 1}', 'policy_clause', f"{profile['title']} — coverage note", note,
                      {'page': page, 'label': f'page {page}, note after last row'},
                      _clause_facts(profile, [profile['title'], 'Coverage note'], 'Coverage note', note))
    for r in rows:
        prohibited = bool(re.search(r'\bprohibited\b', r['carry_rule'] or '', re.I))
        content = (f"{r['list_number']}. {r['generic_name']} — {r['category']}. "
                   f"Allowed quantity & documents: {r['carry_rule'] or 'not printed'}")
        fact = {'jurisdiction': profile['jurisdiction'], 'list_number': r['list_number'],
                'generic_name': r['generic_name'],
                'name_key': re.sub(r'[^a-z0-9 ]+', ' ', r['generic_name'].lower()).strip(),
                'category': r['category'], 'carry_rule': r['carry_rule'], 'prohibited': prohibited}
        yield _record(profile, f"row{r['list_number']}", 'controlled_list_entry',
                      f"{r['generic_name']} — {r['category']}", content,
                      {'page': r['page'], 'row': r['list_number'], 'label': f"page {r['page']}, row {r['list_number']}"},
                      {'controlled_substances': [fact]})


def make_parser(func, profile):
    """Bind a profile; also copies acquisition metadata (URL, retrieval date) from the sidecar when present."""
    def parser(path):
        side = load_sidecar(path)
        prof = dict(profile)
        prof.setdefault('url', side.get('final_url') or side.get('url'))
        yield from func(path, prof)
    parser.__name__ = func.__name__
    return parser
