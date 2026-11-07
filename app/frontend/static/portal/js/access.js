// Patient > Doctor Access: accept or reject doctor requests, revoke access.
function doctorLine(r) {
  const d = r.doctor || {};
  const details = [d.doctor_id, d.speciality, d.hospital, d.country].filter(Boolean).join(' · ');
  return h('div', {class: 'flex-grow-1 min-w-0'},
    h('div', {class: 'fw-semibold'}, d.full_name || 'Doctor', d.verified ? h('span', {class: 'chip chip-teal ms-2'}, icon('patch-check'), 'Verified account') : null),
    h('div', {class: 'small hb-muted text-truncate', text: details}),
    h('div', {class: 'small hb-muted', text: r.status === 'pending' ? `Requested ${fmtWhen(r.requested_at)}` : `Access since ${fmtWhen(r.decided_at)}`}));
}

async function decide(r, decision) {
  const d = r.doctor || {};
  if (decision === 'accept' && !await confirmDialog({title: 'Give this doctor access?',
    message: `${d.full_name} (${d.doctor_id}) will be able to view your trips, medical history and documents, and add medical-history entries. You can revoke access at any time.`,
    confirmText: 'Accept'})) return;
  try { await api(`/api/access-requests/${r.id}/decision`, {method: 'POST', body: {decision}}); toast(decision === 'accept' ? 'Access granted' : 'Request declined'); loadAccess(); }
  catch (err) { toast(err.message, 'error'); }
}

async function revoke(r) {
  const d = r.doctor || {};
  if (!await confirmDialog({title: 'Revoke access?', message: `${d.full_name} will immediately lose access to your records.`, confirmText: 'Revoke', danger: true})) return;
  try { await api(`/api/access-grants/${r.id}/revoke`, {method: 'POST'}); toast('Access revoked'); loadAccess(); }
  catch (err) { toast(err.message, 'error'); }
}

async function loadAccess() {
  try {
    const a = await api('/api/access-requests');
    $('#accessPending').replaceChildren(...(a.pending.length ? [h('div', {class: 'section-label mt-0', text: `Pending requests (${a.pending.length})`}),
      ...a.pending.map(r => h('div', {class: 'activity-item'}, h('span', {class: 'ic'}, icon('hospital')), doctorLine(r),
        h('div', {class: 'd-flex gap-2 flex-shrink-0'},
          h('button', {class: 'btn btn-sm btn-light', type: 'button', onclick: () => decide(r, 'reject')}, 'Reject'),
          h('button', {class: 'btn btn-sm btn-primary', type: 'button', onclick: () => decide(r, 'accept')}, 'Accept'))))] : []));
    if (!a.pending.length) {
      $('#accessPending').replaceChildren(h('div', {class: 'small hb-muted', text: 'No pending requests.'}));
    }
    $('#accessGranted').replaceChildren(...(a.granted.length ? a.granted.map(r => {
      const d = r.doctor || {};
      return h('tr', {},
        h('td', {}, h('div', {class: 'primary', text: d.full_name || 'Doctor'}), d.country ? h('div', {class: 'sub', text: d.country}) : null),
        h('td', {class: 'text-nowrap', text: d.doctor_id || '—'}),
        h('td', {text: d.speciality || '—'}),
        h('td', {text: d.hospital || '—'}),
        h('td', {class: 'text-nowrap sub', text: fmtWhen(r.decided_at)}),
        h('td', {class: 'text-end'}, h('button', {class: 'btn btn-sm btn-outline-danger', type: 'button', onclick: () => revoke(r)}, 'Revoke')));
    }) : [h('tr', {}, h('td', {colspan: 6}, emptyState('person-lock', 'No doctors have access', 'Doctors you accept will appear here. You can revoke access at any time.')))]));
  } catch (err) { $('#accessPending').replaceChildren(h('div', {class: 'text-danger small', text: err.message})); }
}
loadAccess();
