/* Shared footer and navigation polish; no styling changes to Jurnalul de sistem. */
(() => {
  'use strict';
  if (/\/jurnal(?:\.html)?\/?$/i.test(location.pathname)) return;
  const script = document.querySelector('script[src$="site-chrome.js"]');
  const prefix = script ? script.getAttribute('src').replace(/site-chrome\.js$/, '') : '';
  const redirectForms = () => {
    const change = (a) => {
      const raw = a.getAttribute('href') || '';
      if (/tinyurl\.com\/ProgramareServicii/i.test(raw) || /jotform\.com\/(?:lifestylecoachSB\/EFest2025|(?:build\/)?250983119555363)/i.test(raw)) {
        a.setAttribute('href','/programare.html');
        a.removeAttribute('target');
        a.removeAttribute('rel');
      } else if (/jotform\.com\/(?:build\/)?242982957700365/i.test(raw)) {
        a.setAttribute('href','/profil-wellness.html');
        a.removeAttribute('target');
        a.removeAttribute('rel');
      }
    };
    document.querySelectorAll('a[href]').forEach(change);
  };
  function mountFooter() {
    const holder = document.getElementById('footer-placeholder') || document.getElementById('ns-shared-footer');
    const mount = holder || document.createElement('div');
    if (!holder) {
      mount.id = 'ns-shared-footer';
      document.body.appendChild(mount);
    }
    fetch(prefix + 'footer.html', {cache:'force-cache'})
      .then(response => {
        if (!response.ok) throw new Error('Footer unavailable');
        return response.text();
      })
      .then(html => {
        if (!html.includes('ns-global-footer')) return;
        mount.innerHTML = html;
        redirectForms();
        document.querySelectorAll('footer:not(.ns-global-footer)').forEach(node => {
          // Protect special interactive/legal footers in modals.
          if (!node.closest('[role="dialog"],.modal,.modal-overlay') && !node.contains(mount)) {
            node.classList.add('ns-legacy-footer-hidden');
          }
        });
      })
      .catch(() => {
        // Keep original footers in place as graceful fallback.
      });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',()=>{redirectForms();mountFooter();},{once:true});
  else {redirectForms();mountFooter();}
})();
