#!/usr/bin/env python3
"""Generează magazinul static NutriSib (hub /magazin/ + Herbalife) din:
   - produse/herbalife/<slug>/produs.md + imagini (sursă locală, neurcată în Git)
   - produse/herbalife/_scripturi/herbalife-preturi-iulie2026.json (preț + VP)
Rulare din rădăcina repo-ului:  python3 scripts/magazin_build.py
"""
import os, re, json, hashlib, html, datetime, yaml, markdown
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'produse', 'herbalife')
PRICES = os.path.join(SRC, '_scripturi', 'herbalife-preturi-iulie2026.json')
OUT = os.path.join(ROOT, 'magazin')
HL = os.path.join(OUT, 'herbalife')
SITE = 'https://nutrisib.club'
TODAY = datetime.date.today().isoformat()
PRAG_VP, TRANSPORT = 125, 25
VANZATOR = 'PASCU RADU VASILE ÎNTREPRINDERE INDIVIDUALĂ'
E = lambda s: html.escape(str(s or ''), quote=True)

CATS = [  # (cheie, etichetă, regex pe denumire)
    ('mese', 'Shake-uri & mese', r'formula 1|protein drink mix|formula 3|tri blend|protein bake'),
    ('gustari', 'Gustări proteice', r'chipsuri|baton proteic|express batoane'),
    ('bauturi', 'Băuturi & infuzii', r'aloe vera|aloemax|ceai|iced coffee|liftoff'),
    ('sport', 'Nutriție sportivă H24', r'herbalife24|h24'),
    ('suplimente', 'Suplimente alimentare', r'formula 2|xtra|herbalifeline|beta heart|fibre|microbiotic|immune|active mind|phyto|night mode|gels|collagen'),
    ('ingrijire', 'Îngrijirea pielii & corpului', r'hl/skin|herbal aloe|skin masc'),
    ('accesorii', 'Accesorii & cărți', r'carte|cook'),
]
def categorie(nume):
    n = nume.lower()
    for k, lab, rx in CATS:
        if re.search(rx, n): return k, lab
    return 'suplimente', 'Suplimente alimentare'

