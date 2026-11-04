/* NutriSib – coș de cumpărături (fără dependențe) */
(function () {
  'use strict';
  var KEY = 'nutrisib_cos_v1';
  var PRAG_VP = 125, TRANSPORT = 25;
  var catalogPromise = null;

  function read() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } }
  function write(c) { try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) {} updateCount(); }
  function count(c) { var n = 0; for (var k in c) n += c[k]; return n; }
  function updateCount() {
    var n = count(read());
    document.querySelectorAll('.mz-cart-count').forEach(function (el) { el.textContent = n; el.setAttribute('data-n', n); });
  }
  function add(sku, qty) { var c = read(); c[sku] = Math.min(99, (c[sku] || 0) + qty); write(c); }
  function setQty(sku, qty) { var c = read(); if (qty <= 0) delete c[sku]; else c[sku] = Math.min(99, qty); write(c); }
  function catalog() {
    if (!catalogPromise) catalogPromise = fetch('/magazin/catalog.json', { cache: 'no-cache' }).then(function (r) { return r.json(); })
      .then(function (d) { var m = {}; d.produse.forEach(function (p) { m[p.sku] = p; }); return { list: d.produse, bySku: m, cfg: d.config }; });
    return catalogPromise;
  }
  function lei(n) { return n.toLocaleString('ro-RO') + ' lei'; }
  function vpFmt(n) { return (Math.round(n * 100) / 100).toLocaleString('ro-RO', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

  /* ---- Pagina de produs: cantitate + adaugă ---- */
  function initBuy() {
    var box = document.querySelector('[data-mz-buy]');
    if (!box) return;
    var input = box.querySelector('input[type=number]');
    box.querySelectorAll('[data-step]').forEach(function (b) {
      b.addEventListener('click', function () { var v = (+input.value || 1) + (+b.getAttribute('data-step')); input.value = Math.max(1, Math.min(99, v)); });
    });
    box.querySelector('[data-add]').addEventListener('click', function () {
      add(box.getAttribute('data-mz-buy'), Math.max(1, Math.min(99, +input.value || 1)));
      var ok = box.querySelector('.mz-added'); if (ok) ok.style.display = 'block';
    });
  }

  /* ---- Galerie ---- */
  function initGallery() {
    var main = document.querySelector('.mz-gallery-main img');
    document.querySelectorAll('.mz-thumbs button').forEach(function (b) {
      b.addEventListener('click', function () {
        document.querySelectorAll('.mz-thumbs button').forEach(function (x) { x.classList.remove('active'); });
        b.classList.add('active'); main.src = b.getAttribute('data-src'); main.alt = b.getAttribute('data-alt') || main.alt;
        main.classList.toggle('is-photo', b.hasAttribute('data-photo'));
      });
    });
  }

  /* ---- Tab-uri ---- */
  function initTabs() {
    var tabs = document.querySelectorAll('.mz-tab');
    tabs.forEach(function (t) {
      t.addEventListener('click', function () {
        tabs.forEach(function (x) { x.classList.remove('active'); x.setAttribute('aria-selected', 'false'); });
        document.querySelectorAll('.mz-panel').forEach(function (p) { p.classList.remove('active'); });
        t.classList.add('active'); t.setAttribute('aria-selected', 'true');
        var p = document.getElementById(t.getAttribute('aria-controls')); if (p) p.classList.add('active');
      });
    });
  }

  /* ---- Catalog: filtre + căutare ---- */
  function initCatalog() {
    var grid = document.querySelector('[data-mz-grid]');
    if (!grid) return;
    var chips = document.querySelectorAll('[data-filter]'), search = document.querySelector('.mz-search'), empty = document.querySelector('.mz-empty');
    var current = 'toate';
    function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
    function apply() {
      var q = norm(search ? search.value : ''), shown = 0;
      grid.querySelectorAll('.mz-card').forEach(function (c) {
        var ok = (current === 'toate' || c.getAttribute('data-cat') === current) && (!q || norm(c.getAttribute('data-text')).indexOf(q) > -1);
        c.classList.toggle('hidden', !ok); if (ok) shown++;
      });
      if (empty) empty.style.display = shown ? 'none' : 'block';
    }
    chips.forEach(function (ch) {
      ch.addEventListener('click', function () {
        chips.forEach(function (x) { x.classList.remove('active'); }); ch.classList.add('active');
        current = ch.getAttribute('data-filter'); apply();
        if (history.replaceState) history.replaceState(null, '', current === 'toate' ? location.pathname : '#' + current);
      });
    });
    if (search) search.addEventListener('input', apply);
    var h = location.hash.slice(1); if (h) { var c = document.querySelector('[data-filter="' + h + '"]'); if (c) c.click(); }
  }

  /* ---- Pagina coș + checkout ---- */
  function initCart() {
    var root = document.querySelector('[data-mz-cart]');
    if (!root) return;
    var linesEl = root.querySelector('[data-lines]'), sumEl = root.querySelector('[data-summary]'), form = document.querySelector('[data-mz-form]');
    var emptyEl = root.querySelector('[data-empty]'), filledEls = document.querySelectorAll('[data-filled]');

    function render(cat) {
      var c = read(), lines = [], sub = 0, vp = 0;
      Object.keys(c).forEach(function (sku) {
        var p = cat.bySku[sku]; if (!p) { delete c[sku]; return; }
        var q = c[sku]; sub += p.pret * q; vp += p.vp * q; lines.push({ p: p, q: q });
      });
      var has = lines.length > 0;
      emptyEl.style.display = has ? 'none' : 'block';
      filledEls.forEach(function (e) { e.style.display = has ? '' : 'none'; });
      linesEl.innerHTML = lines.map(function (l) {
        return '<div class="mz-line"><img src="' + l.p.img_mic + '" alt="" loading="lazy">' +
          '<div><a class="mz-line-title" href="' + l.p.url + '">' + esc(l.p.denumire) + '</a>' +
          '<div class="mz-line-meta">' + esc(l.p.varianta || '') + ' · cod ' + l.p.sku + ' · ' + vpFmt(l.p.vp) + ' VP</div>' +
          '<div class="mz-qty"><button type="button" data-sku="' + l.p.sku + '" data-d="-1" aria-label="Scade">−</button><input type="number" value="' + l.q + '" readonly aria-label="Cantitate"><button type="button" data-sku="' + l.p.sku + '" data-d="1" aria-label="Crește">+</button></div></div>' +
          '<div class="mz-line-right"><div class="mz-price" style="font-size:1rem">' + lei(l.p.pret * l.q) + '</div><button type="button" class="mz-remove" data-rm="' + l.p.sku + '">Elimină</button></div></div>';
      }).join('');
      var free = vp >= PRAG_VP, ship = has ? (free ? 0 : TRANSPORT) : 0, pct = Math.min(100, vp / PRAG_VP * 100);
      sumEl.innerHTML =
        '<div class="mz-sum-row"><span>Subtotal produse</span><span>' + lei(sub) + '</span></div>' +
        '<div class="mz-sum-row"><span>Transport</span><span>' + (free ? 'Gratuit' : lei(ship)) + '</span></div>' +
        '<div class="mz-vp-bar" aria-hidden="true"><i style="width:' + pct + '%"></i></div>' +
        '<div class="mz-vp-text">' + (free ? '<strong>Transport gratuit</strong> – ai ' + vpFmt(vp) + ' VP.' : 'Ai <strong>' + vpFmt(vp) + ' VP</strong>. Mai ai <strong>' + vpFmt(PRAG_VP - vp) + ' VP</strong> până la transport gratuit (' + PRAG_VP + ' VP).') + '</div>' +
        '<div class="mz-sum-row total"><span>Total de plată</span><span>' + lei(sub + ship) + '</span></div>';
      linesEl.querySelectorAll('[data-d]').forEach(function (b) {
        b.addEventListener('click', function () { var s = b.getAttribute('data-sku'); setQty(s, (read()[s] || 0) + (+b.getAttribute('data-d'))); render(cat); });
      });
      linesEl.querySelectorAll('[data-rm]').forEach(function (b) { b.addEventListener('click', function () { setQty(b.getAttribute('data-rm'), 0); render(cat); }); });
    }

    catalog().then(function (cat) { render(cat); }).catch(function () { linesEl.innerHTML = '<p>Catalogul nu a putut fi încărcat. Reîncarcă pagina.</p>'; });

    if (!form) return;
    var firma = form.querySelector('[name=pe_firma]'), firmaBox = form.querySelector('[data-firma]');
    if (firma) firma.addEventListener('change', function () {
      firmaBox.style.display = firma.checked ? '' : 'none';
      firmaBox.querySelectorAll('[data-req]').forEach(function (i) { i.required = firma.checked; });
    });
    var prof = form.querySelector('[data-profil]'), consProf = form.querySelector('[name=consimtamant_profil]');
    function profilFilled() { var f = false; prof.querySelectorAll('input,select').forEach(function (i) { if (i.name !== 'consimtamant_profil' && i.value) f = true; }); return f; }

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var err = form.querySelector('.mz-error'); err.style.display = 'none';
      if (!form.reportValidity()) return;
      var c = read(); if (!count(c)) { return; }
      if (profilFilled() && !consProf.checked) { err.textContent = 'Ai completat profilul nutrițional: bifează consimțământul pentru prelucrarea acestor date sau lasă câmpurile goale.'; err.style.display = 'block'; consProf.focus(); return; }
      var fd = new FormData(form), data = {};
      fd.forEach(function (v, k) { data[k] = typeof v === 'string' ? v.trim() : v; });
      data.pe_firma = !!(firma && firma.checked);
      data.consimtamant_profil = !!consProf.checked;
      data.accept_termeni = !!form.querySelector('[name=accept_termeni]').checked;
      if (!data.consimtamant_profil) ['greutate_actuala', 'greutate_dorita', 'inaltime', 'sex', 'an_nastere'].forEach(function (k) { delete data[k]; });
      var items = Object.keys(c).map(function (s) { return { sku: s, qty: c[s] }; });
      var btn = form.querySelector('[type=submit]'); btn.disabled = true; btn.textContent = 'Se pregătește plata securizată…';
      fetch('/.netlify/functions/magazin-checkout', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ items: items, client: data }) })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (res.ok && res.j.url) { location.href = res.j.url; return; }
          throw new Error(res.j && res.j.error || 'Eroare necunoscută');
        })
        .catch(function (e) { err.textContent = 'Comanda nu a putut fi inițiată: ' + e.message; err.style.display = 'block'; btn.disabled = false; btn.textContent = 'Continuă spre plată'; });
    });
  }

  function initSuccess() {
    if (!document.querySelector('[data-mz-success]')) return;
    if (/[?&]session_id=/.test(location.search)) { try { localStorage.removeItem(KEY); } catch (e) {} updateCount(); }
  }

  function esc(s) { return String(s).replace(/[&<>"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]; }); }

  document.addEventListener('DOMContentLoaded', function () {
    updateCount(); initBuy(); initGallery(); initTabs(); initCatalog(); initCart(); initSuccess();
  });
})();
