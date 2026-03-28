/* ═══════════════════════════════════════════════════════════════════════════
   NUTRISIB — Cookie Consent & Tracking Manager
   ═══════════════════════════════════════════════════════════════════════════
   
   INSTALARE:
   1. Urcă acest fișier pe server (ex: https://nutrisib.club/cookies.js)
   2. Adaugă în FIECARE pagină, înainte de </body>:
      <script src="https://nutrisib.club/cookies.js"></script>
   3. ȘTERGE din <head> scripturile vechi de GA4:
      <script async src="...gtag/js?id=G-1TQP0TLWC5"></script>
      <script>window.dataLayer=...gtag('config','G-1TQP0TLWC5');</script>
   
   Ce face scriptul:
   - Pe PAGINA PRINCIPALĂ: arată banner cookie + încarcă tracking (dacă e consimțit)
   - Pe CELELALTE PAGINI: doar încarcă tracking (dacă e consimțit), fără banner
   - Butonul 🍪 apare pe TOATE paginile pentru re-editare consimțământ
   ═══════════════════════════════════════════════════════════════════════════ */

(function() {
'use strict';

/* ┌──────────────────────────────────────────────────────────┐
   │  CONFIGURARE — Pune ID-urile tale aici                  │
   └──────────────────────────────────────────────────────────┘ */

var CONFIG = {
    GA_ID:     'G-1TQP0TLWC5',          // Google Analytics 4
    FB_PIXEL:  '351919528248445',          // Facebook Pixel NutriSib
    COOKIE_NAME: 'nutrisib_consent',
    COOKIE_DAYS: 365,
    // Pagini pe care apare bannerul automat (la prima vizită)
    // Gol = doar homepage ('/')
    HOMEPAGE_PATHS: ['/', '/index.html']
};


/* ┌──────────────────────────────────────────────────────────┐
   │  UTILITĂȚI COOKIES                                       │
   └──────────────────────────────────────────────────────────┘ */

function setCookie(name, val, days) {
    var d = new Date();
    d.setTime(d.getTime() + days * 864e5);
    document.cookie = name + '=' + encodeURIComponent(JSON.stringify(val)) +
        ';expires=' + d.toUTCString() + ';path=/;SameSite=Lax;Secure';
}

function getCookie(name) {
    var m = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (m) { try { return JSON.parse(decodeURIComponent(m[2])); } catch(e) { return null; } }
    return null;
}

function deleteCookie(name) {
    document.cookie = name + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;SameSite=Lax';
}


/* ┌──────────────────────────────────────────────────────────┐
   │  ÎNCĂRCARE SCRIPTURI TRACKING                            │
   └──────────────────────────────────────────────────────────┘ */

var trackingLoaded = { ga: false, fb: false };

function loadGA4() {
    if (trackingLoaded.ga || !CONFIG.GA_ID) return;
    trackingLoaded.ga = true;

    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + CONFIG.GA_ID;
    document.head.appendChild(s);

    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', CONFIG.GA_ID, { anonymize_ip: true });
    console.log('[NutriSib Cookies] ✅ GA4 activ');
}

function loadFBPixel() {
    if (trackingLoaded.fb || !CONFIG.FB_PIXEL) return;
    trackingLoaded.fb = true;

    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){
    n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};
    if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];
    t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t,s)}(window,document,'script',
    'https://connect.facebook.net/en_US/fbevents.js');

    fbq('init', CONFIG.FB_PIXEL);
    fbq('track', 'PageView');
    console.log('[NutriSib Cookies] ✅ FB Pixel activ');
}

function loadAllTracking(consent) {
    if (consent.analytics) loadGA4();
    if (consent.marketing) loadFBPixel();
}


/* ┌──────────────────────────────────────────────────────────┐
   │  FUNCȚII DE CONVERSII (apelabile din orice pagină)       │
   └──────────────────────────────────────────────────────────┘ */

window.trackConversion = function(type, value) {
    var c = getCookie(CONFIG.COOKIE_NAME);
    if (c && c.analytics && window.gtag) {
        gtag('event', 'generate_lead', {
            event_category: 'lead', event_label: type, value: value || 0, currency: 'RON'
        });
    }
    if (c && c.marketing && window.fbq) {
        fbq('track', 'Lead', { content_name: type, value: value || 0, currency: 'RON' });
    }
};

