// HealthBridge shared helpers. Untrusted text is always inserted with textContent (never innerHTML).
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

function h(tag, attrs = {}, ...children) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === 'class') e.className = v;
    else if (k === 'text') e.textContent = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
    else if (k === 'dataset') Object.assign(e.dataset, v);
    else e.setAttribute(k, v === true ? '' : v);
  }
  for (const c of children.flat()) if (c !== null && c !== undefined && c !== false) e.append(c instanceof Node ? c : String(c));
  return e;
}
const icon = (name, cls = '') => h('i', {class: `bi bi-${name} ${cls}`, 'aria-hidden': 'true'});

function getCookie(name) {
  return document.cookie.split('; ').find(c => c.startsWith(name + '='))?.split('=').slice(1).join('=') || '';
}

class ApiError extends Error {
  constructor(message, status, errors) { super(message); this.status = status; this.errors = errors || {}; }
}

async function api(path, {method = 'GET', body, form} = {}) {
  const opts = {method, headers: {}, credentials: 'same-origin'};
  if (method !== 'GET') opts.headers['X-CSRF-Token'] = decodeURIComponent(getCookie('hb_csrf'));
  if (form) opts.body = form;
  else if (body !== undefined) { opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body); }
  let res;
  try { res = await fetch(path, opts); } catch (e) { throw new ApiError('Cannot reach the server. Check your connection.', 0); }
  if (res.status === 401 && !path.startsWith('/api/auth/login') && !path.startsWith('/api/auth/signup')) {
    window.location.href = '/login';
    throw new ApiError('Your session has ended. Please sign in again.', 401);
  }
  const data = res.headers.get('content-type')?.includes('json') ? await res.json().catch(() => ({})) : {};
  if (!res.ok) {
    const d = data.detail;
    if (d && typeof d === 'object' && !Array.isArray(d)) throw new ApiError(d.message || 'Request failed', res.status, d.errors);
    throw new ApiError(typeof d === 'string' ? d : 'Something went wrong. Please try again.', res.status);
  }
  return data;
}

// ---------- toasts ----------
function toast(message, type = 'success') {
  let wrap = $('#toasts');
  if (!wrap) { wrap = h('div', {id: 'toasts', class: 'toast-container position-fixed bottom-0 end-0 p-3'}); document.body.append(wrap); }
  const colors = {success: 'text-bg-success', error: 'text-bg-danger', info: 'text-bg-dark'};
  const t = h('div', {class: `toast align-items-center border-0 ${colors[type] || colors.info}`, role: type === 'error' ? 'alert' : 'status', 'aria-live': 'polite'},
    h('div', {class: 'd-flex'}, h('div', {class: 'toast-body', text: message}),
      h('button', {type: 'button', class: 'btn-close btn-close-white me-2 m-auto', 'data-bs-dismiss': 'toast', 'aria-label': 'Close'})));
  wrap.append(t);
  const bt = bootstrap.Toast.getOrCreateInstance(t, {delay: 3500});
  t.addEventListener('hidden.bs.toast', () => t.remove());
  bt.show();
}

// ---------- after a medical-history change: reprocess the trip summary now, or keep editing ----------
function reprocessPrompt() {
  if ($('#reprocessPrompt')) return;   // one prompt at a time while the patient keeps editing
  let wrap = $('#toasts');
  if (!wrap) { wrap = h('div', {id: 'toasts', class: 'toast-container position-fixed bottom-0 end-0 p-3'}); document.body.append(wrap); }
  const t = h('div', {id: 'reprocessPrompt', class: 'toast border-0 shadow', role: 'status', 'aria-live': 'polite'});
  const close = () => bootstrap.Toast.getOrCreateInstance(t).hide();
  t.append(h('div', {class: 'toast-body'},
    h('div', {class: 'fw-semibold mb-1'}, icon('clock-history', 'me-1 text-primary'), 'Your travel summary is now out of date'),
    h('div', {class: 'small hb-muted mb-2', text: 'Update the parts that changed now, or keep editing and update later from the Travel Health Summary.'}),
    h('div', {class: 'd-flex gap-2'},
      h('button', {class: 'btn btn-sm btn-primary', type: 'button', text: 'Reprocess now', onclick: async () => {
        close();
        try {
          const r = await api('/api/trips/reprocess', {method: 'POST'});
          toast(r.queued ? `Updating ${r.queued === 1 ? 'your trip summary' : `${r.queued} trip summaries`}` : 'No upcoming trips to update', 'info');
        } catch (err) { toast(err.message, 'error'); }
      }}),
      h('button', {class: 'btn btn-sm btn-outline-primary', type: 'button', text: 'Continue updating', onclick: close}))));
  wrap.append(t);
  t.addEventListener('hidden.bs.toast', () => t.remove());
  bootstrap.Toast.getOrCreateInstance(t, {autohide: false}).show();
}

