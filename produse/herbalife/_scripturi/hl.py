import re, json, os, csv, sys, time, requests
from concurrent.futures import ThreadPoolExecutor
OUT = os.path.expanduser('~/mnt/produse/herbalife')
CACHE = os.path.expanduser('~/hl_manifest.json')
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36', 'Accept-Language': 'ro-RO,ro;q=0.9'}
S = requests.Session(); S.headers.update(H)
KIND = [('canister', 'ambalaj'), ('prepared-product', 'preparat'), ('lifestyle', 'lifestyle'), ('nutritional-facts', 'tabel-nutritional')]
def pick(im):
    if not im: return None
    return (im.get('desktopImage') or {}).get('_publishUrl') or (im.get('thumbnailImage') or {}).get('_publishUrl')
def page(url):
    for a in range(3):
        try:
            h = S.get(url, timeout=30).text
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
            pd = json.loads(m.group(1))['props']['pageProps']['productDetails']['productData']
            v = pd['variant']; a_ = v.get('aemresponse') or {}
            imgs = [pick(a_.get('defaultImage'))] + [pick(x) for x in a_.get('additionalImages') or []] + [pick(t.get('image')) for t in a_.get('productTabs') or []]
            seen = []; [seen.append(i) for i in imgs if i and i not in seen]
            name = v.get('name'); name = name.get('ro-RO') if isinstance(name, dict) else (name or v.get('productName'))
            return {'slug': url.rstrip('/').split('/')[-1], 'url': url, 'sku': v.get('sku'), 'name': name, 'cat': v.get('category_name'), 'imgs': seen}
        except Exception as e:
            err = e; time.sleep(2)
    return {'url': url, 'error': str(err)}
def manifest():
    if os.path.exists(CACHE): return json.load(open(CACHE))
    sm = S.get('https://www.herbalife.com/ro-ro/products_sitemap.xml', timeout=30).text
    locs = re.findall(r'<loc>([^<]+)</loc>', sm)
    with ThreadPoolExecutor(6) as ex: res = list(ex.map(page, locs))
    json.dump(res, open(CACHE, 'w'), ensure_ascii=False, indent=1); return res
def jobs(res):
    out = []
    for p in res:
        if 'error' in p: continue
        d = os.path.join(OUT, p['slug']); cnt = {}; p['files'] = []
        for u in p['imgs']:
            k = next((lab for key, lab in KIND if key in u), 'imagine')
            cnt[k] = cnt.get(k, 0) + 1
            ext = os.path.splitext(u.split('?')[0])[1].lower() or '.png'
            order = {'ambalaj': '01', 'preparat': '02', 'lifestyle': '03', 'tabel-nutritional': '04'}.get(k, '05')
            fn = f"{order}-{k}{'' if cnt[k]==1 else '-'+str(cnt[k])}{ext}"
            p['files'].append(f"{p['slug']}/{fn}"); out.append((u, os.path.join(d, fn)))
    return out
def dl(j):
    u, f = j
    if os.path.exists(f) and os.path.getsize(f) > 0: return 'skip'
    os.makedirs(os.path.dirname(f), exist_ok=True)
    for a in range(3):
        try:
            r = S.get(u, timeout=60)
            if r.status_code == 200 and r.content:
                open(f + '.part', 'wb').write(r.content); os.replace(f + '.part', f); return 'ok'
            err = r.status_code
        except Exception as e: err = e
        time.sleep(2)
    return f'FAIL {err} {u}'
if __name__ == '__main__':
    res = manifest()
    js = jobs(res); deadline = time.time() + float(sys.argv[1] if len(sys.argv) > 1 else 150)
    st = {}
    with ThreadPoolExecutor(8) as ex:
        futs = []
        for j in js:
            futs.append(ex.submit(lambda j=j: dl(j) if time.time() < deadline else 'later'))
        for f in futs:
            r = f.result(); st[r if not r.startswith('FAIL') else 'fail'] = st.get(r if not r.startswith('FAIL') else 'fail', 0) + 1
            if r.startswith('FAIL'): print(r)
    with open(os.path.join(OUT, 'herbalife-produse-ro.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh, delimiter=';'); w.writerow(['SKU', 'Denumire', 'Categorie', 'Folder', 'Imagini', 'URL produs'])
        for p in sorted([p for p in res if 'error' not in p], key=lambda p: p['name'] or ''):
            w.writerow([p['sku'], p['name'], p['cat'], p['slug'], ' | '.join(x.split('/', 1)[1] for x in p['files']), p['url']])
    print('produse:', len(res), 'erori pagini:', sum('error' in p for p in res), 'fisiere:', len(js), st)
