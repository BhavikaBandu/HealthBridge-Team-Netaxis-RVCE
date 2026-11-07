// Shared by patient and doctor sign-up; the form says where to post and where to go next.
const form = $('#signupForm');
const endpoint = form.dataset.endpoint || '/api/auth/signup';
const home = form.dataset.home || '/dashboard';
bindPasswordRules($('#password'), $('#pwRules'));
fillCountrySelect($('#origin_country'), {placeholder: 'Select country'});

form.addEventListener('submit', async e => {
  e.preventDefault();
  clearErrors(form);
  const data = formData(form);
  const errors = {};
  if (!data.full_name) errors.full_name = 'Enter your full name';
  if (!data.email) errors.email = 'Enter your email address';
  if (!data.password) errors.password = 'Create a password';
  else if (!PW_RULES.every(([, , t]) => t(data.password))) errors.password = 'Password does not meet all the requirements';
  if (data.password && data.password !== data.confirm_password) errors.confirm_password = 'Passwords do not match';
  if (Object.keys(errors).length) return showErrors(form, {message: 'Please fix the highlighted fields.', errors});
  await withBusy($('#signupBtn'), async () => {
    try {
      await api(endpoint, {method: 'POST', body: data});
      window.location.href = home;
    } catch (err) { showErrors(form, err); }
  });
});
$('#full_name').focus();
