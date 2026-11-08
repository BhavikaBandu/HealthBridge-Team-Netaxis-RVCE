// Doctor > Patient Records. Only patients who accepted this doctor's request are reachable (enforced by the API).
// Picking a patient opens it in the side panel (doctor_nav.js); its sections are switched from there.
(() => {
let patients = [];
let current = null;      // selected patient code
let tab = 'medications';
let declaration = 'unknown';
let pickerIndex = -1;
const HISTORY = ['medications', 'conditions', 'procedures', 'allergies'];
let docTypes = {};
const PAGE_TITLE = $('#pageTitle').textContent;
const PAGE_SUB = $('#pageSub').textContent;
const base = () => `/api/doctor/patients/${encodeURIComponent(current)}`;

// ---------- patient picker (combobox) ----------
function filtered() {
  const q = $('#patientSearch').value.trim().toLowerCase();
  return patients.filter(p => !q || p.full_name.toLowerCase().includes(q) || p.patient_id.toLowerCase().includes(q));
}

function renderPicker(open = true) {
  const list = $('#pickerList');
  const items = filtered();
  list.replaceChildren(...(items.length ? items.map((p, i) => h('button', {
      type: 'button', role: 'option', class: `picker-item ${i === pickerIndex ? 'active' : ''}`, 'aria-selected': String(i === pickerIndex),
      onmousedown: e => { e.preventDefault(); choose(p); }},
      h('span', {class: 'hb-avatar', style: 'width:34px;height:34px;font-size:.85rem', text: p.full_name[0].toUpperCase()}),
      h('span', {}, h('span', {class: 'fw-semibold d-block', text: p.full_name}),
        h('span', {class: 'small hb-muted', text: `${p.patient_id}${p.origin_country_name ? ' · ' + p.origin_country_name : ''}`}))))
    : [h('div', {class: 'small hb-muted p-2', text: patients.length ? 'No matching patients.' : 'No patients have granted you access yet.'})]));
  list.classList.toggle('d-none', !open);
  $('#patientSearch').setAttribute('aria-expanded', String(open));
}

function choose(p) {
  $('#patientSearch').value = '';
  renderPicker(false);
  openPatient(p.patient_id, 'medications', true);
}

$('#patientSearch').addEventListener('focus', () => { pickerIndex = -1; renderPicker(); });
$('#patientSearch').addEventListener('input', () => { pickerIndex = 0; renderPicker(); });
$('#patientSearch').addEventListener('blur', () => setTimeout(() => renderPicker(false), 100));
$('#patientSearch').addEventListener('keydown', e => {
  const items = filtered();
  if (e.key === 'ArrowDown') { e.preventDefault(); pickerIndex = Math.min(items.length - 1, pickerIndex + 1); renderPicker(); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); pickerIndex = Math.max(0, pickerIndex - 1); renderPicker(); }
  else if (e.key === 'Enter') { e.preventDefault(); if (items[Math.max(0, pickerIndex)]) choose(items[Math.max(0, pickerIndex)]); }
  else if (e.key === 'Escape') renderPicker(false);
});

// ---------- overview vs. patient view ----------
const SECTION_KEYS = PATIENT_SECTIONS.map(s => s[0]);
const mainLink = () => $('.hb-nav a[href="/doctor/patients"]');

function showOverview() {
  current = null;
  $('#workspace').classList.add('d-none');
  $('#overview').classList.remove('d-none');
  mainLink()?.classList.add('active');
  $('#pageTitle').textContent = PAGE_TITLE;
  $('#pageSub').textContent = PAGE_SUB;
  renderPatientNav();
}

function openPatient(code, section, push) {
  const p = patients.find(x => x.patient_id === code);
  if (!p) { if (getOpenPatient()?.id === code) setOpenPatient(null); return showOverview(); }
  section = SECTION_KEYS.includes(section) ? section : 'medications';
  const url = `/doctor/patients?patient=${encodeURIComponent(code)}&section=${section}`;
  if (push) history.pushState(null, '', url); else history.replaceState(null, '', url);
  setOpenPatient({id: p.patient_id, name: p.full_name});
  renderPatientNav(section);
  mainLink()?.classList.remove('active');
  $('#overview').classList.add('d-none');
  $('#workspace').classList.remove('d-none');
  $('#pageSub').textContent = [p.full_name, p.patient_id, p.origin_country_name].filter(Boolean).join(' \u00b7 ');
  const fresh = current !== code;
  if (fresh) { analysis = null; analysisKey = null; tripChoice = null; }
  current = code;
  selectTab(section);
  if (fresh) loadDeclaration();
  window.scrollTo(0, 0);
}

// Sidebar section links switch in place on this page (other pages navigate normally).
$('#patientNav')?.addEventListener('click', e => {
  const a = e.target.closest('a[data-section]');
  if (!a || !current) return;
  e.preventDefault();
  openPatient(current, a.dataset.section, true);
});

function fromUrl() {
  const q = new URLSearchParams(location.search);
  const code = q.get('patient');
  code ? openPatient(code, q.get('section'), false) : showOverview();
}
window.addEventListener('popstate', fromUrl);

// ---------- selected patient ----------
async function loadDeclaration() {
  try { declaration = (await api(base())).allergy_declaration; } catch { declaration = 'unknown'; }
  syncAddBtn();
}

function syncAddBtn() {
  const none = tab === 'allergies' && declaration === 'none';
  $('#addBtn').disabled = none;
  $('#addBtn').title = none ? 'The patient has declared no known allergies.' : '';
}

// ---------- cross-border findings (stored trip analysis; reading never runs the AI) ----------
let analysis = null, analysisKey = null, tripChoice = null, selectedRecord = null;
const CONF_CHIP = {High: 'mild', Medium: 'moderate', Low: 'unknown'};
const FINDING_TABS = {medications: 'medicine', procedures: 'procedure', documents: 'report'};

async function ensureAnalysis(force) {
  const key = `${current}|${tripChoice || ''}`;
  if (!force && analysisKey === key && analysis) return analysis;
  try {
    analysis = await api(`/api/doctor/patients/${encodeURIComponent(current)}/analysis${tripChoice ? '?trip_id=' + tripChoice : ''}`);
  } catch { analysis = {trips: [], findings: [], flags: []}; }
  analysisKey = key;
  const sel = $('#tripSelect');
  sel.replaceChildren(...analysis.trips.map(t => h('option', {value: t.id, text: `${t.origin_name} → ${t.destination_name} · ${fmtDate(t.departure_date)}`})));
  if (analysis.trip) sel.value = analysis.trip.id;
  sel.classList.toggle('d-none', analysis.trips.length < 2);
  return analysis;
}
$('#tripSelect').addEventListener('change', async e => { tripChoice = e.target.value; await ensureAnalysis(true); loadTab(); });

const destShort = () => analysis?.trip ? (analysis.trip.destination_country === 'AE' ? 'UAE' : analysis.trip.destination_name) : 'Destination';
const findingFor = id => (analysis?.findings || []).find(f => f.record_id === id);

function matchCell(id) {
  const f = findingFor(id);
  if (!f) return h('td', {}, h('span', {class: 'hb-muted small', text: analysis?.running ? 'Analysing…' : '—'}));
  return h('td', {}, f.confidence ? h('span', {class: `chip chip-${CONF_CHIP[f.confidence] || 'unknown'}`, text: f.confidence}) : h('span', {class: 'hb-muted small', text: '—'}),
    f.freshness === 'stale' ? h('i', {class: 'bi bi-clock-history ms-1 dc-stale-note', title: 'Out of date: the record changed after the analysis'}) : null);
}

function sourcesLine(sources, prefix = ' · Sources: ') {
  if (!sources?.length) return null;
  // Names only (search them in the Knowledge Explorer); no links.
  return h('span', {}, h('span', {class: 'hb-muted', text: prefix}), sources.map(s => s.label).join(', '));
}

function findingBox(id) {
  const box = $('#findingBox');
  selectedRecord = id;
  $$('#tabBody tr[data-record]').forEach(tr => tr.classList.toggle('row-selected', tr.dataset.record === id));
  const f = findingFor(id);
  if (!analysis?.trip) return box.replaceChildren(h('div', {class: 'small hb-muted', text: 'Findings appear once the patient has a trip.'}));
  if (!f) return box.replaceChildren(h('div', {class: 'small hb-muted', text: analysis.running ? 'Analysis in progress for this trip…' : 'No findings for this record yet.'}));
  // The AI's own match strength (comparison.ai_match) is stored for later use and not shown here.
  const comp = f.comparison || {};
  const head = h('div', {class: 'd-flex flex-wrap justify-content-between align-items-center gap-2'},
    h('div', {class: 'fw-semibold'}, icon({medicine: 'capsule', procedure: 'bandaid', report: 'file-earmark-text'}[f.agent], 'text-primary me-2'), f.title),
    f.match_label ? h('span', {class: `chip chip-${f.confidence ? CONF_CHIP[f.confidence] : 'teal'}`, text: f.confidence ? `${f.match_label} · ${f.confidence}` : f.match_label}) : null);
  const parts = [head];
  if (comp.rows?.length) {
    // Cells the AI filled from the label / provider text carry a marker; hover shows the quoted words.
    const filled = new Map((comp.filled || []).map(x => [`${x.row}|${x.column}`, x]));
    const cell = (row, col, value, mutedRe) => {
      const fill = filled.get(`${row}|${col}`);
      if (!fill) return h('span', {class: mutedRe.test(value) ? 'hb-muted' : '', text: value});
      return h('span', {title: `From ${fill.source}: “${fill.quote}”`}, value, h('span', {class: 'fx-filled', text: 'from source'}));
    };
    const grid = h('div', {class: 'fx-grid mt-3'}, h('span'), ...comp.columns.map(c => h('span', {class: 'hb-muted', text: c})));
    comp.rows.forEach(([label, a, b]) => grid.append(h('span', {class: 'hb-muted', text: label}),
      cell(label, comp.columns[0], a, /not stated|—/i), cell(label, comp.columns[1], b, /not stated|—|no match/i)));
    parts.push(grid);
  }
  if (comp.allergy) {
    const al = comp.allergy;
    const look = {direct: ['exclamation-octagon', 'text-danger'], possible: ['exclamation-triangle', 'text-warning'],
                  none: ['check-circle', 'text-success'], unchecked: ['question-circle', 'hb-muted']}[al.status] || ['info-circle', 'hb-muted'];
    parts.push(h('div', {class: 'fx-allergy small mt-3'}, icon(look[0], `${look[1]} me-2`),
      h('span', {class: 'fw-semibold me-1', text: 'Allergy check:'}), al.note,
      al.by === 'ai' ? h('span', {class: 'hb-muted ms-1', text: '(AI check – confirm with prescriber)'}) : null));
  }
  if (f.facts?.length) {
    const basisText = {sources: `${destShort()} lab source`, rule: 'reviewed rule'};
    parts.push(h('div', {class: 'mt-2'}, f.facts.map(x => h('div', {class: `fx-fact ${x.problem ? 'text-danger' : ''}`},
      h('span', {text: x.label}), h('span', {}, h('span', {class: 'fw-semibold', text: x.value}), x.converted ? ` → ` : '',
        x.converted ? h('span', {class: 'fw-semibold', text: x.converted}) : null,
        x.converted && basisText[x.basis] ? h('span', {class: 'hb-muted small ms-1', text: `(${basisText[x.basis]})`}) : null)))));
  }
  if (f.context) {   // documents without values (letters, referrals): the context is the short summary
    parts.push(f.facts?.length ? h('div', {class: 'small hb-muted mt-2', text: f.context})
      : h('div', {class: 'mt-2 text-pre-wrap', text: f.context}));
  }
  const tail = [f.verify ? h('span', {}, h('span', {class: 'hb-muted', text: 'Verify: '}), f.verify) : null, sourcesLine(f.sources)].filter(Boolean);
  if (tail.length) parts.push(h('div', {class: 'small fx-tail'}, ...tail));
  const dc = assessmentSection(f);
  if (dc) parts.push(dc);
  box.replaceChildren(h('div', {class: 'hb-card fx-card'}, h('div', {class: 'hb-card-body'}, ...parts)));
}

// Dopamine-Cortisol controller result: two filled bars with percentages, the display tag and the reason.
const DC_TAG = {VALIDATED_FOR_DISPLAY: ['dc-validated', 'patch-check'], DISPLAY_WITH_LIMITATIONS: ['dc-limited', 'exclamation-circle'],
                HUMAN_REVIEW: ['dc-review', 'search'], BLOCKED: ['dc-blocked', 'slash-circle']};
function assessmentSection(f) {
  const a = f.assessment;
  const stale = f.freshness === 'stale';
  if (!a?.disposition && !stale) return null;
  const bar = (name, value, cls, hint) => h('div', {class: 'dc-row', title: hint},
    h('span', {class: 'dc-name', text: name}),
    h('div', {class: 'dc-track', role: 'meter', 'aria-label': name, 'aria-valuemin': '0', 'aria-valuemax': '100', 'aria-valuenow': String(Math.round(value * 100))},
      h('div', {class: `dc-fill ${cls}`, style: `width:${Math.round(value * 100)}%`})),
    h('span', {class: 'dc-pct', text: `${Math.round(value * 100)}%`}));
  const [tagCls, tagIcon] = DC_TAG[a?.disposition] || ['dc-review', 'question-circle'];
  const tags = h('div', {class: 'd-flex flex-wrap align-items-center gap-2'},
    a?.label ? h('span', {class: `dc-tag ${tagCls}`}, icon(tagIcon, 'me-1'), a.label) : null,
    stale ? h('span', {class: 'dc-tag dc-stale', title: 'The medical history changed after this finding was made'}, icon('clock-history', 'me-1'), 'Out of date') : null);
  return h('div', {class: 'dc-section'},
    h('div', {class: 'd-flex flex-wrap justify-content-between align-items-center gap-2 mb-2'},
      h('span', {class: 'small fw-semibold', text: 'Controller assessment'}), tags),
    a?.disposition ? bar('Dopamine', a.dopamine, 'dc-d', 'Go signal: evidence found, checks passed, code and AI agree') : null,
    a?.disposition ? bar('Cortisol', a.cortisol, 'dc-c', 'Caution signal: missing details, risk, conflicts, failed checks') : null,
    a?.reason ? h('div', {class: 'small hb-muted mt-2', text: a.reason}) : null,
    stale ? h('div', {class: 'small mt-1 dc-stale-note', text: 'The record changed after this was analysed. It updates when the patient reprocesses the trip.'}) : null);
}

function selectableRows(tbody) {
  const rows = $$('tr[data-record]', tbody);
  rows.forEach(tr => tr.addEventListener('click', e => {
    if (e.target.closest('a,button')) return;
    if (tr.dataset.record === selectedRecord) return clearFinding();   // click again to close
    findingBox(tr.dataset.record);
  }));
  // Nothing is opened by default; keep the box only if the selected record is still listed.
  if (selectedRecord && rows.some(tr => tr.dataset.record === selectedRecord)) findingBox(selectedRecord);
  else clearFinding();
}

function clearFinding() {
  selectedRecord = null;
  $$('#tabBody tr[data-record]').forEach(tr => tr.classList.remove('row-selected'));
  $('#findingBox').replaceChildren();
}

// ---------- complete patient report (summary + all findings + flags with sources), English or Arabic ----------
function reportCard(a) {
  const lang = h('select', {class: 'form-select w-auto report-lang', 'aria-label': 'Report language'},
    h('option', {value: 'en', text: 'English'}), h('option', {value: 'ar', text: 'العربية (Arabic)'}));
  const label = h('span', {text: 'Generate report'});
  const btn = h('button', {class: 'btn btn-primary', type: 'button'}, icon('file-earmark-arrow-down', 'me-1'), label);
  const note = h('div', {class: 'small hb-muted', text: 'Generate the complete patient report for this trip: summary, medication, procedure and document findings, flags and sources.'});
  const base = `/api/doctor/patients/${encodeURIComponent(current)}/report`;
  const status = async () => {
    try {
      const st = await api(`${base}?trip_id=${a.trip.id}&language=${lang.value}`);
      label.textContent = st.current ? 'Download report' : st.exists ? 'Update report' : 'Generate report';
    } catch { /* optional */ }
  };
  lang.addEventListener('change', status);
  btn.addEventListener('click', async () => {
    const win = window.open('', '_blank');   // opened now so the browser doesn't block it after the wait
    if (win) win.document.write('<p style="font-family:sans-serif;padding:2rem">' + (lang.value === 'ar' ? 'جارٍ إعداد التقرير…' : 'Preparing the report…') + '</p>');
    await withBusy(btn, async () => {
      try {
        const r = await api(base, {method: 'POST', body: {trip_id: a.trip.id, language: lang.value}});
        if (win) win.location = `${r.report_url}?print=1`; else location.href = `${r.report_url}?print=1`;
        status();
      } catch (err) { if (win) win.close(); toast(err.message, 'error'); }
    });
  });
  status();
  return h('div', {class: 'hb-card mb-3'}, h('div', {class: 'hb-card-body d-flex flex-wrap align-items-center gap-3'},
    h('div', {class: 'me-auto', style: 'max-width: 560px'}, h('div', {class: 'fw-semibold'}, icon('file-earmark-medical', 'text-primary me-2'), 'Complete patient report'), note),
    h('label', {class: 'small hb-muted', text: 'Language'}), lang, btn));
}

// Same content as the patient's Travel Health Summary (flags + quantity advice), plus the sources of each item.
function renderFlags() {
  const a = analysis;
  const out = $('#findingBox');
  if (!a?.trip) return out.replaceChildren(h('div', {class: 'hb-card'}, emptyState('flag', 'No trip', 'Flags are prepared for each trip the patient adds.')));
  const flags = a.flags.filter(f => f.kind === 'flag');   // quantity advice is not shown to doctors
  if (!flags.length) return out.replaceChildren(h('div', {class: 'hb-card'}, emptyState('flag', a.running ? 'Analysis in progress' : 'No flags',
    a.running ? 'Flags appear when the analysis finishes.' : 'No jurisdiction flags for this trip.')));
  const src = f => f.sources?.length ? h('div', {class: 'small hb-muted mt-1'}, sourcesLine(f.sources, 'Sources: ')) : null;
  const flagCard = h('div', {class: 'hb-card'}, h('div', {class: 'hb-card-body'},
    h('h2', {class: 'hb-card-title mb-2'}, icon('flag', 'text-danger'), 'Flags to act on'),
    h('div', {class: 'ts-list'}, flags.length ? flags.map(f => h('div', {class: 'ts-row justify-content-start align-items-start gap-2'},
      icon(f.severity === 'action' ? 'exclamation-triangle' : 'info-circle', f.severity === 'action' ? 'text-danger' : 'text-warning'),
      h('div', {}, h('span', {text: f.text}),
        /safer option/.test(f.origin || '') ? h('span', {class: 'chip chip-teal ms-2', title: 'Sources disagreed; the stricter requirement was chosen', text: 'Safer option'}) : null,
        src(f)))) : h('p', {class: 'small hb-muted mb-0', text: 'No flags for this trip.'}))));
  const staleNote = a.freshness?.flags_stale ? h('div', {class: 'stale-banner mb-3'}, icon('clock-history'),
    'The patient’s medicines or documents changed after these flags were made. They update when the patient reprocesses the trip.') : null;
  out.replaceChildren(...[reportCard(a), staleNote, flagCard].filter(Boolean),
    h('p', {class: 'small hb-muted mt-3 mb-0'}, icon('info-circle', 'me-1'),
      'Generated from the patient’s records and official sources. Not a clinical decision or a travel clearance.'));
}

function selectTab(t) {
  tab = t;
  $('#pageTitle').textContent = PATIENT_SECTIONS.find(s => s[0] === t)[1];
  const isFlags = t === 'flags';
  $('#q').classList.toggle('d-none', isFlags);
  $('#filter').classList.toggle('d-none', isFlags);
  $('#findingBox').replaceChildren();
  selectedRecord = null;
  // Flags has no table: the records card shows only when the patient has more than one trip to choose from.
  $('#recordsCard').classList.toggle('d-none', isFlags && !(analysis?.trips?.length > 1));
  $('#tabBody').classList.toggle('d-none', isFlags);
  if (isFlags) { $('#addBtn').classList.add('d-none'); loadTab(); return; }
  const isHistory = HISTORY.includes(t);
  $('#addBtn').classList.toggle('d-none', !isHistory);
  if (isHistory) $('#addBtn span').textContent = KINDS[t].add;
  syncAddBtn();
  $('#q').value = '';
  $('#q').placeholder = t === 'documents' ? 'Search documents\u2026' : 'Search\u2026';
  $('#filter').replaceChildren(...(t === 'documents'
    ? [h('option', {value: '', text: 'All types'}), ...Object.entries(docTypes).map(([v, l]) => h('option', {value: v, text: l}))]
    : KINDS[t].statuses.map(([v, l]) => h('option', {value: v, text: v ? l : 'All statuses'}))));
  $('#filter').setAttribute('aria-label', t === 'documents' ? 'Filter by type' : 'Filter by status');
  loadTab();
}

let loadSeq = 0;
async function loadTab() {
  const body = $('#tabBody');
  const mine = ++loadSeq;
  const p = new URLSearchParams();
  if ($('#q').value.trim()) p.set('q', $('#q').value.trim());
  if ($('#filter').value) p.set(tab === 'documents' ? 'doc_type' : 'status', $('#filter').value);
  const filtered = p.toString() !== '';
  body.replaceChildren(h('div', {class: 'skeleton', style: 'height:60px'}));
  try {
    await ensureAnalysis();
    if (tab === 'flags') {
      if (mine !== loadSeq) return;
      $('#recordsCard').classList.toggle('d-none', !(analysis?.trips?.length > 1));
      renderFlags();
      return;
    }
    const data = await api(tab === 'documents' ? `${base()}/documents?${p}` : `${base()}/history/${tab}?${p}`);
    if (mine !== loadSeq) return;  // a newer search replaced this one
    tab === 'documents' ? renderDocuments(data, filtered) : renderHistory(data, filtered);
  } catch (err) { if (mine === loadSeq) body.replaceChildren(h('div', {class: 'alert alert-danger', text: err.message})); }
}
let qTimer;
$('#q').addEventListener('input', () => { clearTimeout(qTimer); qTimer = setTimeout(loadTab, 250); });
$('#filter').addEventListener('change', loadTab);

function renderHistory(data, filtered) {
  const cfg = KINDS[tab];
  if (!data.items.length) {
    const text = filtered ? 'Try a different search or filter.' : tab === 'allergies' ? (declaration === 'none' ? 'The patient has declared no known allergies.'
      : declaration === 'unknown' ? 'The patient has not stated their allergy status.' : 'No allergies listed.') : 'Nothing recorded yet.';
    return $('#tabBody').replaceChildren(emptyState('journal-medical', `No ${cfg.singular.toLowerCase()} records`, text));
  }
  const cols = cfg.cols.slice(0, -1);  // no action column: doctors cannot edit or delete
  const withMatch = tab in FINDING_TABS;
  const tbody = h('tbody', {}, data.items.map(item => h('tr', withMatch ? {'data-record': item.id, class: 'row-selectable'} : {}, cfg.row(item),
    withMatch ? matchCell(item.id) : null, h('td', {class: 'sub text-nowrap', text: fmtWhen(item.created_at)}))));
  $('#tabBody').replaceChildren(h('div', {class: 'table-responsive'}, h('table', {class: 'table hb-table'},
    h('thead', {}, h('tr', {}, cols.map(c => h('th', {text: c})), withMatch ? h('th', {text: `${destShort()} match`}) : null, h('th', {text: 'Added'}))),
    tbody)));
  if (withMatch) selectableRows(tbody); else $('#findingBox').replaceChildren();
}

function renderDocuments(docs, filtered) {
  if (!docs.length) return $('#tabBody').replaceChildren(emptyState('folder2-open', 'No documents',
    filtered ? 'Try a different search or filter.' : 'The patient has not uploaded any documents.'));
  const TYPE = {medication: 'Medication', condition: 'Condition', procedure: 'Procedure', allergy: 'Allergy'};
  $('#tabBody').replaceChildren(h('div', {class: 'table-responsive'}, h('table', {class: 'table hb-table'},
    h('thead', {}, h('tr', {}, ['Document', 'Type', 'Date', 'Linked to', ''].map(c => h('th', {text: c})))),
    h('tbody', {}, docs.map(d => h('tr', {'data-record': d.id, class: 'row-selectable'},
      h('td', {}, h('div', {class: 'd-flex align-items-center gap-2'},
        h('span', {class: `doc-icon ${d.mime_type === 'application/pdf' ? '' : 'img'}`}, icon(d.mime_type === 'application/pdf' ? 'file-earmark-pdf' : 'file-earmark-image')),
        h('div', {}, h('div', {class: 'primary', text: d.name}), h('div', {class: 'sub', text: `${d.original_filename} · ${fmtSize(d.size_bytes)}`})))),
      h('td', {text: d.doc_type_label}),
      h('td', {class: 'text-nowrap', text: fmtDate(d.document_date)}),
      h('td', {}, d.links.length ? d.links.map(l => h('span', {class: 'link-pill'}, icon('link-45deg'), `${TYPE[l.record_type]}: ${l.label}`)) : h('span', {class: 'hb-muted', text: 'No link'})),
      h('td', {class: 'text-end text-nowrap'},
        h('a', {class: 'btn btn-sm btn-light me-1', href: `${base()}/documents/${d.id}/download?inline=1`, target: '_blank', rel: 'noopener', title: 'Preview', 'aria-label': `Preview ${d.name}`}, icon('eye')),
        h('a', {class: 'btn btn-sm btn-light', href: `${base()}/documents/${d.id}/download`, title: 'Download', 'aria-label': `Download ${d.name}`}, icon('download')))))))));
  selectableRows($('#tabBody tbody'));
}

// ---------- doctor adds a record (same forms as the patient portal) ----------
const formFor = k => $(`#${k}Modal form`);
const modalFor = k => bootstrap.Modal.getOrCreateInstance($(`#${k}Modal`));

$('#addBtn').addEventListener('click', () => {
  const form = formFor(tab);
  form.reset(); clearErrors(form);
  form.closest('.modal-content').querySelector('.modal-title').textContent = `${KINDS[tab].add} (doctor entry)`;
  if (tab === 'medications') syncMedication(form);
  modalFor(tab).show();
});

$$('form[data-kind]').forEach(form => {
  const k = form.dataset.kind;
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const body = payload(k, form);
    const errors = clientErrors(k, body);
    if (Object.keys(errors).length) return showErrors(form, {message: 'Please fix the highlighted fields.', errors});
    await withBusy(form.querySelector('[data-save]'), async () => {
      try {
        const r = await api(`${base()}/history/${k}`, {method: 'POST', body});
        modalFor(k).hide();
        toast(`${KINDS[k].singular} added to the patient's record`);
        if (r.possible_duplicate) toast(`Note: an entry with the same name already exists. Both are kept.`, 'info');
        if (k === 'allergies') { declaration = 'known'; syncAddBtn(); }
        loadTab();
      } catch (err) { showErrors(form, err); }
    });
  });
});

(async () => {
  bindHistoryForms();
  await fillHistoryFormOptions();
  try { docTypes = (await reference()).document_types || {}; } catch { /* filter shows "All types" only */ }
  try { patients = await api('/api/doctor/patients'); }
  catch (err) {
    $('#patientSearch').disabled = true;
    $('#patientSearch').placeholder = err.message;
  }
  // Forget an open patient whose access has ended.
  const open = getOpenPatient();
  if (open && !patients.some(p => p.patient_id === open.id)) setOpenPatient(null);
  fromUrl();
  if (['#pending', '#request'].includes(location.hash)) $(location.hash)?.scrollIntoView();
})();
})();
