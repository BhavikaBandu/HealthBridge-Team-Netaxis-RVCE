const form = $('#uploadForm');
const modal = () => bootstrap.Modal.getOrCreateInstance($('#uploadModal'));
const MAX_MB = 10;
const TYPE_LABEL = {medication: 'Medication', condition: 'Condition', procedure: 'Procedure', allergy: 'Allergy'};
let editing = null;
let records = [];

function linkPills(doc) {
  if (!doc.links.length) return h('span', {class: 'hb-muted', text: 'No link'});
  return h('div', {}, doc.links.map(l => h('span', {class: `link-pill ${l.record_archived || l.missing ? 'archived' : ''}`},
    icon('link-45deg'), `${TYPE_LABEL[l.record_type]}: ${l.label}`, l.record_archived ? ' (archived record)' : '')));
}

function actions(doc) {
  const items = [
    h('li', {}, h('a', {class: 'dropdown-item', href: `/api/documents/${doc.id}/download?inline=1`, target: '_blank', rel: 'noopener'}, icon('eye', 'me-2'), 'Preview')),
    h('li', {}, h('a', {class: 'dropdown-item', href: `/api/documents/${doc.id}/download`}, icon('download', 'me-2'), 'Download')),
  ];
  if (!doc.archived) items.push(h('li', {}, h('button', {class: 'dropdown-item', type: 'button', onclick: () => openForm(doc)}, icon('pencil', 'me-2'), 'Edit details & link')));
  items.push(h('li', {}, h('hr', {class: 'dropdown-divider'})));
  items.push(h('li', {}, doc.archived
    ? h('button', {class: 'dropdown-item', type: 'button', onclick: () => archive(doc, false)}, icon('arrow-counterclockwise', 'me-2'), 'Restore')
    : h('button', {class: 'dropdown-item', type: 'button', onclick: () => archive(doc, true)}, icon('archive', 'me-2'), 'Archive')));
  items.push(h('li', {}, h('button', {class: 'dropdown-item text-danger', type: 'button', onclick: () => remove(doc)}, icon('trash', 'me-2'), 'Delete permanently')));
  return h('td', {class: 'text-end'}, h('div', {class: 'dropdown'},
    h('button', {class: 'btn btn-icon btn-light', type: 'button', 'data-bs-toggle': 'dropdown', 'data-bs-popper-config': '{"strategy":"fixed"}', 'aria-expanded': 'false', 'aria-label': 'Document actions'}, icon('three-dots')),
    h('ul', {class: 'dropdown-menu dropdown-menu-end'}, items)));
}

async function load() {
  const p = new URLSearchParams();
  if ($('#q').value.trim()) p.set('q', $('#q').value.trim());
  if ($('#typeFilter').value) p.set('doc_type', $('#typeFilter').value);
  if ($('#showArchived').checked) p.set('archived', 'true');
  $('#table tbody').replaceChildren(h('tr', {}, h('td', {colspan: 6}, h('div', {class: 'skeleton', style: 'height:22px'}))));
  $('#empty').replaceChildren();
  try {
    const data = await api(`/api/documents?${p}`);
    $('#table tbody').replaceChildren(...data.items.map(d => h('tr', {class: d.archived ? 'archived' : ''},
      h('td', {}, h('div', {class: 'd-flex align-items-center gap-2'},
        h('span', {class: `doc-icon ${d.mime_type === 'application/pdf' ? '' : 'img'}`}, icon(d.mime_type === 'application/pdf' ? 'file-earmark-pdf' : 'file-earmark-image')),
        h('div', {class: 'min-w-0'}, h('div', {class: 'primary', text: d.name}),
          h('div', {class: 'sub', text: `${d.original_filename} · ${fmtSize(d.size_bytes)}`}),
          d.notes ? h('div', {class: 'sub fst-italic', text: d.notes}) : null))),
      h('td', {text: d.doc_type_label}),
      h('td', {class: 'text-nowrap', text: fmtDate(d.document_date)}),
      h('td', {}, linkPills(d)),
      h('td', {class: 'text-nowrap sub', text: fmtWhen(d.uploaded_at)}),
      actions(d))));
    $('#table').classList.toggle('d-none', !data.items.length);
    if (!data.items.length) {
      const filtered = p.has('q') || p.has('doc_type');
      $('#empty').replaceChildren(p.has('archived') ? emptyState('archive', 'No archived documents', null)
        : filtered ? emptyState('search', 'No matching documents', 'Try a different search or type.')
        : emptyState('folder2-open', 'No documents yet', 'Upload reports, prescriptions or scans to keep them with your records.',
            h('button', {class: 'btn btn-primary', type: 'button', onclick: () => openForm(null)}, icon('cloud-arrow-up', 'me-1'), 'Upload Document')));
    }
  } catch (err) {
    $('#table tbody').replaceChildren(h('tr', {}, h('td', {colspan: 6, class: 'text-danger', text: err.message})));
  }
}

async function loadRecords() {
  records = await api('/api/history-records');
  const sel = $('#d_link');
  const groups = Object.entries(TYPE_LABEL).map(([type, label]) => {
    const opts = records.filter(r => r.record_type === type)
      .map(r => h('option', {value: `${type}:${r.record_id}`, text: r.label + (r.archived ? ' (archived)' : '')}));
    return opts.length ? h('optgroup', {label: label + 's'}, opts) : null;
  }).filter(Boolean);
  sel.replaceChildren(h('option', {value: '', text: records.length ? 'No link' : 'No link (add medical history first)'}), ...groups);
}

