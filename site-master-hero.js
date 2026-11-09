/* NutriSib construction — canonical two-column hero for every regular page.
 * Jurnalul de sistem intentionally retains its complete original hero.
 * Content copied from each page's own heading, eyebrow and KPI statistics.
 * All navigation, forms and articles outside the hero remain untouched.
 */
(() => {
  'use strict';
  const text = el => (el?.textContent || '').replace(/\s+/g,' ').trim();
  const make = (tag, className, content) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (content !== undefined) el.textContent = content;
    return el;
  };
  const FIELDS = [
    ['C','Calibrare','Evaluare inițială și orientare după obiective'],
    ['E','Energie','Nutriție și obiceiuri adaptate rutinei'],
    ['L','Longevitate','Continuitate și stil de viață echilibrat'],
    ['OS','Optimizare sistemică','Monitorizare și ajustări în timp']
  ];

  function init() {
    // Exception approved by site owner: never restyle or rebuild Jurnalul de sistem.
    if (/\/(?:jurnal|jurnal\.html)\/?$/i.test(location.pathname)) return;
    const hero = document.querySelector('.ns-uniform-hero');
    if (!hero || hero.classList.contains('ns-master-hero')) return;
    if (hero.querySelector('form,input,textarea,select,iframe,[contenteditable]')) return;
    const heading = hero.querySelector('h1');
    if (!heading) return;

    const script = document.querySelector('script[src$="site-master-hero.js"]');
    const src = script ? script.getAttribute('src') : 'site-master-hero.js';
    const prefix = src.slice(0,src.lastIndexOf('site-master-hero.js'));

    const eyebrowNode = hero.querySelector('.hero-eyebrow,.pv-hero-eyebrow,.ns-kicker,.journal-meta,.hero-badge');
    const eyebrow = text(eyebrowNode).slice(0,82) || 'NUTRISIB · METODA C.E.L.O.S.';

    const leadNodes = [...hero.querySelectorAll(
      '.hero-sub,.hero-subtitle,.hero-body,.pv-hero-sub,.pv-hero-subtitle,.journal-sub,.journal-subtitle,.hero-intro'
    )].filter(el => !el.closest('aside,.hero-kpis,.hero-stats,.pv-kpi-bar'));
    if (!leadNodes.length) {
      const candidate=[...hero.querySelectorAll('p')].find(el=>
        !el.closest('aside,.hero-kpis,.hero-stats,.pv-kpi-bar')
        && !el.matches('.ns-kicker,.hero-eyebrow')
        && text(el).length>20
      );
      if(candidate) leadNodes.push(candidate);
    }
    const lead = [...new Set(leadNodes.map(text))].join(' ').slice(0,320)
      || (document.querySelector('meta[name="description"]')?.content||'').slice(0,280)
      || 'Descoperă evaluările, serviciile și metodologia NutriSib.';

    // Gather data before replacing legacy markup. IDs of live counters must survive.
    const originalStats = hero.querySelector('.hero-kpis,.hero-stats,.pv-kpi-bar');
    const stats = [];
    if (originalStats) {
      for (const item of originalStats.children) {
        const val = item.querySelector('.hero-kpi-num,.hero-stat-num,.pv-kpi-num');
        const label = item.querySelector('.hero-kpi-label,.hero-stat-label,.pv-kpi-label');
        if (val && label) {
          stats.push({valueNode:val,label:text(label)});
        }
      }
    }
    const sourceSide = hero.querySelector('.hero-card-side,.celos-side-card');
    const rows = [];
    if (sourceSide) {
      for (const item of sourceSide.querySelectorAll('.celos-letter,.celos-item')) {
        const badge = text(item.querySelector('.celos-badge'));
        const title = text(item.querySelector('strong'));
        const subtitle = text(item.querySelector('.celos-letter-text span,.celos-item-text span'));
        if (badge && title) rows.push([badge,title,subtitle]);
      }
    }

    // Keep the page's original h1 and its ID for fragment links/ARIA.
    heading.className = 'ns-master-hero__title';
    heading.removeAttribute('style');
    const layout = make('div','ns-master-hero__grid');
    const content = make('div','ns-master-hero__content');
    content.append(
      make('p','ns-master-hero__eyebrow',eyebrow),
      heading,
      make('p','ns-master-hero__lead',lead)
    );

    const actions = make('div','ns-master-hero__actions');
    const service = make('a','ns-master-hero__action ns-master-hero__action--primary','Descoperă serviciile →');
    const onServices = /\/(?:servicii|servicii\.html)\/?$/i.test(location.pathname);
    const onBlog = /\/blog\/(?:index\.html)?$/i.test(location.pathname);
    service.href=onServices?'#catalog':onBlog?'#blog-search-input':prefix+'servicii.html';
    if (onServices) service.textContent='Explorează catalogul ↓';
    if (onBlog) service.textContent='Caută articole →';
    const appointment=make('a','ns-master-hero__action ns-master-hero__action--secondary','Programează-te ↗');
    appointment.href=prefix+'programare.html';
    appointment.target='_blank';appointment.rel='noopener noreferrer';
    actions.append(service,appointment);
    content.append(actions);

    const minis=make('div','ns-master-hero__minis');
    if (stats.length) {
      for (const item of stats.slice(0,4)) {
        const mini=make('div','ns-master-hero__mini');
        item.valueNode.className='ns-master-hero__mini-value';
        mini.append(item.valueNode,make('span','ns-master-hero__mini-label',item.label));
        minis.append(mini);
      }
    } else {
      [
        ['Evaluare','Pornim de la obiectivele tale'],
        ['Nutriție','Recomandări practice'],
        ['Monitorizare','Ajustări în timp'],
        ['Resurse','Ghiduri și informații utile']
      ].forEach(([value,label])=>{
        const mini=make('div','ns-master-hero__mini');
        mini.append(make('strong','ns-master-hero__mini-value',value),make('span','ns-master-hero__mini-label',label));
        minis.append(mini);
      });
    }
    content.append(minis);

    const visual=make('div','ns-master-hero__visual');
    const panel=make('aside','ns-master-hero__panel');
    panel.setAttribute('aria-label','Elementele metodei C.E.L.O.S.');
    panel.append(make('h2','ns-master-hero__panel-title','Sistemul C.E.L.O.S.™'));
    const list=make('div','ns-master-hero__panel-list');
    (rows.length>=4 ? rows.slice(0,4):FIELDS).forEach(([letter,title,detail])=>{
      const line=make('div','ns-master-hero__panel-item');
      const body=make('div','ns-master-hero__panel-copy');
      body.append(make('strong','',title),make('span','',detail));
      line.append(make('span','ns-master-hero__panel-badge',letter),body);
      list.append(line);
    });
    panel.append(list,make('p','ns-master-hero__panel-foot','Evaluare · Personalizare · Monitorizare'));
    visual.append(panel);
    layout.append(content,visual);

    hero.replaceChildren(layout);
    hero.className='ns-master-hero';
    hero.dataset.masterHero='1';
  }

  if (document.readyState==='loading') {
    document.addEventListener('DOMContentLoaded',init,{once:true});
  } else {
    init();
  }
})();