window.trackProgramare = function(serviciu, valoare) {
    trackConversion('programare_' + serviciu, valoare);
    if (window.fbq) fbq('track', 'Schedule', { content_name: serviciu, value: valoare || 0, currency: 'RON' });
};


/* ┌──────────────────────────────────────────────────────────┐
   │  INJECT CSS (scoped cu prefix .ncc-)                     │
   └──────────────────────────────────────────────────────────┘ */

function injectCSS() {
    if (document.getElementById('ncc-styles')) return;
    var style = document.createElement('style');
    style.id = 'ncc-styles';
    style.textContent = '\
/* ── NutriSib Cookie Consent ── */\
.ncc-overlay {\
    position:fixed;inset:0;background:rgba(0,0,0,0.55);\
    backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);\
    z-index:2500;opacity:0;transition:opacity .4s ease;\
    pointer-events:none;\
}\
.ncc-overlay.ncc-active { opacity:1;pointer-events:auto; }\
\
.ncc-banner {\
    position:fixed;bottom:0;left:0;right:0;z-index:2501;\
    padding:0 16px 16px;\
    transform:translateY(110%);\
    transition:transform .55s cubic-bezier(.16,1,.3,1);\
}\
.ncc-banner.ncc-active { transform:translateY(0); }\
\
.ncc-inner {\
    max-width:620px;margin:0 auto;\
    background:#fff;border:1px solid var(--color-border, #e5e7eb);\
    border-radius:var(--radius-card, 12px);\
    box-shadow:0 -4px 30px rgba(0,0,0,0.12), 0 -1px 8px rgba(0,0,0,0.06);\
    overflow:hidden;\
    font-family:"Inter",sans-serif;\
}\
\
.ncc-head {\
    padding:20px 24px 0;\
    display:flex;align-items:center;gap:12px;\
}\
.ncc-head-icon {\
    width:42px;height:42px;\
    background:linear-gradient(135deg, var(--color-navy, #1B2A4A), var(--color-brand-medium, #3E92CC));\
    border-radius:10px;\
    display:flex;align-items:center;justify-content:center;\
    flex-shrink:0;\
}\
.ncc-head-icon svg { width:22px;height:22px; }\
.ncc-head h3 {\
    font-family:"Lora",serif;font-size:1.05rem;font-weight:700;\
    color:var(--color-navy, #1B2A4A);margin:0;\
}\
\
.ncc-body {\
    padding:14px 24px 0;\
    font-size:.88rem;line-height:1.65;\
    color:var(--color-text-light, #4b5563);\
}\
.ncc-body a {\
    color:var(--color-brand-medium, #3E92CC);text-decoration:none;\
    border-bottom:1px solid transparent;transition:border-color .2s;\
}\
.ncc-body a:hover { border-bottom-color:var(--color-brand-medium, #3E92CC); }\
\
/* ── Categorii ── */\
.ncc-cats {\
    padding:0 24px;max-height:0;overflow:hidden;\
    transition:max-height .4s ease, padding .3s ease;\
}\
.ncc-cats.ncc-open { max-height:320px;padding:14px 24px; }\
\
.ncc-cat {\
    display:flex;align-items:center;justify-content:space-between;\
    padding:11px 14px;\
    background:var(--color-pearl, #F8FAFC);\
    border:1px solid var(--color-border, #e5e7eb);\
    border-radius:8px;margin-bottom:8px;\
    transition:border-color .2s;\
}\
.ncc-cat:last-child { margin-bottom:0; }\
.ncc-cat:hover { border-color:var(--color-brand-medium, #3E92CC); }\
\
.ncc-cat-info { display:flex;flex-direction:column;gap:1px; }\
.ncc-cat-name { font-size:.85rem;font-weight:700;color:var(--color-navy, #1B2A4A); }\
.ncc-cat-desc { font-size:.75rem;color:var(--color-text-light, #4b5563); }\
\
/* ── Toggle ── */\
.ncc-toggle { position:relative;width:42px;height:22px;flex-shrink:0; }\
.ncc-toggle input { opacity:0;width:0;height:0; }\
.ncc-toggle-sl {\
    position:absolute;inset:0;\
    background:var(--color-border, #e5e7eb);\
    border-radius:100px;cursor:pointer;\
    transition:background .3s;\
}\
.ncc-toggle-sl::before {\
    content:"";position:absolute;top:3px;left:3px;\
    width:16px;height:16px;background:#fff;\
    border-radius:50%;transition:transform .3s;\
    box-shadow:0 1px 3px rgba(0,0,0,0.15);\
}\
.ncc-toggle input:checked + .ncc-toggle-sl { background:var(--color-brand-medium, #3E92CC); }\
.ncc-toggle input:checked + .ncc-toggle-sl::before { transform:translateX(20px); }\
.ncc-toggle input:disabled + .ncc-toggle-sl { opacity:.6;cursor:not-allowed; }\
\
/* ── Butoane (refolosesc stilul site-ului) ── */\
.ncc-actions {\
    padding:18px 24px 22px;\
    display:flex;gap:8px;flex-wrap:wrap;\
}\
.ncc-btn {\
    flex:1;min-width:100px;\
    padding:.6rem 1.2rem;\
    border:none;border-radius:8px;\
    font-family:"Inter",sans-serif;\
    font-size:.85rem;font-weight:800;\
    cursor:pointer;transition:all .15s ease;\
    text-align:center;\
}\
.ncc-btn-accept {\
    background:var(--color-navy, #1B2A4A);\
    color:#fff;\
    box-shadow:0 3px 0 #051336, 0 4px 6px rgba(0,0,0,0.1);\
    order:3;\
}\
.ncc-btn-accept:hover {\
    transform:translateY(1px);\
    box-shadow:0 2px 0 #051336, 0 3px 4px rgba(0,0,0,0.1);\
    background:#0c2a75;\
}\
.ncc-btn-accept:active {\
    transform:translateY(3px);\
    box-shadow:0 0 0 #051336;\
}\
\
.ncc-btn-reject {\
    background:var(--color-pearl, #F8FAFC);\
    color:var(--color-text-medium, #374151);\
    box-shadow:0 3px 0 #cbd5e1, 0 4px 6px rgba(0,0,0,0.1);\
    order:1;\
}\
.ncc-btn-reject:hover {\
    transform:translateY(1px);\
    box-shadow:0 2px 0 #cbd5e1;\
    background:#f1f5f9;\
}\
\
.ncc-btn-custom {\
    background:transparent;\
    color:var(--color-brand-medium, #3E92CC);\
    border:1.5px solid var(--color-border, #e5e7eb) !important;\
    box-shadow:none;\
    order:2;\
}\
.ncc-btn-custom:hover {\
    background:var(--color-brand-light, #eaf2f8);\
    border-color:var(--color-brand-medium, #3E92CC) !important;\
}\
\
/* ── Floating reopen ── */\
.ncc-reopen {\
    position:fixed;bottom:18px;left:18px;z-index:2499;\
    width:42px;height:42px;\
    background:var(--color-navy, #1B2A4A);\
    border:none;border-radius:50%;\
    display:flex;align-items:center;justify-content:center;\
    cursor:pointer;\
    box-shadow:0 3px 0 #051336, 0 4px 12px rgba(0,0,0,0.2);\
    transition:all .2s;\
    opacity:0;transform:scale(.7);\
    pointer-events:none;\
}\
.ncc-reopen.ncc-active {\
    opacity:1;transform:scale(1);pointer-events:auto;\
}\
.ncc-reopen:hover {\
    transform:scale(1.08) translateY(-1px);\
    box-shadow:0 4px 0 #051336, 0 6px 16px rgba(0,0,0,0.25);\
}\
.ncc-reopen svg { width:20px;height:20px; }\
\
/* ── Responsive ── */\
@media (max-width:500px) {\
    .ncc-head { padding:16px 18px 0; }\
    .ncc-body { padding:10px 18px 0; }\
    .ncc-cats.ncc-open { padding:10px 18px; }\
    .ncc-actions { padding:14px 18px 18px;flex-direction:column; }\
    .ncc-btn { min-width:100%; }\
    .ncc-btn-accept { order:1; }\
    .ncc-btn-custom { order:2; }\
    .ncc-btn-reject { order:3; }\
}\
';
    document.head.appendChild(style);
}


