/* Paginile Herbalife: fereastra „distribuitor independent” (o dată pe sesiune) + video TikTok la cerere */
(function () {
  'use strict';
  var KEY = 'nutrisib_hl_modal_v1';
  function seen() { try { return sessionStorage.getItem(KEY) === '1'; } catch (e) { return false; } }
  function mark() { try { sessionStorage.setItem(KEY, '1'); } catch (e) {} }
  function modal() {
    if (seen()) return;
    var back = document.createElement('div'); back.className = 'mz-modal-back';
    back.innerHTML =
      '<div class="mz-modal" role="dialog" aria-modal="true" aria-labelledby="mz-modal-t"><div class="mz-modal-inner">' +
      '<button type="button" class="mz-modal-x" aria-label="Închide">×</button>' +
      '<h2 id="mz-modal-t">Această pagină este operată de un Distribuitor Independent Herbalife Nutrition: <strong>RADU PASCU</strong></h2>' +
      '<div class="mz-modal-cols"><div><h3>Ești deja client?</h3>' +
      '<p>Relația de unu-la-unu cu Distribuitorul tău Independent Herbalife Nutrition este esențială pentru atingerea obiectivelor tale. Dacă RADU PASCU nu este Distribuitorul tău Independent Herbalife Nutrition, te încurajăm să cumperi produsele de la Distribuitorul tău Independent Herbalife Nutrition. Altfel, <button type="button" class="mz-modal-continue">CLICK AICI</button> pentru a continua pe această pagină.</p></div>' +
      '<div><h3>Ești deja Distribuitor Independent Herbalife Nutrition sau Client Privilegiat?</h3>' +
      '<p>Pentru a achiziționa produse prin intermediul contului tău personal și pentru a primi toate beneficiile te rugăm să accesezi <a href="https://www.myherbalife.com/ro-RO" target="_blank" rel="noopener">myherbalife.com</a></p></div></div>' +
      '</div></div>';
    function close() { mark(); back.remove(); document.removeEventListener('keydown', esc); }
    function esc(e) { if (e.key === 'Escape') close(); }
    back.querySelector('.mz-modal-x').addEventListener('click', close);
    back.querySelector('.mz-modal-continue').addEventListener('click', close);
    back.addEventListener('click', function (e) { if (e.target === back) close(); });
    document.addEventListener('keydown', esc);
    document.body.appendChild(back);
    back.querySelector('.mz-modal-continue').focus();
  }
  function video() {
    document.querySelectorAll('[data-tiktok]').forEach(function (box) {
      box.querySelector('button').addEventListener('click', function () {
        var id = box.getAttribute('data-tiktok'), u = box.getAttribute('data-user');
        box.outerHTML = '<blockquote class="tiktok-embed" cite="https://www.tiktok.com/@' + u + '/video/' + id + '" data-video-id="' + id + '" style="max-width:605px;min-width:325px"><section><a target="_blank" rel="noopener" href="https://www.tiktok.com/@' + u + '/video/' + id + '">@' + u + ' pe TikTok</a></section></blockquote>';
        var sc = document.createElement('script'); sc.src = 'https://www.tiktok.com/embed.js'; sc.async = true; document.body.appendChild(sc);
      });
    });
  }
  document.addEventListener('DOMContentLoaded', function () { modal(); video(); });
})();
