# Pagini coș, confirmare și pagini legale – rulat de magazin_build.py (folosește funcțiile de acolo)
from magazin_lr import TRANSPORT_LR
FIRMA = dict(
    denumire=VANZATOR, cui='38416337', regcom='F32/667/2017',
    adresa='Str. Podului 44G/1, Sibiu, jud. Sibiu',
    email='nutrisib.club@gmail.com', telefon=None,
)
def camp(v, ce): return E(v) if v else f'<mark>[de completat: {ce}]</mark>'
ID_FIRMA = (f"<strong>{E(FIRMA['denumire'])}</strong>, cu sediul în {camp(FIRMA['adresa'], 'adresa sediului')}, "
            f"CUI {FIRMA['cui']}, nr. de înregistrare în Registrul Comerțului {FIRMA['regcom']}, "
            f"e-mail <a href=\"mailto:{FIRMA['email']}\">{FIRMA['email']}</a>{', telefon ' + E(FIRMA['telefon']) if FIRMA['telefon'] else ''}")

# ======================= coș + checkout =======================
body = cos_body()
build_page(os.path.join(OUT, 'cos', 'index.html'), 'Coșul de cumpărături | Magazin NutriSib', 'Coșul de cumpărături NutriSib.', '/magazin/cos/', body, robots='noindex, follow', scripts=SB_SCRIPTS)

body = '''<section class="content-card" data-mz-success style="text-align:center;max-width:760px;margin-left:auto;margin-right:auto">
  <span class="mz-eyebrow">Comandă înregistrată</span>
  <h1 class="mz-p-title">Mulțumim pentru comandă!</h1>
  <p>Plata a fost procesată. În câteva minute primești pe e-mail confirmarea comenzii și factura.</p>
  <p>Dacă ai întrebări despre comandă, răspunde direct la e-mailul de confirmare.</p>
  <p style="margin-top:1.5rem"><a class="mz-btn" style="display:inline-flex;flex:none" href="/magazin/">Înapoi în magazin</a></p>
</section>
'''
build_page(os.path.join(OUT, 'comanda-confirmata', 'index.html'), 'Comandă confirmată | Magazin NutriSib', 'Confirmarea comenzii NutriSib.', '/magazin/comanda-confirmata/', body, robots='noindex, nofollow')