/* ┌──────────────────────────────────────────────────────────┐
   │  INJECT HTML                                             │
   └──────────────────────────────────────────────────────────┘ */

var SHIELD_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>';

var COOKIE_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="8" cy="9" r="1" fill="#fff"/><circle cx="15" cy="12" r="1" fill="#fff"/><circle cx="10" cy="15" r="1" fill="#fff"/><circle cx="14" cy="7" r="1" fill="#fff"/></svg>';

function injectHTML() {
    if (document.getElementById('nccBanner')) return;

    // Overlay
    var overlay = document.createElement('div');
    overlay.className = 'ncc-overlay';
    overlay.id = 'nccOverlay';
    document.body.appendChild(overlay);

    // Banner
    var banner = document.createElement('div');
    banner.className = 'ncc-banner';
    banner.id = 'nccBanner';
    banner.innerHTML = '\
<div class="ncc-inner">\
    <div class="ncc-head">\
        <div class="ncc-head-icon">' + SHIELD_SVG + '</div>\
        <h3>Protejăm datele tale</h3>\
    </div>\
    <div class="ncc-body">\
        Folosim cookies analitice și de marketing pentru a înțelege cum folosești site-ul \
        și pentru a-ți arăta conținut relevant. \
        Alegi tu ce permiți. \
        <a href="#" onclick="event.preventDefault(); \
            if(typeof toggleModal===\'function\') toggleModal(\'privacyModal\',true);">Politica de confidențialitate</a>\
    </div>\
    <div class="ncc-cats" id="nccCats">\
        <div class="ncc-cat">\
            <div class="ncc-cat-info">\
                <span class="ncc-cat-name">Esențiale</span>\
                <span class="ncc-cat-desc">Funcționarea corectă a site-ului</span>\
            </div>\
            <label class="ncc-toggle"><input type="checkbox" checked disabled><span class="ncc-toggle-sl"></span></label>\
        </div>\
        <div class="ncc-cat">\
            <div class="ncc-cat-info">\
                <span class="ncc-cat-name">Analitice</span>\
                <span class="ncc-cat-desc">Google Analytics — cine vizitează, de unde, ce pagini</span>\
            </div>\
            <label class="ncc-toggle"><input type="checkbox" id="nccAnalytics"><span class="ncc-toggle-sl"></span></label>\
        </div>\
        <div class="ncc-cat">\
            <div class="ncc-cat-info">\
                <span class="ncc-cat-name">Marketing</span>\
                <span class="ncc-cat-desc">Facebook Pixel — retargeting & urmărire conversii</span>\
            </div>\
            <label class="ncc-toggle"><input type="checkbox" id="nccMarketing"><span class="ncc-toggle-sl"></span></label>\
        </div>\
    </div>\
    <div class="ncc-actions">\
        <button class="ncc-btn ncc-btn-reject" id="nccReject">Refuz</button>\
        <button class="ncc-btn ncc-btn-custom" id="nccCustom">Personalizează</button>\
        <button class="ncc-btn ncc-btn-accept" id="nccAccept">Accept tot</button>\
    </div>\
</div>';
    document.body.appendChild(banner);

    // Reopen button (pe toate paginile)
    var reopen = document.createElement('button');
    reopen.className = 'ncc-reopen';
    reopen.id = 'nccReopen';
    reopen.title = 'Setări cookies';
    reopen.innerHTML = COOKIE_SVG;
    document.body.appendChild(reopen);

    // Attach events
    document.getElementById('nccAccept').addEventListener('click', acceptAll);
    document.getElementById('nccReject').addEventListener('click', rejectAll);
    document.getElementById('nccCustom').addEventListener('click', toggleCustomize);
    document.getElementById('nccReopen').addEventListener('click', reopenBanner);
    overlay.addEventListener('click', function() { /* nu închide la click pe overlay — forțează alegere */ });
}


