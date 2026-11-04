#!/usr/bin/env python3
"""Șabloane și constante comune magazinului NutriSib (Herbalife, LR, …).
Importat de scripts/magazin_build.py (Herbalife) și scripts/magazin_lr.py (LR)."""
import os, re, json, html, datetime, markdown
SITE = 'https://nutrisib.club'
TODAY = datetime.date.today().isoformat()
PRAG_VP, TRANSPORT = 125, 25
VANZATOR = 'PASCU RADU VASILE ÎNTREPRINDERE INDIVIDUALĂ'
CONTACT_TEL = '+40770276406'; CONTACT_TEL_AFIS = '+40 770 276 406'; CONTACT_EMAIL = 'nutrisib.club@gmail.com'
def precomanda_box(magazin, deschidere=''):
    """Caseta afișată cât timp comenzile online pentru un magazin nu sunt deschise."""
    return (f'<div class="mz-soon-box"><strong>Comenzile online pentru produsele {magazin} se deschid în curând{deschidere}.</strong> '
            f'Până atunci poți face o <strong>precomandă</strong> sau poți cere informații suplimentare: '
            f'<span class="mz-contact"><a href="tel:{CONTACT_TEL}">📞 {CONTACT_TEL_AFIS}</a> '
            f'<a href="mailto:{CONTACT_EMAIL}?subject=Precomand%C4%83%20{magazin}">✉ {CONTACT_EMAIL}</a></span></div>')
REGCOM = 'F32/667/2017'   # format nou ONRC (14 caractere) doar după ce e emis oficial
E = lambda s: html.escape(str(s or ''), quote=True)

CUR = ' aria-current="page"'
def vp_fmt(v): return f'{v:.2f}'.replace('.', ',')
def lei(n): return f'{n:,}'.replace(',', '.') + ' lei'
def write(path, s):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(s)
def jsonld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>\n'

# ======================= șabloane comune =======================
def head(title, desc, canon, og_img=None, extra='', robots=None):
    return f'''<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
{f'<meta name="robots" content="{robots}">' if robots else ''}
<link rel="canonical" href="{SITE}{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="NutriSib">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{SITE}{canon}">
<meta property="og:image" content="{SITE}{og_img or '/imagini/logo_alb.png'}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Lora:ital,wght@0,400..700;1,400..700&family=Montserrat:wght@700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/celos.css">
<link rel="stylesheet" href="/magazin/assets/magazin.css">
{extra}</head>
<body>
<div class="container-main">
<header class="nav-bar">
  <a href="/" class="nav-brand"><img src="/logo/logo_navy_pearl.png" alt="NutriSib" class="logo-image"></a>
  <nav class="nav-links" aria-label="Navigare principală">
    <a href="/">Acasă</a>
    <a href="/#povestea">Povestea</a>
    <a href="/#metoda">Metoda</a>
    <a href="/blog/">Blog</a>
    <a href="/magazin/" class="active">Magazin</a>
    <a href="/contact.html">Contact</a>
    <a href="/magazin/cont/">Contul meu</a>
    <a href="/magazin/cos/" class="mz-cart-link" aria-label="Coșul de cumpărături">Coș <span class="mz-cart-count" data-n="0">0</span></a>
  </nav>
  <a href="/magazin/cos/" class="mz-cart-mobile" aria-label="Coșul de cumpărături"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23 6H6"/></svg><span class="mz-cart-count" data-n="0">0</span></a>
  <button class="mobile-menu-btn" aria-label="Meniu" onclick="var n=document.querySelector('.nav-links');n.style.display=(n.style.display==='flex'?'none':'flex')">☰</button>
</header>
<main>
'''

SHOPFOOT = f'''<section class="content-card">
  <div class="mz-shopfoot">
    <div>
      <p style="margin:0 0 .4rem"><strong>Magazinul NutriSib</strong> este operat de {VANZATOR}<br>CUI 38416337 · Nr. Reg. Com. {REGCOM}</p>
      <nav class="mz-legal-nav" aria-label="Informații legale">
        <a href="/magazin/termeni-si-conditii/">Termeni și condiții</a>
        <a href="/magazin/livrare/">Livrare</a>
        <a href="/magazin/retur/">Retur în 14 zile</a>
        <a href="/magazin/confidentialitate/">Protecția datelor (GDPR)</a>
      </nav>
    </div>
    <div class="mz-anpc-wrap">
      <a class="mz-anpc" href="https://anpc.ro/ce-este-sal/" target="_blank" rel="nofollow noopener"><b>ANPC</b> Soluționarea alternativă a litigiilor (SAL)</a>
    </div>
  </div>
</section>
'''

