/* NutriSib – cont de client (Supabase Auth, link magic pe e-mail). Comanda funcționează și fără cont. */
(function () {
  'use strict';
  if (!window.supabase || !window.NS_SUPABASE) {
    document.addEventListener('DOMContentLoaded', function () {
      var o = document.querySelector('[data-mz-account] [data-out]');
      if (o) { o.style.display = ''; o.querySelector('[data-login]').innerHTML = '<p class="mz-login-msg err">Conectarea nu este disponibilă momentan. Poți comanda în continuare fără cont.</p>'; }
    });
    return;
  }
  var sb = window.supabase.createClient(window.NS_SUPABASE.url, window.NS_SUPABASE.anonKey, { auth: { persistSession: true, detectSessionInUrl: true, autoRefreshToken: true } });
  var CLIENT_FIELDS = ['nume', 'prenume', 'telefon', 'judet', 'localitate', 'adresa', 'cod_postal', 'firma_denumire', 'firma_cui', 'firma_regcom', 'firma_adresa'];
  var PROFIL_FIELDS = ['greutate_actuala', 'greutate_dorita', 'inaltime', 'an_nastere', 'sex'];
  function $(s, r) { return (r || document).querySelector(s); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]; }); }
  function lei(n) { n = Math.round(Number(n) * 100) / 100; var z = n % 1 ? 2 : 0; return n.toLocaleString('ro-RO', { minimumFractionDigits: z, maximumFractionDigits: 2 }) + ' lei'; }
  function session() { return sb.auth.getSession().then(function (r) { return r.data.session; }); }

  /* ---------- formular de conectare (link magic) ---------- */
  function initLogin(box) {
    if (!box) return;
    box.querySelector('form').addEventListener('submit', function (e) {
      e.preventDefault();
      var email = box.querySelector('[name=email]').value.trim(), msg = box.querySelector('.mz-login-msg'), btn = box.querySelector('button');
      if (!email) return;
      btn.disabled = true; msg.style.display = 'block'; msg.className = 'mz-login-msg'; msg.textContent = 'Se trimite linkul…';
      sb.auth.signInWithOtp({ email: email, options: { emailRedirectTo: location.origin + (box.getAttribute('data-redirect') || '/magazin/cont/') } })
        .then(function (r) {
          btn.disabled = false;
          if (r.error) { msg.className = 'mz-login-msg err'; msg.textContent = 'Nu am putut trimite linkul: ' + r.error.message; return; }
          msg.textContent = 'Ți-am trimis un link de conectare la ' + email + '. Deschide e-mailul pe acest dispozitiv și apasă pe link.';
        });
    });
  }

  /* ---------- pagina „Contul meu” ---------- */
  function initAccount() {
    var root = $('[data-mz-account]'); if (!root) return;
    var out = $('[data-out]', root), inn = $('[data-in]', root);
    initLogin($('[data-login]', root));
    session().then(function (s) {
      if (!s) { out.style.display = ''; return; }
      inn.style.display = '';
      $('[data-email]', root).textContent = s.user.email;
      $('[data-logout]', root).addEventListener('click', function () { sb.auth.signOut().then(function () { location.reload(); }); });
      loadOrders(); loadClient(s.user.id); loadProfil(s.user.id);
    });

    function loadOrders() {
      var el = $('[data-orders]', root);
      sb.from('magazin_comenzi').select('*').order('creata', { ascending: false }).then(function (r) {
        if (r.error) { el.innerHTML = '<p>Istoricul nu a putut fi încărcat.</p>'; return; }
        if (!r.data.length) { el.innerHTML = '<p>Nu ai încă nicio comandă. <a href="/magazin/herbalife/">Vezi produsele</a>.</p>'; return; }
        el.innerHTML = r.data.map(function (o) {
          var st = o.status === 'platita' ? 'Plătită' : o.status === 'expediata' ? 'Expediată' : o.status === 'livrata' ? 'Livrată' : o.status;
          var f = o.factura ? ' · factura ' + esc(o.factura.serie) + ' ' + esc(o.factura.numar) : '';
          return '<details class="mz-order"><summary><span><strong>' + esc(o.id) + '</strong> · ' + new Date(o.creata).toLocaleDateString('ro-RO') + '</span><span>' + esc(st) + ' · <strong>' + lei(o.total) + '</strong></span></summary>' +
            '<ul>' + (o.produse || []).map(function (l) { return '<li>' + l.qty + ' × ' + esc(l.denumire) + ' ' + esc(l.varianta || '') + ' – ' + lei(l.pret * l.qty) + '</li>'; }).join('') + '</ul>' +
            '<p class="mz-buy-note">Transport: ' + (Number(o.transport) ? lei(o.transport) : 'gratuit') + (Number(o.vp_total) ? ' · ' + esc(o.vp_total) + ' VP' : '') + f + '</p>' +
            '<button type="button" class="mz-btn ghost" data-reorder=\'' + esc(JSON.stringify((o.produse || []).map(function (l) { return [l.sku, l.qty]; }))) + '\'>Comandă din nou</button></details>';
        }).join('');
        el.querySelectorAll('[data-reorder]').forEach(function (b) {
          b.addEventListener('click', function () {
            var c = {}; try { c = JSON.parse(localStorage.getItem('nutrisib_cos_v1')) || {}; } catch (e) {}
            JSON.parse(b.getAttribute('data-reorder')).forEach(function (x) { c[x[0]] = Math.min(99, (c[x[0]] || 0) + x[1]); });
            try { localStorage.setItem('nutrisib_cos_v1', JSON.stringify(c)); } catch (e) {}
            location.href = '/magazin/cos/';
          });
        });
      });
    }
    function loadClient(uid) {
      var f = $('[data-client-form]', root);
      sb.from('magazin_clienti').select('*').eq('id', uid).maybeSingle().then(function (r) {
        if (r.data) CLIENT_FIELDS.forEach(function (k) { if (f.elements[k] && r.data[k] != null) f.elements[k].value = r.data[k]; });
      });
      f.addEventListener('submit', function (e) {
        e.preventDefault(); var row = { id: uid, actualizat: new Date().toISOString() };
        CLIENT_FIELDS.forEach(function (k) { if (f.elements[k]) row[k] = f.elements[k].value.trim() || null; });
        sb.from('magazin_clienti').upsert(row).then(function (r) { flash(f, r.error ? 'Eroare: ' + r.error.message : 'Datele au fost salvate.'); });
      });
    }
    function loadProfil(uid) {
      var f = $('[data-profil-form]', root);
      sb.from('magazin_profil_nutritional').select('*').eq('user_id', uid).maybeSingle().then(function (r) {
        if (r.data) { PROFIL_FIELDS.forEach(function (k) { if (r.data[k] != null) f.elements[k].value = r.data[k]; }); f.elements.consimtamant.checked = true; }
      });
      f.addEventListener('submit', function (e) {
        e.preventDefault();
        if (!f.elements.consimtamant.checked) { flash(f, 'Pentru a salva profilul, bifează consimțământul.'); return; }
        var row = { user_id: uid, consimtamant: new Date().toISOString(), actualizat: new Date().toISOString() };
        PROFIL_FIELDS.forEach(function (k) { row[k] = f.elements[k].value || null; });
        sb.from('magazin_profil_nutritional').upsert(row).then(function (r) { flash(f, r.error ? 'Eroare: ' + r.error.message : 'Profilul a fost salvat.'); });
      });
      $('[data-profil-delete]', root).addEventListener('click', function () {
        if (!confirm('Ștergi definitiv profilul nutrițional?')) return;
        sb.from('magazin_profil_nutritional').delete().eq('user_id', uid).then(function (r) {
          if (!r.error) { f.reset(); } flash(f, r.error ? 'Eroare: ' + r.error.message : 'Profilul a fost șters și consimțământul retras.');
        });
      });
    }
    function flash(f, t) { var m = f.querySelector('.mz-form-msg'); m.textContent = t; m.style.display = 'block'; }
  }

  /* ---------- integrare cu pagina coșului ---------- */
  function initCheckout() {
    var form = $('[data-mz-form]'); if (!form) return;
    var bar = $('[data-account-bar]');
    session().then(function (s) {
      if (!s) { if (bar) { bar.innerHTML = 'Ai cont? <a href="/magazin/cont/">Conectează-te</a> pentru date precompletate și istoricul comenzilor. Poți comanda și fără cont.'; } return; }
      if (bar) bar.innerHTML = 'Ești conectat ca <strong>' + esc(s.user.email) + '</strong>. Comanda va apărea în <a href="/magazin/cont/">contul tău</a>.';
      var em = form.elements.email; if (em && !em.value) { em.value = s.user.email; }
      var save = $('[data-save-account]'); if (save) save.style.display = '';
      sb.from('magazin_clienti').select('*').eq('id', s.user.id).maybeSingle().then(function (r) {
        if (!r.data) return;
        CLIENT_FIELDS.forEach(function (k) { if (form.elements[k] && !form.elements[k].value && r.data[k]) form.elements[k].value = r.data[k]; });
        if (r.data.firma_denumire && form.elements.pe_firma && !form.elements.pe_firma.checked) { form.elements.pe_firma.click(); }
      });
      sb.from('magazin_profil_nutritional').select('*').eq('user_id', s.user.id).maybeSingle().then(function (r) {
        if (!r.data) return;
        PROFIL_FIELDS.forEach(function (k) { if (form.elements[k] && r.data[k] != null) form.elements[k].value = r.data[k]; });
        form.elements.consimtamant_profil.checked = true;
      });
    });
    /* apelat de cos.js înainte de trimiterea comenzii: salvează datele în cont (dacă e bifat) și întoarce tokenul */
    window.NSAuth = {
      beforeCheckout: function (data) {
        return session().then(function (s) {
          if (!s) return null;
          var jobs = [];
          var keep = form.elements.salveaza_in_cont && form.elements.salveaza_in_cont.checked;
          if (keep) {
            var row = { id: s.user.id, actualizat: new Date().toISOString() };
            CLIENT_FIELDS.forEach(function (k) { row[k] = (data[k] || '') || null; });
            jobs.push(sb.from('magazin_clienti').upsert(row));
            if (data.consimtamant_profil) {
              var p = { user_id: s.user.id, consimtamant: new Date().toISOString(), actualizat: new Date().toISOString() };
              PROFIL_FIELDS.forEach(function (k) { p[k] = data[k] || null; });
              jobs.push(sb.from('magazin_profil_nutritional').upsert(p));
            }
          }
          return Promise.all(jobs).then(function () { return s.access_token; }, function () { return s.access_token; });
        });
      }
    };
  }

  document.addEventListener('DOMContentLoaded', function () { initAccount(); initCheckout(); });
})();
