const params = new URLSearchParams(location.search);
let kind = ['medications', 'conditions', 'procedures', 'allergies'].includes(params.get('tab')) ? params.get('tab') : 'medications';
let editing = null;
let declaration = 'unknown';

const formFor = k => $(`#${k}Modal form`);
const modalFor = k => bootstrap.Modal.getOrCreateInstance($(`#${k}Modal`));

// ---------- list ----------
async function loadCounts() {
  await Promise.all(Object.keys(KINDS).map(async k => {
    try { $(`[data-count="${k}"]`).textContent = (await api(`/api/${k}?limit=1`)).total; } catch { /* ignore */ }
  }));
}

function actionsCell(item) {
  return h('td', {class: 'text-end'}, h('div', {class: 'dropdown'},
    h('button', {class: 'btn btn-icon btn-light', type: 'button', 'data-bs-toggle': 'dropdown', 'data-bs-popper-config': '{"strategy":"fixed"}', 'aria-expanded': 'false', 'aria-label': 'Actions'}, icon('three-dots')),
    h('ul', {class: 'dropdown-menu dropdown-menu-end'},
      item.archived || item.reported_by_role === 'doctor' ? null  // doctor-added entries can be archived, not edited
        : h('li', {}, h('button', {class: 'dropdown-item', type: 'button', onclick: () => openForm(item)}, icon('pencil', 'me-2'), 'Edit')),
      h('li', {}, item.archived
        ? h('button', {class: 'dropdown-item', type: 'button', onclick: () => setArchived(item, false)}, icon('arrow-counterclockwise', 'me-2'), 'Restore')
        : h('button', {class: 'dropdown-item text-danger', type: 'button', onclick: () => setArchived(item, true)}, icon('archive', 'me-2'), 'Archive')))));
}

async function load() {
  const cfg = KINDS[kind];
  const p = new URLSearchParams();
  if ($('#q').value.trim()) p.set('q', $('#q').value.trim());
  if ($('#statusFilter').value) p.set('status', $('#statusFilter').value);
  if ($('#showArchived').checked) p.set('archived', 'true');
  $('#table thead').replaceChildren(h('tr', {}, cfg.cols.map(c => h('th', {text: c}))));
  $('#table tbody').replaceChildren(h('tr', {}, h('td', {colspan: cfg.cols.length}, h('div', {class: 'skeleton', style: 'height:22px'}))));
  $('#empty').replaceChildren();
  try {
    const data = await api(`/api/${kind}?${p}`);
    $('#table tbody').replaceChildren(...data.items.map(item => h('tr', {class: item.archived ? 'archived' : ''}, cfg.row(item), actionsCell(item))));
    $('#table').classList.toggle('d-none', !data.items.length);
    if (!data.items.length) {
      const filtered = p.has('q') || p.has('status');
      let text = filtered ? 'Try a different search or filter.' : `Add your first ${cfg.singular.toLowerCase()} to keep your history up to date.`;
      if (kind === 'allergies' && !filtered && !p.has('archived')) {
        text = declaration === 'none' ? 'You have declared no known allergies.'
          : declaration === 'unknown' ? 'Your allergy status is unknown. Choose an option above.' : 'Add the allergies you know about.';
      }
      $('#empty').replaceChildren(emptyState(p.has('archived') ? 'archive' : 'journal-medical', p.has('archived') ? 'Nothing archived' : `No ${cfg.singular.toLowerCase()} records`, text));
    }
  } catch (err) {
    $('#table tbody').replaceChildren(h('tr', {}, h('td', {colspan: cfg.cols.length, class: 'text-danger', text: err.message})));
  }
}

async function setArchived(item, archive) {
  const cfg = KINDS[kind];
  const name = item.name || item.allergen;
  if (archive && !await confirmDialog({title: `Archive ${cfg.singular.toLowerCase()}?`,
    message: `“${name}” will be moved to your archive. Linked documents are kept. You can restore it later.`, confirmText: 'Archive'})) return;
  try {
    await api(`/api/${kind}/${item.id}/${archive ? 'archive' : 'restore'}`, {method: 'POST'});
    toast(archive ? `${cfg.singular} archived` : `${cfg.singular} restored`);
    if (kind !== 'conditions') reprocessPrompt();   // conditions are not analysed
    load(); loadCounts();
  } catch (err) { toast(err.message, 'error'); }
}

