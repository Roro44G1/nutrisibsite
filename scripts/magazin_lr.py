#!/usr/bin/env python3
"""Generează magazinul LR (/magazin/lr/) din:
   - produse/lr/lr-sanatate.json (extras de pe shop.lrworld.com, zona Sănătate) + produse/lr/img/<cod>.jpg
     (sursă locală, neurcată în Git – vezi .gitignore)
Folosește șabloanele comune din magazin_build.py (partea de până la „date produse”), fără să regenereze Herbalife.
Adaugă produsele LR în magazin/catalog.json (magazin = "lr"), fără să atingă intrările Herbalife.
Prețul afișat = prețul de client LR din fișier. Transport LR: fix, pe comandă. Comenzile LR se plasează separat de cele Herbalife.
Rulare din rădăcina repo-ului:  python3 scripts/magazin_lr.py
"""
import os, re, json, html, datetime
from PIL import Image

_HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(_HERE, 'magazin_build.py'), encoding='utf-8').read()
exec(compile(_src[:_src.index('# ======================= date produse')], 'magazin_build.py (șabloane comune)', 'exec'))

SRC_LR = os.path.join(ROOT, 'produse', 'lr')
DATA = os.path.join(SRC_LR, 'lr-sanatate.json')
LRD = os.path.join(OUT, 'lr')
TRANSPORT_LR = 25
BRAND = 'LR Health & Beauty'
STATUT = 'partener independent LR'

# Denumirile grupelor LR, așa cum apar pe site (fișierul le are cu majuscule)
GRUPE = {'SPECIALIȘTI ÎN SĂNĂTATE': 'Specialiști în sănătate', 'LR HEALTH MISSION': 'LR Health Mission', 'LR BODY MISSION': 'LR Body Mission'}
TAB_NUME = {'Denumire': 'Descriere'}
# Corecturi de date față de fișierul LR, fiecare cu motivul ei
CORECTII = {
    # Setul dublu are 2 × 1.000 ml (ca celelalte seturi duble la același preț); fișierul LR indică 1.000 ml și 309,91 RON / 1 l.
    '80802-782': {'marime': '2.000 ml'},
}
# Produse din fișier care nu intră în magazin
EXCLUSE = {
    '81292-26': 'set de prezentare cu 10 cutii la alegere; aromele nu se pot alege din coș',
}

def slugify(s):
    s = s.lower().translate(str.maketrans('ăâîșşțţ', 'aaisstt'))
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')
def ro_num(s): return float(s.replace('.', '').replace(',', '.'))
def lei2(x):
    if abs(x - round(x)) < 1e-9: return f'{int(round(x)):,}'.replace(',', '.') + ' lei'
    return f'{x:,.2f}'.replace(',', '§').replace('.', ',').replace('§', '.') + ' lei'
def nume_curat(s):
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'(\S)- ', r'\1 – ', s); return s.replace(' - ', ' – ')

def md_curat(t, titlu_tab=None):
    t = re.sub(r'<img[^>]*>', '', t)
    t = re.sub(r'^\s*mai mult\s*$', '', t, flags=re.M)
    t = re.sub(r'^###\s+.*\n', '', t.lstrip(), count=1) if t.lstrip().startswith('### ') else t   # titlul tab-ului / al produsului, deja afișat
    t = re.sub(r'\^(\d+)', r'<sup>\1</sup>', t)
    return re.sub(r'\n{3,}', '\n\n', t).strip()

def puncte(short_md):
    """Textul scurt LR („• a • b • c …”) ca listă markdown."""
    t = md_curat(short_md)
    if '•' in t:
        t = re.sub(r'\s*•\s*', '\n- ', t).strip()
        # nota de la final („*Acest produs include …”) iese din ultimul punct și devine paragraf
        t = re.sub(r'\s+(\\\*[^\n]+)$', r'\n\n\1', t)
    return t

def unitate(marime):
    m = re.match(r'^([\d.]+)\s*(ml|g)$', marime or '')
    if not m: return None
    q = ro_num(m.group(1)); return (q / 1000, '1 l' if m.group(2) == 'ml' else '1 kg')

