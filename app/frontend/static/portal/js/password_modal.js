// Shared Change Password modal (patient and doctor profiles). Same rules and endpoint for both roles.
const pwForm = $('#pwForm');
bindPasswordRules($('#new_password'), $('#pwRules'));
$('#pwModal').addEventListener('show.bs.modal', () => {
  pwForm.reset(); clearErrors(pwForm);
  $('#new_password').dispatchEvent(new Event('input'));
});
$('#pwModal').addEventListener('shown.bs.modal', () => $('#current_password').focus());
pwForm.addEventListener('submit', async e => {
  e.preventDefault();
  const d = formData(pwForm);
  const errors = {};
  if (!d.current_password) errors.current_password = 'Enter your current password';
  if (!d.new_password) errors.new_password = 'Enter a new password';
  else if (!PW_RULES.every(([, , t]) => t(d.new_password))) errors.new_password = 'Password does not meet all the requirements';
  if (d.new_password && d.new_password !== d.confirm_new_password) errors.confirm_new_password = 'Passwords do not match';
  if (Object.keys(errors).length) return showErrors(pwForm, {message: 'Please fix the highlighted fields.', errors});
  await withBusy($('#pwSave'), async () => {
    try {
      const r = await api('/api/auth/change-password', {method: 'POST', body: d});
      bootstrap.Modal.getInstance($('#pwModal')).hide();
      toast(r.message || 'Password updated');
    } catch (err) { showErrors(pwForm, err); }
  });
});

