# Pachete Herbalife – rulat din magazin_build.py (înainte de secțiunea catalog)
import math
PK = json.load(open(os.path.join(os.path.dirname(__file__), 'herbalife_pachete.json'), encoding='utf-8'))
SLOT = PK['sloturi']
def pret_pachet(suma):
    """Cel mai mare preț terminat în 49 sau 99, <= 95% din suma componentelor."""
    t = (suma * 95) // 100; x = (t // 100) * 100 + 99
    while x > t: x -= 50
    return x

PACHETE = []
for pk in PK['pachete']:
    unitati = []                       # o unitate = un produs din pachet, cu varianta lui
    for slot, q in pk['compozitie']:
        for _ in range(q): unitati.append(slot)
    implicit = [SLOT[s]['optiuni'][0] for s in unitati]
    suma = sum(BYSKU_ALL[k]['pret'] for k in implicit); vp = round(sum(BYSKU_ALL[k]['vp'] for k in implicit), 2)
    pret = pret_pachet(suma)
    comp_txt = ' + '.join(f"{q} × {SLOT[s]['eticheta']}" if q > 1 else SLOT[s]['eticheta'] for s, q in pk['compozitie'])
    PACHETE.append(dict(pk, unitati=unitati, implicit=implicit, suma=suma, pret=pret, vp=vp, economie=suma - pret,
                        procent=round((suma - pret) / suma * 100, 1), comp_txt=comp_txt,
                        url=f"/magazin/herbalife/pachete/{pk['slug']}/"))

def img_pachet(p):
    """Imagine compusă din ambalajele produselor din pachet (o singură dată pe produs distinct)."""
    vs, seen = [], set()
    for k in p['implicit']:
        if k not in seen: seen.add(k); vs.append(BYSKU_ALL[k])
    if len(vs) == 1: vs = vs * min(3, len(p['implicit']))      # ex. Formula 1 – pachet de 3
    return img_grup('pachet ' + p['slug'], vs, allow_dup=True) or vs[0]['img_mic']

def card_pachet(p):
    return f'''<a class="mz-card mz-card-pk" href="{p['url']}" data-text="{E(p['nume'] + ' pachet ' + p['comp_txt'])}">
  <div class="mz-card-img"><img src="{img_pachet(p)}" alt="Pachet {E(p['nume'])}" loading="lazy" width="420" height="420"><span class="mz-card-vp">{vp_fmt(p['vp'])} VP</span><span class="mz-card-off">−{lei(p['economie'])}</span></div>
  <div class="mz-card-body">
    <span class="mz-card-cat">Pachet · {len(p['unitati'])} produse</span>
    <h3 class="mz-card-title">{E(p['nume'])}</h3>
    <span class="mz-card-meta">{E(p['comp_txt'])}</span>
    <div class="mz-card-foot"><span class="mz-price"><s class="mz-old">{lei(p['suma'])}</s>{lei(p['pret'])}</span><span class="mz-card-more">Detalii →</span></div>
  </div>
</a>'''

def eticheta_optiune(k, opts):
    v = BYSKU_ALL[k]; parti = [x for x in (v['aroma'], v['marime']) if x]
    nume_dif = len({BYSKU_ALL[o]['denumire'] for o in opts}) > 1
    return ((v['denumire'] + ' – ') if nume_dif else '') + (' · '.join(parti) or v['denumire'])