function openForm(doc) {
  editing = doc;
  form.reset(); clearErrors(form);
  $('#upTitle').textContent = doc ? 'Edit Document' : 'Upload Document';
  $('#upSave').textContent = doc ? 'Save Changes' : 'Upload';
  $('#fileWrap').classList.toggle('d-none', !!doc);
  const existing = $('#existingLinks');
  existing.classList.toggle('d-none', !(doc && doc.links.length));
  if (doc) {
    fillForm(form, doc);
    // Single link in the UI: preselect the first link; others (from the API) are shown so they can be removed.
    $('#d_link').value = doc.links.length ? `${doc.links[0].record_type}:${doc.links[0].record_id}` : '';
    existing.replaceChildren(h('div', {class: 'section-label mt-0', text: 'Current links'}),
      ...doc.links.map(l => h('span', {class: 'link-pill me-2'}, `${TYPE_LABEL[l.record_type]}: ${l.label}`,
        h('button', {type: 'button', class: 'btn btn-sm p-0 ms-1', 'aria-label': `Unlink ${l.label}`, onclick: () => unlink(doc, l)}, icon('x-lg')))));
  }
  modal().show();
}

async function unlink(doc, link) {
  try {
    const updated = await api(`/api/documents/${doc.id}/links/${link.link_id}`, {method: 'DELETE'});
    toast('Link removed');
    openForm(updated); load();
  } catch (err) { toast(err.message, 'error'); }
}

async function archive(doc, on) {
  if (on && !await confirmDialog({title: 'Archive document?', message: `“${doc.name}” will be hidden from your documents. You can restore it later.`, confirmText: 'Archive'})) return;
  try { await api(`/api/documents/${doc.id}/${on ? 'archive' : 'restore'}`, {method: 'POST'}); toast(on ? 'Document archived' : 'Document restored'); reprocessPrompt(); load(); }
  catch (err) { toast(err.message, 'error'); }
}

async function remove(doc) {
  if (!await confirmDialog({title: 'Delete document permanently?', message: `“${doc.name}” and its file will be deleted, and any links removed. This cannot be undone.`, confirmText: 'Delete', danger: true})) return;
  try { await api(`/api/documents/${doc.id}`, {method: 'DELETE'}); toast('Document deleted'); reprocessPrompt(); load(); }
  catch (err) { toast(err.message, 'error'); }
}

$('#file').addEventListener('change', () => {
  const f = $('#file').files[0];
  if (f && !$('#d_name').value) $('#d_name').value = f.name.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ').slice(0, 200);
});

form.addEventListener('submit', async e => {
  e.preventDefault();
  const d = formData(form);
  const errors = {};
  const file = $('#file').files[0];
  if (!editing) {
    if (!file) errors.file = 'Choose a file to upload';
    else if (!/\.(pdf|jpe?g|png)$/i.test(file.name)) errors.file = 'Only PDF, JPG and PNG files are accepted';
    else if (file.size > MAX_MB * 1024 * 1024) errors.file = `File is larger than ${MAX_MB} MB`;
  }
  if (!d.name) errors.name = 'Enter a document name';
  if (!d.doc_type) errors.doc_type = 'Choose a document type';
  if (Object.keys(errors).length) return showErrors(form, {message: 'Please fix the highlighted fields.', errors});
  const [recordType, recordId] = (d.link || '').split(':');
  await withBusy($('#upSave'), async () => {
    try {
      if (editing) {
        await api(`/api/documents/${editing.id}`, {method: 'PATCH', body: {name: d.name, doc_type: d.doc_type, document_date: d.document_date, notes: d.notes}});
        const current = editing.links[0];
        const same = current && current.record_type === recordType && current.record_id === recordId;
        if (current && !same) await api(`/api/documents/${editing.id}/links/${current.link_id}`, {method: 'DELETE'});
        if (recordType && !same) await api(`/api/documents/${editing.id}/links`, {method: 'POST', body: {record_type: recordType, record_id: recordId}});
        toast('Document updated');
        reprocessPrompt();
      } else {
        const fd = new FormData();
        fd.append('file', file);
        for (const k of ['name', 'doc_type', 'document_date', 'notes']) if (d[k]) fd.append(k, d[k]);
        if (recordType) { fd.append('record_type', recordType); fd.append('record_id', recordId); }
        await api('/api/documents', {method: 'POST', form: fd});
        toast('Document uploaded');
        reprocessPrompt();
      }
      modal().hide();
      load();
    } catch (err) { showErrors(form, err); }
  });
});

let qTimer;
$('#q').addEventListener('input', () => { clearTimeout(qTimer); qTimer = setTimeout(load, 250); });
$('#typeFilter').addEventListener('change', load);
$('#showArchived').addEventListener('change', load);
$('#uploadBtn').addEventListener('click', () => openForm(null));

(async () => {
  const ref = await reference();
  for (const [k, v] of Object.entries(ref.document_types)) {
    $('#typeFilter').append(h('option', {value: k, text: v}));
    $('#d_type').append(h('option', {value: k, text: v}));
  }
  await loadRecords().catch(() => {});
  await load();
  if (new URLSearchParams(location.search).get('new')) { history.replaceState(null, '', '/documents'); openForm(null); }
})();
