#!/usr/bin/env python3
"""Șabloane și constante comune magazinului NutriSib (Herbalife, LR, …).
Importat de scripts/magazin_build.py (Herbalife) și scripts/magazin_lr.py (LR)."""
import os, json, html, datetime, markdown
SITE = 'https://nutrisib.club'
TODAY = datetime.date.today().isoformat()
PRAG_VP, TRANSPORT = 125, 25
VANZATOR = 'PASCU RADU VASILE ÎNTREPRINDERE INDIVIDUALĂ'
REGCOM = 'F32/667/2017'   # format nou ONRC (14 caractere) doar după ce e emis oficial
E = lambda s: html.escape(str(s or ''), quote=True)

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
    <a href="/magazin/cont/">Contul meu</a>
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
      <p style="margin:0 0 .4rem"><strong>Magazinul NutriSib</strong> este operat de {VANZATOR}<br>CUI 38416337 · Nr. Reg. Com. {REGCOM}</p>
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

SB_SCRIPTS = ('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js"></script>\n'
              '<script src="/magazin/assets/sb-config.js"></script>\n<script src="/magazin/assets/cont.js" defer></script>\n')
