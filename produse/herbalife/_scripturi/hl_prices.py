import re, json, math, subprocess
skus = {p['sku'].upper(): p for p in json.load(open('hl_manifest.json')) if 'sku' in p}
txt = subprocess.run(['pdftotext','-layout','mnt/nutrisib/produse/herbalife/herbalife-preturi.pdf','-'],capture_output=True,text=True).stdout.splitlines()
N = r'(\d+(?:\.\d{2})?)'
rx = re.compile(r'(?<![\w.])([0-9A-Z]{4})\s{2,}(\S.*?)\s{2,}' + r'\s+'.join([N]*7) + r'(?!\.?\d)')
res = {}
for i, l in enumerate(txt):
    for m in rx.finditer(l):
        c = m.group(1)
        if c in skus: res.setdefault(c, []).append(dict(line=i+1, nume_pdf=m.group(2).strip(), vals=[float(x) for x in m.groups()[2:]]))
# code lines without numbers -> numbers on adjacent line in same column
num7 = re.compile(r'\s+'.join([r'(\d+\.\d{2})']*7))
for c in skus:
    if c in res: continue
    for i, l in enumerate(txt):
        m = re.search(r'(?<![\w.])' + re.escape(c) + r'(?![\w])', l)
        if not m: continue
        for j in (i-1, i+1, i+2):
            if 0 <= j < len(txt):
                for n in num7.finditer(txt[j]):
                    if 0 < n.start() - m.start() < 160:
                        res.setdefault(c, []).append(dict(line=j+1, nume_pdf='(rand vecin)', vals=[float(x) for x in n.groups()]))
r10 = lambda x: int(math.floor(x/10 + 0.5) * 10)
old = json.load(open('hl_prices.json'))
out = {}
for c, v in res.items():
    a = v[0]['vals']; out[c] = dict(vp=a[0], baza=a[1], lista=a[2], p25=a[3], p35=a[4], p42=a[5], p50=a[6], pret=r10(a[3]), nume_pdf=v[0]['nume_pdf'], line=v[0]['line'], n=len(v))
print('gasite', len(out), '/', len(skus), 'lipsa:', [s for s in skus if s not in out])
print('multiple:', {c: o['n'] for c, o in out.items() if o['n'] > 1})
print('diferente fata de metoda 1:', {c: (old[c]['p25'], out[c]['p25']) for c in old if c in out and old[c]['p25'] != out[c]['p25']})
json.dump(out, open('hl_prices.json', 'w'), indent=1, ensure_ascii=False)
for c in sorted(out): o = out[c]; print(f"{c:5} VP {o['vp']:6.2f} 25%={o['p25']:7.2f} -> {o['pret']:4d} | {o['nume_pdf'][:48]:48} | site: {skus[c]['name'][:40]}")
