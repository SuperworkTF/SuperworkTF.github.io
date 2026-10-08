const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function observeReveal(root = document) {
  const els = root.querySelectorAll('.reveal:not(.in)');
  if (!('IntersectionObserver' in window)) { els.forEach(el => el.classList.add('in')); return; }
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      e.target.classList.add('in');
      io.unobserve(e.target);
    });
  }, { threshold: 0.12 });
  els.forEach((el, i) => { el.style.transitionDelay = `${(i % 5) * 90}ms`; io.observe(el); });
}

function cardHTML(app, base) {
  const icon = app.icon ? `<img src="${base}${esc(app.icon)}" alt="" loading="lazy">` : '';
  const video = app.video ? `<video muted loop playsinline preload="none" src="${base}${esc(app.video)}"></video>` : '';
  return `
    <a class="acard reveal" href="${base}${esc(app.path)}" data-id="${esc(app.id)}">
      <div class="acard-media">
        <img src="${base}${esc(app.thumbSm)}" alt="${esc(app.name)}" loading="lazy" style="object-position:${esc(app.thumbPos)}">
        ${video}
        <span class="acard-more">자세히 보기 →</span>
      </div>
      <div class="acard-body">${icon}<div><div class="acard-genre">${esc(app.genre)}</div><b>${esc(app.name)}</b></div></div>
      <p class="acard-desc">${esc(app.desc)}</p>
    </a>`;
}

function wireCards(root) {
  root.querySelectorAll('.acard').forEach(card => {
    const v = card.querySelector('video');
    if (!v) return;
    const play = () => { card.classList.add('playing'); v.play().catch(() => {}); };
    const stop = () => { card.classList.remove('playing'); v.pause(); };
    card.addEventListener('mouseenter', play);
    card.addEventListener('focus', play);
    card.addEventListener('mouseleave', stop);
    card.addEventListener('blur', stop);
  });
}

async function renderAppGroups({ base = './', container }) {
  const data = await fetch(`${base}assets/apps.json`).then(r => r.json());
  container.innerHTML = data.categories.map(c => {
    const list = data.apps.filter(a => a.category === c.id);
    return `
      <div class="group" id="apps-${esc(c.id)}">
        <div class="group-head reveal">
          <div><h3>${esc(c.label)}<i>${list.length}</i></h3><p>${esc(c.desc)}</p></div>
          <div class="group-nav">
            <button class="arrow" data-dir="-1" aria-label="${esc(c.label)} 이전">←</button>
            <button class="arrow" data-dir="1" aria-label="${esc(c.label)} 다음">→</button>
          </div>
        </div>
        <div class="track">${list.map(a => cardHTML(a, base)).join('')}</div>
      </div>`;
  }).join('');
  container.querySelectorAll('.group').forEach(g => {
    const track = g.querySelector('.track');
    g.querySelectorAll('.arrow').forEach(b => b.addEventListener('click', () =>
      track.scrollBy({ left: Number(b.dataset.dir) * track.clientWidth * 0.8, behavior: 'smooth' })));
  });
  wireCards(container);
  observeReveal(container);
  if (location.hash.startsWith('#apps-')) document.querySelector(location.hash)?.scrollIntoView();
  return data;
}