def img_lr(cod, w):
    """produse/lr/img/<cod>.jpg (fundal alb, portret) -> magazin/lr/img/<cod>-<w>.webp, pătrat, centrat pe alb."""
    src = os.path.join(SRC_LR, 'img', f'{cod}.jpg'); rel = f'img/{cod}-{w}.webp'; dst = os.path.join(LRD, rel)
    if not os.path.exists(src): return None
    if not os.path.exists(dst):
        im = Image.open(src).convert('RGB'); side = max(im.size)
        sq = Image.new('RGB', (side, side), (255, 255, 255)); sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
        sq = sq.resize((w, w), Image.LANCZOS); os.makedirs(os.path.dirname(dst), exist_ok=True)
        sq.save(dst + '.part', 'WEBP', quality=84, method=6); os.replace(dst + '.part', dst)
    return f'/magazin/lr/{rel}'

# ======================= date =======================
D = json.load(open(DATA, encoding='utf-8'))
CATEG = []   # [{slug, nume, sub: [{nume, sku:[...]}]}]
for c in D['categorii']:
    g = GRUPE.get(c['grup'], c['grup'].title()); slug = slugify(g)
    grp = next((x for x in CATEG if x['slug'] == slug), None)
    if not grp: grp = {'slug': slug, 'nume': g, 'sub': []}; CATEG.append(grp)
    if c['produse'] and c['nume'].upper() != c['grup'].upper(): grp['sub'].append({'nume': c['nume'], 'sku': c['produse']})

produse = []
for cod, r in D['produse'].items():
    if cod in EXCLUSE: continue
    # prețul curent LR = cel dinaintea „(Net: …)”; la seturile în promoție LR, primul preț din casetă e cel vechi, tăiat
    pm = re.search(r'([\d.]+,\d\d) RON \(Net:', r['price_box'] or '')
    if not pm: raise SystemExit(f'{cod}: lipsește prețul')
    marime = re.sub(r'^.*?Cod produs:\s*\S+\s*', '', r['name_box']).strip()
    marime = CORECTII.get(cod, {}).get('marime', marime)
    pret = ro_num(pm.group(1))
    u = unitate(marime); pret_unitar = f'{lei2(round(pret / u[0] + 1e-9, 2))} / {u[1]}' if u else ''
    g0, s0 = r['cats'][0].split(' > ', 1)
    nume = nume_curat(r['h1'])
    secs = [(TAB_NUME.get(t['t'], t['t']), md_curat(t['md'])) for t in r['tabs']]
    secs = [(t, c) for t, c in secs if c]
    slug = f'{slugify(nume)}-{cod}'
    produse.append(dict(cod=cod, sku=f'LR-{cod}', denumire=nume, marime=marime, pret=pret, pret_unitar=pret_unitar,
                        cat=slugify(GRUPE.get(g0, g0)), cat_label=GRUPE.get(g0, g0), subcat=s0, puncte=puncte(r['short_md']), secs=secs,
                        url=f'/magazin/lr/{slug}/', slug=slug, img=img_lr(cod, 900), img_mic=img_lr(cod, 420), sursa=r['href']))
BYCOD = {p['cod']: p for p in produse}
for _g in CATEG:   # categoriile rămase fără produse (după excluderi) nu apar
    for _s in _g['sub']: _s['sku'] = [k for k in _s['sku'] if k in BYCOD]
    _g['sub'] = [_s for _s in _g['sub'] if _s['sku']]

# ======================= catalog.json (se păstrează intrările celorlalte magazine) =======================
cat_path = os.path.join(OUT, 'catalog.json')
cat = json.load(open(cat_path, encoding='utf-8'))
cat['produse'] = [p for p in cat['produse'] if p.get('magazin') != 'lr'] + [
    {'sku': p['sku'], 'denumire': p['denumire'], 'varianta': p['marime'], 'pret': p['pret'], 'vp': 0, 'url': p['url'], 'img_mic': p['img_mic'], 'cat': p['cat'], 'magazin': 'lr'}
    for p in produse]
