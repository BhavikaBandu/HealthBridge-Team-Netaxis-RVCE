let offset = 0;
let workflow = '';
let workflowStats = {};
let requestSeq = 0;
const pageSize = 6;

function setNotice(text) {
  el('notice').textContent = text || '';
  el('notice').classList.toggle('d-none', !text);
}

function emptyWorkflowMessage(wf) {
  const stats = workflowStats[wf];
  if (!wf || !stats || stats.sources > 0) return null;
  return `No verified ${WORKFLOW_LABELS[wf].toLowerCase()} sources have been acquired yet. ` +
    'This workflow will show results once a permitted official source is reviewed and ingested. ' +
    'Nothing is shown here rather than unverified content.';
}

function card(item) {
  const col = node('div', 'col-md-6 col-xl-4');
  const c = node('article', 'card record-card shadow-sm');
  const body = node('div', 'card-body d-flex flex-column');
  const lang = item.language ? ' · ' + item.language : '';
  body.append(node('div', 'meta mb-2', `${WORKFLOW_LABELS[item.workflow] || item.workflow} · ${item.jurisdiction} · ${item.source_id}${lang}`));
  body.append(node('h3', '', item.title));
  body.append(node('p', 'small text-muted mb-2', item.content.length > 180 ? item.content.slice(0, 180) + '…' : item.content));
  // One row: type / match badges on the left, the original document link on the far right.
  const badges = node('div', 'd-flex flex-wrap align-items-center gap-1 mt-auto');
  badges.append(node('span', 'badge text-bg-light border', item.kind.replace(/_/g, ' ')));
  if (item.match_type === 'keyword') badges.append(node('span', 'badge badge-soft', 'Keyword match'));
  if (item.match_type === 'semantic') badges.append(node('span', 'badge badge-semantic', `Similar meaning · ${item.score}`));
  if (item.source_link) badges.append(link(item.source_link, 'Original document ↗', 'small ms-auto'));
  body.append(badges);
  c.append(body);
  col.append(c);
  return col;
}

async function load() {
  const emptyMsg = emptyWorkflowMessage(workflow);
  el('emptyWorkflow').textContent = emptyMsg || '';
  el('emptyWorkflow').classList.toggle('d-none', !emptyMsg);
  el('resultsArea').classList.toggle('d-none', !!emptyMsg);
  if (emptyMsg) { setNotice(''); return; }

  el('status').replaceChildren(node('span', 'spinner-border spinner-border-sm me-2'), 'Searching…');
  const p = new URLSearchParams({q: el('query').value.trim(), limit: String(pageSize), offset: String(offset)});
  if (workflow) p.set('workflow', workflow);
  const myRequest = ++requestSeq;
  try {
    const data = await getJson('/api/search?' + p);
    if (myRequest !== requestSeq) return;  // a newer search started; ignore this stale response
    el('results').replaceChildren();
    setNotice(data.notice);
    if (!data.results.length) {
      el('results').append(node('div', 'col-12 text-muted py-4',
        offset ? 'No more results.' : `No matching records for “${el('query').value.trim()}”. Try another spelling, a code or a description.`));
    }
    for (const item of data.results) el('results').append(card(item));
    const q = el('query').value.trim();
    el('status').textContent = q
      ? `Total found: ${data.total.toLocaleString()} (${data.keyword_total.toLocaleString()} keyword · ${data.semantic_total} similar meaning)`
      : `Total found: ${data.total.toLocaleString()}`;
    const pages = Math.max(1, Math.ceil(data.total / pageSize));
    el('pageInfo').textContent = data.total ? `Page ${Math.floor(offset / pageSize) + 1} of ${pages.toLocaleString()}` : '';
    el('prev').disabled = offset === 0;
    el('next').disabled = offset + data.results.length >= data.total;
  } catch (err) {
    if (myRequest !== requestSeq) return;
    el('results').replaceChildren(node('div', 'col-12 alert alert-danger', err.message));
    el('status').textContent = '';
    el('pageInfo').textContent = '';
    el('prev').disabled = el('next').disabled = true;
  }
}