// ---------- confirm dialog ----------
function confirmDialog({title, message, confirmText = 'Confirm', danger = false}) {
  return new Promise(resolve => {
    const m = h('div', {class: 'modal fade', tabindex: '-1', 'aria-modal': 'true', role: 'dialog'},
      h('div', {class: 'modal-dialog modal-dialog-centered'}, h('div', {class: 'modal-content'},
        h('div', {class: 'modal-header'}, h('h5', {class: 'modal-title', text: title}), h('button', {type: 'button', class: 'btn-close', 'data-bs-dismiss': 'modal', 'aria-label': 'Close'})),
        h('div', {class: 'modal-body'}, h('p', {class: 'mb-0', text: message})),
        h('div', {class: 'modal-footer'}, h('button', {type: 'button', class: 'btn btn-light', 'data-bs-dismiss': 'modal', text: 'Cancel'}),
          h('button', {type: 'button', class: `btn ${danger ? 'btn-danger' : 'btn-primary'}`, 'data-ok': '1', text: confirmText})))));
    document.body.append(m);
    const modal = new bootstrap.Modal(m);
    let ok = false;
    m.querySelector('[data-ok]').addEventListener('click', () => { ok = true; modal.hide(); });
    m.addEventListener('hidden.bs.modal', () => { m.remove(); resolve(ok); });
    modal.show();
  });
}

// ---------- forms ----------
function clearErrors(form) {
  $$('.is-invalid', form).forEach(e => e.classList.remove('is-invalid'));
  $$('.invalid-feedback[data-auto]', form).forEach(e => e.remove());
  const a = $('.form-alert', form); if (a) { a.classList.add('d-none'); a.textContent = ''; }
}

function showErrors(form, err) {
  clearErrors(form);
  let shown = false;
  for (const [field, msg] of Object.entries(err.errors || {})) {
    const input = form.querySelector(`[name="${field}"]`);
    if (!input) continue;
    input.classList.add('is-invalid');
    const fb = h('div', {class: 'invalid-feedback d-block', 'data-auto': '1', text: msg});
    (input.closest('.input-group') || input.closest('.form-check') || input).after(fb);
    shown = true;
  }
  const alert = $('.form-alert', form);
  const unmatched = Object.entries(err.errors || {}).filter(([f]) => !form.querySelector(`[name="${f}"]`)).map(([, m]) => m);
  if (alert && (!shown || unmatched.length)) { alert.textContent = unmatched.length ? unmatched.join(' ') : err.message; alert.classList.remove('d-none'); }
  else if (!alert && !shown) toast(err.message, 'error');
  form.querySelector('.is-invalid')?.focus();
}

function formData(form) {
  const out = {};
  for (const el of form.elements) {
    if (!el.name || el.disabled) continue;
    if (el.type === 'checkbox') out[el.name] = el.checked;
    else if (el.type === 'radio') { if (el.checked) out[el.name] = el.value; }
    else out[el.name] = el.value.trim() === '' ? null : el.value.trim();
  }
  return out;
}

function fillForm(form, data) {
  for (const el of form.elements) {
    if (!el.name || !(el.name in data)) continue;
    const v = data[el.name];
    if (el.type === 'checkbox') el.checked = !!v;
    else if (el.type === 'radio') el.checked = el.value === v;
    else el.value = v ?? '';
  }
}

