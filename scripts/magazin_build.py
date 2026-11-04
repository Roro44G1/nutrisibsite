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
# Comenzile online Herbalife: False = catalogul se vede, dar nu se poate comanda (precomenzi la telefon/e-mail).
# Se trece pe True după ce facturarea automată SmartBill funcționează, apoi se rulează din nou build-ul.
HL_ACTIV = False
from magazin_comun import *   # SITE, TODAY, PRAG_VP, TRANSPORT, VANZATOR, REGCOM, E, head, foot, crumbs, md2html, lei, …

CATDATA = json.load(open(os.path.join(os.path.dirname(__file__), 'herbalife_categorii.json'), encoding='utf-8'))
CATEGORII = CATDATA['categorii']
CAT_BY_SLUG = {c['slug']: c for c in CATEGORII}
SKU_CATS = {}   # sku -> [(slug categorie, nume subcategorie), ...] în ordinea meniului
for _c in CATEGORII:
    for _sub in _c['sub']:
        for _s in _sub['sku']: SKU_CATS.setdefault(_s, []).append((_c['slug'], _sub['nume']))
def categorie(sku):
    opts = SKU_CATS[sku]; pref = CATDATA.get('categorie_principala', {}).get(sku)
    slug, sub = next((o for o in opts if o[0] == pref), opts[0])
    return slug, CAT_BY_SLUG[slug]['nume'], sub

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

SOON_HL = precomanda_box('Herbalife', ', cu oferte speciale de deschidere')
DISP_HL = 'https://schema.org/InStock' if HL_ACTIV else 'https://schema.org/PreOrder'
BUY_ROW = '''<div class="mz-buy-row">
          <div class="mz-qty"><button type="button" data-step="-1" aria-label="Scade cantitatea">−</button><input type="number" min="1" max="99" value="1" aria-label="Cantitate"><button type="button" data-step="1" aria-label="Crește cantitatea">+</button></div>
          <button type="button" class="mz-btn" data-add>Adaugă în coș</button>
        </div>
        <div class="mz-added">Produsul a fost adăugat. <a href="/magazin/cos/">Vezi coșul →</a></div>'''
HL_SCRIPTS = '<script src="/magazin/assets/herbalife.js" defer></script>\n'
def build_page(path, title, desc, canon, body, og_img=None, extra='', robots=None, scripts=''):
    if '/magazin/herbalife/' in canon: scripts = HL_SCRIPTS + scripts
    write(path, head(title, desc, canon, og_img, extra, robots) + body + foot(scripts))

