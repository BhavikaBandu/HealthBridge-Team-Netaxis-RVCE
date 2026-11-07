const form = $('#requestForm');
const input = $('#patient_id');
const list = $('#lookupList');
let matches = [];
let lookupSeq = 0;
let lookupTimer;

async function loadCounts() {
  try {
    // Shared by the doctor Dashboard (counts) and Patient Access page (form + table): update what exists.
    const d = await api('/api/doctor/dashboard');
    if ($('#assignedCount')) $('#assignedCount').textContent = d.assigned_patients;
    if ($('#pendingCount')) $('#pendingCount').textContent = d.pending_invitations;
    if ($('#arrivalsCount')) $('#arrivalsCount').textContent = d.upcoming_arrivals ?? 0;
    const blocked = d.verification_status !== 'approved';
    if (form) { $('#sendBtn').disabled = blocked; input.disabled = blocked; }
  } catch (err) { toast(err.message, 'error'); }
}

async function cancel(r) {
  if (!await confirmDialog({title: 'Cancel request?', message: `Your access request for ${r.name || r.patient_code} will be withdrawn.`, confirmText: 'Cancel request'})) return;
  try { await api(`/api/doctor/access-requests/${r.id}/cancel`, {method: 'POST'}); toast('Request cancelled'); refresh(); }
  catch (err) { toast(err.message, 'error'); }
}

async function loadPending() {
  const body = $('#pendingBody');
  try {
    const rows = await api('/api/doctor/access-requests?status=pending');
    if (!rows.length) {
      body.replaceChildren(h('tr', {}, h('td', {colspan: 6}, emptyState('envelope-open', 'No pending invitations', 'Requests you send will appear here until the patient responds.'))));
      return;
    }
    body.replaceChildren(...rows.map(r => h('tr', {},
      h('td', {class: 'fw-semibold text-nowrap', text: r.patient_code}),
      h('td', {text: r.name || '—'}),
      h('td', {text: r.country || '—'}),
      h('td', {class: 'text-break', text: r.email || '—'}),
      h('td', {}, h('span', {class: 'chip chip-moderate', text: 'Pending'})),
      h('td', {class: 'text-end'}, h('button', {class: 'btn btn-sm btn-light', type: 'button', title: 'Cancel request', 'aria-label': `Cancel request for ${r.patient_code}`, onclick: () => cancel(r)}, icon('x-lg'))))));
  } catch (err) { body.replaceChildren(h('tr', {}, h('td', {colspan: 6, class: 'text-danger', text: err.message}))); }
}

const refresh = () => Promise.all([loadCounts(), $('#pendingBody') ? loadPending() : null]);

// ---------- patient ID lookup dropdown ----------
function showList(content) {
  list.replaceChildren(...content);
  list.classList.toggle('d-none', !content.length);
  input.setAttribute('aria-expanded', String(content.length > 0));
}

function choose(p) {
  input.value = p.patient_id;
  showList([h('div', {class: 'picker-item active'}, icon('person-check', 'text-primary'),
    h('span', {}, h('span', {class: 'fw-semibold d-block', text: p.full_name}), h('span', {class: 'small hb-muted', text: `${p.patient_id}${p.country ? ' · ' + p.country : ''}`})))]);
  setTimeout(() => showList([]), 1500);
}

async function lookup() {
  const q = input.value.trim().toUpperCase();
  if (q.length < 5) { matches = []; showList([]); return; }
  const mine = ++lookupSeq;
  try {
    matches = await api(`/api/doctor/patient-lookup?q=${encodeURIComponent(q)}`);
    if (mine !== lookupSeq) return;
    showList(matches.length ? matches.map(p => h('button', {type: 'button', role: 'option', class: 'picker-item',
        onmousedown: e => { e.preventDefault(); choose(p); }},
        h('span', {class: 'hb-avatar', style: 'width:34px;height:34px;font-size:.85rem', text: p.full_name[0].toUpperCase()}),
        h('span', {}, h('span', {class: 'fw-semibold d-block', text: p.full_name}),
          h('span', {class: 'small hb-muted', text: `${p.patient_id}${p.country ? ' · ' + p.country : ''}`}))))
      : [h('div', {class: 'small hb-muted p-2'}, icon('search', 'me-1'), 'No patient found')]);
  } catch (err) { showList([h('div', {class: 'small text-danger p-2', text: err.message})]); }
}

if (form) input.addEventListener('input', () => { clearTimeout(lookupTimer); lookupTimer = setTimeout(lookup, 250); });
if (form) input.addEventListener('focus', lookup);
if (form) input.addEventListener('blur', () => setTimeout(() => showList([]), 150));
if (form) input.addEventListener('keydown', e => { if (e.key === 'Escape') showList([]); });

if (form) form.addEventListener('submit', async e => {
  e.preventDefault();
  clearErrors(form);
  $('#requestOk').classList.add('d-none');
  const code = input.value.trim().toUpperCase();
  if (!/^HC-[A-Z0-9]{4,12}$/.test(code)) return showErrors(form, {message: 'Enter a valid Patient ID, e.g. HC-8F3A92C1.', errors: {patient_id: 'Enter a valid Patient ID, e.g. HC-8F3A92C1'}});
  await withBusy($('#sendBtn'), async () => {
    try {
      const r = await api('/api/doctor/access-requests', {method: 'POST', body: {patient_id: code}});
      $('#requestOk').textContent = r.message;
      $('#requestOk').classList.remove('d-none');
      form.reset();
      showList([]);
      refresh();
    } catch (err) { showErrors(form, err); }
  });
});

refresh();
