/* ═══════════════════════════════════════════════════════════════════
   NutriSib — Meridiane MTC · Script comun
   w-script.js · © 2026 dr.ing. Radu Pascu

   Fiecare pagină HTML definește variabila globală MERIDIAN_DATA
   înainte de a include acest script:

   <script>
     var MERIDIAN_DATA = {
       optLabels: [ ... ],   // 7 etichete pentru dropdown
       edata: [ ... ],       // 7 obiecte cu: stare, fiziologic,
                             //   nutritie, suplimente, emotional,
                             //   relatiiParinti, terapie
       defaultIdx: 3         // indexul selectat la inițializare (de obicei 3 = echilibru)
     };
   <\/script>
   <script src="w-script.js"><\/script>

   ═══════════════════════════════════════════════════════════════════ */

(function () {

  /* ── SCROLL PROGRESS BAR ── */
  window.addEventListener('scroll', function () {
    var d = document.documentElement;
    var pct = d.scrollTop / (d.scrollHeight - d.clientHeight) * 100;
    var bar = document.getElementById('scrollBar');
    if (bar) bar.style.width = pct + '%';
  });

  /* ── TAB NAVIGATION ── */
  var btns   = document.querySelectorAll('.tbtn');
  var panels = document.querySelectorAll('.tpanel');

  btns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-tab');
      panels.forEach(function (p) { p.classList.remove('active'); });
      btns.forEach(function (b)   { b.classList.remove('active'); });
      var target = document.getElementById(id);
      if (target) target.classList.add('active');
      btn.classList.add('active');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  /* ── EVALUARE FUNCȚIONALĂ ── */
  var rlabels = [
    { key: 'fiziologic',      label: '🧬 Fiziologie & simptome',       color: '#065f46' },
    { key: 'nutritie',        label: '🥗 Nutriție recomandată',         color: '#15803d' },
    { key: 'suplimente',      label: '💊 Suplimente & fitoterapie',     color: '#0284c7' },
    { key: 'emotional',       label: '🧠 Stare emoțională',             color: '#9333ea' },
    { key: 'relatiiParinti',  label: '👪 Relația cu părinții (arhetip)',color: '#c2410c' },
    { key: 'terapie',         label: '💆 Terapie & stil de viață',      color: '#0f766e' }
  ];

  /* Datele de evaluare vin din pagina HTML via MERIDIAN_DATA */
  if (typeof MERIDIAN_DATA === 'undefined') { return; }

  var edata     = MERIDIAN_DATA.edata;
  var optLabels = MERIDIAN_DATA.optLabels;
  var defIdx    = typeof MERIDIAN_DATA.defaultIdx === 'number' ? MERIDIAN_DATA.defaultIdx : 3;

  /* Populează select-ul */
  var sel = document.getElementById('selStare');
  if (sel) {
    optLabels.forEach(function (lbl, i) {
      var o = document.createElement('option');
      o.value = i;
      o.textContent = lbl;
      if (i === defIdx) o.selected = true;
      sel.appendChild(o);
    });
  }

  /* Randează rezultatul */
  function renderResult(idx) {
    var panel = document.getElementById('rpanel');
    if (!panel) return;
    var d = edata[idx];
    if (!d) return;
    var items = rlabels.map(function (l) {
      return '<div class="ritem">'
        + '<div class="rlabel" style="color:' + l.color + '">' + l.label + '</div>'
        + '<p>' + (d[l.key] || '') + '</p>'
        + '</div>';
    }).join('');
    panel.innerHTML = '<h3>Stare: ' + d.stare + '</h3><div class="rgrid">' + items + '</div>';
  }

  /* Bara interactivă */
  var bbar   = document.getElementById('bbar');
  var barrow = document.getElementById('barrow');
  var dragging = false;

  function posToIdx(clientX) {
    var r = bbar.getBoundingClientRect();
    var x = Math.max(0, Math.min(clientX - r.left, r.width));
    return Math.min(6, Math.floor(x / r.width * 7));
  }

  function setIdx(idx) {
    idx = Math.max(0, Math.min(6, idx));
    if (barrow) barrow.style.left = (idx / 6 * 100) + '%';
    if (sel)    sel.value = idx;
    renderResult(idx);
  }

  if (bbar) {
    bbar.addEventListener('click',     function (e) { if (!dragging) setIdx(posToIdx(e.clientX)); });
    bbar.addEventListener('mousedown', function (e) { dragging = true; setIdx(posToIdx(e.clientX)); e.preventDefault(); });
    bbar.addEventListener('touchstart',function (e) { dragging = true; setIdx(posToIdx(e.touches[0].clientX)); e.preventDefault(); }, { passive: false });
  }
  document.addEventListener('mousemove', function (e) { if (dragging) setIdx(posToIdx(e.clientX)); });
  document.addEventListener('mouseup',   function ()  { dragging = false; });
  document.addEventListener('touchmove', function (e) { if (dragging) setIdx(posToIdx(e.touches[0].clientX)); });
  document.addEventListener('touchend',  function ()  { dragging = false; });
  if (sel) sel.addEventListener('change', function () { setIdx(parseInt(this.value)); });

  /* Inițializare */
  setIdx(defIdx);

  /* ── ANTI-COPY ── */
  document.addEventListener('contextmenu', function (e) { e.preventDefault(); });
  document.addEventListener('keydown', function (e) {
    if (
      (e.ctrlKey && e.key === 'u') ||
      e.key === 'F12' ||
      (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J'))
    ) { e.preventDefault(); }
  });

})();
