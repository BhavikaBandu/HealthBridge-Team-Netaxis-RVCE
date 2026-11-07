// Shared helpers. All untrusted source text is inserted with textContent, never innerHTML.
const el = id => document.getElementById(id);

function node(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined && text !== null) e.textContent = text;
  return e;
}

function link(url, label, cls) {
  const a = node('a', cls || '', label);
  // Only allow http(s) links from source data.
  if (/^https?:\/\//i.test(url || '')) { a.href = url; a.target = '_blank'; a.rel = 'noopener noreferrer'; }
  return a;
}

async function getJson(url) {
  let res;
  try { res = await fetch(url); } catch (e) { throw new Error('Cannot reach the server. Is uvicorn running?'); }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = typeof data.detail === 'string' ? data.detail
      : Array.isArray(data.detail) ? data.detail.map(d => d.msg).join('; ') : 'Request failed';
    const err = new Error(`${detail} (HTTP ${res.status})`);
    err.status = res.status;
    throw err;
  }
  return data;
}

const WORKFLOW_LABELS = {medicines: 'Medicines', medical_reports: 'Medical reports', procedures: 'Procedures', policies: 'Policies'};
const kxDate = s => s ? new Date(s).toLocaleString() : '—';

function row(label, value) {
  const tr = node('tr');
  tr.append(node('th', 'text-nowrap', label));
  const td = node('td');
  if (value instanceof Node) td.append(value); else td.textContent = (value === null || value === undefined || value === '') ? '—' : String(value);
  tr.append(td);
  return tr;
}