_seen = {}
def webp(src, name, width, crop=False):
    """src -> magazin/herbalife/img/<name>-<width>.webp; deduplicare după conținut."""
    if not src or not os.path.exists(src): return None
    h = hashlib.md5(open(src, 'rb').read()).hexdigest()[:10] + f'-{width}'
    if h in _seen: return _seen[h]
    rel = f'img/{name}-{width}.webp'; dst = os.path.join(HL, rel)
    if not os.path.exists(dst):
        im = Image.open(src); im.load()
        im = im.convert('RGBA') if im.mode in ('P', 'LA', 'RGBA') else im.convert('RGB')
        if crop and im.mode == 'RGBA':  # taie marginile transparente și centrează pe pătrat cu margine 6%
            bb = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
            if bb:
                im = im.crop(bb); side = round(max(im.size) * 1.12)
                c = Image.new('RGBA', (side, side), (0, 0, 0, 0)); c.paste(im, ((side - im.width) // 2, (side - im.height) // 2)); im = c
        if im.width > width: im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im.save(dst + '.part', 'WEBP', quality=82, method=6); os.replace(dst + '.part', dst)
    url = f'/magazin/herbalife/{rel}'; _seen[h] = url; return url

def parse_md(path):
    t = open(path, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---\n(.*)', t, re.S)
    meta = yaml.safe_load(m.group(1)); body = m.group(2)
    disc = ''
    dm = re.search(r'\n---\n\n\*(.+?)\*\s*$', body, re.S)
    if dm: disc = dm.group(1).strip(); body = body[:dm.start()]
    parts = re.split(r'\n## ', '\n' + body)
    head_, secs = parts[0], []
    for p in parts[1:]:
        title, _, content = p.partition('\n'); secs.append((title.strip(), content.strip()))
    intro = re.sub(r'^# .*$|^\*.*\*$|^!\[.*$', '', head_, flags=re.M).strip()
    return meta, intro, secs, disc

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
      <p style="margin:0 0 .4rem"><strong>Magazinul NutriSib</strong> este operat de {VANZATOR}, CUI 38416337, Reg. Com. F32/667/2017.</p>
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

def build_page(path, title, desc, canon, body, og_img=None, extra='', robots=None):
    write(path, head(title, desc, canon, og_img, extra, robots) + body + foot())

# ======================= date produse =======================
def load_products():
    prices = json.load(open(PRICES, encoding='utf-8'))
    out = []
    for slug in sorted(os.listdir(SRC)):
        d = os.path.join(SRC, slug); mdp = os.path.join(d, 'produs.md')
        if not os.path.isfile(mdp): continue
        meta, intro, secs, disc = parse_md(mdp)
        sku = str(meta['sku']).upper(); pr = prices[sku]
        k, lab = categorie(meta['denumire'])
        imgs = {}
        for f in meta.get('imagini') or []:
            kind = next((x for x in ('ambalaj', 'preparat', 'lifestyle', 'nutritional') if x in f), 'alta')
            imgs.setdefault(kind, os.path.join(d, f))
        aroma = meta.get('aroma') or ''
        p = dict(slug=slug, sku=sku, denumire=meta['denumire'], aroma=aroma, marime=meta.get('marime') or '',
                 cat=k, cat_label=lab, meta_desc=meta.get('meta_descriere') or '', intro=intro, secs=secs, disc=disc,
                 pret=pr['pret'], vp=pr['vp'], url=f'/magazin/herbalife/{slug}/')
        p['varianta'] = ' · '.join(x for x in [aroma if aroma != 'Original' else '', p['marime']] if x)
        p['img'] = webp(imgs.get('ambalaj'), slug + '-ambalaj', 900, True)
        p['img_mic'] = webp(imgs.get('ambalaj'), slug + '-ambalaj', 420, True)
        p['galerie'] = [x for x in [(p['img'], 'ambalaj'), (webp(imgs.get('preparat'), slug + '-preparat', 1000), 'preparat'),
                                    (webp(imgs.get('lifestyle'), slug + '-lifestyle', 1000), 'lifestyle')] if x[0]]
        p['img_nutr'] = webp(imgs.get('nutritional'), slug + '-tabel-nutritional', 900)
        out.append(p)
    return out

produse = load_products()
fam = {}
for p in produse: fam.setdefault(p['denumire'], []).append(p)
for v in fam.values(): v.sort(key=lambda p: (p['pret'], p['varianta']))

os.makedirs(OUT, exist_ok=True)
json.dump({'generat': TODAY, 'config': {'prag_vp': PRAG_VP, 'transport': TRANSPORT, 'moneda': 'RON'},
           'produse': [{**{k: p[k] for k in ('sku', 'denumire', 'varianta', 'pret', 'vp', 'url', 'img_mic', 'cat')}, 'magazin': 'herbalife'} for p in produse]},
          open(os.path.join(OUT, 'catalog.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ======================= pagini produs =======================
for p in produse:
    variante = fam[p['denumire']]
    title = f"{p['denumire']}{' – ' + p['varianta'] if p['varianta'] else ''} | Herbalife | NutriSib"
    desc = (p['meta_desc'] or p['intro'])[:300]
    cr_html, cr_ld = crumbs([('Magazin', '/magazin/'), ('Herbalife', '/magazin/herbalife/'), (p['cat_label'], f'/magazin/herbalife/#{p["cat"]}'), (p['denumire'], None)])
    prod_ld = {'@context': 'https://schema.org', '@type': 'Product', 'name': f"{p['denumire']} {p['varianta']}".strip(), 'sku': p['sku'],
               'mpn': p['sku'], 'brand': {'@type': 'Brand', 'name': 'Herbalife'}, 'category': p['cat_label'],
               'image': [SITE + g for g, _ in p['galerie']], 'description': desc,
               'offers': {'@type': 'Offer', 'url': SITE + p['url'], 'priceCurrency': 'RON', 'price': str(p['pret']),
                          'availability': 'https://schema.org/InStock', 'itemCondition': 'https://schema.org/NewCondition',
                          'seller': {'@type': 'Organization', 'name': 'NutriSib'},
                          'shippingDetails': {'@type': 'OfferShippingDetails', 'shippingDestination': {'@type': 'DefinedRegion', 'addressCountry': 'RO'},
                                              'shippingRate': {'@type': 'MonetaryAmount', 'value': str(TRANSPORT), 'currency': 'RON'}},
                          'hasMerchantReturnPolicy': {'@type': 'MerchantReturnPolicy', 'applicableCountry': 'RO',
                                                      'returnPolicyCategory': 'https://schema.org/MerchantReturnFiniteReturnWindow', 'merchantReturnDays': 14,
                                                      'returnMethod': 'https://schema.org/ReturnByMail', 'returnFees': 'https://schema.org/ReturnFeesCustomerResponsibility'}}}
    thumbs = ''.join(
        f'<button type="button" class="{"active" if i == 0 else ""}" data-src="{g}" data-alt="{E(p["denumire"])} – {kind}"{"" if kind == "ambalaj" else " data-photo"} aria-label="Imagine {kind}"><img src="{g}" alt="" loading="lazy"></button>'
        for i, (g, kind) in enumerate(p['galerie'])) if len(p['galerie']) > 1 else ''
    specs = ''.join(f'<span>{lab}: <b>{E(v)}</b></span>' for lab, v in [('Aromă', p['aroma'] if p['aroma'] != 'Original' else ''), ('Mărime', p['marime']), ('Cod', p['sku']), ('Valoare', vp_fmt(p['vp']) + ' VP')] if v)
    var_html = ''
    if len(variante) > 1:
        var_html = '<div class="mz-variants"><div class="mz-variants-label">Alege varianta</div><div class="mz-chips">' + ''.join(
            f'<a class="mz-chip{" active" if v["sku"] == p["sku"] else ""}" href="{v["url"]}"{CUR if v["sku"] == p["sku"] else ""}>{E(v["varianta"] or v["sku"])}</a>' for v in variante) + '</div></div>'
    tabs = ''.join(f'<button class="mz-tab{" active" if i == 0 else ""}" role="tab" aria-selected="{"true" if i == 0 else "false"}" aria-controls="tab-{i}" id="t-{i}">{E(t)}</button>' for i, (t, _) in enumerate(p['secs']))
    panels = ''.join(f'<div class="mz-panel{" active" if i == 0 else ""}" role="tabpanel" id="tab-{i}" aria-labelledby="t-{i}">{md2html(c, p["img_nutr"])}</div>' for i, (t, c) in enumerate(p['secs']))
    body = f'''<div class="mz-crumbs-wrap">{cr_html}</div>
<section class="content-card">
  <div class="mz-product">
    <div>
      <div class="mz-gallery-main"><img src="{p['img']}" alt="{E(p['denumire'])} {E(p['varianta'])} – ambalaj cu etichetă în limba română" width="900" height="900"></div>
      <div class="mz-thumbs">{thumbs}</div>
    </div>
    <div>
      <div class="mz-p-cat">Herbalife · {E(p['cat_label'])}</div>
      <h1 class="mz-p-title">{E(p['denumire'])}</h1>
      {f'<p class="mz-p-sub">{E(p["intro"])}</p>' if p['intro'] else ''}
      <div class="mz-p-specs">{specs}</div>
      {var_html}
      <div class="mz-buybox" data-mz-buy="{p['sku']}">
        <div class="mz-price">{lei(p['pret'])}</div>
        <div class="mz-buy-row">
          <div class="mz-qty"><button type="button" data-step="-1" aria-label="Scade cantitatea">−</button><input type="number" min="1" max="99" value="1" aria-label="Cantitate"><button type="button" data-step="1" aria-label="Crește cantitatea">+</button></div>
          <button type="button" class="mz-btn" data-add>Adaugă în coș</button>
        </div>
        <div class="mz-added">Produsul a fost adăugat. <a href="/magazin/cos/">Vezi coșul →</a></div>
        <p class="mz-buy-note">Acest produs are <strong>{vp_fmt(p['vp'])} VP</strong>. Transport gratuit pentru comenzile de minimum {PRAG_VP} VP; sub prag, transportul costă {TRANSPORT} lei. <a href="/magazin/livrare/">Detalii livrare</a></p>
      </div>
      <div class="mz-advice">Nu știi dacă produsul ți se potrivește? Alegerea suplimentelor are sens după o evaluare a stilului tău de viață și a obiectivelor. <a href="/evaluare.html">Începe evaluarea NutriSib →</a></div>
    </div>
  </div>
</section>
<section class="content-card">
  <div class="mz-tabs" role="tablist">{tabs}</div>
  {panels}
  {f'<p class="mz-disclaimer">{E(p["disc"])}</p>' if p['disc'] else ''}
  <p class="mz-disclaimer">Descrierea, ingredientele și informațiile nutriționale provin de la producător (Herbalife). Suplimentele alimentare nu înlocuiesc o dietă variată și echilibrată și un stil de viață sănătos. Produsele Herbalife sunt vândute de {VANZATOR}, distribuitor independent Herbalife.</p>
</section>
'''
    build_page(os.path.join(HL, p['slug'], 'index.html'), title, desc, p['url'], body, p['img'], cr_ld + jsonld(prod_ld))

# ======================= catalog Herbalife =======================
order = [c[0] for c in CATS]
cards = []
for nume, vs in sorted(fam.items(), key=lambda kv: (order.index(kv[1][0]['cat']), -len(kv[1]), kv[0])):
    from collections import Counter
    mod = Counter(v['pret'] for v in vs).most_common(1)[0][0]
    p0 = next(v for v in vs if v['pret'] == mod); pmin, pmax, n = min(v['pret'] for v in vs), max(v['pret'] for v in vs), len(vs)
    arome = sorted({v['aroma'] for v in vs if v['aroma'] and v['aroma'] != 'Original'})
    meta = f'{len(arome)} arome' if len(arome) > 1 else (f'{n} variante' if n > 1 else p0['varianta'])
    text = ' '.join([nume, p0['cat_label']] + [v['varianta'] + ' ' + v['sku'] for v in vs])
    cards.append(f'''<a class="mz-card" href="{p0['url']}" data-cat="{p0['cat']}" data-text="{E(text)}">
  <div class="mz-card-img"><img src="{p0['img_mic']}" alt="{E(nume)}" loading="lazy" width="420" height="420"><span class="mz-card-vp">{vp_fmt(p0['vp'])} VP</span></div>
  <div class="mz-card-body">
    <span class="mz-card-cat">{E(p0['cat_label'])}</span>
    <h2 class="mz-card-title">{E(nume)}</h2>
    <span class="mz-card-meta">{E(meta)}</span>
    <div class="mz-card-foot"><span class="mz-price">{'<small>de la</small>' if pmin != pmax else ''}{lei(pmin)}</span><span class="mz-card-more">Detalii →</span></div>
  </div>
</a>''')
present = [c for c in CATS if any(p['cat'] == c[0] for p in produse)]
chips = '<button class="mz-chip active" data-filter="toate">Toate</button>' + ''.join(f'<button class="mz-chip" data-filter="{k}">{E(l)}</button>' for k, l, _ in present)
cr_html, cr_ld = crumbs([('Magazin', '/magazin/'), ('Herbalife', None)])
item_ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Produse Herbalife – NutriSib', 'numberOfItems': len(fam),
           'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': SITE + vs[0]['url'], 'name': nume} for i, (nume, vs) in enumerate(sorted(fam.items()))]}
body = f'''<div class="mz-crumbs-wrap">{cr_html}</div>
<section class="hero-card mz-hero">
  <div class="hero-content">
    <span class="mz-eyebrow">Magazin NutriSib · Herbalife</span>
    <h1 class="hero-title">Herbalife</h1>
    <p class="mz-lead">Catalogul complet Herbalife România – {len(produse)} produse și variante, cu ambalaj și etichetă în limba română. Prețuri finale, fără costuri ascunse.</p>
  </div>
</section>
<section class="content-card">
  <div class="mz-ship-note"><strong>Transport gratuit</strong> pentru comenzile de minimum {PRAG_VP} VP. Fiecare produs afișează valoarea VP, iar coșul o adună automat. Sub prag, transportul costă {TRANSPORT} lei.</div>
  <div class="mz-toolbar" style="margin:1.25rem 0">
    <div class="mz-chips" role="group" aria-label="Filtrează după categorie">{chips}</div>
    <input class="mz-search" type="search" placeholder="Caută produs, aromă sau cod…" aria-label="Caută în catalog">
  </div>
  <div class="mz-grid" data-mz-grid>
{chr(10).join(cards)}
  </div>
  <p class="mz-empty">Niciun produs nu corespunde căutării.</p>
</section>
'''
build_page(os.path.join(HL, 'index.html'), 'Produse Herbalife – catalog complet România | Magazin NutriSib',
           f'Catalogul complet Herbalife România: {len(produse)} produse și variante, cu etichetă în limba română, prețuri finale și transport gratuit de la {PRAG_VP} VP.',
           '/magazin/herbalife/', body, produse[0]['img'], cr_ld + jsonld(item_ld))

# ======================= hub /magazin/ =======================
thumbs = ''.join(f'<img src="{fam[n][0]["img_mic"]}" alt="" loading="lazy">' for n in ('Formula 1 Shake Mix Nutritiv', 'Băutură Concentrată Herbal Aloe Vera', 'Herbalife24® Hydrate') if n in fam)
cr_html, cr_ld = crumbs([('Acasă', '/'), ('Magazin', None)])
body = f'''<section class="hero-card mz-hero">
  <div class="hero-content">
    <span class="mz-eyebrow">Magazin NutriSib</span>
    <h1 class="hero-title">Instrumente pentru un sistem biologic calibrat</h1>
    <p class="mz-lead">Un singur loc pentru resursele NutriSib: ghidurile și cursurile digitale construite pe metoda C.E.L.O.S. și produse nutriționale selectate, cu informații complete de la producător.</p>
  </div>
</section>
<section class="content-card">
  <h2 class="mz-section-title">Alege magazinul</h2>
  <div class="mz-stores">
    <a class="mz-store" href="/magazin/herbalife/">
      <div><span class="mz-pill gold">Disponibil</span><h2>Herbalife</h2>
      <p>Shake-uri Formula 1, proteine, nutriție sportivă H24, suplimente alimentare și îngrijirea pielii – {len(produse)} produse și variante, cu etichetă în limba română.</p></div>
      <div class="mz-store-foot"><div class="mz-store-thumbs">{thumbs}</div><span class="mz-go">Intră în magazin →</span></div>
    </a>
    <a class="mz-store" href="/shop/">
      <div><span class="mz-pill">Acces instant</span><h2>NutriSib Digital</h2>
      <p>Ghiduri PDF, seria BIOS și kit-uri de transformare dezvoltate de dr.ing. Radu Pascu, livrate imediat pe email.</p></div>
      <div class="mz-store-foot"><span></span><span class="mz-go">Vezi produsele digitale →</span></div>
    </a>
    <div class="mz-store is-soon" aria-disabled="true">
      <div><span class="mz-pill">În curând</span><h2>LR Health &amp; Beauty</h2>
      <p>Produsele LR vor fi disponibile în curând.</p></div>
      <div class="mz-store-foot"><span></span><span class="mz-go" style="opacity:.5">În pregătire</span></div>
    </div>
    <div class="mz-store is-soon" aria-disabled="true">
      <div><span class="mz-pill">În curând</span><h2>FitLine</h2>
      <p>Produsele FitLine vor fi disponibile în curând.</p></div>
      <div class="mz-store-foot"><span></span><span class="mz-go" style="opacity:.5">În pregătire</span></div>
    </div>
  </div>
</section>
<section class="content-card">
  <h2 class="mz-section-title">Cum funcționează</h2>
  <div class="mz-principles">
    <div class="mz-principle"><h3>Prețuri finale</h3><p>Prețul afișat este prețul plătit. Transportul este gratuit pentru comenzile Herbalife de minimum {PRAG_VP} VP; sub prag costă {TRANSPORT} lei.</p></div>
    <div class="mz-principle"><h3>Plată securizată</h3><p>Plata cu cardul se face prin Stripe. Datele cardului nu ajung pe serverele NutriSib.</p></div>
    <div class="mz-principle"><h3>Alegere informată</h3><p>Fiecare produs are descrierea, ingredientele și tabelul nutrițional de la producător. Pentru recomandări personalizate, <a href="/evaluare.html">începe evaluarea</a>.</p></div>
  </div>
</section>
'''
build_page(os.path.join(OUT, 'index.html'), 'Magazin NutriSib – produse digitale, Herbalife, LR și FitLine',
           'Magazinul NutriSib: ghiduri și cursuri digitale C.E.L.O.S. și produse nutriționale Herbalife cu etichetă în limba română. LR și FitLine în curând.',
           '/magazin/', body, None, cr_ld)

# ======================= sitemap =======================
LEGAL = ['/magazin/termeni-si-conditii/', '/magazin/livrare/', '/magazin/retur/', '/magazin/confidentialitate/']
byurl = {p['url']: p for p in produse}
xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
for u, pr in [('/magazin/', '0.8'), ('/magazin/herbalife/', '0.8')] + [(p['url'], '0.7') for p in produse] + [(u, '0.3') for u in LEGAL]:
    img = ''.join(f'<image:image><image:loc>{SITE}{g}</image:loc></image:image>' for g, _ in byurl[u]['galerie']) if u in byurl else ''
    xml += f'  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority>{img}</url>\n'
write(os.path.join(ROOT, 'sitemap-magazin.xml'), xml + '</urlset>\n')

exec(open(os.path.join(os.path.dirname(__file__), 'magazin_pagini.py'), encoding='utf-8').read())

if __name__ == '__main__':
    print(f'OK: {len(produse)} pagini produs, {len(fam)} familii, {len(_seen)} imagini webp')