# ======================= date produse =======================
def load_products():
    prices = json.load(open(PRICES, encoding='utf-8'))
    out = []
    for slug in sorted(os.listdir(SRC)):
        d = os.path.join(SRC, slug); mdp = os.path.join(d, 'produs.md')
        if not os.path.isfile(mdp): continue
        meta, intro, secs, disc = parse_md(mdp)
        sku = str(meta['sku']).upper(); pr = prices[sku]
        k, lab, subcat = categorie(sku)
        imgs = {}
        for f in meta.get('imagini') or []:
            kind = next((x for x in ('ambalaj', 'preparat', 'lifestyle', 'nutritional') if x in f), 'alta')
            imgs.setdefault(kind, os.path.join(d, f))
        aroma = meta.get('aroma') or ''
        p = dict(slug=slug, sku=sku, denumire=meta['denumire'], aroma=aroma, marime=meta.get('marime') or '',
                 cat=k, cat_label=lab, subcat=subcat, meta_desc=meta.get('meta_descriere') or '', intro=intro, secs=secs, disc=disc,
                 pret=pr['pret'], vp=pr['vp'], url=f'/magazin/herbalife/{slug}/')
        p['varianta'] = ' · '.join(x for x in [aroma if aroma != 'Original' else '', p['marime']] if x)
        p['src_ambalaj'] = imgs.get('ambalaj')
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
json.dump({'generat': TODAY, 'config': {'prag_vp': PRAG_VP, 'transport': TRANSPORT, 'moneda': 'RON', 'herbalife': {'activ': HL_ACTIV}},
           'produse': [{**{k: p[k] for k in ('sku', 'denumire', 'varianta', 'pret', 'vp', 'url', 'img_mic', 'cat')}, 'magazin': 'herbalife', **({} if HL_ACTIV else {'inactiv': True})} for p in produse]},
          open(os.path.join(OUT, 'catalog.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ======================= pagini produs =======================
from collections import Counter
_DESC_N = Counter(scurt((p['meta_desc'] or p['intro'])[:300]) for p in produse)
for p in produse:
    variante = fam[p['denumire']]
    title = f"{p['denumire']}{' – ' + p['varianta'] if p['varianta'] else ''} | Herbalife | NutriSib"
    desc = (p['meta_desc'] or p['intro'])[:300]
    if _DESC_N[scurt(desc)] > 1:  # aceeași descriere la mai multe ambalaje → descrieri unice pentru Google
        desc = f"{p['varianta'] or p['denumire']}: {desc}"
    if len(desc) < 70:
        desc += f". Produs Herbalife cu etichetă în limba română, preț final {p['pret']} lei."
    cr_html, cr_ld = crumbs([('Magazin', '/magazin/'), ('Herbalife', '/magazin/herbalife/'), (p['cat_label'], f'/magazin/herbalife/{p["cat"]}/'), (p['denumire'], None)])
    prod_ld = {'@context': 'https://schema.org', '@type': 'Product', 'name': f"{p['denumire']} {p['varianta']}".strip(), 'sku': p['sku'],
               'mpn': p['sku'], 'brand': {'@type': 'Brand', 'name': 'Herbalife'}, 'category': p['cat_label'],
               'image': [SITE + g for g, _ in p['galerie']], 'description': desc,
               'offers': {'@type': 'Offer', 'url': SITE + p['url'], 'priceCurrency': 'RON', 'price': str(p['pret']),
                          'availability': DISP_HL, 'itemCondition': 'https://schema.org/NewCondition',
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
      <div class="mz-buybox"{f' data-mz-buy="{p["sku"]}"' if HL_ACTIV else ''}>
        <div class="mz-price">{lei(p['pret'])}</div>
        {BUY_ROW if HL_ACTIV else SOON_HL}
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

# ======================= catalog Herbalife (pe categorii, ca în MyHerbalife) =======================
from collections import Counter
BYSKU = {p['sku']: p for p in produse}
def card(nume, vs):
    mod = Counter(v['pret'] for v in vs).most_common(1)[0][0]
    p0 = next(v for v in vs if v['pret'] == mod); pmin, pmax, n = min(v['pret'] for v in vs), max(v['pret'] for v in vs), len(vs)
    arome = sorted({v['aroma'] for v in vs if v['aroma'] and v['aroma'] != 'Original'})
    meta = f'{len(arome)} arome' if len(arome) > 1 else (f'{n} variante' if n > 1 else p0['varianta'])
    text = ' '.join([nume, p0['cat_label'], p0['subcat']] + [v['varianta'] + ' ' + v['sku'] for v in vs])
    return f'''<a class="mz-card" href="{p0['url']}" data-text="{E(text)}">
  <div class="mz-card-img"><img src="{img_grup(nume, vs) or p0['img_mic']}" alt="{E(nume)}" loading="lazy" width="420" height="420"><span class="mz-card-vp">{vp_fmt(p0['vp'])} VP</span></div>
  <div class="mz-card-body">
    <span class="mz-card-cat">{E(p0['subcat'] or p0['cat_label'])}</span>
    <h3 class="mz-card-title">{E(nume)}</h3>
    <span class="mz-card-meta">{E(meta)}</span>
    <div class="mz-card-foot"><span class="mz-price">{'<small>de la</small>' if pmin != pmax else ''}{lei(pmin)}</span><span class="mz-card-more">Detalii →</span></div>
  </div>
</a>'''

def e_plic(p): return 'plicule' in (p['marime'] or '').lower()
def nume_card(p): return p['denumire'] + (' – plicuri' if e_plic(p) and any(not e_plic(v) for v in fam[p['denumire']]) else '')
CARD_FAM = {}
for p in produse: CARD_FAM.setdefault(nume_card(p), []).append(p)
for v in CARD_FAM.values(): v.sort(key=lambda p: (p['pret'], p['varianta']))

def img_grup(nume, vs, allow_dup=False):
    """Imagine compusă din ambalajele variantelor (etichete RO), pentru cardurile cu mai multe variante."""
    srcs, seen = [], set()
    for v in vs:
        if v['src_ambalaj'] and (allow_dup or v['img'] not in seen): seen.add(v['img']); srcs.append(v['src_ambalaj'])
    if len(srcs) < 2: return None
    srcs = srcs[:5]
    slug = re.sub(r'[^a-z0-9]+', '-', nume.lower().translate(str.maketrans('ăâîșşțţ', 'aaisstt'))).strip('-')
    dst = os.path.join(HL, 'img', f'grup-{slug}-840.webp'); url = f'/magazin/herbalife/img/grup-{slug}-840.webp'
    if os.path.exists(dst): return url
    ims = []
    for f in srcs:
        im = Image.open(f).convert('RGBA'); bb = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
        if bb: im = im.crop(bb)
        ims.append(im)
    H = 600; ims = [im.resize((round(im.width * H / im.height), H), Image.LANCZOS) for im in ims]
    n = len(ims); mid = n // 2
    scale = [0.86 if i != mid else 1.0 for i in range(n)]
    ims = [im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS) for im, sc in zip(ims, scale)]
    step = max(im.width for im in ims) * (0.5 if n > 2 else 0.7)
    W = round(step * (n - 1) + ims[-1].width); Hc = max(im.height for im in ims)
    canvas = Image.new('RGBA', (W, Hc), (0, 0, 0, 0))
    order = sorted(range(n), key=lambda i: -abs(i - mid))   # cele din margini în spate, centrul în față
    for i in order:
        im = ims[i]; canvas.alpha_composite(im, (round(step * i), Hc - im.height))
    side = round(max(W, Hc) * 1.08); sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    sq.alpha_composite(canvas, ((side - W) // 2, (side - Hc) // 2)); sq.thumbnail((840, 840), Image.LANCZOS)
    sq.save(dst + '.part', 'WEBP', quality=84, method=6); os.replace(dst + '.part', dst)
    return url

def familii_din(skus):
    """Grupurile de card (denumire, separat plicuri) care au cel puțin un SKU în listă, în ordinea listei."""
    out = {}
    for s_ in skus:
        p = BYSKU.get(s_)
        if p and nume_card(p) not in out: out[nume_card(p)] = CARD_FAM[nume_card(p)]
    return out

BYSKU_ALL = BYSKU
exec(open(os.path.join(os.path.dirname(__file__), 'magazin_pachete.py'), encoding='utf-8').read())

def sectiune_categorie(c, h='h2'):
    blocks = []
    for sub in c['sub']:
        fs = familii_din(sub['sku'])
        if not fs: continue
        title = f'<h3 class="mz-sub-title">{E(sub["nume"])}</h3>' if sub['nume'] else ''
        blocks.append(f'<div class="mz-subsec">{title}<div class="mz-grid">{"".join(card(n, v) for n, v in fs.items())}</div></div>')
    n_prod = len({s_ for sub in c['sub'] for s_ in sub['sku'] if s_ in BYSKU})
    return f'''<section class="content-card mz-catsec" id="{c['slug']}">
  <div class="mz-cat-head"><{h} class="mz-cat-title"><a href="/magazin/herbalife/{c['slug']}/">{E(c['nume'])}</a></{h}><span class="mz-cat-count">{n_prod} {'produs' if n_prod == 1 else 'produse'}</span></div>
  {''.join(blocks)}
</section>'''

def nav_categorii(activ=None):
    items = [('/magazin/herbalife/', 'Toate', activ is None), ('/magazin/herbalife/pachete/', 'Pachete la ofertă', activ == 'pachete')] + [(f'/magazin/herbalife/{c["slug"]}/', c['nume'], activ == c['slug']) for c in CATEGORII]
    return '<nav class="mz-chips mz-catnav" aria-label="Categorii Herbalife">' + ''.join(
        f'<a class="mz-chip{" active" if a else ""}" href="{u}"{CUR if a else ""}>{E(t)}</a>' for u, t, a in items) + '</nav>'

SHIP = f'<div class="mz-ship-note"><strong>Transport gratuit</strong> pentru comenzile de minimum {PRAG_VP} VP. Fiecare produs afișează valoarea VP, iar coșul o adună automat. Sub prag, transportul costă {TRANSPORT} lei.</div>' + '<p class="mz-offer-link"><a href="/magazin/oferta/">📄 Oferta NutriSib – lista completă de prețuri (cu PDF descărcabil) →</a></p>'
if not HL_ACTIV: SHIP = SHIP.replace('<p class="mz-offer-link">', SOON_HL + '<p class="mz-offer-link">', 1)

# --- pagina principală a catalogului ---
cr_html, cr_ld = crumbs([('Magazin', '/magazin/'), ('Herbalife', None)])
item_ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Produse Herbalife – NutriSib', 'numberOfItems': len(fam),
           'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': SITE + vs[0]['url'], 'name': nume} for i, (nume, vs) in enumerate(sorted(fam.items()))]}
body = f'''<div class="mz-crumbs-wrap">{cr_html}</div>
<section class="hero-card mz-hero mz-hero-hl">
  <div class="hero-content">
    <span class="mz-eyebrow">Magazin NutriSib · Herbalife</span>
    <h1 class="hero-title">Herbalife</h1>
    <p class="mz-lead">Catalogul complet Herbalife România. Prețuri finale, fără costuri ascunse.</p>
  </div>
  <div class="mz-hero-brand"><img src="/magazin/assets/herbalife-logo.webp" alt="Herbalife" width="640" height="177"></div>
</section>
<section class="content-card mz-catalog-top">
  {SHIP}
  <div class="mz-toolbar" style="margin-top:1.25rem">
    {nav_categorii()}
    <input class="mz-search" type="search" placeholder="Caută produs, aromă sau cod…" aria-label="Caută în catalog">
  </div>
</section>
<div data-mz-grid>
<section class="content-card mz-catsec mz-pk-teaser" id="pachete">
  <div class="mz-cat-head"><h2 class="mz-cat-title"><a href="/magazin/herbalife/pachete/">Pachete la ofertă</a></h2><span class="mz-cat-count"><a href="/magazin/herbalife/pachete/">Toate cele {len(PACHETE)} pachete →</a></span></div>
  <div class="mz-grid">{''.join(card_pachet(p) for p in sorted(PACHETE, key=lambda p: -p['economie'])[:4])}</div>
</section>
{chr(10).join(sectiune_categorie(c) for c in CATEGORII)}
</div>
<p class="mz-empty content-card">Niciun produs nu corespunde căutării.</p>
<section class="content-card mz-video">
  <h2 class="mz-section-title">Herbalife în imagini</h2>
  <div class="mz-video-facade" data-tiktok="7622323586174356767" data-user="herbalife">
    <p><strong>Video de pe contul oficial TikTok @herbalife</strong></p>
    <p class="mz-buy-note">Videoclipul se încarcă de pe TikTok doar dacă apeși butonul de mai jos. TikTok poate seta cookie-uri proprii.</p>
    <button type="button" class="mz-btn" style="flex:none">▶ Încarcă videoclipul</button>
    <p class="mz-buy-note"><a href="https://www.tiktok.com/@herbalife/video/7622323586174356767" target="_blank" rel="noopener">Sau deschide-l direct pe TikTok →</a></p>
  </div>
</section>
'''
build_page(os.path.join(HL, 'index.html'), 'Produse Herbalife – catalog complet România | Magazin NutriSib',
           f'Catalogul complet Herbalife România pe categorii: mic dejun și mese sănătoase, nutriția de bază, gama sport, nutriție externă și altele. {len(produse)} produse cu etichetă în limba română.',
           '/magazin/herbalife/', body, produse[0]['img'], cr_ld + jsonld(item_ld))

# --- pagini de categorie ---
for c in CATEGORII:
    cr_html, cr_ld = crumbs([('Magazin', '/magazin/'), ('Herbalife', '/magazin/herbalife/'), (c['nume'], None)])
    skus = [s_ for sub in c['sub'] for s_ in sub['sku'] if s_ in BYSKU]
    subs = ', '.join(sub['nume'] for sub in c['sub'] if sub['nume'])
    fams = familii_din(skus)
    desc = f"{c['nume']} – produse Herbalife cu etichetă în limba română{': ' + subs if subs else ''}. {len(skus)} produse, prețuri finale, transport gratuit de la {PRAG_VP} VP."
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': f"{c['nume']} – Herbalife", 'url': f"{SITE}/magazin/herbalife/{c['slug']}/",
          'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(fams), 'itemListElement': [
              {'@type': 'ListItem', 'position': i + 1, 'url': SITE + vs[0]['url'], 'name': n} for i, (n, vs) in enumerate(fams.items())]}}
    body = f'''<div class="mz-crumbs-wrap">{cr_html}</div>
<section class="hero-card mz-hero mz-hero-hl">
  <div class="hero-content">
    <span class="mz-eyebrow">Herbalife · categorie</span>
    <h1 class="hero-title">{E(c['nume'])}</h1>
    <p class="mz-lead">{len(skus)} {'produs' if len(skus) == 1 else 'produse și variante'}{' – ' + E(subs) if subs else ''}.</p>
  </div>
  <div class="mz-hero-brand"><img src="/magazin/assets/herbalife-logo.webp" alt="Herbalife" width="640" height="177"></div>
</section>
<section class="content-card mz-catalog-top">
  {SHIP}
  <div class="mz-toolbar" style="margin-top:1.25rem">{nav_categorii(c['slug'])}</div>
</section>
<div data-mz-grid>
{sectiune_categorie(c, 'h2')}
</div>
'''
    build_page(os.path.join(HL, c['slug'], 'index.html'), f"{c['nume']} – Herbalife | Magazin NutriSib", desc,
               f"/magazin/herbalife/{c['slug']}/", body, BYSKU[skus[0]]['img'], cr_ld + jsonld(ld))