cat['config']['transport_lr'] = TRANSPORT_LR
json.dump(cat, open(cat_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ======================= pagini produs =======================
DISC = (f'Descrierea, ingredientele și informațiile nutriționale provin de la producător ({BRAND}). Suplimentele alimentare nu înlocuiesc '
        f'o dietă variată și echilibrată și un stil de viață sănătos. Produsele LR sunt vândute de {VANZATOR}, {STATUT}.')
SHIP_LR = (f'<div class="mz-ship-note"><strong>Transport: {TRANSPORT_LR} lei</strong> pe comandă, prin curier, oriunde în România. '
           'Produsele LR se comandă separat de cele Herbalife.</div>')

for p in produse:
    title = f"{p['denumire']}{' – ' + p['marime'] if p['marime'] else ''} | LR | NutriSib"
    desc_src = re.sub(r'<[^>]+>|[*#\\]|^- ', '', p['puncte'] or (p['secs'][0][1] if p['secs'] else ''), flags=re.M)
    desc = re.sub(r'\s+', ' ', desc_src).strip()[:300] or f"{p['denumire']} – produs LR, preț final {lei2(p['pret'])}."
    cr_html, cr_ld = crumbs([('Magazin', '/magazin/'), ('LR', '/magazin/lr/'), (p['cat_label'], f'/magazin/lr/{p["cat"]}/'), (p['denumire'], None)])
    prod_ld = {'@context': 'https://schema.org', '@type': 'Product', 'name': p['denumire'], 'sku': p['sku'], 'mpn': p['cod'],
               'brand': {'@type': 'Brand', 'name': 'LR'}, 'category': p['cat_label'], 'image': [SITE + p['img']], 'description': desc,
               'offers': {'@type': 'Offer', 'url': SITE + p['url'], 'priceCurrency': 'RON', 'price': f"{p['pret']:.2f}",
                          'availability': 'https://schema.org/InStock', 'itemCondition': 'https://schema.org/NewCondition',
                          'seller': {'@type': 'Organization', 'name': 'NutriSib'},
                          'shippingDetails': {'@type': 'OfferShippingDetails', 'shippingDestination': {'@type': 'DefinedRegion', 'addressCountry': 'RO'},
                                              'shippingRate': {'@type': 'MonetaryAmount', 'value': str(TRANSPORT_LR), 'currency': 'RON'}},
                          'hasMerchantReturnPolicy': {'@type': 'MerchantReturnPolicy', 'applicableCountry': 'RO',
                                                      'returnPolicyCategory': 'https://schema.org/MerchantReturnFiniteReturnWindow', 'merchantReturnDays': 14,
                                                      'returnMethod': 'https://schema.org/ReturnByMail', 'returnFees': 'https://schema.org/ReturnFeesCustomerResponsibility'}}}
    specs = ''.join(f'<span>{lab}: <b>{E(v)}</b></span>' for lab, v in [('Mărime', p['marime']), ('Cod LR', p['cod'])] if v)
    tabs = ''.join(f'<button class="mz-tab{" active" if i == 0 else ""}" role="tab" aria-selected="{"true" if i == 0 else "false"}" aria-controls="tab-{i}" id="t-{i}">{E(t)}</button>' for i, (t, _) in enumerate(p['secs']))
    panels = ''.join(f'<div class="mz-panel{" active" if i == 0 else ""}" role="tabpanel" id="tab-{i}" aria-labelledby="t-{i}">{md2html(c)}</div>' for i, (t, c) in enumerate(p['secs']))
    info = (f'<div class="mz-tabs" role="tablist">{tabs}</div>\n  {panels}\n  ' if p['secs'] else '')
    body = f'''<div class="mz-crumbs-wrap">{cr_html}</div>
<section class="content-card mz-lr">
  <div class="mz-product">
    <div>
      <div class="mz-gallery-main"><img src="{p['img']}" alt="{E(p['denumire'])}" width="900" height="900"></div>
    </div>
    <div>
      <div class="mz-p-cat">LR · {E(p['subcat'])}</div>
      <h1 class="mz-p-title">{E(p['denumire'])}</h1>
      {f'<div class="mz-p-points">{md2html(p["puncte"])}</div>' if p['puncte'] else ''}
      <div class="mz-p-specs">{specs}</div>
      <div class="mz-buybox" data-mz-buy="{p['sku']}">
        <div class="mz-price">{lei2(p['pret'])}</div>
        {f'<div class="mz-unit-price">{p["pret_unitar"]}</div>' if p['pret_unitar'] else ''}
        <div class="mz-buy-row">
          <div class="mz-qty"><button type="button" data-step="-1" aria-label="Scade cantitatea">−</button><input type="number" min="1" max="99" value="1" aria-label="Cantitate"><button type="button" data-step="1" aria-label="Crește cantitatea">+</button></div>
          <button type="button" class="mz-btn" data-add>Adaugă în coș</button>
        </div>
        <div class="mz-added">Produsul a fost adăugat. <a href="/magazin/cos/">Vezi coșul →</a></div>
        <p class="mz-buy-note">Transport: {TRANSPORT_LR} lei pe comandă, oriunde în România. Produsele LR se comandă separat de cele Herbalife. <a href="/magazin/livrare/">Detalii livrare</a></p>
      </div>
      <div class="mz-advice">Nu știi dacă produsul ți se potrivește? Alegerea suplimentelor are sens după o evaluare a stilului tău de viață și a obiectivelor. <a href="/evaluare.html">Începe evaluarea NutriSib →</a></div>
    </div>
  </div>
</section>
<section class="content-card mz-lr">
  {info}<p class="mz-disclaimer">{E(DISC)}</p>
</section>
'''
    build_page(os.path.join(LRD, p['slug'], 'index.html'), title, desc, p['url'], body, p['img'], cr_ld + jsonld(prod_ld))

# ======================= catalog LR (pe grupele și categoriile LR) =======================
def card(p):
    text = ' '.join([p['denumire'], p['cat_label'], p['subcat'], p['marime'], p['cod']])
    return f'''<a class="mz-card" href="{p['url']}" data-text="{E(text)}">
  <div class="mz-card-img"><img src="{p['img_mic']}" alt="{E(p['denumire'])}" loading="lazy" width="420" height="420"></div>
  <div class="mz-card-body">
    <span class="mz-card-cat">{E(p['subcat'])}</span>
    <h3 class="mz-card-title">{E(p['denumire'])}</h3>
    <span class="mz-card-meta">{E(p['marime'])}</span>
    <div class="mz-card-foot"><span class="mz-price">{lei2(p['pret'])}</span><span class="mz-card-more">Detalii →</span></div>
  </div>
</a>'''

def sectiune(c, h='h2'):
    blocks = []
    for sub in c['sub']:
        ps = [BYCOD[k] for k in sub['sku'] if k in BYCOD]
        if ps: blocks.append(f'<div class="mz-subsec"><h3 class="mz-sub-title">{E(sub["nume"])}</h3><div class="mz-grid">{"".join(card(p) for p in ps)}</div></div>')
    n = len({k for sub in c['sub'] for k in sub['sku'] if k in BYCOD})
    return f'''<section class="content-card mz-catsec mz-lr" id="{c['slug']}">
  <div class="mz-cat-head"><{h} class="mz-cat-title"><a href="/magazin/lr/{c['slug']}/">{E(c['nume'])}</a></{h}><span class="mz-cat-count">{n} {'produs' if n == 1 else 'produse'}</span></div>
  {''.join(blocks)}
</section>'''

def nav(activ=None):
    items = [('/magazin/lr/', 'Toate', activ is None)] + [(f'/magazin/lr/{c["slug"]}/', c['nume'], activ == c['slug']) for c in CATEG]
    return '<nav class="mz-chips mz-catnav" aria-label="Categorii LR">' + ''.join(
        f'<a class="mz-chip{" active" if a else ""}" href="{u}"{CUR if a else ""}>{E(t)}</a>' for u, t, a in items) + '</nav>'

cr_html, cr_ld = crumbs([('Magazin', '/magazin/'), ('LR', None)])
item_ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Produse LR – NutriSib', 'numberOfItems': len(produse),
           'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': SITE + p['url'], 'name': p['denumire']} for i, p in enumerate(produse)]}