async function details(id) {
  try {
    const r = await getJson('/api/records/' + id);
    el('detailTitle').textContent = r.title;
    const body = el('detailBody');
    body.replaceChildren();
    if (!r.is_active_version) body.append(node('div', 'alert alert-warning py-2 small', 'This record belongs to a superseded source version.'));

    const meta = r.metadata || {};
    body.append(node('h4', 'h6 mt-1', 'Record'));
    const t1 = node('table', 'table table-sm small detail-table');
    const content = node('div', 'text-pre-wrap', r.content);
    t1.append(row('Record ID', r.external_id), row('Type', r.kind.replace(/_/g, ' ')), row('Workflow', WORKFLOW_LABELS[r.workflow] || r.workflow),
      row('Jurisdiction', r.jurisdiction), row('Location in source', meta.location_label || null), row('Language', r.language),
      row('Content', content),
      row('Original document', r.source_link ? link(r.source_link, r.source_link) : null),
      row('Stored copy', r.source.stored_file_url ? link(location.origin + r.source.stored_file_url, 'Open the file held in this knowledge base ↗') : null));
    body.append(t1);

    if (meta.facts) {
      body.append(node('h4', 'h6', 'Extracted facts'));
      body.append(node('p', 'small text-muted mb-1', 'Structured values copied from this passage; fields the source does not state are left empty.'));
      body.append(node('pre', 'kx-facts small', JSON.stringify(meta.facts, null, 2)));
    }

    body.append(node('h4', 'h6', 'Provenance'));
    const t2 = node('table', 'table table-sm small detail-table');
    const limits = (r.source.limitations || []).length ? node('ul', 'mb-0 ps-3') : null;
    (r.source.limitations || []).forEach(l => limits.append(node('li', '', l)));
    t2.append(row('Source', `${r.source.source_id} — ${r.source.title}`),
      row('Catalogue ID', r.source.catalogue_id), row('Publisher', r.source.publisher), row('Limitations', limits),
      row('Version', `${r.version.version_label} (#${r.version.version_id}, ${r.version.status})`),
      row('SHA-256', node('code', '', r.version.sha256)),
      row('Raw file', r.version.raw_path), row('Archived snapshot', r.version.snapshot_path),
      row('Parser', r.version.parser), row('Ingested', kxDate(r.version.ingested_at)),
      row('Publisher', r.source.origin_url ? link(r.source.origin_url, r.source.origin_url) : null),
      row('Licence', r.source.licence_note), row('Access note', r.source.access_note));
    body.append(t2);

    body.append(node('h4', 'h6', 'Source metadata'));
    const t3 = node('table', 'table table-sm small detail-table');
    for (const [k, v] of Object.entries(r.metadata || {})) {
      if (['facts', 'location', 'location_label'].includes(k)) continue;   // shown above
      if (k === 'references' && Array.isArray(v)) {
        const list = node('div');
        v.forEach(ref => { const d = node('div'); d.append(node('span', 'text-muted me-1', ref.content_type), link(ref.url, ref.url)); list.append(d); });
        t3.append(row('references', list));
      } else {
        t3.append(row(k, typeof v === 'object' && v !== null ? JSON.stringify(v) : v));
      }
    }
    body.append(t3);
    body.append(node('p', 'small text-muted mb-0', 'Reference information only. Not clinical decision support.'));
    bootstrap.Modal.getOrCreateInstance(el('detailModal')).show();
  } catch (err) {
    setNotice(err.message);
  }
}

async function loadStats() {
  try {
    const rows = await getJson('/api/workflows');
    let total = 0;
    for (const w of rows) { workflowStats[w.workflow] = w; total += w.records; }
    document.querySelectorAll('[data-count]').forEach(b => {
      const key = b.dataset.count;
      const n = key ? (workflowStats[key] ? workflowStats[key].records : 0) : total;
      b.textContent = n.toLocaleString();
      b.className = 'badge rounded-pill ' + (n ? 'text-bg-secondary' : 'text-bg-light border');
    });
  } catch (err) { /* counts are optional; search still works */ }
}

document.querySelectorAll('#workflowTabs [data-workflow]').forEach(btn => btn.addEventListener('click', () => {
  document.querySelectorAll('#workflowTabs .nav-link').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  workflow = btn.dataset.workflow;
  offset = 0;
  load();
}));
el('searchForm').addEventListener('submit', e => { e.preventDefault(); offset = 0; load(); });
el('prev').addEventListener('click', () => { offset = Math.max(0, offset - pageSize); load(); });
el('next').addEventListener('click', () => { offset += pageSize; load(); });

// A search started from the doctor dashboard arrives as ?q=...
const startQuery = new URLSearchParams(location.search).get('q');
if (startQuery) el('query').value = startQuery.slice(0, 200);
loadStats().then(load);
