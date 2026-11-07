// Doctor sidebar: the patient opened from Patient Records stays listed under the main links with its record sections.
const PATIENT_SECTIONS = [
  ['medications', 'Medications', 'capsule'],
  ['conditions', 'Conditions', 'heart-pulse'],
  ['procedures', 'Procedures', 'bandaid'],
  ['allergies', 'Allergies', 'exclamation-triangle'],
  ['documents', 'Documents', 'file-earmark-text'],
  ['flags', 'Flags', 'flag'],
];
const OPEN_KEY = 'hb_open_patient';

function getOpenPatient() {
  try { return JSON.parse(sessionStorage.getItem(OPEN_KEY)); } catch { return null; }
}
function setOpenPatient(p) {
  try { p ? sessionStorage.setItem(OPEN_KEY, JSON.stringify(p)) : sessionStorage.removeItem(OPEN_KEY); } catch { /* optional */ }
  renderPatientNav();
}

// active = the section shown right now (only on the Patient Records page)
function renderPatientNav(active) {
  const box = document.getElementById('patientNav');
  if (!box) return;
  const p = getOpenPatient();
  box.classList.toggle('d-none', !p);
  if (!p) return box.replaceChildren();
  const url = s => `/doctor/patients?patient=${encodeURIComponent(p.id)}&section=${s}`;
  box.replaceChildren(
    h('div', {class: 'pn-label'}, h('span', {text: 'Open patient'}),
      h('button', {type: 'button', class: 'pn-close', title: 'Close patient', 'aria-label': `Close ${p.name}`, onclick: closeOpenPatient}, icon('x-lg'))),
    h('div', {class: 'pn-patient'},
      h('span', {class: 'pn-avatar', text: (p.name || '?')[0].toUpperCase()}),
      h('div', {class: 'min-w-0'}, h('div', {class: 'pn-name text-truncate', text: p.name}), h('div', {class: 'pn-id', text: p.id}))),
    h('div', {class: 'pn-links'}, PATIENT_SECTIONS.map(([key, label, ic]) => h('a', {
      href: url(key), 'data-section': key, class: key === active ? 'active' : '', ...(key === active ? {'aria-current': 'page'} : {})},
      icon(ic), label))));
}

function closeOpenPatient() {
  const p = getOpenPatient();
  setOpenPatient(null);
  if (location.pathname === '/doctor/patients' && p && new URLSearchParams(location.search).get('patient') === p.id) location.href = '/doctor/patients';
}

renderPatientNav();