/* ┌──────────────────────────────────────────────────────────┐
   │  LOGICA BANNERULUI                                       │
   └──────────────────────────────────────────────────────────┘ */

var customizeOpen = false;

function showBanner() {
    document.getElementById('nccBanner').classList.add('ncc-active');
    document.getElementById('nccOverlay').classList.add('ncc-active');
    document.getElementById('nccReopen').classList.remove('ncc-active');
}

function hideBanner() {
    document.getElementById('nccBanner').classList.remove('ncc-active');
    document.getElementById('nccOverlay').classList.remove('ncc-active');
    document.getElementById('nccCats').classList.remove('ncc-open');
    customizeOpen = false;
    var btn = document.getElementById('nccCustom');
    btn.textContent = 'Personalizează';
    setTimeout(function() {
        document.getElementById('nccReopen').classList.add('ncc-active');
    }, 500);
}

function saveConsent(consent) {
    setCookie(CONFIG.COOKIE_NAME, consent, CONFIG.COOKIE_DAYS);
    loadAllTracking(consent);
    hideBanner();
}

function acceptAll() {
    saveConsent({ essential: true, analytics: true, marketing: true, ts: Date.now() });
}

function rejectAll() {
    saveConsent({ essential: true, analytics: false, marketing: false, ts: Date.now() });
}