async function withBusy(button, fn) {
  const label = button.innerHTML;
  button.disabled = true;
  button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Saving…';
  try { return await fn(); } finally { button.disabled = false; button.innerHTML = label; }
}

// ---------- password helpers ----------
const PW_RULES = [
  ['length', 'At least 8 characters', p => p.length >= 8],
  ['upper', 'One uppercase letter (A-Z)', p => /[A-Z]/.test(p)],
  ['lower', 'One lowercase letter (a-z)', p => /[a-z]/.test(p)],
  ['number', 'One number (0-9)', p => /\d/.test(p)],
  ['special', 'One special character (e.g. !@#$%)', p => /[^A-Za-z0-9]/.test(p)],
];
function bindPasswordRules(input, list) {
  list.replaceChildren(...PW_RULES.map(([k, label]) => h('li', {dataset: {rule: k}}, icon('circle'), label)));
  const update = () => PW_RULES.forEach(([k, , test]) => {
    const li = list.querySelector(`[data-rule="${k}"]`), ok = test(input.value);
    li.classList.toggle('ok', ok);
    li.querySelector('i').className = `bi bi-${ok ? 'check-circle-fill' : 'circle'}`;
  });
  input.addEventListener('input', update);
  update();
}
function bindPasswordToggles(root = document) {
  $$('[data-toggle-pw]', root).forEach(btn => btn.addEventListener('click', () => {
    const input = btn.closest('.input-group').querySelector('input');
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
    btn.querySelector('i').className = `bi bi-${show ? 'eye-slash' : 'eye'}`;
  }));
}

// ---------- formatting ----------
const fmtDate = s => s ? new Date(s + (s.length === 10 ? 'T00:00:00' : '')).toLocaleDateString(undefined, {day: 'numeric', month: 'short', year: 'numeric'}) : '—';
function fmtWhen(iso) {
  const d = new Date(iso), now = new Date();
  const time = d.toLocaleTimeString(undefined, {hour: 'numeric', minute: '2-digit'});
  const days = Math.floor((new Date(now.toDateString()) - new Date(d.toDateString())) / 86400000);
  if (days === 0) return `Today, ${time}`;
  if (days === 1) return `Yesterday, ${time}`;
  return d.toLocaleDateString(undefined, {day: 'numeric', month: 'short', year: 'numeric'});
}
const fmtSize = n => n < 1024 ? `${n} B` : n < 1048576 ? `${(n / 1024).toFixed(0)} KB` : `${(n / 1048576).toFixed(1)} MB`;
const cap = s => s ? s.charAt(0).toUpperCase() + s.slice(1) : '';
const chip = (status, label) => h('span', {class: `chip chip-${status}`, text: label || cap(status)});
const today = () => new Date().toISOString().slice(0, 10);

// ---------- reference lists ----------
let _ref;
async function reference() { return _ref ||= api('/api/portal/reference'); }
async function fillCountrySelect(select, {placeholder = 'Select country', value} = {}) {
  const ref = await reference();
  const opts = [h('option', {value: '', text: placeholder})];
  ref.countries.forEach((c, i) => {
    opts.push(h('option', {value: c.code, text: c.name}));
    if (i === 2) opts.push(h('option', {disabled: true, text: '──────────'}));
  });
  select.replaceChildren(...opts);
  if (value) select.value = value;
}

function emptyState(iconName, title, text, action) {
  return h('div', {class: 'empty-state'}, icon(iconName), h('div', {class: 'fw-semibold text-body mb-1', text: title}),
    text ? h('div', {class: 'small mb-3', text}) : null, action || null);
}

// ---------- shell (authenticated pages) ----------
document.addEventListener('DOMContentLoaded', () => {
  bindPasswordToggles();
  $$('[data-copy]').forEach(btn => btn.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(btn.dataset.copy); toast(`${btn.dataset.copyLabel || 'ID'} copied`); }
    catch { toast('Could not copy. Select and copy it manually.', 'error'); }
  }));
  $$('[data-logout]').forEach(btn => btn.addEventListener('click', async () => {
    try { await api('/api/auth/logout', {method: 'POST'}); } catch { /* ignore */ }
    window.location.href = '/login';
  }));
});