body = f'''<div class="mz-crumbs-wrap">{crumbs([('Magazin', '/magazin/'), ('Contul meu', None)])[0]}</div>
<div data-mz-account>
<section class="content-card" data-out style="display:none;max-width:620px;margin-left:auto;margin-right:auto">
  <h1 class="mz-p-title">Contul meu</h1>
  <p>Introdu adresa de e-mail și îți trimitem un link de conectare – fără parolă. Contul se creează automat la prima conectare.</p>
  <div data-login data-redirect="/magazin/cont/">
    <form class="mz-form"><div class="mz-field"><label for="l-email">E-mail</label><input id="l-email" name="email" type="email" required autocomplete="email"></div>
    <button class="mz-btn" type="submit" style="width:100%;margin-top:.75rem">Trimite-mi linkul de conectare</button></form>
    <p class="mz-login-msg" role="status" style="display:none"></p>
  </div>
  <p class="mz-buy-note">Contul este opțional: poți comanda și fără el. Dacă ai comandat deja fără cont, comenzile făcute cu aceeași adresă de e-mail apar automat în istoric.</p>
</section>
<div data-in style="display:none">
  <section class="content-card">
    <div class="mz-cat-head"><h1 class="mz-cat-title">Contul meu</h1><span class="mz-cat-count"><span data-email></span> · <button type="button" class="mz-remove" data-logout>Deconectare</button></span></div>
    <h2 class="mz-section-title">Comenzile mele</h2>
    <div data-orders><p>Se încarcă…</p></div>
  </section>
  <section class="content-card">
    <form class="mz-form" data-client-form>
      <fieldset><legend>Date de livrare salvate</legend><div class="mz-fields">
        {fld('nume', 'Nume', req=False)}{fld('prenume', 'Prenume', req=False)}{fld('telefon', 'Telefon', 'tel', req=False)}
        <div class="mz-field"><label for="f-judet">Județ</label><select id="f-judet" name="judet">{opt_jud}</select></div>
        {fld('localitate', 'Localitate', req=False)}{fld('cod_postal', 'Cod poștal', req=False)}
        {fld('adresa', 'Adresă', req=False, full=True)}
      </div></fieldset>
      <fieldset><legend>Date de facturare pe firmă (opțional)</legend><div class="mz-fields">
        <div class="mz-field full"><label for="c-fd">Denumirea firmei</label><input id="c-fd" name="firma_denumire"></div>
        <div class="mz-field"><label for="c-fc">CUI / CIF</label><input id="c-fc" name="firma_cui"></div>
        <div class="mz-field"><label for="c-fr">Nr. Registrul Comerțului</label><input id="c-fr" name="firma_regcom"></div>
        <div class="mz-field full"><label for="c-fa">Adresa sediului social</label><input id="c-fa" name="firma_adresa"></div>
      </div></fieldset>
      <button class="mz-btn" type="submit">Salvează datele</button><p class="mz-form-msg" role="status"></p>
    </form>
  </section>
  <section class="content-card">
    <form class="mz-form" data-profil-form>
      <fieldset><legend>Profilul nutrițional (opțional)</legend>
      <p class="mz-buy-note">Datele de mai jos pot fi considerate date privind sănătatea. Le păstrăm doar cu acordul tău explicit și le poți șterge oricând.</p>
      <div class="mz-fields">
        {fld('greutate_actuala', 'Greutate actuală (kg)', 'number', False, extra='min="30" max="300" step="0.1"')}
        {fld('greutate_dorita', 'Greutate dorită (kg)', 'number', False, extra='min="30" max="300" step="0.1"')}
        {fld('inaltime', 'Înălțime (cm)', 'number', False, extra='min="100" max="230"')}
        {fld('an_nastere', 'Anul nașterii', 'number', False, extra=f'min="{cur_year-100}" max="{cur_year-18}"')}
        <div class="mz-field"><label for="p-sex">Sex</label><select id="p-sex" name="sex"><option value="">–</option><option>Feminin</option><option>Masculin</option></select></div>
      </div>
      <label class="mz-check"><input type="checkbox" name="consimtamant"> <span>Sunt de acord ca {E(VANZATOR)} să prelucreze aceste date în scopul recomandărilor personalizate, conform <a href="/magazin/confidentialitate/">politicii de confidențialitate</a>.</span></label>
      </fieldset>
      <div style="display:flex;gap:.75rem;flex-wrap:wrap"><button class="mz-btn" type="submit" style="flex:none">Salvează profilul</button><button class="mz-btn ghost" type="button" data-profil-delete style="flex:none">Șterge profilul</button></div>
      <p class="mz-form-msg" role="status"></p>
    </form>
  </section>
  <section class="content-card"><p class="mz-buy-note" style="margin:0">Vrei să îți ștergi contul și toate datele asociate? Scrie-ne la <a href="mailto:{FIRMA['email']}?subject=Stergere%20cont%20magazin">{FIRMA['email']}</a> de pe adresa contului. Facturile emise se păstrează conform legislației contabile.</p></section>
</div>
</div>
'''
build_page(os.path.join(OUT, 'cont', 'index.html'), 'Contul meu | Magazin NutriSib', 'Contul de client NutriSib: istoricul comenzilor și datele de livrare.', '/magazin/cont/', body, robots='noindex, follow', scripts=SB_SCRIPTS)

