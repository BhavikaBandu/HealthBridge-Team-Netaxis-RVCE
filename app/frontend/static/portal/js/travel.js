// Patient > Travel Health Summary. Reads the stored analysis of the chosen trip; never runs the AI on page load.
(() => {
let trips = [];
let current = null;
let pollTimer = null;
const CONF = {High: 'mild', Medium: 'moderate', Low: 'unknown'};
const TAG = {stopped: 'stopped', completed: 'done', planned: 'planned'};

const SHORT = {AE: 'UAE', GB: 'UK', US: 'USA'};
const placeName = (code, name) => SHORT[code] || name;
const tripLabel = t => `${placeName(t.origin_country, t.origin_name)} → ${placeName(t.destination_country, t.destination_name)} · `
  + `${fmtDate(t.departure_date)}${t.return_date ? ' – ' + fmtDate(t.return_date) : ''}`;

// ---------- trip picker ----------
function renderTripList(open = true) {
  const q = $('#tripSearch').value.trim().toLowerCase();
  const items = trips.filter(t => !q || tripLabel(t).toLowerCase().includes(q) || (t.purpose_description || '').toLowerCase().includes(q));
  $('#tripList').replaceChildren(...(items.length ? items.map(t => h('button', {type: 'button', role: 'option', class: 'picker-item',
      onmousedown: e => { e.preventDefault(); chooseTrip(t); }},
      icon('airplane', 'text-primary'), h('span', {}, h('span', {class: 'fw-semibold d-block', text: tripLabel(t)}),
        h('span', {class: 'small hb-muted', text: t.purpose_label}))))
    : [h('div', {class: 'small hb-muted p-2', text: 'No matching trips'})]));
  $('#tripList').classList.toggle('d-none', !open);
  $('#tripSearch').setAttribute('aria-expanded', String(open));
}
$('#tripSearch').addEventListener('focus', () => { $('#tripSearch').select(); renderTripList(); });
$('#tripSearch').addEventListener('input', () => renderTripList());
$('#tripSearch').addEventListener('blur', () => setTimeout(() => { renderTripList(false); $('#tripSearch').value = current ? tripLabel(current) : ''; }, 120));

function chooseTrip(t) {
  current = t;
  $('#tripSearch').value = tripLabel(t);
  renderTripList(false);
  history.replaceState(null, '', `/travel-summary?trip=${t.id}`);
  $('#refreshBtn').classList.remove('d-none');
  $('#reportBar').classList.remove('d-none');
  load();
  reportStatus();
}

// ---------- printable report (English / Arabic) ----------
async function reportStatus() {
  if (!current) return;
  const lang = $('#reportLang').value;
  try {
    const st = await api(`/api/trips/${current.id}/report?language=${lang}`);
    $('#reportBtn span').textContent = st.current ? 'Download report' : (st.exists ? 'Update report' : 'Generate report');
    $('#reportNote').textContent = st.current ? 'Ready. Opens a printable copy you can save as PDF.'
      : st.exists ? 'Your summary changed since the last report.' : 'A printable copy of this summary.';
  } catch { /* status is optional */ }
}
$('#reportLang').addEventListener('change', reportStatus);

$('#reportBtn').addEventListener('click', async () => {
  if (!current) return;
  const lang = $('#reportLang').value;
  const win = window.open('', '_blank');   // opened now so the browser doesn't block it after the wait
  if (win) win.document.write('<p style="font-family:sans-serif;padding:2rem">' + (lang === 'ar' ? 'جارٍ إعداد التقرير…' : 'Preparing your report…') + '</p>');
  await withBusy($('#reportBtn'), async () => {
    try {
      if (lang === 'ar') $('#reportNote').textContent = 'Translating to Arabic. This takes about half a minute…';
      const r = await api(`/api/trips/${current.id}/report`, {method: 'POST', body: {language: lang}});
      if (win) win.location = `${r.report_url}?print=1`; else location.href = `${r.report_url}?print=1`;
      reportStatus();
    } catch (err) {
      if (win) win.close();
      toast(err.message, 'error');
      reportStatus();
    }
  });
});

// ---------- summary ----------
function setState(node) {
  $('#summaryState').replaceChildren(...(node ? [node] : []));
}

function confChip(c) {
  return c ? h('span', {class: `chip chip-${CONF[c] || 'unknown'} ms-2 flex-shrink-0`, text: c}) : null;
}

function row(main, sub, chip, tag) {
  return h('div', {class: 'ts-row'},
    h('div', {class: 'min-w-0'}, h('div', {class: 'fw-semibold'}, main, tag ? h('span', {class: 'small hb-muted fw-normal', text: ` · ${tag}`}) : null),
      h('div', {class: 'small hb-muted', text: sub})),
    chip);
}

function render(data) {
  const meds = data.findings.filter(f => f.agent === 'medicine');
  const procs = data.findings.filter(f => f.agent === 'procedure');
  const dest = data.trip.destination_country === 'AE' ? 'UAE' : data.trip.destination_name;
  const where = ['UAE', 'UK', 'USA'].includes(dest) ? `the ${dest}` : dest;   // "the UAE", but "Switzerland"
  $('#medTitle').textContent = `Medicines in ${where}`;
  $('#procTitle').textContent = `Procedures in ${where}`;
  const tagOf = f => [TAG[f.record_status], f.freshness === 'stale' ? 'out of date' : null].filter(Boolean).join(' · ');
  $('#medList').replaceChildren(...(meds.length ? meds.map(f => row(f.title.split(' → ')[0], f.patient_line, confChip(f.confidence), tagOf(f)))
    : [h('p', {class: 'small hb-muted mb-0', text: 'No medicines in your history.'})]));
  $('#procList').replaceChildren(...(procs.length ? procs.map(f => row(f.title.split(' → ')[0], f.patient_line, confChip(f.confidence), tagOf(f)))
    : [h('p', {class: 'small hb-muted mb-0', text: 'No procedures in your history.'})]));
  const labs = data.findings.filter(f => f.agent === 'report').flatMap(f => (f.facts || []).filter(x => x.converted).map(x =>
    row(`${x.label} ${x.value}`, `≈ ${x.converted} (${dest} units)`, null)));
  $('#labBlock').classList.toggle('d-none', !labs.length);
  $('#labList').replaceChildren(...labs);

  const flags = data.flags.filter(f => f.kind === 'flag');
  $('#flagList').replaceChildren(...(flags.length ? flags.map(f => h('div', {class: 'ts-row justify-content-start gap-2'},
      icon(f.severity === 'action' ? 'exclamation-triangle' : 'info-circle', f.severity === 'action' ? 'text-danger' : 'text-warning'),
      h('span', {text: f.text})))
    : [h('p', {class: 'small hb-muted mb-0', text: 'No flags for this trip.'})]));
  const qty = data.flags.filter(f => f.kind === 'quantity');
  $('.ts-quantity').classList.toggle('d-none', !qty.length);
  $('#qtyList').replaceChildren(...qty.map(f => h('p', {class: 'mb-1'}, h('span', {class: 'fw-semibold', text: f.subject}), ` — ${f.text}`)));
}

const isStale = d => !!(d.freshness && (d.freshness.stale || d.freshness.new_records || d.freshness.flags_stale));

async function load() {
  clearTimeout(pollTimer);
  if (!current) return;
  try {
    const data = await api(`/api/trips/${current.id}/analysis`);
    const hasResults = data.findings.length || data.flags.length;
    $('#summaryBody').classList.toggle('d-none', !hasResults);
    if (hasResults) render(data);
    if (!data.running && !hasResults) $('#reportBar').classList.add('d-none');
    else $('#reportBar').classList.remove('d-none');
    if (data.running) {
      setState(h('div', {class: 'alert alert-info small d-flex align-items-center gap-2'},
        h('span', {class: 'spinner-border spinner-border-sm'}), hasResults ? 'Updating your summary…' : 'Preparing your summary. This takes about a minute.'));
      pollTimer = setTimeout(load, 4000);
    } else if (!hasResults) {
      setState(h('div', {class: 'hb-card'}, emptyState('clipboard2-pulse', 'No summary yet',
        'Choose "Refresh summary" to analyse your records for this trip.')));
    } else if (isStale(data)) {
      setState(h('div', {class: 'stale-banner mb-3'}, icon('clock-history'),
        h('span', {class: 'flex-grow-1', text: 'Your medical history changed after this summary was made, so some parts are out of date.'}),
        h('button', {class: 'btn btn-sm btn-primary', type: 'button', text: 'Reprocess now', onclick: () => $('#refreshBtn').click()})));
    } else {
      setState(null);
    }
  } catch (err) { setState(h('div', {class: 'alert alert-danger', text: err.message})); }
}

$('#refreshBtn').addEventListener('click', async () => {
  if (!current) return;
  await withBusy($('#refreshBtn'), async () => {
    try { await api(`/api/trips/${current.id}/analysis/refresh`, {method: 'POST'}); toast('Refreshing your summary'); load(); }
    catch (err) { toast(err.message, 'error'); }
  });
});

(async () => {
  try { trips = (await api('/api/trips')).items; } catch (err) { setState(h('div', {class: 'alert alert-danger', text: err.message})); return; }
  if (!trips.length) {
    $('#tripSearch').disabled = true;
    $('#refreshBtn').classList.add('d-none');
    setState(h('div', {class: 'hb-card'}, emptyState('airplane', 'Add a trip first',
      'Your travel health summary is prepared for each trip.'), h('div', {class: 'text-center pb-4'}, h('a', {class: 'btn btn-primary', href: '/trips', text: 'Go to My Trips'}))));
    return;
  }
  // No trip is chosen by default; the patient picks one (a link with ?trip= opens that trip directly).
  const wanted = trips.find(t => t.id === new URLSearchParams(location.search).get('trip'));
  if (wanted) chooseTrip(wanted);
  else setState(h('div', {class: 'hb-card'}, emptyState('airplane', 'Choose a trip', 'Pick a trip above to see what your records mean for that destination.')));
})();
})();
