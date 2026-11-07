// Shared by the patient Medical History page and the doctor Patient Records page:
// display config for the four record types and the add/edit form helpers (same rules for both portals).
const scheduleText = s => {
  const parts = ['morning', 'afternoon', 'night'].filter(k => s[k]).map(cap);
  if (s.as_needed) parts.push('As needed');
  if (s.custom) parts.push(s.custom);
  return parts.join(', ');
};
const docPills = docs => docs.length ? h('div', {}, docs.map(d => h('span', {class: `link-pill ${d.archived ? 'archived' : ''}`, title: d.archived ? 'Archived document' : ''}, icon('paperclip'), d.name))) : null;
// Who entered the record: patient -> "Self-reported"; doctor -> "Doctor reported" with the doctor's ID.
const reporter = item => item.reported_by_role === 'doctor'
  ? h('span', {class: 'chip chip-doctor', title: item.reported_by_id ? `Entered by doctor ${item.reported_by_id}` : 'Entered by a doctor'},
      icon('hospital'), item.reported_by_id ? `Doctor reported · ${item.reported_by_id}` : 'Doctor reported')
  : h('span', {class: 'chip chip-self', title: 'Entered by the patient; not clinically verified', text: item.reported_by_label || 'Self-reported'});

const KINDS = {
  medications: {
    singular: 'Medication', add: 'Add Medication',
    statuses: [['', 'All'], ['ongoing', 'Ongoing'], ['stopped', 'Stopped']],
    cols: ['Medicine', 'Dose & schedule', 'Duration', 'Status', ''],
    row: m => [
      h('td', {}, h('div', {class: 'primary', text: m.name}),
        h('div', {class: 'sub', text: [m.strength, m.dosage_form && cap(m.dosage_form), m.brand && `Brand: ${m.brand}`, m.manufacturer].filter(Boolean).join(' · ')}),
        docPills(m.documents)),
      h('td', {}, h('div', {text: m.dose || '—'}), h('div', {class: 'sub', text: scheduleText(m.schedule)}),
        m.instructions ? h('div', {class: 'sub fst-italic', text: m.instructions}) : null),
      h('td', {class: 'text-nowrap'}, h('div', {text: m.start_date_unknown ? 'Start unknown' : fmtDate(m.start_date)}),
        h('div', {class: 'sub', text: m.ongoing ? 'Ongoing' : `to ${fmtDate(m.stop_date)}`})),
      h('td', {}, chip(m.ongoing ? 'ongoing' : 'stopped', m.ongoing ? 'Ongoing' : 'Stopped'), ' ', reporter(m)),
    ],
  },
  conditions: {
    singular: 'Condition', add: 'Add Condition',
    statuses: [['', 'All'], ['active', 'Active'], ['resolved', 'Resolved'], ['unknown', 'Unknown']],
    cols: ['Condition', 'Diagnosed', 'Status', ''],
    row: c => [
      h('td', {}, h('div', {class: 'primary', text: c.name}), c.notes ? h('div', {class: 'sub', text: c.notes}) : null, docPills(c.documents)),
      h('td', {class: 'text-nowrap', text: c.diagnosis_date ? fmtDate(c.diagnosis_date) : (c.diagnosis_year || '—')}),
      h('td', {}, chip(c.status), ' ', reporter(c)),
    ],
  },
  procedures: {
    singular: 'Procedure', add: 'Add Procedure',
    statuses: [['', 'All'], ['completed', 'Completed'], ['planned', 'Planned']],
    cols: ['Procedure', 'Date', 'Where', 'Status', ''],
    row: p => [
      h('td', {}, h('div', {class: 'primary', text: p.name}), p.notes ? h('div', {class: 'sub', text: p.notes}) : null, docPills(p.documents)),
      h('td', {class: 'text-nowrap', text: fmtDate(p.procedure_date)}),
      h('td', {}, h('div', {text: p.hospital || '—'}), h('div', {class: 'sub', text: p.country_name || ''})),
      h('td', {}, chip(p.status === 'planned' ? 'planned' : 'completed', cap(p.status)), ' ', reporter(p)),
    ],
  },
  allergies: {
    singular: 'Allergy', add: 'Add Allergy',
    statuses: [['', 'All'], ['mild', 'Mild'], ['moderate', 'Moderate'], ['severe', 'Severe'], ['unknown', 'Unknown']],
    cols: ['Allergen', 'Reaction', 'Severity', ''],
    row: a => [
      h('td', {}, h('div', {class: 'primary', text: a.allergen}), a.notes ? h('div', {class: 'sub', text: a.notes}) : null, docPills(a.documents)),
      h('td', {text: a.reaction || '—'}),
      h('td', {}, chip(a.severity), ' ', reporter(a)),
    ],
  },
};

function syncMedication(form) {
  const ongoing = form.ongoing.checked;
  $('#stopWrap').classList.toggle('d-none', ongoing);
  if (ongoing) form.stop_date.value = '';
  form.start_date.disabled = form.start_date_unknown.checked;
  if (form.start_date_unknown.checked) form.start_date.value = '';
}

function payload(k, form) {
  const d = formData(form);
  if (k !== 'medications') {
    if (k === 'conditions' && d.diagnosis_year) d.diagnosis_year = Number(d.diagnosis_year);
    return d;
  }
  const out = {name: d.name, brand: d.brand, manufacturer: d.manufacturer, strength_value: d.strength_value ? Number(d.strength_value) : null,
    strength_unit: d.strength_unit, dosage_form: d.dosage_form, dose: d.dose, start_date: d.start_date,
    start_date_unknown: d.start_date_unknown, ongoing: d.ongoing, stop_date: d.ongoing ? null : d.stop_date, instructions: d.instructions,
    schedule: {morning: d.sch_morning, afternoon: d.sch_afternoon, night: d.sch_night, as_needed: d.sch_as_needed, custom: d.sch_custom}};
  return out;
}

function clientErrors(k, body) {
  const e = {};
  if (k === 'allergies') { if (!body.allergen) e.allergen = 'Allergen is required'; }
  else if (!body.name) e.name = `${KINDS[k].singular} name is required`;
  if (k === 'medications') {
    if (!body.start_date_unknown && !body.start_date) e.start_date = "Enter the start date, or tick 'Start date unknown'";
    if (!body.ongoing && !body.stop_date) e.stop_date = 'Enter the stop date (or switch Ongoing on)';
    if (!body.ongoing && body.stop_date && body.start_date && body.stop_date < body.start_date) e.stop_date = 'Stop date cannot be before the start date';
    if (body.strength_value && !body.strength_unit) e.strength_unit = 'Choose a unit';
  }
  return e;
}

function bindHistoryForms() {
  const med = $('form[data-kind="medications"]');
  if (med) {
    med.ongoing.addEventListener('change', () => syncMedication(med));
    med.start_date_unknown.addEventListener('change', () => syncMedication(med));
  }
}

async function fillHistoryFormOptions() {
  const ref = await reference();
  const unit = $('#medicationsModal [name="strength_unit"]'), formSel = $('#m_form');
  ref.strength_units.forEach(u => unit.append(h('option', {value: u, text: u})));
  ref.dosage_forms.forEach(f => formSel.append(h('option', {value: f, text: cap(f)})));
  await fillCountrySelect($('#p_country'), {placeholder: 'Select country'});
}
