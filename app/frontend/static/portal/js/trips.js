let editing = null;
const form = $('#tripForm');
const modal = () => bootstrap.Modal.getOrCreateInstance($('#tripModal'));
const STATUS = {planned: 'Planned', ongoing: 'Ongoing', completed: 'Completed'};

function syncPurpose() {
  const special = form.purpose_type.value === 'specialised';
  $('#descWrap').classList.toggle('d-none', !special);
}
$$('input[name="purpose_type"]').forEach(r => r.addEventListener('change', syncPurpose));
$('#departure_date').addEventListener('change', () => { $('#return_date').min = $('#departure_date').value; });

function openForm(trip) {
  editing = trip;
  form.reset(); clearErrors(form);
  $('#tripTitle').textContent = trip ? 'Edit Trip' : 'Create New Trip';
  $('#tripSave').textContent = trip ? 'Save Changes' : 'Create Trip';
  if (trip) fillForm(form, trip);
  syncPurpose();
  modal().show();
}

function tripCard(t) {
  const dates = h('div', {class: 'small hb-muted'}, icon('calendar3', 'me-1'), fmtDate(t.departure_date), ' – ',
    t.return_date ? fmtDate(t.return_date) : h('span', {class: 'fst-italic', text: 'no return date'}));
  const menu = h('div', {class: 'dropdown ms-auto'},
    h('button', {class: 'btn btn-icon btn-light', type: 'button', 'data-bs-toggle': 'dropdown', 'data-bs-popper-config': '{"strategy":"fixed"}', 'aria-expanded': 'false', 'aria-label': 'Trip actions'}, icon('three-dots')),
    h('ul', {class: 'dropdown-menu dropdown-menu-end'},
      t.archived ? null : h('li', {}, h('button', {class: 'dropdown-item', type: 'button', onclick: () => openForm(t)}, icon('pencil', 'me-2'), 'Edit')),
      h('li', {}, t.archived
        ? h('button', {class: 'dropdown-item', type: 'button', onclick: () => setArchived(t, false)}, icon('arrow-counterclockwise', 'me-2'), 'Restore')
        : h('button', {class: 'dropdown-item text-danger', type: 'button', onclick: () => setArchived(t, true)}, icon('archive', 'me-2'), 'Archive'))));
  return h('div', {class: `hb-card trip-card ${t.archived ? 'archived' : ''}`},
    h('div', {class: 'thumb'}, icon(t.purpose_type === 'specialised' ? 'hospital' : 'airplane')),
    h('div', {class: 'flex-grow-1 min-w-0'},
      h('div', {class: 'd-flex flex-wrap align-items-center gap-2 mb-1'}, chip(t.status, STATUS[t.status]),
        t.archived ? chip('archived', 'Archived') : null, h('span', {class: 'chip chip-teal', text: t.purpose_label})),
      h('div', {class: 'route', text: `${t.origin_name} → ${t.destination_name}`}),
      dates,
      t.purpose_description ? h('div', {class: 'small mt-1 text-truncate', title: t.purpose_description, text: t.purpose_description}) : null),
    menu);
}

async function setArchived(t, archive) {
  if (archive && !await confirmDialog({title: 'Archive trip?', message: `${t.origin_name} → ${t.destination_name} will be removed from your trips list.`, confirmText: 'Archive'})) return;
  try {
    await api(`/api/trips/${t.id}/${archive ? 'archive' : 'restore'}`, {method: 'POST'});
    toast(archive ? 'Trip archived' : 'Trip restored');
    load();
  } catch (err) { toast(err.message, 'error'); }
}

async function load() {
  try {
    const {items} = await api('/api/trips');  // active trips only
    $('#tripList').replaceChildren(...(items.length ? items.map(tripCard) : [h('div', {class: 'hb-card'},
      emptyState('airplane', 'No trips yet', 'Create a trip to plan travel or specialised care.',
        h('button', {class: 'btn btn-primary', type: 'button', onclick: () => openForm(null)}, icon('plus-lg', 'me-1'), 'Create Trip')))]));
  } catch (err) { $('#tripList').replaceChildren(h('div', {class: 'alert alert-danger', text: err.message})); }
}

form.addEventListener('submit', async e => {
  e.preventDefault();
  const d = formData(form);
  const errors = {};
  if (!d.origin_country) errors.origin_country = 'Select the origin country';
  if (!d.destination_country) errors.destination_country = 'Select the destination country';
  if (d.origin_country && d.origin_country === d.destination_country) errors.destination_country = 'Destination must be different from origin';
  if (!d.departure_date) errors.departure_date = 'Enter the departure date';
  if (d.return_date && d.departure_date && d.return_date < d.departure_date) errors.return_date = 'Return date cannot be before departure';
  if (d.purpose_type === 'specialised' && !d.purpose_description) errors.purpose_description = 'Briefly describe the specialised care';
  if (d.purpose_type !== 'specialised') d.purpose_description = null;
  if (Object.keys(errors).length) return showErrors(form, {message: 'Please fix the highlighted fields.', errors});
  await withBusy($('#tripSave'), async () => {
    try {
      await api(editing ? `/api/trips/${editing.id}` : '/api/trips', {method: editing ? 'PATCH' : 'POST', body: d});
      modal().hide();
      toast(editing ? 'Trip updated' : 'Trip created');
      load();
    } catch (err) { showErrors(form, err); }
  });
});

$('#newTrip').addEventListener('click', () => openForm(null));

(async () => {
  await Promise.all([fillCountrySelect($('#origin_country')), fillCountrySelect($('#destination_country'))]);
  await load();
  if (new URLSearchParams(location.search).get('new')) { history.replaceState(null, '', '/trips'); openForm(null); }
})();
