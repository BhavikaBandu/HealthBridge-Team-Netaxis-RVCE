const form = $('#loginForm');
const role = () => $('input[name="role"]:checked').value;

const HOME = {patient: '/dashboard', doctor: '/doctor/dashboard'};

function applyRole() {
  const doctor = role() === 'doctor';
  $('#signupHref').href = doctor ? '/doctor/signup' : '/signup';
  $('#signupHref').textContent = doctor ? 'Create a doctor account' : 'Create a patient account';
  clearErrors(form);
}
if (new URLSearchParams(location.search).get('role') === 'doctor') $('#roleDoctor').checked = true;
$$('input[name="role"]').forEach(r => r.addEventListener('change', applyRole));

form.addEventListener('submit', async e => {
  e.preventDefault();
  clearErrors(form);
  const data = formData(form);
  if (!data.email || !data.password) {
    showErrors(form, {message: 'Enter your email and password.', errors: {
      ...(data.email ? {} : {email: 'Enter your email address'}), ...(data.password ? {} : {password: 'Enter your password'})}});
    return;
  }
  const btn = $('#loginBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Signing in…';
  try {
    const me = await api('/api/auth/login', {method: 'POST', body: {email: data.email, password: data.password, remember: data.remember, role: role()}});
    window.location.href = HOME[me.role] || '/login';  // each role has its own portal
  } catch (err) {
    showErrors(form, err);
    btn.disabled = false;
    btn.textContent = 'Sign in';
  }
});
applyRole();
$('#email').focus();