// ---------- allergy declaration ----------
const DECL_HINT = {unknown: 'Not stated yet. An empty list does not mean you have no allergies.',
  none: 'You have stated that you have no known allergies.', known: 'Add each allergy below.'};
function renderDeclaration() {
  $$('input[name="declaration"]').forEach(r => { r.checked = r.value === declaration; });
  $('#declHint').textContent = DECL_HINT[declaration];
  if (kind === 'allergies') $('#addBtn').disabled = declaration !== 'known';
}
$$('input[name="declaration"]').forEach(r => r.addEventListener('change', async () => {
  const previous = declaration;
  try {
    declaration = (await api('/api/allergy-declaration', {method: 'PUT', body: {declaration: r.value}})).declaration;
    toast('Allergy status updated');
  } catch (err) { declaration = previous; toast(err.message, 'error'); }
  renderDeclaration(); load();
}));

// ---------- forms ----------
function openForm(item) {
  editing = item;
  const form = formFor(kind), cfg = KINDS[kind];
  form.reset(); clearErrors(form);
  form.closest('.modal-content').querySelector('.modal-title').textContent = item ? `Edit ${cfg.singular}` : cfg.add;
  if (item) {
    fillForm(form, item);
    if (kind === 'medications') {
      for (const k of ['morning', 'afternoon', 'night', 'as_needed']) form[`sch_${k}`].checked = !!item.schedule[k];
      form.sch_custom.value = item.schedule.custom || '';
    }
  }
  if (kind === 'medications') syncMedication(form);
  modalFor(kind).show();
}

$$('form[data-kind]').forEach(form => {
  const k = form.dataset.kind;
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const body = payload(k, form);
    const errors = clientErrors(k, body);
    if (Object.keys(errors).length) return showErrors(form, {message: 'Please fix the highlighted fields.', errors});
    await withBusy(form.querySelector('[data-save]'), async () => {
      try {
        await api(editing ? `/api/${k}/${editing.id}` : `/api/${k}`, {method: editing ? 'PATCH' : 'POST', body});
        modalFor(k).hide();
        toast(editing ? `${KINDS[k].singular} updated` : `${KINDS[k].singular} added`);
        if (k !== 'conditions') reprocessPrompt();
        load(); loadCounts();
      } catch (err) { showErrors(form, err); }
    });
  });
});

// ---------- tabs & filters ----------
function selectTab(k) {
  kind = k;
  $$('#kindTabs [data-kind]').forEach(b => b.classList.toggle('active', b.dataset.kind === k));
  $('#addBtn span').textContent = KINDS[k].add;
  $('#addBtn').disabled = k === 'allergies' && declaration !== 'known';
  $('#allergyDecl').classList.toggle('d-none', k !== 'allergies');
  $('#statusFilter').replaceChildren(...KINDS[k].statuses.map(([v, l]) => h('option', {value: v, text: v ? l : 'All statuses'})));
  $('#q').value = '';
  history.replaceState(null, '', `/medical-history?tab=${k}`);
  load();
}
$$('#kindTabs [data-kind]').forEach(b => b.addEventListener('click', () => selectTab(b.dataset.kind)));
let qTimer;
$('#q').addEventListener('input', () => { clearTimeout(qTimer); qTimer = setTimeout(load, 250); });
$('#statusFilter').addEventListener('change', load);
$('#showArchived').addEventListener('change', load);
$('#addBtn').addEventListener('click', () => openForm(null));

(async () => {
  bindHistoryForms();
  await fillHistoryFormOptions();
  try { declaration = (await api('/api/allergy-declaration')).declaration; } catch { /* ignore */ }
  renderDeclaration();
  selectTab(kind);
  loadCounts();
  if (params.get('new') && kind !== 'allergies') openForm(null);
})();
