#!/usr/bin/env python3
"""Generează magazinul LR (/magazin/lr/) și îl integrează în hub, magazin/catalog.json și sitemap.
Surse:
   - produse/lr/lr-sanatate.json – produse, prețuri, PV, texte, categorii; extras din shop.lrworld.com/RO, meniul SĂNĂTATE
   - produse/lr/img/<cod>.jpg     – imaginile oficiale (sursă locală, neurcată în Git; WebP-urile generate sunt în magazin/lr/img/)
   - scripts/lr_produse.json      – denumirile afișate și familiile de variante
Rulare din rădăcina repo-ului:  python3 scripts/magazin_lr.py
scripts/magazin_build.py (Herbalife) apelează la final integreaza(), ca hub-ul, catalogul și sitemap-ul să păstreze LR.
"""
import os, re, json, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from magazin_comun import *

# Activare: True după ce facturarea automată e configurată (de la 17.11.2026). Cât e False, paginile LR se văd,
# dar nu se pot comanda: nu au buton de coș, au noindex, lipsesc din sitemap, iar checkout-ul respinge produsele LR.
LR_ACTIV = False
TRANSPORT_LR = 25

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'produse', 'lr')
OUT = os.path.join(ROOT, 'magazin')
LRD = os.path.join(OUT, 'lr')
LR_CATALOG = os.path.join(LRD, 'catalog-lr.json')
BASE = '/magazin/lr/'
BRAND = 'LR Health & Beauty'
ACCESORII = {'70102-1', '8135-2'}   # nu sunt suplimente alimentare


def lei2(n):
    """Preț cu bani, ca în magazinul LR: 1189.9 -> '1.189,90 lei'."""
    return f'{n:,.2f}'.replace(',', ' ').replace('.', ',').replace(' ', '.') + ' lei'


def num(s): return float(s.replace('.', '').replace(',', '.'))


def slugify(s):
    s = s.lower().translate(str.maketrans('ăâîșşțţ', 'aaisstt'))
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


PRET_RE = re.compile(r'([\d.]+,\d{2}) RON(?: ([\d.]+,\d{2}) RON)? \(Net: ([\d.]+,\d{2}) RON\)'
                     r'(?: \(([\d.]+,\d{2}) RON per 1 (\w+)\))? PV: ([\d.]+,\d{2}) GV: ([\d.]+,\d{2})')


def pret_din_sursa(price_box):
    """Prețul curent (după eventuala reducere LR), prețul pe unitate și PV-ul din caseta de preț LR."""
    m = PRET_RE.match(price_box)
    if not m: raise ValueError(f'caseta de preț necunoscută: {price_box!r}')
    curent = m.group(2) or m.group(1)
    unitar = f'{m.group(4)} lei / {m.group(5)}' if m.group(4) else None
    return round(num(curent), 2), unitar, round(num(m.group(6)), 2)


# ---------------- curățarea textelor LR ----------------
TAB_NUME = {'Denumire': 'Descriere', 'Ingrediente': 'Ingrediente', 'Utilizare': 'Mod de utilizare',
            'Află mai multe': 'Află mai multe', 'FAQ': 'Întrebări frecvente'}


def curata_md(t):
    t = re.sub(r'<img[^>]*>', '', t)
    t = t.replace('<', '&lt;').replace('>', '&gt;')          # textul sursei e date, nu HTML
    t = re.sub(r'(?m)^\s*(mai mult|Title)\s*$', '', t)
    t = re.sub(r'\n\s*\+\s*\n', '\n\n**+** ', t)            # „+ 1 x GRATIS …” (cadoul din seturi)
    return re.sub(r'\n{3,}', '\n\n', t).strip()


def md_html(t):
    h = md2html(t)
    return re.sub(r'\^([0-9][0-9,]*)', r'<sup>\1</sup>', h)


