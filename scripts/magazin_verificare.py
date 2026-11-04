#!/usr/bin/env python3
"""Verifică magazinul generat: prețuri (față de lista Herbalife și de sursa LR), pachete, linkuri interne, date structurate.
Rulare din rădăcina repo-ului: python3 scripts/magazin_verificare.py"""
import os, re, json, glob, math, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); os.chdir(ROOT)
err, ok = [], 0
def bad(m): err.append(m)
cat = json.load(open('magazin/catalog.json', encoding='utf-8'))
P = {p['sku']: p for p in cat['produse']}
src = json.load(open('produse/herbalife/_scripturi/herbalife-preturi-iulie2026.json', encoding='utf-8')) if os.path.exists('produse/herbalife/_scripturi/herbalife-preturi-iulie2026.json') else None
lei = lambda n: f'{n:,}'.replace(',', '.') + ' lei'
# LR: prețul = prețul curent din magazinul LR România (produse/lr/lr-sanatate.json), cu bani
sys.path.insert(0, 'scripts')
import magazin_lr as LR
lr_src = json.load(open('produse/lr/lr-sanatate.json', encoding='utf-8'))['produse'] if os.path.exists('produse/lr/lr-sanatate.json') else None
lr_cfg = cat['config'].get('lr', {})
def verifica_lr(s, p):
    global ok
    if lr_src:
        pret, _, pv = LR.pret_din_sursa(lr_src[s]['price_box'])
        if abs(p['pret'] - pret) > 1e-9: bad(f'LR {s}: preț {p["pret"]} ≠ sursa LR {pret}')
        if abs(p['pv'] - pv) > 1e-9: bad(f'LR {s}: PV {p["pv"]} ≠ sursa LR {pv}')
    if bool(p.get('inactiv')) == bool(lr_cfg.get('activ')): bad(f'LR {s}: starea inactiv nu corespunde cu config.lr.activ')
    f = 'magazin' + p['url'][len('/magazin'):] + 'index.html'
    if not os.path.exists(f): bad(f'LR {s}: lipsește pagina {p["url"]}'); return
    h = open(f, encoding='utf-8').read()
    if f'<div class="mz-price">{LR.lei2(p["pret"])}</div>' not in h: bad(f'LR {s}: prețul {LR.lei2(p["pret"])} nu apare în pagină')
    if f'"price": "{p["pret"]:.2f}"' not in h: bad(f'LR {s}: JSON-LD cu alt preț')
    if lr_cfg.get('activ'):
        if f'data-mz-buy="{s}"' not in h: bad(f'LR {s}: lipsește butonul de coș')
    else:
        if 'data-mz-buy' in h or 'noindex' not in h: bad(f'LR {s}: pagina „în curând” are buton de coș sau e indexabilă')
    ok += 1
# 1) prețuri produse = coloana 25% rotunjită la cel mai apropiat multiplu de 10
for s, p in P.items():
    if p.get('magazin') == 'lr': verifica_lr(s, p); continue
    if src:
        r = src[s]; exp = int(math.floor(r['p25'] / 10 + 0.5) * 10) if r.get('p25') is not None else int(math.floor(r['lista'] / 10 + 0.5) * 10)
        if p['pret'] != exp: bad(f'{s}: preț {p["pret"]} ≠ {exp} (lista 25% = {r.get("p25")})')
        if abs(p['vp'] - r['vp']) > 1e-9: bad(f'{s}: VP {p["vp"]} ≠ {r["vp"]}')
    f = 'magazin' + p['url'][len('/magazin'):] + 'index.html'
    if not os.path.exists(f): bad(f'{s}: lipsește pagina {p["url"]}'); continue
    h = open(f, encoding='utf-8').read()
    if f'<div class="mz-price">{lei(p["pret"])}</div>' not in h: bad(f'{s}: prețul {lei(p["pret"])} nu apare în pagina produsului')
    if f'"price": "{p["pret"]}"' not in h: bad(f'{s}: JSON-LD cu alt preț')
    vp = f'{p["vp"]:.2f}'.replace('.', ',')
    if vp + ' VP' not in h: bad(f'{s}: VP {vp} nu apare în pagină')
    ok += 1
# 2) pachete
def pk_price(s_):
    t = (s_ * 95) // 100; x = (t // 100) * 100 + 99
    while x > t: x -= 50
    return x
for pk in cat.get('pachete', []):
    suma = sum(P[k]['pret'] for k in pk['implicit']); pret = pk_price(suma)
    if pret % 100 not in (49, 99): bad(f'{pk["id"]}: prețul {pret} nu se termină în 49/99')
    if pret > suma * 0.95: bad(f'{pk["id"]}: reducere sub 5%')
    for u, k in zip(pk['unitati'], pk['implicit']):
        if k not in u['optiuni']: bad(f'{pk["id"]}: implicit {k} nu e opțiune')
    h = open('magazin' + pk['url'][len('/magazin'):] + 'index.html', encoding='utf-8').read()
    if f'data-pret>{lei(pret)}<' not in h or f'<s data-sum>{lei(suma)}</s>' not in h: bad(f'{pk["id"]}: prețurile din pagină nu corespund ({lei(suma)} → {lei(pret)})')
    ok += 1
# 3) oferta: fiecare produs/pachet apare cu prețul corect
of = open('magazin/oferta/index.html', encoding='utf-8').read()
for s, p in P.items():
    if p.get('magazin') == 'lr': continue
    if not re.search(re.escape(f'<td class="cod">{s}</td><td><a href="https://nutrisib.club{p["url"]}">') + r'.*?' + re.escape(f'<strong>{lei(p["pret"])}</strong>'), of): bad(f'oferta: {s} lipsește sau are alt preț')
for pk in cat.get('pachete', []):
    if f'https://nutrisib.club{pk["url"]}' not in of: bad(f'oferta: pachetul {pk["id"]} lipsește')
# 4) linkuri interne
pages = glob.glob('magazin/**/*.html', recursive=True)
for f in pages:
    h = open(f, encoding='utf-8').read()
    for u in re.findall(r'(?:href|src|data-src)="((?:https://nutrisib\.club)?/[^"#?]*)', h):
        path = u.replace('https://nutrisib.club', '').lstrip('/')
        if path == '' : path = 'index.html'
        elif path.endswith('/'): path += 'index.html'
        if not os.path.exists(path): bad(f'{f}: link spart {u}')
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h):
        try: json.loads(m)
        except Exception as e: bad(f'{f}: JSON-LD invalid')
print(f'Verificate: {len(P)} produse ({sum(1 for p in P.values() if p.get("magazin") == "lr")} LR), {len(cat.get("pachete", []))} pachete, {len(pages)} pagini.')
print('ERORI:' if err else 'Nicio eroare.'); [print(' -', e) for e in err[:60]]
sys.exit(1 if err else 0)