function saveCustom() {
    var a = document.getElementById('nccAnalytics').checked;
    var m = document.getElementById('nccMarketing').checked;
    saveConsent({ essential: true, analytics: a, marketing: m, ts: Date.now() });
}

function toggleCustomize() {
    customizeOpen = !customizeOpen;
    var cats = document.getElementById('nccCats');
    var btn = document.getElementById('nccCustom');
    if (customizeOpen) {
        cats.classList.add('ncc-open');
        btn.textContent = 'Salvează selecția';
        btn.removeEventListener('click', toggleCustomize);
        btn.addEventListener('click', saveCustom);
    } else {
        cats.classList.remove('ncc-open');
        btn.textContent = 'Personalizează';
        btn.removeEventListener('click', saveCustom);
        btn.addEventListener('click', toggleCustomize);
    }
}

function reopenBanner() {
    // Resetează toggles la consimțământul curent
    var consent = getCookie(CONFIG.COOKIE_NAME);
    if (consent) {
        var a = document.getElementById('nccAnalytics');
        var m = document.getElementById('nccMarketing');
        if (a) a.checked = !!consent.analytics;
        if (m) m.checked = !!consent.marketing;
    }
    document.getElementById('nccReopen').classList.remove('ncc-active');
    showBanner();
}


/* ┌──────────────────────────────────────────────────────────┐
   │  DETECTARE PAGINA PRINCIPALĂ                             │
   └──────────────────────────────────────────────────────────┘ */

function isHomepage() {
    var path = window.location.pathname.replace(/\/+$/, '') || '/';
    for (var i = 0; i < CONFIG.HOMEPAGE_PATHS.length; i++) {
        if (path === CONFIG.HOMEPAGE_PATHS[i] || path === CONFIG.HOMEPAGE_PATHS[i].replace(/\/+$/, '')) {
            return true;
        }
    }
    return false;
}


/* ┌──────────────────────────────────────────────────────────┐
   │  INIȚIALIZARE                                            │
   └──────────────────────────────────────────────────────────┘ */

function init() {
    injectCSS();
    injectHTML();

    var consent = getCookie(CONFIG.COOKIE_NAME);

    if (!consent) {
        // Niciun consimțământ încă
        if (isHomepage()) {
            // Pe pagina principală: arată bannerul
            setTimeout(showBanner, 900);
        }
        // Pe alte pagini: nu se încarcă nimic, nu se arată nimic
        // (doar butonul 🍪 apare dacă vrea să seteze manual)
    } else {
        // Consimțământ existent: încarcă tracking-ul pe ORICE pagină
        loadAllTracking(consent);
        // Arată butonul de re-editare
        document.getElementById('nccReopen').classList.add('ncc-active');
    }
}

// Pornește când DOM-ul e gata
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

})();
