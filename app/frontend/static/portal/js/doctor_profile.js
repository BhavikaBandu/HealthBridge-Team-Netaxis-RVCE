let profile;
const form = $('#profileForm');

const initials = name => (name || 'DR').replace(/^dr\.?\s+/i, '').split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join('') || 'DR';

function row(label, value, extra) {
  return h('div', {class: 'profile-row'},
    h('div', {}, h('div', {class: 'k', text: label}), h('div', {class: `v ${value ? '' : 'hb-muted fw-normal'}`, text: value || 'Not provided'})),
    extra || null);
}

function render() {
  const p = profile;
  $('#nameHeading').textContent = p.full_name;
  $('#avatar').textContent = initials(p.full_name);
  $('#profileView').replaceChildren(
    row('Full name', p.full_name),
    row('Email', p.email),
    row('Phone number', p.phone),
    row('Origin country', p.origin_country_name),
    row('Preferred language', p.preferred_language_name),
    row('Hospital', p.hospital),
    row('Domain / medical speciality', p.speciality));
  // Registration number sits under the Doctor ID in the header, with a copy button.
  const reg = $('#regLine');
  if (p.registration_number) {
    $('#regValue').textContent = p.registration_number;
    $('#regCopy').dataset.copy = p.registration_number;
    reg.classList.remove('d-none');
  }
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
    try { profile = await api('/api/doctor/profile', {method: 'PATCH', body: data}); render(); toggleEdit(false); toast('Profile updated'); }
    catch (err) { showErrors(form, err); }
  });
});

(async () => {
  await fillCountrySelect($('#origin_country'), {placeholder: 'Select country'});
  try { profile = await api('/api/doctor/profile'); render(); }
  catch (err) { $('#profileView').replaceChildren(h('div', {class: 'text-danger', text: err.message})); }
})();
