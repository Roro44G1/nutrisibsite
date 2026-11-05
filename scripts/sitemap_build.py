#!/usr/bin/env python3
"""Generează sitemap-urile nutrisib.club din fișierele HTML din repo.

Rulare (din rădăcina repo-ului):  python scripts/sitemap_build.py

O pagină intră în sitemap doar dacă:
  - are <link rel="canonical"> care indică exact adresa ei curată
    (litere mici, fără .html, așa cum o servește Netlify: blog/x.html -> /blog/x);
  - nu are meta robots „noindex”;
  - nu cade sub o regulă X-Robots-Tag: noindex din netlify.toml.

Paginile din magazin/ au propriul sitemap (sitemap-magazin.xml, generat de
scripts/magazin_build.py); aici doar îl includem în indexul sitemap.xml.

lastmod = data ultimului commit care a modificat fișierul, ignorând commit-urile
marcate „[seo]” (modificări doar de metadate, nu de conținut).
Scriptul afișează la final paginile fără canonical corect, ca să fie reparate.
"""
import os, re, subprocess, sys, datetime
from xml.sax.saxutils import escape

SITE = "https://nutrisib.club"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()
SKIP_DIRS = ("magazin/", "netlify/", "node_modules/", "scripts/", "patches/", ".git/")
GROUPS = [("blog/", "sitemap-blog.xml"), ("micronutrienti/", "sitemap-micronutrienti.xml"), ("", "sitemap-main.xml")]

CANON_RE = re.compile(r'<link\b[^>]*\brel\s*=\s*["\']canonical["\'][^>]*>', re.I)
HREF_RE = re.compile(r'\bhref\s*=\s*["\']([^"\']+)["\']', re.I)
ROBOTS_RE = re.compile(r'<meta\b[^>]*\bname\s*=\s*["\'](?:robots|googlebot)["\'][^>]*>', re.I)
CONTENT_RE = re.compile(r'\bcontent\s*=\s*["\']([^"\']*)["\']', re.I)


def git(*args):
    try:
        return subprocess.run(["git", "-C", ROOT, "-c", "core.quotepath=false", *args],
                              capture_output=True, text=True, encoding="utf-8").stdout.strip()
    except FileNotFoundError:
        return ""


def html_files():
    tracked = git("ls-files", "*.html", "*.htm")
    if tracked:
        return tracked.splitlines()
    out = []
    for d, _, fs in os.walk(ROOT):
        for f in fs:
            if f.lower().endswith((".html", ".htm")):
                out.append(os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/"))
    return out


def clean_url(f):
    p = "/" + f
    if p.lower().endswith("/index.html"):
        p = p[: -len("index.html")]
    else:
        p = re.sub(r"\.html?$", "", p, flags=re.I)
    return SITE + p.lower()


def noindex_patterns():
    """Căile marcate X-Robots-Tag: noindex în netlify.toml."""
    try:
        txt = open(os.path.join(ROOT, "netlify.toml"), encoding="utf-8").read()
    except OSError:
        return []
    pats = []
    for block in re.split(r"\[\[headers\]\]", txt)[1:]:
        m = re.search(r'for\s*=\s*"([^"]+)"', block)
        if m and re.search(r'X-Robots-Tag\s*=\s*"[^"]*noindex', block, re.I):
            pats.append(m.group(1).lower())
    return pats


def blocked(path, pats):
    for p in pats:
        if p.endswith("/*"):
            if path.startswith(p[:-1]) or path == p[:-2]:
                return True
        elif path == p:
            return True
    return False


def lastmod(f):
    d = git("log", "-1", "--format=%cs", "--invert-grep", "--fixed-strings", "--grep=[seo]", "--", f)
    return d or git("log", "-1", "--format=%cs", "--", f) or TODAY


def write_urlset(name, entries):
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, lm in entries:
        xml.append(f"  <url><loc>{escape(url)}</loc><lastmod>{lm}</lastmod></url>")
    xml.append("</urlset>")
    with open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(xml) + "\n")


def main():
    if git("rev-parse", "--is-shallow-repository") == "true":
        print("ATENȚIE: clonă shallow — datele lastmod pot fi greșite (rulează git fetch --unshallow).")
    pats = noindex_patterns()
    groups = {name: [] for _, name in GROUPS}
    fara_canonical, canonical_alt, noindex = [], [], 0
    for f in sorted(html_files()):
        if f.startswith(SKIP_DIRS) or not os.path.exists(os.path.join(ROOT, f)):
            continue
        url = clean_url(f)
        path = url[len(SITE):]
        if blocked(path, pats):
            continue
        if not re.fullmatch(r"[a-z0-9_\-./]+", path):
            continue  # nume cu spații / diacritice: nu sunt pagini publice
        head = open(os.path.join(ROOT, f), encoding="utf-8", errors="replace").read(60000)
        rob = " ".join(CONTENT_RE.search(t).group(1) for t in ROBOTS_RE.findall(head) if CONTENT_RE.search(t))
        if "noindex" in rob.lower():
            noindex += 1
            continue
        tags = CANON_RE.findall(head)
        if not tags:
            fara_canonical.append(f)
            continue
        href = HREF_RE.search(tags[0])
        if not href or href.group(1) != url:
            canonical_alt.append(f"{f} -> {href.group(1) if href else '?'}")
            continue
        for prefix, name in GROUPS:
            if f.startswith(prefix):
                groups[name].append((url, lastmod(f)))
                break

    groups["sitemap-main.xml"].sort(key=lambda e: (e[0] != SITE + "/", e[0]))
    index = []
    for _, name in reversed(GROUPS):
        entries = groups[name]
        if name != "sitemap-main.xml":
            entries.sort(key=lambda e: (not e[0].endswith("/"), e[0]))
        write_urlset(name, entries)
        index.append((name, max((lm for _, lm in entries), default=TODAY)))
        print(f"{name}: {len(entries)} pagini")

    mag = os.path.join(ROOT, "sitemap-magazin.xml")
    if os.path.exists(mag):
        dates = re.findall(r"<lastmod>([^<]+)</lastmod>", open(mag, encoding="utf-8").read())
        index.append(("sitemap-magazin.xml", max(dates) if dates else TODAY))
        print(f"sitemap-magazin.xml: {open(mag, encoding='utf-8').read().count('<url>')} pagini (generat de magazin_build.py)")

    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for name, lm in index:
        xml.append(f"  <sitemap><loc>{SITE}/{name}</loc><lastmod>{lm}</lastmod></sitemap>")
    xml.append("</sitemapindex>")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(xml) + "\n")

    print(f"Excluse cu noindex în pagină: {noindex}")
    if fara_canonical:
        print(f"\nFără <link rel=\"canonical\"> ({len(fara_canonical)}) — nu intră în sitemap:")
        for x in fara_canonical:
            print("  ", x)
    if canonical_alt:
        print(f"\nCanonical către altă adresă ({len(canonical_alt)}) — nu intră în sitemap:")
        for x in canonical_alt:
            print("  ", x)


if __name__ == "__main__":
    sys.exit(main())
