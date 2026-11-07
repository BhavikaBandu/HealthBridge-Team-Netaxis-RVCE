let profile;
const form = $('#profileForm');

function row(label, value, extra) {
  return h('div', {class: 'profile-row'},
    h('div', {}, h('div', {class: 'k', text: label}), h('div', {class: 'v', text: value || 'Not provided'}, value ? null : null)),
    extra || null);
}

function render() {
  const p = profile;
  $('#nameHeading').textContent = p.full_name;
  $('#avatar').textContent = (p.full_name || 'P')[0].toUpperCase();
  $('#profileView').replaceChildren(
    row('Full name', p.full_name),
    row('Email', p.email),
    row('Phone number', p.phone),
    row('Origin country', p.origin_country_name),
    row('Preferred language', p.preferred_language_name),
    row('Member since', fmtDate(p.member_since.slice(0, 10))));
  $$('#profileView .v').forEach(v => { if (v.textContent === 'Not provided') v.classList.add('hb-muted', 'fw-normal'); });
  const body = $('#completeness .hb-card-body');
  body.replaceChildren(p.profile_complete
    ? h('div', {class: 'd-flex gap-2 align-items-center'}, icon('check-circle-fill', 'text-success fs-5'), 'Your profile is complete.')
    : h('div', {class: 'd-flex gap-2'}, icon('exclamation-circle-fill', 'text-warning fs-5'),
        h('div', {}, h('div', {class: 'fw-semibold', text: 'Profile incomplete'}), `Please add your ${p.missing_fields.join(' and ')}.`)));
}

function toggleEdit(on) {
  form.classList.toggle('d-none', !on);
  $('#profileView').classList.toggle('d-none', on);
  $('#editBtn').classList.toggle('d-none', on);
  if (on) { clearErrors(form); fillForm(form, profile); $('#full_name').focus(); }
}

$('#editBtn').addEventListener('click', () => toggleEdit(true));
$('#cancelEdit').addEventListener('click', () => toggleEdit(false));
form.addEventListener('submit', async e => {
  e.preventDefault();
  const data = formData(form);
  if (!data.full_name) return showErrors(form, {message: 'Full name is required', errors: {full_name: 'Full name is required'}});
  if (!data.email) return showErrors(form, {message: 'Email is required', errors: {email: 'Email is required'}});
  await withBusy($('#saveProfile'), async () => {
    try {
      profile = await api('/api/profile', {method: 'PATCH', body: data});
      render(); toggleEdit(false); toast('Profile updated');
    } catch (err) { showErrors(form, err); }
  });
});

(async () => {
  await fillCountrySelect($('#origin_country'), {placeholder: 'Select country'});
  try { profile = await api('/api/profile'); render(); }
  catch (err) { $('#profileView').replaceChildren(h('div', {class: 'text-danger', text: err.message})); }
})();