def legal(slug, title, desc, inner):
    nav = ' '.join(f'<a href="/magazin/{s}/">{t}</a>' for s, t in [('termeni-si-conditii', 'Termeni și condiții'), ('livrare', 'Livrare'), ('retur', 'Retur'), ('confidentialitate', 'Confidențialitate')])
    b = f'''<div class="mz-crumbs-wrap">{crumbs([('Magazin', '/magazin/'), (title, None)])[0]}</div>
<section class="content-card"><div class="mz-legal">
<nav class="mz-legal-nav" aria-label="Pagini legale">{nav}</nav>
<h1 class="mz-p-title">{E(title)}</h1>
<p><em>Ultima actualizare: {datetime.date.today().strftime('%d.%m.%Y')}</em></p>
{inner}
</div></section>
'''
    build_page(os.path.join(OUT, slug, 'index.html'), f'{title} | Magazin NutriSib', desc, f'/magazin/{slug}/', b)

legal('termeni-si-conditii', 'Termeni și condiții', 'Termenii și condițiile de vânzare ale magazinului online NutriSib.', f'''
<h2>1. Cine vinde</h2>
<p>Magazinul online de la adresa nutrisib.club/magazin este operat de {ID_FIRMA} („Vânzătorul”). Vânzătorul este distribuitor independent Herbalife și revinde produse originale Herbalife, achiziționate de la Herbalife România. Pentru produsele LR, Vânzătorul este partener independent LR și revinde produse originale LR Health &amp; Beauty.</p>
<h2>2. Produse și informații</h2>
<p>Descrierile, ingredientele, informațiile nutriționale și imaginile produselor provin de la producător. Imaginile au caracter informativ; alimentele prezentate în imagini sunt ilustrative și nu fac parte din conținutul produsului. Suplimentele alimentare nu înlocuiesc o dietă variată și echilibrată și un stil de viață sănătos. Dacă ai o afecțiune, urmezi un tratament, ești însărcinată sau alăptezi, cere părerea medicului înainte de a consuma suplimente.</p>
<h2>3. Prețuri</h2>
<p>Prețurile sunt exprimate în lei (RON) și sunt prețuri finale pentru produs. Vânzătorul nu este înregistrat în scopuri de TVA, astfel că facturile se emit fără TVA. Costul transportului se afișează separat în coș, înainte de plată: transportul este gratuit pentru comenzile Herbalife care însumează minimum {PRAG_VP} VP (valoarea VP a fiecărui produs este afișată pe pagina lui) și costă {TRANSPORT} lei pentru comenzile sub acest prag. Produsele LR și cele Herbalife se comandă separat, din coșul fiecărui magazin. Pentru comenzile LR, transportul costă {TRANSPORT_LR} lei, indiferent de valoarea comenzii. Prețul valabil este cel afișat în momentul plasării comenzii.</p>
<h2>4. Comanda și încheierea contractului</h2>
<p>Comanda se plasează din coș, prin completarea datelor de livrare și facturare, acceptarea acestor termeni și plata online. Contractul se consideră încheiat în momentul în care primești pe e-mail confirmarea comenzii. Dacă un produs comandat nu mai este disponibil, te informăm și îți rambursăm integral suma aferentă în cel mult 14 zile.</p>
<h2>5. Plata</h2>
<p>Plata se face online, cu cardul, prin procesatorul de plăți Stripe. Datele cardului sunt introduse direct pe pagina securizată Stripe și nu sunt transmise și nici stocate de Vânzător. Factura se emite electronic și se trimite pe adresa de e-mail indicată în comandă.</p>
<h2>6. Livrarea</h2>
<p>Condițiile de livrare sunt descrise pe pagina <a href="/magazin/livrare/">Livrare</a>.</p>
<h2>7. Dreptul de retragere (retur în 14 zile)</h2>
<p>Ai dreptul să te retragi din contract în 14 zile de la primirea produselor, fără a invoca un motiv, în condițiile și cu excepțiile descrise pe pagina <a href="/magazin/retur/">Retur</a>.</p>
<h2>8. Garanția de conformitate</h2>
<p>Produsele beneficiază de garanția legală de conformitate, potrivit OUG nr. 140/2021. Dacă primești un produs deteriorat, greșit sau neconform, scrie-ne la <a href="mailto:{FIRMA['email']}">{FIRMA['email']}</a>, cu fotografii, iar noi îl înlocuim sau îți rambursăm contravaloarea, inclusiv costurile de transport.</p>
<h2>9. Date personale</h2>
<p>Prelucrarea datelor personale este descrisă în <a href="/magazin/confidentialitate/">Politica de confidențialitate</a>.</p>
<h2>10. Reclamații și soluționarea litigiilor</h2>
<p>Reclamațiile se trimit la <a href="mailto:{FIRMA['email']}">{FIRMA['email']}</a> și primesc răspuns în cel mult 30 de zile. Dacă nu ajungem la o soluție amiabilă, te poți adresa Autorității Naționale pentru Protecția Consumatorilor (ANPC), inclusiv prin procedura de <a href="https://anpc.ro/ce-este-sal/" target="_blank" rel="nofollow noopener">Soluționare Alternativă a Litigiilor (SAL)</a>, sau instanțelor competente din România. Platforma europeană de soluționare online a litigiilor (SOL/ODR) nu mai funcționează din 20 iulie 2025.</p>
<h2>11. Legea aplicabilă</h2>
<p>Acești termeni sunt guvernați de legea română, inclusiv OUG nr. 34/2014 privind drepturile consumatorilor în cadrul contractelor încheiate cu profesioniștii.</p>
''')