build_pachete_pages()
_cat = json.load(open(os.path.join(OUT, 'catalog.json'), encoding='utf-8'))
_cat['pachete'] = [{'id': p['id'], 'nume': p['nume'], 'url': p['url'], 'img_mic': img_pachet(p), 'unitati': [{'slot': u, 'eticheta': SLOT[u]['eticheta'], 'optiuni': SLOT[u]['optiuni']} for u in p['unitati']], 'implicit': p['implicit']} for p in PACHETE]
_cat['config']['reducere_pachet'] = 0.05
json.dump(_cat, open(os.path.join(OUT, 'catalog.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

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
      <div><span class="mz-pill gold">{'Disponibil' if HL_ACTIV else 'Precomenzi · deschidere în curând'}</span><h2>Herbalife</h2>
      <p>{'' if HL_ACTIV else 'Comenzile online se deschid în curând, cu oferte speciale de deschidere – până atunci, precomenzi la telefon sau e-mail. '}Shake-uri Formula 1, proteine, nutriție sportivă H24, suplimente alimentare și îngrijirea pielii – {len(produse)} produse și variante, cu etichetă în limba română.</p></div>
      <div class="mz-store-foot"><div class="mz-store-thumbs">{thumbs}</div><span class="mz-go">{'Intră în magazin' if HL_ACTIV else 'Vezi catalogul și prețurile'} →</span></div>
    </a>
    <a class="mz-store" href="/shop/">
      <div><span class="mz-pill">Acces instant</span><h2>NutriSib Digital</h2>
      <p>Ghiduri PDF, seria BIOS și kit-uri de transformare dezvoltate de dr.ing. Radu Pascu, livrate imediat pe email.</p></div>
      <div class="mz-store-foot"><span></span><span class="mz-go">Vezi produsele digitale →</span></div>
    </a>
    <!--LR--><div class="mz-store is-soon" aria-disabled="true">
      <div><span class="mz-pill">În curând</span><h2>LR Health &amp; Beauty</h2>
      <p>Produsele LR vor fi disponibile în curând.</p></div>
      <div class="mz-store-foot"><span></span><span class="mz-go" style="opacity:.5">În pregătire</span></div>
    </div><!--/LR-->
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
    <div class="mz-principle"><h3>Oferta NutriSib</h3><p>Toate prețurile produselor și pachetelor într-o singură listă, cu link la fiecare produs. <a href="/magazin/oferta/">Vezi oferta</a> sau <a href="/magazin/oferta/oferta-nutrisib-herbalife.pdf">descarcă PDF-ul</a>.</p></div>
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
for u, pr in [('/magazin/', '0.8'), ('/magazin/herbalife/', '0.8')] + [(f'/magazin/herbalife/{c["slug"]}/', '0.75') for c in CATEGORII] + [('/magazin/herbalife/pachete/', '0.8')] + [(p['url'], '0.7') for p in PACHETE] + [('/magazin/oferta/', '0.6')] + [(p['url'], '0.7') for p in produse] + [(u, '0.3') for u in LEGAL]:
    img = ''.join(f'<image:image><image:loc>{SITE}{g}</image:loc></image:image>' for g, _ in byurl[u]['galerie']) if u in byurl else ''
    xml += f'  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority>{img}</url>\n'
write(os.path.join(ROOT, 'sitemap-magazin.xml'), xml + '</urlset>\n')

exec(open(os.path.join(os.path.dirname(__file__), 'magazin_pagini.py'), encoding='utf-8').read())

# LR: cardul din hub, produsele din catalog.json și sitemap-ul (paginile LR le generează scripts/magazin_lr.py)
import magazin_lr; magazin_lr.integreaza()

if __name__ == '__main__':
    print(f'OK: {len(produse)} pagini produs, {len(fam)} familii, {len(_seen)} imagini webp')
