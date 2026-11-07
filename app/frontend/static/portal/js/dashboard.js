const STATUS_LABEL = {planned: 'Planned', ongoing: 'Ongoing', completed: 'Completed'};

function renderTrip(t) {
  const hero = $('#tripHero');
  if (!t) {
    hero.className = 'trip-hero empty';
    hero.replaceChildren(icon('airplane', 'plane'),
      h('div', {class: 'd-flex align-items-center gap-2 fw-semibold'}, icon('airplane'), 'Upcoming Trip'),
      h('h2', {text: 'No upcoming trips'}),
      h('div', {class: 'meta mb-3', text: 'Plan your next journey so your records are ready before you travel.'}),
      h('a', {class: 'btn', href: '/trips?new=1'}, icon('plus-lg', 'me-1'), 'Create a trip'));
    return;
  }
  const dates = `${fmtDate(t.departure_date)} – ${t.return_date ? fmtDate(t.return_date) : 'no return date'}`;
  hero.className = 'trip-hero';
  hero.replaceChildren(icon('airplane', 'plane'),
    h('div', {class: 'd-flex align-items-center gap-2 fw-semibold'}, icon('airplane'), t.status === 'ongoing' ? 'Current Trip' : 'Upcoming Trip',
      h('span', {class: 'chip', style: 'background:rgba(255,255,255,.2);color:#fff', text: STATUS_LABEL[t.status]})),
    h('h2', {text: `${t.origin_name} → ${t.destination_name}`}),
    h('div', {class: 'meta mb-3'}, icon('calendar3', 'me-1'), dates, ' • ', t.purpose_label),
    h('a', {class: 'btn', href: '/trips'}, 'View trip details ', icon('arrow-right')));
}

async function load() {
  try {
    const d = await api('/api/dashboard/summary');
    renderTrip(d.upcoming_trip);
    for (const [k, v] of Object.entries(d.counts)) {
      const el = document.querySelector(`[data-count="${k}"]`);
      if (el) el.textContent = v;
    }
    $('[data-count="medications"]').textContent = d.counts.medications_total;  // all medications (ongoing + stopped)
    if (!d.profile_complete) {
      const p = await api('/api/profile');
      $('#missingFields').textContent = 'add your ' + p.missing_fields.join(' and ');
      $('#profileBanner').classList.remove('d-none');
    }
  } catch (err) {
    $('#tripHero').replaceChildren(h('div', {class: 'text-white', text: err.message}));
    toast(err.message, 'error');
  }
}

load();