legal('livrare', 'Livrare', 'Costuri și condiții de livrare pentru comenzile din magazinul NutriSib.', f'''
<div class="mz-box"><p style="margin:0"><strong>Transport gratuit</strong> pentru comenzile Herbalife de minimum <strong>{PRAG_VP} VP</strong>. Sub acest prag, transportul costă <strong>{TRANSPORT} lei</strong>.</p><p style="margin:.5rem 0 0">Pentru comenzile <strong>LR</strong>, transportul costă <strong>{TRANSPORT_LR} lei</strong>, indiferent de valoare. Produsele LR și cele Herbalife se comandă separat, fiecare comandă cu transportul ei.</p></div>
<h2>Comenzi LR și Herbalife</h2>
<p>Produsele LR și cele Herbalife au coșuri separate și se comandă separat: produsele LR din <a href="/magazin/lr/cos/">coșul LR</a>, cele Herbalife din <a href="/magazin/cos/">coșul Herbalife</a>. Fiecare comandă are propriul cost de transport, propria factură și se livrează în colet separat.</p>
<h2>Ce este VP</h2>
<p>VP (valoarea în volum) este o valoare atribuită de Herbalife fiecărui produs. O găsești pe pagina fiecărui produs și în coș, unde VP-ul produselor se adună automat. Când totalul ajunge la {PRAG_VP} VP, transportul devine gratuit.</p>
<h2>Unde livrăm</h2>
<p>Livrăm prin curier, la adresa indicată în comandă, oriunde în România.</p>
<h2>Când ajunge comanda</h2>
<p>Termenul estimat de livrare îți este comunicat în e-mailul de confirmare a comenzii. Livrarea are loc în cel mult 30 de zile de la confirmarea comenzii, potrivit legii. Dacă intervine o întârziere, te anunțăm și poți alege să anulezi comanda, cu rambursarea integrală a sumei plătite.</p>
<h2>La primirea coletului</h2>
<p>Verifică integritatea coletului în prezența curierului. Dacă ambalajul este deteriorat sau produsele sunt neconforme, scrie-ne la <a href="mailto:{FIRMA['email']}">{FIRMA['email']}</a> cu fotografii, iar noi rezolvăm situația conform garanției legale de conformitate.</p>
''')