body = f'''<div class="mz-crumbs-wrap">{cr_html}</div>
<section class="hero-card mz-hero">
  <div class="hero-content">
    <span class="mz-eyebrow">Magazin NutriSib · LR</span>
    <h1 class="hero-title">LR Health &amp; Beauty</h1>
    <p class="mz-lead">Gama LR pentru sănătate: geluri de băut Aloe Vera, suplimente alimentare LR Lifetakt și mesele LR Figuactive. {len(produse)} produse, cu prețuri finale, fără costuri ascunse.</p>
  </div>
</section>
<section class="content-card mz-catalog-top">
  {SHIP_LR}
  <div class="mz-toolbar" style="margin-top:1.25rem">
    {nav()}
    <input class="mz-search" type="search" placeholder="Caută produs sau cod LR…" aria-label="Caută în catalogul LR">
  </div>
</section>
<div data-mz-grid>
{chr(10).join(sectiune(c) for c in CATEG)}
</div>
<p class="mz-empty content-card">Niciun produs nu corespunde căutării.</p>
'''
build_page(os.path.join(LRD, 'index.html'), 'Produse LR – geluri Aloe Vera, LR Lifetakt, LR Figuactive | Magazin NutriSib',
           f'Produsele LR din gama Sănătate: geluri de băut Aloe Vera, suplimente alimentare LR Lifetakt și mesele LR Figuactive. {len(produse)} produse, prețuri finale, livrare prin curier în toată România.',
           '/magazin/lr/', body, produse[0]['img'], cr_ld + jsonld(item_ld))