def foot(scripts=''):
    return f'''{SHOPFOOT}</main>
<div id="footer-placeholder"></div>
</div>
<script src="/magazin/assets/cos.js" defer></script>
{scripts}<script>fetch('/footer.html').then(function(r){{return r.ok?r.text():''}}).then(function(t){{var c=document.getElementById('footer-placeholder');if(c)c.innerHTML=t}}).catch(function(){{}});</script>
<script src="/cookies.js"></script>
</body>
</html>
'''

def crumbs(items):
    h = '<nav class="mz-crumbs" aria-label="Breadcrumb">' + '<span>/</span>'.join(f'<a href="{u}">{E(t)}</a>' if u else E(t) for t, u in items) + '</nav>'
    ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': t, **({'item': SITE + u} if u else {})} for i, (t, u) in enumerate(items)]}
    return h, jsonld(ld)

MD = markdown.Markdown(extensions=['extra', 'sane_lists'])
def md2html(t, img_nutr=None):
    if img_nutr:
        t = re.sub(r'!\[([^\]]*)\]\(04-tabel-nutritional\.[a-z]+\)', lambda m: f'![{m.group(1)}]({img_nutr})', t)
    MD.reset(); return MD.convert(t).replace('<img ', '<img loading="lazy" ')

SB_SCRIPTS = ('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js"></script>\n'
              '<script src="/magazin/assets/sb-config.js"></script>\n<script src="/magazin/assets/cont.js" defer></script>\n')


# ======================= pagina coșului (Herbalife: /magazin/cos/, LR: /magazin/lr/cos/) =======================
JUDETE = ['Alba','Arad','Argeș','Bacău','Bihor','Bistrița-Năsăud','Botoșani','Brașov','Brăila','București','Buzău','Caraș-Severin','Călărași','Cluj','Constanța','Covasna','Dâmbovița','Dolj','Galați','Giurgiu','Gorj','Harghita','Hunedoara','Ialomița','Iași','Ilfov','Maramureș','Mehedinți','Mureș','Neamț','Olt','Prahova','Satu Mare','Sălaj','Sibiu','Suceava','Teleorman','Timiș','Tulcea','Vaslui','Vâlcea','Vrancea']
opt_jud = '<option value="">Alege județul</option>' + ''.join(f'<option>{j}</option>' for j in JUDETE)
def fld(name, label, typ='text', req=True, full=False, extra='', ac=''):
    return (f'<div class="mz-field{" full" if full else ""}"><label for="f-{name}">{label}{" <span class=req>*</span>" if req else ""}</label>'
            f'<input id="f-{name}" name="{name}" type="{typ}"{" required" if req else ""}{f" autocomplete={ac}" if ac else ""} {extra}></div>')