def build_pachete_pages():
    pag_ld = lambda p: {'@context': 'https://schema.org', '@type': 'Product', 'name': f"Pachet {p['nume']} – Herbalife", 'sku': p['id'],
        'brand': {'@type': 'Brand', 'name': 'Herbalife'}, 'image': [SITE + img_pachet(p)], 'description': f"Pachet Herbalife: {p['comp_txt']}.",
        'offers': {'@type': 'Offer', 'url': SITE + p['url'], 'priceCurrency': 'RON', 'price': str(p['pret']), 'availability': 'https://schema.org/InStock',
                   'itemCondition': 'https://schema.org/NewCondition', 'seller': {'@type': 'Organization', 'name': 'NutriSib'}}}
    # --- lista pachetelor ---
    cr_html, cr_ld = crumbs([('Magazin', '/magazin/'), ('Herbalife', '/magazin/herbalife/'), ('Pachete la ofertă', None)])
    body = f'''<div class="mz-crumbs-wrap">{cr_html}</div>
<section class="hero-card mz-hero mz-hero-hl">
  <div class="hero-content">
    <span class="mz-eyebrow">Herbalife · pachete</span>
    <h1 class="hero-title">Pachete la ofertă</h1>
    <p class="mz-lead">Combinații de produse Herbalife la un preț mai mic decât suma produselor cumpărate separat. Alegi aromele pentru fiecare produs din pachet.</p>
  </div>
  <div class="mz-hero-brand"><img src="/magazin/assets/herbalife-logo.webp" alt="Herbalife" width="640" height="177"></div>
</section>
<section class="content-card mz-catalog-top">
  {SHIP}
  <div class="mz-toolbar" style="margin-top:1.25rem">{nav_categorii('pachete')}</div>
</section>
<section class="content-card mz-catsec" id="pachete">
  <div class="mz-cat-head"><h2 class="mz-cat-title">Pachete la ofertă</h2><span class="mz-cat-count">{len(PACHETE)} pachete</span></div>
  <div class="mz-grid">{''.join(card_pachet(p) for p in PACHETE)}</div>
  <p class="mz-buy-note" style="margin-top:1.25rem">Prețul tăiat este suma prețurilor actuale ale produselor din pachet cumpărate separat, pentru variantele afișate. Reducerea este de cel puțin 5%.</p>
</section>
'''
    build_page(os.path.join(HL, 'pachete', 'index.html'), 'Pachete Herbalife la ofertă | Magazin NutriSib',
               f'{len(PACHETE)} pachete Herbalife – Formula 1, Protein Drink Mix, ceai, aloe, fibre – la un preț mai mic decât produsele cumpărate separat.',
               '/magazin/herbalife/pachete/', body, img_pachet(PACHETE[0]), cr_ld)
    # --- pagina fiecărui pachet ---
    for p in PACHETE:
        cr_html, cr_ld = crumbs([('Magazin', '/magazin/'), ('Herbalife', '/magazin/herbalife/'), ('Pachete la ofertă', '/magazin/herbalife/pachete/'), (p['nume'], None)])
        rows = []
        for i, s in enumerate(p['unitati']):
            opts = SLOT[s]['optiuni']
            if len(opts) > 1:
                sel = f'<select data-unit="{i}" aria-label="{E(SLOT[s]["eticheta"])} – alege varianta">' + ''.join(
                    f'<option value="{k}"{" selected" if k == p["implicit"][i] else ""}>{E(eticheta_optiune(k, opts))}{"" if BYSKU_ALL[k]["pret"] == BYSKU_ALL[opts[0]]["pret"] else " (" + lei(BYSKU_ALL[k]["pret"]) + ")"}</option>' for k in opts) + '</select>'
            else:
                sel = f'<input type="hidden" data-unit="{i}" value="{opts[0]}"><span class="mz-pk-fix">{E(BYSKU_ALL[opts[0]]["varianta"])}</span>'
            k0 = p['implicit'][i]
            rows.append(f'''<li class="mz-pk-row"><img src="{BYSKU_ALL[k0]['img_mic']}" alt="" data-img="{i}" loading="lazy">
  <div><a href="{BYSKU_ALL[k0]['url']}" data-link="{i}">{E(BYSKU_ALL[k0]['denumire'])}</a><div class="mz-pk-sel">{sel}</div></div>
  <span class="mz-pk-price" data-price="{i}">{lei(BYSKU_ALL[k0]['pret'])}</span></li>''')
        body = f'''<div class="mz-crumbs-wrap">{cr_html}</div>
<section class="content-card">
  <div class="mz-product">
    <div><div class="mz-gallery-main"><img src="{img_pachet(p)}" alt="Pachet {E(p['nume'])}" width="840" height="840"></div></div>
    <div data-mz-pachet="{p['id']}">
      <div class="mz-p-cat">Herbalife · Pachet la ofertă</div>
      <h1 class="mz-p-title">{E(p['nume'])}</h1>
      <p class="mz-p-sub">Pachet de {len(p['unitati'])} produse: {E(p['comp_txt'])}. Alege varianta fiecărui produs.</p>
      <ol class="mz-pk-list">{''.join(rows)}</ol>
      <div class="mz-buybox">
        <div class="mz-pk-sum">Preț produse separat: <s data-sum>{lei(p['suma'])}</s> · Economisești <strong data-save>{lei(p['economie'])} ({str(p['procent']).replace('.', ',')}%)</strong></div>
        <div class="mz-price" data-pret>{lei(p['pret'])}</div>
        <div class="mz-buy-row">
          <div class="mz-qty"><button type="button" data-step="-1" aria-label="Scade cantitatea">−</button><input type="number" min="1" max="20" value="1" aria-label="Cantitate"><button type="button" data-step="1" aria-label="Crește cantitatea">+</button></div>
          <button type="button" class="mz-btn" data-add-pk>Adaugă pachetul în coș</button>
        </div>
        <div class="mz-added">Pachetul a fost adăugat. <a href="/magazin/cos/">Vezi coșul →</a></div>
        <p class="mz-buy-note">Acest pachet are <strong data-vp>{vp_fmt(p['vp'])} VP</strong>{' – transport gratuit' if p['vp'] >= PRAG_VP else f'. Transport gratuit de la {PRAG_VP} VP pe comandă'}.</p>
      </div>
      <div class="mz-advice">Detaliile fiecărui produs (ingrediente, informații nutriționale, mod de utilizare) le găsești pe pagina lui – apasă pe numele produsului.</div>
    </div>
  </div>
</section>
'''
        build_page(os.path.join(HL, 'pachete', p['slug'], 'index.html'), f"Pachet {p['nume']} – Herbalife | NutriSib",
                   f"Pachet Herbalife {p['nume']}: {p['comp_txt']}. {lei(p['pret'])} în loc de {lei(p['suma'])}.",
                   p['url'], body, img_pachet(p), cr_ld + jsonld(pag_ld(p)))
