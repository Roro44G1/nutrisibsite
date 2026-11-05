import json, os, re
from markdownify import markdownify as md
OUT = os.path.expanduser('~/mnt/produse/herbalife')
man = {p['slug']: p for p in json.load(open(os.path.expanduser('~/hl_manifest.json')))}
raw = json.load(open(os.path.expanduser('~/hl_raw.json')))
def h2m(x):
    if isinstance(x, dict): x = x.get('html') or x.get('ro-RO') or ''
    if not x: return ''
    x = re.sub(r'(?:<br\s*/?>\s*)+', '</p><p>', x)
    x = re.sub(r'<u>', '<strong>', x); x = re.sub(r'</u>', '</strong>', x)
    t = md(x, heading_style='ATX', bullets='-', strong_em_symbol='*')
    t = t.replace('\xa0', ' ')
    lines = []
    for ln in t.split('\n'):
        st = ln.strip()
        lines.append(ln.rstrip() if re.match(r'^(-|\d+\.)\s', st) and ln.startswith(' ') and len(ln)-len(ln.lstrip()) < 8 else st)
    t = '\n'.join(lines); t = re.sub(r'\*\*\s*\*\*', '', t); t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip()
def yq(s): return '"' + str(s or '').replace('\\', '\\\\').replace('"', '\\"') + '"'
files_by_slug = {}
for line in open(os.path.join(OUT, 'herbalife-produse-ro.csv'), encoding='utf-8-sig').read().splitlines()[1:]:
    c = line.split(';'); files_by_slug[c[3]] = [f.strip() for f in c[4].split('|') if f.strip()]
n = 0
for slug, v in raw.items():
    a = v.get('aemresponse') or {}; p = man[slug]
    name = v['name'].get('ro-RO') if isinstance(v.get('name'), dict) else v.get('name')
    attrs = a.get('attributes') or {}
    flavor = ', '.join((attrs.get('flavor') or {}).get('values') or [])
    size = ', '.join(sum([(attrs[k] or {}).get('values') or [] for k in attrs if k.startswith('size')], []))
    imgs = files_by_slug.get(slug, [])
    L = ['---', f'sku: {yq(v.get("sku"))}', f'denumire: {yq(name)}', f'aroma: {yq(flavor)}', f'marime: {yq(size)}',
         f'categorie: {yq(v.get("category_name"))}', f'meta_descriere: {yq(a.get("metaDescription"))}',
         f'url_sursa: {yq(p["url"])}', 'imagini:'] + [f'  - {i}' for i in imgs] + ['---', '', f'# {name}', '']
    meta = ' · '.join(x for x in [flavor and f'Aromă: {flavor}', size and f'Mărime: {size}', f'Cod: {v.get("sku")}'] if x)
    L += [f'*{meta}*', '']
    if imgs: L += [f'![{name}]({imgs[0]})', '']
    sd = h2m(v.get('description'))
    if sd: L += [sd, '']
    for t in a.get('productTabs') or []:
        L += [f'## {t.get("title")}', '']
        for k in ['description', 'descriptionLeft', 'descriptionRight']:
            s = h2m(t.get(k))
            if s: L += [s, '']
        for it in t.get('accordion') or []:
            L += [f'### {it.get("title","")}', '', h2m(it.get('description') or it.get('content')), '']
        s = h2m(t.get('ingredients'))
        if s: L += ['### Ingrediente', '', s, '']
        s = h2m(t.get('allergenInfo'))
        if s: L += ['### Informații despre alergeni', '', s, '']
        if t.get('image') and t.get('productTabIndex') != 'pTabOverview' and any('tabel-nutritional' in i for i in imgs):
            tn = next(i for i in imgs if 'tabel-nutritional' in i)
            L += ['### Informații nutriționale', '', f'![Informații nutriționale – {name}]({tn})', '']
    s = h2m(a.get('skuDisclaimer'))
    if s: L += ['---', '', f'*{s.strip("*")}*', '']
    open(os.path.join(OUT, slug, 'produs.md'), 'w', encoding='utf-8').write('\n'.join(L).rstrip() + '\n'); n += 1
print('scrise', n)