cur_year = datetime.date.today().year
def cos_body(magazin='herbalife'):
    """Coșul + formularul de comandă. Fiecare magazin are coșul lui (comenzi separate)."""
    lr = magazin == 'lr'
    return f'''<div class="mz-crumbs-wrap">{crumbs([('Magazin', '/magazin/')] + ([('LR', '/magazin/lr/')] if lr else []) + [('Coș', None)])[0]}</div>
<div data-mz-cart>
<section class="content-card" data-empty style="display:none;text-align:center">
  <h1 class="mz-p-title">Coșul este gol</h1>
  <p>Adaugă produse din magazin și revino aici pentru comandă.</p>
  <p><a class="mz-btn" style="display:inline-flex;flex:none" href="/magazin/{magazin}/">Vezi produsele {"LR" if lr else "Herbalife"}</a></p>
</section>
<div class="mz-checkout" data-filled>
    <section class="content-card mz-co-lines">
      <h1 class="mz-section-title">Coșul tău{" LR" if lr else ""}</h1>
      <div data-lines></div>
    </section>
    <aside class="content-card mz-summary">
      <h2 class="mz-section-title">Sumar comandă</h2>
      <div data-summary></div>
      <p class="mz-buy-note">Prețurile sunt finale, în lei. Livrarea se face prin curier, pe teritoriul României.</p>
    </aside>
    <section class="content-card mz-co-form">
      <form class="mz-form" data-mz-form novalidate>
        <div class="mz-account-bar" data-account-bar>Poți comanda și fără cont. <a href="/magazin/cont/">Conectează-te</a> pentru date precompletate și istoricul comenzilor.</div>
        <fieldset>
          <legend>Date de contact și livrare</legend>
          <div class="mz-fields">
            {fld('nume', 'Nume', ac='family-name')}{fld('prenume', 'Prenume', ac='given-name')}
            {fld('email', 'E-mail', 'email', ac='email')}{fld('telefon', 'Telefon', 'tel', ac='tel', extra='pattern="[0-9+ ]{{10,15}}" title="Număr de telefon valid"')}
            <div class="mz-field"><label for="f-judet">Județ <span class=req>*</span></label><select id="f-judet" name="judet" required>{opt_jud}</select></div>
            {fld('localitate', 'Localitate', ac='address-level2')}
            {fld('adresa', 'Adresă (stradă, număr, bloc, scară, apartament)', full=True, ac='street-address')}
            {fld('cod_postal', 'Cod poștal', req=False, ac='postal-code', extra='inputmode="numeric" maxlength="6"')}
            <div class="mz-field full"><label for="f-observatii">Observații pentru livrare</label><textarea id="f-observatii" name="observatii" rows="2" maxlength="400"></textarea></div>
          </div>
        </fieldset>
        <fieldset>
          <legend>Facturare</legend>
          <div class="mz-fields" data-pf>
            <div class="mz-field"><label for="f-cnp">CNP (opțional)</label><input id="f-cnp" name="cnp" inputmode="numeric" maxlength="13" pattern="[0-9]{{13}}" title="CNP-ul are 13 cifre" autocomplete="off"></div>
            <p class="mz-field-note">Completează-l doar dacă vrei ca CNP-ul să apară pe factură. Dacă îl lași gol, factura se emite fără CNP, conform legii. Nu îl salvăm în cont.</p>
          </div>
          <label class="mz-check"><input type="checkbox" name="pe_firma"> <span>Vreau factură pe firmă (persoană juridică)</span></label>
          <div class="mz-fields" data-firma style="display:none;margin-top:.75rem">
            <div class="mz-field full"><label for="f-firma">Denumirea firmei <span class=req>*</span></label><input id="f-firma" name="firma_denumire" data-req></div>
            <div class="mz-field"><label for="f-cui">CUI / CIF <span class=req>*</span></label><input id="f-cui" name="firma_cui" data-req></div>
            <div class="mz-field"><label for="f-rc">Nr. Registrul Comerțului</label><input id="f-rc" name="firma_regcom"></div>
            <div class="mz-field full"><label for="f-fadr">Adresa sediului social <span class=req>*</span></label><input id="f-fadr" name="firma_adresa" data-req></div>
          </div>
        </fieldset>
        <fieldset>
          <details class="mz-optional" data-profil>
            <summary>Profilul tău nutrițional (opțional)</summary>
            <p>Dacă vrei ca recomandările NutriSib să țină cont de obiectivele tale, poți completa datele de mai jos. Nu sunt necesare pentru comandă. Fiind date legate de sănătate, le prelucrăm doar cu acordul tău explicit (art. 9 GDPR) și le poți retrage oricând.</p>
            <div class="mz-fields">
              {fld('greutate_actuala', 'Greutate actuală (kg)', 'number', False, extra='min="30" max="300" step="0.1"')}
              {fld('greutate_dorita', 'Greutate dorită (kg)', 'number', False, extra='min="30" max="300" step="0.1"')}
              {fld('inaltime', 'Înălțime (cm)', 'number', False, extra='min="100" max="230"')}
              {fld('an_nastere', 'Anul nașterii', 'number', False, extra=f'min="{cur_year-100}" max="{cur_year-18}"')}
              <div class="mz-field"><label for="f-sex">Sex</label><select id="f-sex" name="sex"><option value="">–</option><option>Feminin</option><option>Masculin</option></select></div>
            </div>
            <label class="mz-check"><input type="checkbox" name="consimtamant_profil"> <span>Sunt de acord ca {E(VANZATOR)} să prelucreze datele din profilul nutrițional în scopul recomandărilor personalizate, conform <a href="/magazin/confidentialitate/" target="_blank">politicii de confidențialitate</a>.</span></label>
          </details>
        </fieldset>
        <label class="mz-check" data-save-account style="display:none"><input type="checkbox" name="salveaza_in_cont" checked> <span>Salvează adresa și datele de facturare în contul meu, pentru comenzile viitoare.</span></label>
        <label class="mz-check"><input type="checkbox" name="accept_termeni" required> <span>Am citit și accept <a href="/magazin/termeni-si-conditii/" target="_blank">Termenii și condițiile</a> și <a href="/magazin/confidentialitate/" target="_blank">Politica de confidențialitate</a>. Am luat la cunoștință <a href="/magazin/retur/" target="_blank">dreptul de retragere</a>. <span class=req>*</span></span></label>
        <div class="mz-error" role="alert"></div>
        <button type="submit" class="mz-btn gold" style="width:100%;margin-top:1rem">Continuă spre plată</button>
        <p class="mz-secure">🔒 Plata se face pe pagina securizată Stripe. Comanda implică obligația de plată.</p>
      </form>
    </section>
</div>
</div>
'''
