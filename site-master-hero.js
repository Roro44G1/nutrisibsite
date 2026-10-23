/* NutriSib Construction — one shared hero component on every supported content page.
   Preserve actual page heading/description and move standalone highlight widgets
   below the hero. Existing forms, purchase flows and the rest of the page stay put. */
(() => {
  'use strict';

  function normalize(text) {
    return String(text || '').replace(/\s+/g, ' ').trim();
  }

  function initMasterHero() {
    const hero = document.querySelector('.ns-uniform-hero');
    if (!hero || hero.classList.contains('ns-master-hero')) return;

    // Do not rewrite transactional or interactive heroes.
    if (hero.querySelector('form, input, textarea, select, iframe, [contenteditable]')) return;

    const heading = hero.querySelector('h1');
    if (!heading) return;

    const stylesheet = document.querySelector('link[href$="site-master-hero.css"]');
    const stylesheetPath = stylesheet && stylesheet.getAttribute('href') || 'site-master-hero.css';
    const prefix = stylesheetPath.slice(0, stylesheetPath.lastIndexOf('site-master-hero.css'));

    const eyebrowNode = hero.querySelector(
      '.hero-eyebrow, .pv-hero-eyebrow, .ns-kicker, .journal-meta, .hero-badge'
    );
    const eyebrowText = normalize(eyebrowNode && eyebrowNode.textContent)
      .slice(0, 76) || 'NutriSib · C.E.L.O.S.';

    const leads = [...hero.querySelectorAll(
      '.hero-sub, .hero-subtitle, .hero-body, .pv-hero-subtitle, .journal-subtitle, .hero-intro'
    )].filter(el => !el.closest('aside, .hero-kpis, .hero-stats'));
    if (!leads.length) {
      const fallback = [...hero.querySelectorAll('p')].find(el =>
        !el.closest('aside, .hero-kpis, .hero-stats, .ns-hero-actions, .hero-btns')
        && !el.matches('.ns-kicker, .hero-eyebrow')
        && normalize(el.textContent).length > 24
      );
      if (fallback) leads.push(fallback);
    }
    const leadText = [...new Set(leads.map(el => normalize(el.textContent)))]
      .join(' ').slice(0, 330) ||
      normalize(document.querySelector('meta[name="description"]')?.content).slice(0, 260) ||
      'Descoperă serviciile, resursele și metodologia NutriSib.';

    // Preserve informational content that was formerly embedded in oversized heroes.
    const selectors = [
      '.hero-card-side', '.hero-kpis', '.hero-stats', '.celos-card-side',
      '.pv-hero-visual', '.pv-hero-photo', '.pv-hero-card',
      '.journal-navigation', '.journal-nav', '.hero-navigation'
    ];
    const preserved = [];
    for (const selector of selectors) {
      for (const node of hero.querySelectorAll(selector)) {
        if (!preserved.some(other => other.contains(node)) &&
            !node.closest('.ns-master-highlights')) {
          preserved.push(node);
        }
      }
    }

    // Reuse the actual h1, retaining semantic IDs and page-specific emphasis.
    heading.className = 'ns-master-hero__title';
    heading.removeAttribute('style');

    const shell = document.createElement('div');
    shell.className = 'ns-master-hero__grid';

    const content = document.createElement('div');
    content.className = 'ns-master-hero__content';

    const eyebrow = document.createElement('p');
    eyebrow.className = 'ns-master-hero__eyebrow';
    eyebrow.textContent = eyebrowText;

    const lead = document.createElement('p');
    lead.className = 'ns-master-hero__lead';
    lead.textContent = leadText;

    const actions = document.createElement('div');
    actions.className = 'ns-master-hero__actions';
    const services = document.createElement('a');
    services.className = 'ns-master-hero__action ns-master-hero__action--primary';
    services.href = prefix + 'servicii.html';
    services.textContent = 'Descoperă serviciile →';

    const booking = document.createElement('a');
    booking.className = 'ns-master-hero__action ns-master-hero__action--secondary';
    booking.href = 'https://tinyurl.com/ProgramareServicii';
    booking.target = '_blank';
    booking.rel = 'noopener noreferrer';
    booking.textContent = 'Programează-te ↗';
    actions.append(services, booking);
    content.append(eyebrow, heading, lead, actions);

    const visual = document.createElement('div');
    visual.className = 'ns-master-hero__visual';
    visual.setAttribute('aria-hidden', 'true');
    const ring = document.createElement('div');
    ring.className = 'ns-master-hero__visual-inner';
    const mark = document.createElement('div');
    mark.className = 'ns-master-hero__visual-mark';
    mark.textContent = 'C.E.L.O.S.';
    const caption = document.createElement('p');
    caption.className = 'ns-master-hero__visual-caption';
    caption.textContent = 'Evaluare · Personalizare · Monitorizare';
    ring.append(mark, caption);
    visual.append(ring);
    shell.append(content, visual);

    hero.replaceChildren(shell);
    hero.className = 'ns-master-hero';
    hero.dataset.masterHero = '1';

    if (preserved.length) {
      const supplement = document.createElement('section');
      supplement.className = 'ns-master-highlights';
      supplement.setAttribute('aria-label', 'Elemente-cheie și informații suplimentare');
      const inner = document.createElement('div');
      inner.className = 'ns-master-highlights__inner';
      preserved.forEach(node => inner.appendChild(node));
      supplement.appendChild(inner);
      hero.after(supplement);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMasterHero, { once: true });
  } else {
    initMasterHero();
  }
})();