legal('retur', 'Retur în 14 zile', 'Dreptul de retragere și procedura de retur pentru comenzile din magazinul NutriSib.', f'''
<h2>Dreptul de retragere</h2>
<p>Ai dreptul să te retragi din contract, fără a invoca vreun motiv, în termen de <strong>14 zile</strong> de la ziua în care tu (sau o persoană indicată de tine, alta decât curierul) intri în posesia fizică a produselor (OUG nr. 34/2014).</p>
<h2>Excepții</h2>
<p>Dreptul de retragere nu se aplică pentru <strong>produsele sigilate care nu pot fi returnate din motive de protecție a sănătății sau de igienă și care au fost desigilate</strong> după livrare (art. 16 lit. e din OUG nr. 34/2014). Shake-urile, suplimentele alimentare, băuturile, gustările și produsele cosmetice se încadrează în această categorie odată ce sigiliul a fost rupt. Produsele nedesigilate, în ambalajul original intact, pot fi returnate.</p>
<h2>Cum exerciți dreptul de retragere</h2>
<ol>
<li>Ne anunți decizia în termenul de 14 zile, printr-o declarație neechivocă trimisă la <a href="mailto:{FIRMA['email']}">{FIRMA['email']}</a>. Poți folosi modelul de formular de mai jos, dar nu este obligatoriu.</li>
<li>Trimiți produsele în cel mult 14 zile de la data la care ne-ai comunicat decizia, la adresa: {camp(FIRMA['adresa'], 'adresa pentru retururi')}.</li>
<li>Costul direct al returnării produselor este suportat de tine.</li>
</ol>
<h2>Rambursarea</h2>
<p>Îți rambursăm toate sumele primite, inclusiv costul livrării inițiale (cu excepția costurilor suplimentare dacă ai ales altă modalitate de livrare decât cea standard), în cel mult 14 zile de la data la care am fost informați despre decizia de retragere. Rambursarea se face prin aceeași metodă de plată folosită la comandă. Putem amâna rambursarea până la primirea produselor sau până la momentul în care ne trimiți dovada expedierii lor, dacă acesta este mai devreme. Răspunzi doar pentru diminuarea valorii produselor rezultată din manipularea lor în alt mod decât cel necesar pentru a le verifica natura, caracteristicile și funcționarea.</p>
<h2>Model de formular de retragere</h2>
<div class="mz-box">
<p>(Completați și returnați acest formular doar dacă doriți să vă retrageți din contract.)</p>
<p>Către {E(FIRMA['denumire'])}, {camp(FIRMA['adresa'], 'adresa')}, e-mail {FIRMA['email']}:</p>
<p>Vă informez prin prezenta cu privire la retragerea mea din contractul referitor la vânzarea următoarelor produse: ……………………………</p>
<p>Comandate la data: …………… / primite la data: ……………<br>
Numele consumatorului: ……………………………<br>
Adresa consumatorului: ……………………………<br>
Semnătura consumatorului (doar dacă formularul este trimis pe hârtie): ……………<br>
Data: ……………</p>
</div>
<h2>Produse deteriorate sau neconforme</h2>
<p>Dacă ai primit un produs deteriorat, greșit sau neconform, acesta nu este un retur obișnuit: scrie-ne cu fotografii, iar costurile de înlocuire sau rambursare, inclusiv transportul, sunt suportate de noi (garanția legală de conformitate, OUG nr. 140/2021).</p>
''')