def intro_html(short):
    t = curata_md(short)
    if not t: return ''
    nota = ''
    paras = []
    for p in t.split('\n\n'):
        if '•' in p:
            first, *items = [x.strip() for x in p.split('•')]
            if items and '\\*' in items[-1]:
                items[-1], _, rest = items[-1].partition('\\*'); items[-1] = items[-1].strip(); nota = '\\*' + rest.strip()
            if first: paras.append(first)
            paras.append('\n'.join('- ' + x for x in items if x))
        else:
            paras.append(p)
    if nota: paras.append(nota)
    return md_html('\n\n'.join(paras))


def tab_html(titlu_sursa, md, h1):
    t = curata_md(md)
    lines = t.split('\n')
    while lines and (not lines[0].strip() or re.sub(r'^#+\s*', '', lines[0]).strip().lower() in
                     {h1.strip().lower(), titlu_sursa.lower(), TAB_NUME.get(titlu_sursa, '').lower(), 'title'}):
        lines.pop(0)
    t = '\n'.join(lines).strip()
    return md_html(t) if t else ''


# ---------------- imagini (fundal alb -> transparent, pătrat, WebP) ----------------
_img = {}


def webp_lr(alias, slug, width):
    src = os.path.join(SRC, 'img', f'{alias}.jpg')
    rel = f'img/{slug}-{width}.webp'; dst = os.path.join(LRD, rel); url = BASE + rel
    if os.path.exists(dst): return url
    if not os.path.exists(src): return None
    if alias not in _img:
        import numpy as np
        from PIL import Image, ImageFilter
        from scipy import ndimage
        im = Image.open(src).convert('RGB'); a = np.asarray(im).astype(np.int16)
        lab, _ = ndimage.label(a.min(axis=2) >= 238)                 # doar albul legat de margini e fundal
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        alpha = Image.fromarray(np.where(np.isin(lab, list(edge)), 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
        im.putalpha(alpha); im = im.crop(alpha.point(lambda v: 255 if v > 8 else 0).getbbox())
        side = round(max(im.size) * 1.12); c = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        c.paste(im, ((side - im.width) // 2, (side - im.height) // 2)); _img[alias] = c
    from PIL import Image
    im = _img[alias].copy()
    if im.width > width: im = im.resize((width, width), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst + '.part', 'WEBP', quality=84, method=6); os.replace(dst + '.part', dst)
    return url


# ---------------- date ----------------
def incarca():
    data = json.load(open(os.path.join(SRC, 'lr-sanatate.json'), encoding='utf-8'))
    cur = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lr_produse.json'), encoding='utf-8'))
    # categorii în ordinea meniului LR: grupă -> subcategorii (fără paginile de prezentare, care n-au produse)
    cats = {}
    for c in data['categorii']:
        g = cur['grupe'][c['grup']]
        cat = cats.setdefault(g['slug'], {'slug': g['slug'], 'nume': g['nume'], 'sub': []})
        if c['produse']: cat['sub'].append({'nume': cur['subcategorii'].get(c['nume'], c['nume']), 'sku': c['produse']})
    categorii = list(cats.values())
    produse = []
    for alias, s in data['produse'].items():
        k = cur['produse'][alias]
        pret, unitar, pv = pret_din_sursa(s['price_box'])
        cantitate = re.sub(r'^.*Cod produs: \S+\s*', '', s['name_box']) or None
        if 'cantitate' in k and k['cantitate'] is None: cantitate, unitar = None, None
        gama = k.get('gama') or (s['crumbs'][4] if len(s['crumbs']) > 5 else '')
        cat, sub = next((c, sb) for c in categorii for sb in c['sub'] if alias in sb['sku'])
        slug = slugify(f"{k['denumire']} {k['varianta']}") + '-' + slugify(alias)
        p = dict(sku=alias, slug=slug, denumire=k['denumire'], varianta=k['varianta'], aroma=k.get('aroma', ''), gama=gama,
                 cantitate=cantitate, pret=pret, unitar=unitar, pv=pv, cat=cat['slug'], cat_label=cat['nume'], subcat=sub['nume'],
                 url=f'{BASE}{slug}/', sursa=s['href'].split('?')[0] + f'?productAlias={alias}', h1_sursa=s['h1'],
                 intro=intro_html(s['short_md']),
                 tabs=[(TAB_NUME.get(t['t'], t['t']), tab_html(t['t'], t['md'], s['h1']), t['t']) for t in s['tabs']])
        p['tabs'] = [(t, h, o) for t, h, o in p['tabs'] if h]
        p['img'] = webp_lr(alias, slug, 900); p['img_mic'] = webp_lr(alias, slug, 420)
        produse.append(p)
    return categorii, produse, data.get('extras', '')[:10]


# ---------------- pagini ----------------
SOON = ('<div class="mz-soon-box"><strong>Comenzile pentru produsele LR se deschid în curând.</strong> '
        'Poți consulta de pe acum catalogul și prețurile.</div>')
SHIP_LR = (f'<div class="mz-ship-note"><strong>Transport: {TRANSPORT_LR} lei</strong> pentru fiecare comandă cu produse LR, '
           'livrare prin curier oriunde în România.</div>')


def hero(eyebrow, titlu, lead):
    return f'''<section class="hero-card mz-hero mz-hero-hl mz-hero-lr">
  <div class="hero-content">
    <span class="mz-eyebrow">{eyebrow}</span>
    <h1 class="hero-title">{E(titlu)}</h1>
    <p class="mz-lead">{lead}</p>
  </div>
  <div class="mz-hero-brand"><img src="/magazin/assets/lr-logo.svg" alt="LR Health &amp; Beauty" width="240" height="213"></div>
</section>'''


def pagina(path, title, desc, canon, body, og_img=None, extra=''):
    write(path, head(title, desc, canon, og_img, extra, None if LR_ACTIV else 'noindex, follow') + body + foot())


def pagina_produs(p, fam):
    variante = fam[p['denumire']]
    title = f"{p['denumire']}{' – ' + p['varianta'] if p['varianta'] else ''} | LR | NutriSib"
    txt = re.sub(r'<[^>]+>', ' ', p['intro'] or (p['tabs'][0][1] if p['tabs'] else '')).replace('&lt;', '<').replace('&gt;', '>')
    desc = re.sub(r'\s+', ' ', txt).strip()[:300] or f"{p['denumire']} – produs LR Health & Beauty, cod {p['sku']}."
    cr_html, cr_ld = crumbs([('Magazin', '/magazin/'), ('LR', BASE), (p['cat_label'], f"{BASE}{p['cat']}/"), (p['denumire'], None)])
    disp = 'https://schema.org/InStock' if LR_ACTIV else 'https://schema.org/OutOfStock'
    prod_ld = {'@context': 'https://schema.org', '@type': 'Product', 'name': f"{p['denumire']} {p['varianta']}".strip(), 'sku': p['sku'],
               'mpn': p['sku'], 'brand': {'@type': 'Brand', 'name': BRAND}, 'category': p['cat_label'],
               'image': [SITE + p['img']] if p['img'] else [], 'description': desc,
               'offers': {'@type': 'Offer', 'url': SITE + p['url'], 'priceCurrency': 'RON', 'price': f"{p['pret']:.2f}",
                          'availability': disp, 'itemCondition': 'https://schema.org/NewCondition',
                          'seller': {'@type': 'Organization', 'name': 'NutriSib'},
                          'shippingDetails': {'@type': 'OfferShippingDetails', 'shippingDestination': {'@type': 'DefinedRegion', 'addressCountry': 'RO'},
                                              'shippingRate': {'@type': 'MonetaryAmount', 'value': str(TRANSPORT_LR), 'currency': 'RON'}},
                          'hasMerchantReturnPolicy': {'@type': 'MerchantReturnPolicy', 'applicableCountry': 'RO',
                                                      'returnPolicyCategory': 'https://schema.org/MerchantReturnFiniteReturnWindow', 'merchantReturnDays': 14,
                                                      'returnMethod': 'https://schema.org/ReturnByMail', 'returnFees': 'https://schema.org/ReturnFeesCustomerResponsibility'}}}
    specs = ''.join(f'<span>{lab}: <b>{E(v)}</b></span>' for lab, v in
                    [('Gama', p['gama']), ('Aromă', p['aroma']), ('Cantitate', p['cantitate']), ('Cod', p['sku'])] if v)
    var_html = ''
    if len(variante) > 1:
        var_html = '<div class="mz-variants"><div class="mz-variants-label">Alege varianta</div><div class="mz-chips">' + ''.join(
            f'<a class="mz-chip{" active" if v["sku"] == p["sku"] else ""}" href="{v["url"]}"{CUR if v["sku"] == p["sku"] else ""}>{E(v["varianta"] or v["sku"])}</a>' for v in variante) + '</div></div>'
    unitar = f'<div class="mz-unit-price">{E(p["unitar"])}</div>' if p['unitar'] else ''
    if LR_ACTIV:
        cumpara = f'''<div class="mz-buy-row">
          <div class="mz-qty"><button type="button" data-step="-1" aria-label="Scade cantitatea">−</button><input type="number" min="1" max="99" value="1" aria-label="Cantitate"><button type="button" data-step="1" aria-label="Crește cantitatea">+</button></div>
          <button type="button" class="mz-btn" data-add>Adaugă în coș</button>
        </div>
        <div class="mz-added">Produsul a fost adăugat. <a href="/magazin/cos/">Vezi coșul →</a></div>
        <p class="mz-buy-note">Transportul costă {TRANSPORT_LR} lei pentru fiecare comandă cu produse LR. <a href="/magazin/livrare/">Detalii livrare</a></p>'''
        buy_attr = f' data-mz-buy="{p["sku"]}"'
    else:
        cumpara, buy_attr = SOON, ''
    tabs = ''.join(f'<button class="mz-tab{" active" if i == 0 else ""}" role="tab" aria-selected="{"true" if i == 0 else "false"}" aria-controls="tab-{i}" id="t-{i}">{E(t)}</button>' for i, (t, _, _) in enumerate(p['tabs']))
    panels = ''.join(f'<div class="mz-panel{" active" if i == 0 else ""}" role="tabpanel" id="tab-{i}" aria-labelledby="t-{i}">{h}</div>' for i, (_, h, _) in enumerate(p['tabs']))
    ref = ''
    if not any(o == 'Denumire' for _, _, o in p['tabs']):
        baza = next((v for v in variante if v['sku'] != p['sku'] and any(o == 'Denumire' for _, _, o in v['tabs'])), None)
        if baza: ref = f'<p class="mz-buy-note">Descrierea completă a produsului este pe pagina variantei <a href="{baza["url"]}">{E(baza["varianta"])}</a>.</p>'
    supl = '' if p['sku'] in ACCESORII else 'Suplimentele alimentare nu înlocuiesc o dietă variată și echilibrată și un stil de viață sănătos. '
    info = f'''<section class="content-card">
  {f'<div class="mz-tabs" role="tablist">{tabs}</div>' if p['tabs'] else ''}
  {panels}
  {ref}
  <p class="mz-disclaimer">Descrierea, ingredientele și modul de utilizare provin de la producător (LR Health &amp; Beauty), din magazinul oficial LR România. {supl}Produsele LR sunt vândute de {VANZATOR}, partener independent LR.</p>
</section>'''
    body = f'''<div class="mz-crumbs-wrap">{cr_html}</div>
<section class="content-card">
  <div class="mz-product">
    <div>
      <div class="mz-gallery-main"><img src="{p['img']}" alt="{E(p['denumire'])} {E(p['varianta'])} – ambalaj" width="900" height="900"></div>
      <div class="mz-thumbs"></div>
    </div>
    <div>
      <div class="mz-p-cat">{E(p['cat_label'] if p['cat_label'].startswith('LR ') else 'LR · ' + p['cat_label'])}</div>
      <h1 class="mz-p-title">{E(p['denumire'])}</h1>
      {f'<div class="mz-p-short">{p["intro"]}</div>' if p['intro'] else ''}
      <div class="mz-p-specs">{specs}</div>
      {var_html}
      <div class="mz-buybox"{buy_attr}>
        <div class="mz-price">{lei2(p['pret'])}</div>
        {unitar}
        {cumpara}
      </div>
      <div class="mz-advice">Nu știi dacă produsul ți se potrivește? Alegerea suplimentelor are sens după o evaluare a stilului tău de viață și a obiectivelor. <a href="/evaluare.html">Începe evaluarea NutriSib →</a></div>
    </div>
  </div>
</section>
{info}
'''
    pagina(os.path.join(LRD, p['slug'], 'index.html'), title, desc, p['url'], body, p['img'], cr_ld + jsonld(prod_ld))


def genereaza():
    categorii, produse, data_extras = incarca()
    fam = {}
    for p in produse: fam.setdefault(p['denumire'], []).append(p)
    for v in fam.values(): v.sort(key=lambda p: (p['pret'], p['varianta']))
    BYSKU = {p['sku']: p for p in produse}

    for p in produse: pagina_produs(p, fam)

    def card(nume, vs):
        p0 = vs[0]; pmin, pmax = min(v['pret'] for v in vs), max(v['pret'] for v in vs)
        arome = sorted({v['aroma'] for v in vs if v['aroma']})
        meta = f'{len(arome)} arome' if len(arome) > 1 else (f'{len(vs)} variante' if len(vs) > 1 else (p0['varianta'] or p0['gama']))
        text = ' '.join([nume, p0['cat_label'], p0['subcat'], p0['gama']] + [v['varianta'] + ' ' + v['sku'] for v in vs])
        return f'''<a class="mz-card" href="{p0['url']}" data-text="{E(text)}">
  <div class="mz-card-img"><img src="{p0['img_mic']}" alt="{E(nume)}" loading="lazy" width="420" height="420"></div>
  <div class="mz-card-body">
    <span class="mz-card-cat">{E(p0['subcat'] or p0['cat_label'])}</span>
    <h3 class="mz-card-title">{E(nume)}</h3>
    <span class="mz-card-meta">{E(meta)}</span>
    <div class="mz-card-foot"><span class="mz-price">{'<small>de la</small>' if pmin != pmax else ''}{lei2(pmin)}</span><span class="mz-card-more">Detalii →</span></div>
  </div>
</a>'''

    def familii_din(skus):
        out = {}
        for s_ in skus:
            p = BYSKU.get(s_)
            if p and p['denumire'] not in out: out[p['denumire']] = fam[p['denumire']]
        return out

    def sectiune(c, h='h2'):
        blocks = []
        for sub in c['sub']:
            fs = familii_din(sub['sku'])
            if fs: blocks.append(f'<div class="mz-subsec"><h3 class="mz-sub-title">{E(sub["nume"])}</h3><div class="mz-grid">{"".join(card(n, v) for n, v in fs.items())}</div></div>')
        n_prod = len({s_ for sub in c['sub'] for s_ in sub['sku'] if s_ in BYSKU})
        return f'''<section class="content-card mz-catsec" id="{c['slug']}">
  <div class="mz-cat-head"><{h} class="mz-cat-title"><a href="{BASE}{c['slug']}/">{E(c['nume'])}</a></{h}><span class="mz-cat-count">{n_prod} {'produs' if n_prod == 1 else 'produse'}</span></div>
  {''.join(blocks)}
</section>'''

    def nav(activ=None):
        items = [(BASE, 'Toate', activ is None)] + [(f'{BASE}{c["slug"]}/', c['nume'], activ == c['slug']) for c in categorii]
        return '<nav class="mz-chips mz-catnav" aria-label="Categorii LR">' + ''.join(
            f'<a class="mz-chip{" active" if a else ""}" href="{u}"{CUR if a else ""}>{E(t)}</a>' for u, t, a in items) + '</nav>'

    top = SHIP_LR + ('' if LR_ACTIV else SOON)

    # --- catalogul LR ---
    cr_html, cr_ld = crumbs([('Magazin', '/magazin/'), ('LR', None)])
    item_ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Produse LR – NutriSib', 'numberOfItems': len(fam),
               'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': SITE + vs[0]['url'], 'name': n} for i, (n, vs) in enumerate(sorted(fam.items()))]}
    body = f'''<div class="mz-crumbs-wrap">{cr_html}</div>
{hero('Magazin NutriSib · LR', 'LR Health & Beauty','Gama de sănătate LR România: gelurile de băut Aloe Vera, suplimentele LR LIFETAKT, programul LR Health Mission și conceptul Figuactive. Prețuri finale, fără costuri ascunse.')}
<section class="content-card mz-catalog-top">
  {top}
  <div class="mz-toolbar" style="margin-top:1.25rem">
    {nav()}
    <input class="mz-search" type="search" placeholder="Caută produs, aromă sau cod…" aria-label="Caută în catalog">
  </div>
</section>
<div data-mz-grid>
{chr(10).join(sectiune(c) for c in categorii)}
</div>
<p class="mz-empty content-card">Niciun produs nu corespunde căutării.</p>
'''
    pagina(os.path.join(LRD, 'index.html'), 'Produse LR Health & Beauty – gama de sănătate | Magazin NutriSib',
           f'Gama de sănătate LR România pe categorii: gelurile de băut Aloe Vera, LR LIFETAKT, LR Health Mission, Figuactive. {len(produse)} produse și variante.',
           BASE, body, BYSKU['81000-10']['img'], cr_ld + jsonld(item_ld))

    # --- pagini de categorie ---
    for c in categorii:
        cr_html, cr_ld = crumbs([('Magazin', '/magazin/'), ('LR', BASE), (c['nume'], None)])
        skus = list(dict.fromkeys(s_ for sub in c['sub'] for s_ in sub['sku'] if s_ in BYSKU))
        subs = ', '.join(sub['nume'] for sub in c['sub'])
        fams = familii_din(skus)
        ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': f"{c['nume']} – LR", 'url': f"{SITE}{BASE}{c['slug']}/",
              'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(fams), 'itemListElement': [
                  {'@type': 'ListItem', 'position': i + 1, 'url': SITE + vs[0]['url'], 'name': n} for i, (n, vs) in enumerate(fams.items())]}}
        body = f'''<div class="mz-crumbs-wrap">{cr_html}</div>
{hero('LR · categorie', c['nume'], f"{len(skus)} {'produs' if len(skus) == 1 else 'produse și variante'} – {E(subs)}.")}
<section class="content-card mz-catalog-top">
  {top}
  <div class="mz-toolbar" style="margin-top:1.25rem">{nav(c['slug'])}</div>
</section>
<div data-mz-grid>
{sectiune(c)}
</div>
'''
        pagina(os.path.join(LRD, c['slug'], 'index.html'), f"{c['nume']} – LR | Magazin NutriSib",
               f"{c['nume']} – produse LR Health & Beauty: {subs}. {len(skus)} produse, prețuri finale.",
               f"{BASE}{c['slug']}/", body, BYSKU[skus[0]]['img'], cr_ld + jsonld(ld))

    # --- date pentru catalog.json, hub și sitemap ---
    thumbs = [BYSKU[s_]['img_mic'] for s_ in ('81000-10', '81180-99', '81241-18')]
    out = {'generat': TODAY, 'extras_din_sursa': data_extras, 'activ': LR_ACTIV, 'transport': TRANSPORT_LR, 'thumbs': thumbs,
           'familii': len(fam), 'categorii': [c['slug'] for c in categorii],
           'imagini': {p['url']: p['img'] for p in produse if p['img']},
           'produse': [{'sku': p['sku'], 'denumire': p['denumire'], 'varianta': p['varianta'], 'pret': p['pret'], 'vp': 0, 'pv': p['pv'],
                        'url': p['url'], 'img_mic': p['img_mic'], 'cat': p['cat'], 'magazin': 'lr', **({} if LR_ACTIV else {'inactiv': True})}
                       for p in produse]}
    json.dump(out, open(LR_CATALOG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return len(produse), len(fam), len(categorii)


# ---------------- integrare în hub, catalog.json și sitemap ----------------
def card_hub(d):
    n = len(d['produse'])
    thumbs = ''.join(f'<img src="{u}" alt="" loading="lazy">' for u in d['thumbs'])
    if d['activ']:
        return f'''<a class="mz-store" href="{BASE}">
      <div><span class="mz-pill">Disponibil</span><h2>LR Health &amp; Beauty</h2>
      <p>Gelurile de băut Aloe Vera, suplimentele LR LIFETAKT, LR Health Mission și conceptul Figuactive – {n} produse și variante din gama de sănătate LR.</p></div>
      <div class="mz-store-foot"><div class="mz-store-thumbs">{thumbs}</div><span class="mz-go">Intră în magazin →</span></div>
    </a>'''
    return f'''<div class="mz-store is-soon" aria-disabled="true">
      <div><span class="mz-pill gold">În curând</span><h2>LR Health &amp; Beauty</h2>
      <p>Se deschide în curând. Gelurile de băut Aloe Vera, suplimentele LR LIFETAKT, LR Health Mission și conceptul Figuactive – {n} produse și variante din gama de sănătate LR.</p></div>
      <div class="mz-store-foot"><div class="mz-store-thumbs">{thumbs}</div><span class="mz-go" style="color:#8a6d0f">Lansare în curând</span></div>
    </div>'''


VECHI_CARD = re.compile(r'<div class="mz-store is-soon" aria-disabled="true">\s*<div><span class="mz-pill">În curând</span><h2>LR Health &amp; Beauty</h2>'
                        r'[^<]*<p>[^<]*</p></div>\s*<div class="mz-store-foot">(?:(?!</div>).)*</div>\s*</div>', re.S)


def integreaza():
    if not os.path.exists(LR_CATALOG): return
    d = json.load(open(LR_CATALOG, encoding='utf-8'))
    # 1) catalog.json – sursa de prețuri pentru coș și pentru checkout (server)
    cp = os.path.join(OUT, 'catalog.json'); cat = json.load(open(cp, encoding='utf-8'))
    cat['produse'] = [p for p in cat['produse'] if p.get('magazin') != 'lr'] + d['produse']
    cat['config']['lr'] = {'transport': d['transport'], 'activ': d['activ']}
    json.dump(cat, open(cp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # 2) cardul din hub
    hp = os.path.join(OUT, 'index.html'); h = open(hp, encoding='utf-8').read()
    bloc = '<!--LR-->' + card_hub(d) + '<!--/LR-->'
    if '<!--LR-->' in h: h = re.sub(r'<!--LR-->.*?<!--/LR-->', lambda m: bloc, h, flags=re.S)
    elif VECHI_CARD.search(h): h = VECHI_CARD.sub(lambda m: bloc, h, count=1)
    else: raise SystemExit('Nu găsesc cardul LR în magazin/index.html')
    write(hp, h)
    # 3) sitemap: paginile LR doar când magazinul e activ
    sp = os.path.join(ROOT, 'sitemap-magazin.xml'); x = open(sp, encoding='utf-8').read()
    x = re.sub(r'  <!-- LR -->\n.*?  <!-- /LR -->\n', '', x, flags=re.S)
    if d['activ']:
        urls = [(BASE, '0.8')] + [(f'{BASE}{c}/', '0.75') for c in d['categorii']] + [(p['url'], '0.7') for p in d['produse']]
        rows = ''.join(f'  <url><loc>{SITE}{u}</loc><lastmod>{d["generat"]}</lastmod><priority>{pr}</priority>'
                       + (f'<image:image><image:loc>{SITE}{d["imagini"][u]}</image:loc></image:image>' if u in d['imagini'] else '') + '</url>\n'
                       for u, pr in urls)
        x = x.replace('</urlset>', f'  <!-- LR -->\n{rows}  <!-- /LR -->\n</urlset>')
    write(sp, x)


if __name__ == '__main__':
    n, f, c = genereaza()
    integreaza()
    print(f'OK: LR {n} pagini produs, {f} familii, {c} categorii – {"ACTIV" if LR_ACTIV else "în curând (necomandabil)"}')