for c in CATEG:
    cr_html, cr_ld = crumbs([('Magazin', '/magazin/'), ('LR', '/magazin/lr/'), (c['nume'], None)])
    ps = list({k: BYCOD[k] for sub in c['sub'] for k in sub['sku'] if k in BYCOD}.values())
    subs = ', '.join(sub['nume'] for sub in c['sub'])
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': f"{c['nume']} – LR", 'url': f"{SITE}/magazin/lr/{c['slug']}/",
          'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(ps), 'itemListElement': [
              {'@type': 'ListItem', 'position': i + 1, 'url': SITE + p['url'], 'name': p['denumire']} for i, p in enumerate(ps)]}}
    body = f'''<div class="mz-crumbs-wrap">{cr_html}</div>
<section class="hero-card mz-hero">
  <div class="hero-content">
    <span class="mz-eyebrow">LR · categorie</span>
    <h1 class="hero-title">{E(c['nume'])}</h1>
    <p class="mz-lead">{len(ps)} {'produs' if len(ps) == 1 else 'produse'} – {E(subs)}.</p>
  </div>
</section>
<section class="content-card mz-catalog-top">
  {SHIP_LR}
  <div class="mz-toolbar" style="margin-top:1.25rem">{nav(c['slug'])}</div>
</section>
<div data-mz-grid>
{sectiune(c)}
</div>
'''
    build_page(os.path.join(LRD, c['slug'], 'index.html'), f"{c['nume']} – LR | Magazin NutriSib",
               f"{c['nume']} – produse LR: {subs}. {len(ps)} produse, prețuri finale, transport {TRANSPORT_LR} lei.",
               f"/magazin/lr/{c['slug']}/", body, ps[0]['img'], cr_ld + jsonld(ld))

# ======================= sitemap LR =======================
xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
for u, pr, img in [('/magazin/lr/', '0.8', None)] + [(f'/magazin/lr/{c["slug"]}/', '0.75', None) for c in CATEG] + [(p['url'], '0.7', p['img']) for p in produse]:
    im = f'<image:image><image:loc>{SITE}{img}</image:loc></image:image>' if img else ''
    xml += f'  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority>{im}</url>\n'
write(os.path.join(ROOT, 'sitemap-magazin-lr.xml'), xml + '</urlset>\n')
_si = os.path.join(ROOT, 'sitemap.xml'); s = open(_si, encoding='utf-8').read()
if 'sitemap-magazin-lr.xml' not in s:
    s = s.replace('</sitemapindex>', '  <sitemap>\n    <loc>https://nutrisib.club/sitemap-magazin-lr.xml</loc>\n  </sitemap>\n\n</sitemapindex>')
    write(_si, s)

if __name__ == '__main__':
    print(f'OK: {len(produse)} produse LR, {len(CATEG)} grupe, {sum(len(c["sub"]) for c in CATEG)} categorii')