legal('confidentialitate', 'Politica de confidențialitate', 'Cum prelucrează magazinul NutriSib datele personale ale clienților.', f'''
<h2>Operatorul datelor</h2>
<p>Operatorul datelor tale personale este {ID_FIRMA}. Pentru orice întrebare sau cerere privind datele tale, scrie-ne la <a href="mailto:{FIRMA['email']}">{FIRMA['email']}</a>.</p>
<h2>Ce date prelucrăm și de ce</h2>
<ul>
<li><strong>Date de comandă și livrare</strong> (nume, prenume, e-mail, telefon, adresă, produse comandate): pentru încheierea și executarea contractului de vânzare – art. 6 alin. (1) lit. b) GDPR.</li>
<li><strong>Date de facturare</strong> (inclusiv datele firmei, dacă alegi factură pe firmă): pentru emiterea facturii și îndeplinirea obligațiilor fiscale și contabile – art. 6 alin. (1) lit. c) GDPR.</li>
<li><strong>CNP (opțional)</strong>: numai dacă alegi să îl completezi, pentru a fi trecut pe factură; temeiul este obligația legală de facturare – art. 6 alin. (1) lit. c) GDPR, cu garanțiile prevăzute de Legea nr. 190/2018. Dacă nu îl completezi, factura se emite fără CNP. CNP-ul nu este salvat în contul de client.</li>
<li><strong>Contul de client (opțional)</strong>: adresa de e-mail, datele de livrare și facturare salvate și istoricul comenzilor, pentru a-ți oferi acces la comenzile tale și precompletarea formularului – art. 6 alin. (1) lit. b) GDPR. Comenzile plasate fără cont cu aceeași adresă de e-mail apar în istoricul contului.</li>
<li><strong>Date de plată</strong>: plata cu cardul este procesată de Stripe. Noi nu primim și nu stocăm datele cardului; primim doar confirmarea plății.</li>
<li><strong>Profilul nutrițional opțional</strong> (greutate actuală și dorită, înălțime, anul nașterii, sex): numai dacă îl completezi și îți dai acordul explicit, în scopul recomandărilor nutriționale personalizate. Aceste date pot fi considerate date privind sănătatea; temeiul este consimțământul explicit – art. 9 alin. (2) lit. a) GDPR. Comanda nu depinde de aceste date, iar consimțământul poate fi retras oricând, fără a afecta legalitatea prelucrării anterioare.</li>
</ul>
<h2>Cui transmitem datele</h2>
<p>Datele sunt transmise doar furnizorilor care ne ajută să executăm comanda, în calitate de persoane împuternicite: procesatorul de plăți (Stripe), furnizorul de găzduire a site-ului (Netlify), furnizorul bazei de date pentru conturile de client (Supabase), serviciul de trimitere a e-mailurilor (Resend), aplicația de facturare (SmartBill) și firma de curierat. Unii dintre acești furnizori pot prelucra date în afara Spațiului Economic European, pe baza garanțiilor prevăzute de GDPR (de exemplu, clauze contractuale standard). Profilul nutrițional nu este transmis curierului și nu apare pe factură.</p>
<h2>Cât timp păstrăm datele</h2>
<ul>
<li>datele de comandă și facturare: pe durata prevăzută de legislația fiscală și contabilă;</li>
<li>profilul nutrițional: până la retragerea consimțământului, dar nu mai mult de 3 ani de la ultima comandă.</li>
<li>contul de client: până la solicitarea ștergerii contului.</li>
</ul>
<h2>Drepturile tale</h2>
<p>Ai dreptul de acces, rectificare, ștergere, restricționare a prelucrării, portabilitate și opoziție, precum și dreptul de a retrage consimțământul. Pentru exercitarea lor, scrie-ne la <a href="mailto:{FIRMA['email']}">{FIRMA['email']}</a>. Ai, de asemenea, dreptul să depui o plângere la Autoritatea Națională de Supraveghere a Prelucrării Datelor cu Caracter Personal (<a href="https://www.dataprotection.ro" target="_blank" rel="noopener">www.dataprotection.ro</a>).</p>
<h2>Cookie-uri</h2>
<p>Coșul de cumpărături este salvat local, în browserul tău (localStorage), doar pentru a păstra produsele alese; nu este transmis nicăieri până la plasarea comenzii. Pentru celelalte cookie-uri folosite pe site, vezi bannerul de cookie-uri.</p>
''')

# ======================= Oferta NutriSib (centralizator de prețuri) =======================
DATA_OFERTA = datetime.date.today().strftime('%d.%m.%Y')
def _vp(v): return f'{v:.2f}'.replace('.', ',')
rows_pk = ''.join(f'''<tr><td><a href="{SITE}{p['url']}">{E(p['nume'])}</a><div class="mz-of-sub">{E(p['comp_txt'])}</div></td>
<td class="num"><s>{lei(p['suma'])}</s></td><td class="num"><strong>{lei(p['pret'])}</strong></td><td class="num">−{lei(p['economie'])}<br><small>{str(p['procent']).replace('.', ',')}%</small></td><td class="num">{_vp(p['vp'])}</td></tr>''' for p in PACHETE)
sec_prod = ''
for c in CATEGORII:
    rows = ''
    for sub in c['sub']:
        skus = [s_ for s_ in sub['sku'] if s_ in BYSKU]
        if not skus: continue
        if sub['nume']: rows += f'<tr class="mz-of-subhead"><td colspan="5">{E(sub["nume"])}</td></tr>'
        for s_ in skus:
            p = BYSKU[s_]
            rows += f'<tr><td class="cod">{p["sku"]}</td><td><a href="{SITE}{p["url"]}">{E(p["denumire"])}</a></td><td>{E(p["varianta"])}</td><td class="num">{_vp(p["vp"])}</td><td class="num"><strong>{lei(p["pret"])}</strong></td></tr>'
    sec_prod += f'''<h2 class="mz-of-cat">{E(c['nume'])}</h2>
<table class="mz-of"><thead><tr><th>Cod</th><th>Produs</th><th>Variantă</th><th class="num">VP</th><th class="num">Preț</th></tr></thead><tbody>{rows}</tbody></table>'''
body = f'''<div class="mz-crumbs-wrap">{crumbs([('Magazin', '/magazin/'), ('Oferta NutriSib', None)])[0]}</div>
<section class="content-card mz-oferta">
  <div class="mz-of-head">
    <div><span class="mz-eyebrow" style="color:#8a6d0f">Oferta NutriSib · Herbalife</span>
    <h1 class="mz-p-title">Lista de prețuri</h1>
    <p class="mz-buy-note" style="margin:0">Valabilă de la {DATA_OFERTA}. Prețuri finale, în lei. Transport gratuit pentru comenzile de minimum {PRAG_VP} VP; sub prag, {TRANSPORT} lei. {E(VANZATOR)}, CUI 38416337 – neplătitor de TVA.</p></div>
    <img src="/magazin/assets/herbalife-logo.webp" alt="Herbalife" class="mz-of-logo">
  </div>
  <div class="mz-of-actions no-print">
    <a class="mz-btn" style="flex:none" href="/magazin/oferta/oferta-nutrisib-herbalife.pdf" download>⬇ Descarcă PDF</a>
    <button type="button" class="mz-btn ghost" style="flex:none" onclick="window.print()">Tipărește</button>
  </div>
  <p class="mz-buy-note">Fiecare denumire este un link către pagina produsului sau a pachetului, unde poți comanda.</p>
  <h2 class="mz-of-cat">Pachete la ofertă</h2>
  <table class="mz-of mz-of-pk"><thead><tr><th>Pachet</th><th class="num">Preț separat</th><th class="num">Preț pachet</th><th class="num">Economie</th><th class="num">VP</th></tr></thead><tbody>{rows_pk}</tbody></table>
  <p class="mz-buy-note">Pentru pachetele cu variante (aromă, tip de Protein Drink Mix), prețul afișat corespunde variantelor implicite; prețul exact apare pe pagina pachetului după alegerea variantelor.</p>
  {sec_prod}
</section>
'''
build_page(os.path.join(OUT, 'oferta', 'index.html'), 'Oferta NutriSib – lista de prețuri Herbalife', f'Lista completă de prețuri NutriSib pentru produsele și pachetele Herbalife, valabilă de la {DATA_OFERTA}. Descarcă oferta în format PDF.', '/magazin/oferta/', body)
