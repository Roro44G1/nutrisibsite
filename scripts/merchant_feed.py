#!/usr/bin/env python3
"""Fluxuri Google Merchant Center pentru magazinele Herbalife și LR.

Rulare (din rădăcina repo-ului, după magazin_build.py):  python scripts/merchant_feed.py

Scrie două fișiere separate, tab-delimitate, UTF-8:
  magazin/feed/google-merchant-herbalife.tsv   (produse + pachete Herbalife)
  magazin/feed/google-merchant-lr.tsv          (produse LR)

Toate datele vin din paginile generate (JSON-LD + textul taburilor) și din
magazin/catalog.json, ca prețul, titlul și imaginile să fie identice cu pagina.
- Cât timp un magazin e inactiv (config.<magazin>.activ = false), produsele sunt
  „preorder” cu availability_date = DATA_DESCHIDERE; după activare devin „in_stock”.
- Transportul general (25 lei) se setează în contul Merchant Center. Fluxul Herbalife
  suprascrie cu 0 lei doar produsele/pachetele care au singure cel puțin 125 VP.
- Nu se trimite google_product_category (Google o atribuie automat). GTIN-urile vin doar
  din scripts/gtin.json (coduri scanate de pe ambalaje), validate; la pachete se folosește
  GTIN-ul produsului principal. Restul au brand + mpn (codul producătorului).
- Seturile LR „+ cadou” sunt excluse până se decide livrarea cadoului.
- Descrierea = textul scurt de sub titlu + tabul „Prezentare generală”/„Caracteristici”
  (Herbalife) sau „Descriere” (LR; la seturi, descrierea variantei de bază), fără
  linkuri, note de subsol și majuscule integrale.
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://nutrisib.club"
DATA_DESCHIDERE = "2026-11-17T00:00+0200"
OUT_DIR = os.path.join(ROOT, "magazin", "feed")
MAX_IMG_EXTRA = 10

LDJSON_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
SUPERSCRIPT = str.maketrans("", "", "¹²³⁴⁵⁶⁷⁸⁹⁰")


def ld_objects(h):
    for block in LDJSON_RE.findall(h):
        try:
            d = json.loads(block)
        except json.JSONDecodeError:
            continue
        for x in (d if isinstance(d, list) else d.get("@graph", [d])):
            yield x


def text_of(fragment):
    fragment = re.sub(r"<script.*?</script>|<style.*?</style>", " ", fragment, flags=re.S | re.I)
    fragment = re.sub(r"<li[^>]*>", " • ", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def tab_text(h, label):
    """Textul panoului al cărui buton de tab are eticheta dată (ex. „Descriere”)."""
    btn = re.search(r'<button class="mz-tab[^"]*"[^>]*aria-controls="tab-(\d+)"[^>]*>\s*' + re.escape(label) + r"\s*<", h)
    if not btn:
        return ""
    n = int(btn.group(1))
    m = re.search(rf'id="tab-{n}"(.*?)(?=id="tab-{n + 1}"|Descrierea completă a produsului|Descrierea, ingredientele|<footer|$)', h, re.S)
    if not m:
        return ""
    frag = m.group(1)
    frag = frag[frag.find(">") + 1:]          # restul tag-ului de deschidere al panoului
    last_open = frag.rfind("<")
    if last_open > frag.rfind(">"):           # tag-ul următorului element, tăiat la jumătate
        frag = frag[:last_open]
    return text_of(frag)


def short_text(h):
    """Textul scurt de sub titlul produsului (p.mz-p-sub la Herbalife, div.mz-p-short la LR)."""
    m = (re.search(r'<p class="mz-p-sub">(.*?)</p>', h, re.S)
         or re.search(r'<div class="mz-p-short">(.*?)</div>\s*<div class="mz-p-specs"', h, re.S))
    return text_of(m.group(1)) if m else ""


def variant_page_url(h):
    """Pentru seturi: pagina variantei unde LR are descrierea completă."""
    m = re.search(r'Descrierea completă a produsului este pe pagina variantei <a href="([^"]+)"', h)
    return m.group(1) if m else None


def caps_to_sentence(t):
    """Rulări de ≥3 cuvinte scrise integral cu majuscule → majusculă doar la început."""
    def fix(m):
        s = m.group(0).lower()
        return s[0].upper() + s[1:]
    return re.sub(r"\b(?:[A-ZĂÂÎȘȚŞŢ0-9&'\-]{2,}\s+){2,}[A-ZĂÂÎȘȚŞŢ0-9&'\-]{2,}\b", fix, t)


def clean_desc(t, limit=5000):
    t = t.translate(SUPERSCRIPT)
    t = re.sub(r",?\s*(?:https?://|www\.)\S+", "", t)   # fără linkuri în descriere (regula Merchant)
    t = re.sub(r"(?<=\w)\*+|\*+(?=\w)|\s\*+\s", " ", t)
    t = caps_to_sentence(t)
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)
    t = re.sub(r"\s+", " ", t).strip(" •")
    if len(t) > limit:
        cut = t[:limit]
        end = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
        t = cut[: end + 1] if end > limit * 0.6 else cut.rsplit(" ", 1)[0]
    return t


def fmt_price(p):
    return f"{float(p):.2f} RON"


def page(url):
    path = os.path.join(ROOT, url.strip("/"), "index.html")
    return open(path, encoding="utf-8").read()


def product_ld(h):
    prod = next((x for x in ld_objects(h) if x.get("@type") == "Product"), None)
    crumbs = next((x for x in ld_objects(h) if x.get("@type") == "BreadcrumbList"), None)
    names = [i.get("name", "") for i in crumbs["itemListElement"]] if crumbs else []
    return prod, names


def gtin_valid(code):
    """Returnează GTIN-ul în forma de 8/12/13 cifre dacă e valid, altfel None (cifra de control + prefixe interzise de Google)."""
    c = re.sub(r"\s", "", str(code))
    if not re.fullmatch(r"\d{8}|\d{12}|\d{13}|\d{14}", c):
        return None
    digits = [int(x) for x in c]
    total = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(digits[:-1])))
    if (10 - total % 10) % 10 != digits[-1]:
        return None
    if len(c) == 14 and c.startswith("0"):
        c = c[1:]
    g13 = c if len(c) == 13 else ("0" + c if len(c) == 12 else c)
    if len(g13) == 13 and (g13[0] == "2" or g13[:2] in ("02", "04", "05", "98", "99")):
        return None
    return c


def load_gtins():
    path = os.path.join(ROOT, "scripts", "gtin.json")
    if not os.path.exists(path):
        return {}, []
    data = json.load(open(path, encoding="utf-8"))
    ok, bad = {}, []
    for magazin in ("herbalife", "lr"):
        for sku, code in data.get(magazin, {}).items():
            v = gtin_valid(code)
            if v:
                ok[(magazin, sku)] = v
            else:
                bad.append(f"{magazin} {sku}: {code}")
    return ok, bad


def join_parts(*parts):
    out = []
    for p in parts:
        p = (p or "").strip()
        if p and not any(p[:80] in o for o in out):
            out.append(p)
    return " ".join(out)


def build_row(item_id, prod, crumbs, desc, brand_prefix, activ, shipping_free, is_bundle=False, title=None, gtin=""):
    name = prod["name"].replace(" · ", ", ").strip()
    if title is None:
        title = name if brand_prefix.lower() in name.lower() else f"{brand_prefix} {name}"
    imgs = prod.get("image") or []
    imgs = [imgs] if isinstance(imgs, str) else imgs
    offer = prod["offers"]
    row = {
        "id": item_id,
        "title": title[:150],
        "description": desc,
        "link": offer["url"],
        "image_link": imgs[0] if imgs else "",
        "additional_image_link": imgs[1 : 1 + MAX_IMG_EXTRA],
        "availability": "in_stock" if activ else "preorder",
        "availability_date": "" if activ else DATA_DESCHIDERE,
        "price": fmt_price(offer["price"]),
        "brand": prod.get("brand", {}).get("name", ""),
        "gtin": gtin or "",
        "mpn": "" if is_bundle else (prod.get("mpn") or prod.get("sku") or ""),
        "condition": "new",
        "product_type": " > ".join(c for c in crumbs[1:-1] if c),
        "is_bundle": "yes" if is_bundle else "",
        "shipping(country:price)": "RO:0.00 RON" if shipping_free else "",
    }
    return row


COLUMNS = ["id", "title", "description", "link", "image_link", "availability", "availability_date",
           "price", "brand", "gtin", "mpn", "condition", "product_type", "is_bundle", "shipping(country:price)"]


def write_tsv(path, rows, with_bundle, with_shipping):
    cols = [c for c in COLUMNS if (with_bundle or c != "is_bundle") and (with_shipping or not c.startswith("shipping"))]
    n_extra = max((len(r["additional_image_link"]) for r in rows), default=0)
    header = cols[:5] + ["additional_image_link"] * n_extra + cols[5:]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(header) + "\n")
        for r in rows:
            extra = r["additional_image_link"] + [""] * (n_extra - len(r["additional_image_link"]))
            vals = [r[c] for c in cols[:5]] + extra + [r[c] for c in cols[5:]]
            for v in vals:
                if "\t" in v or "\n" in v or v.startswith('"'):
                    raise ValueError(f"valoare invalidă pentru TSV în {r['id']}: {v[:40]!r}")
            fh.write("\t".join(vals) + "\n")


def main():
    cat = json.load(open(os.path.join(ROOT, "magazin", "catalog.json"), encoding="utf-8"))
    cfg = cat["config"]
    prag = cfg.get("prag_vp", 125)
    vp = {p["sku"]: p.get("vp", 0) for p in cat["produse"]}
    hl_activ = cfg.get("herbalife", {}).get("activ", False)
    lr_activ = cfg.get("lr", {}).get("activ", False)

    gtins, gtin_bad = load_gtins()
    hl, lr, excluse, fara_text = [], [], [], []
    for p in cat["produse"]:
        h = page(p["url"])
        prod, crumbs = product_ld(h)
        if float(prod["offers"]["price"]) != float(p["pret"]):
            raise SystemExit(f"Preț diferit pagină/catalog: {p['sku']}")
        if p["magazin"] == "herbalife":
            desc = join_parts(short_text(h), tab_text(h, "Prezentare generală"))
            feat = tab_text(h, "Caracteristici")
            if feat and len(desc) + len(feat) < 4800:
                desc = desc + " Caracteristici: " + feat
            hl.append(build_row(f"HL-{p['sku']}", prod, crumbs, clean_desc(desc), "Herbalife",
                                hl_activ, p.get("vp", 0) >= prag, gtin=gtins.get(("herbalife", p["sku"]))))
        else:
            # Seturile „+ cadou” promit un produs gratuit nedecis încă (vezi magazin-lr-decizii): nu intră în flux.
            if "cadou" in (p["denumire"] + " " + p["varianta"]).lower():
                excluse.append(f"LR-{p['sku']} ({p['denumire']}, {p['varianta']})")
                continue
            descriere = tab_text(h, "Descriere")
            if not descriere and variant_page_url(h):
                descriere = tab_text(page(variant_page_url(h)), "Descriere")
            if not descriere:
                descriere = tab_text(h, "Ingrediente")[:1500]
            desc = join_parts(short_text(h), descriere)
            if not desc:  # pagina nu are niciun text descriptiv: doar datele afișate pe ea
                desc = f"{p['denumire']}, LR Health & Beauty, cod {p['sku']}."
                fara_text.append(f"LR-{p['sku']} ({p['denumire']})")
            lr.append(build_row(f"LR-{p['sku']}", prod, crumbs, clean_desc(desc), "LR", lr_activ, False,
                                gtin=gtins.get(("lr", p["sku"]))))

    for k in cat["pachete"]:
        h = page(k["url"])
        prod, crumbs = product_ld(h)
        lead = re.sub(r"\s*Alege varianta fiecărui produs\.?", "", short_text(h)).strip()  # instrucțiune de interfață
        desc = clean_desc(lead or prod.get("description", ""))
        pk_vp = sum(vp.get(s, 0) for s in k.get("implicit", []))
        nume = k["nume"]
        title = (nume.replace("Pachet", "Pachet Herbalife", 1) if nume.lower().startswith("pachet")
                 else f"Pachet Herbalife {nume}")
        hl.append(build_row(f"HL-{k['id']}", prod, crumbs, desc, "Herbalife", hl_activ, pk_vp >= prag,
                            is_bundle=True, title=title,
                            gtin=gtins.get(("herbalife", (k.get("implicit") or [""])[0]))))  # produsul principal

    write_tsv(os.path.join(OUT_DIR, "google-merchant-herbalife.tsv"), hl, with_bundle=True, with_shipping=True)
    write_tsv(os.path.join(OUT_DIR, "google-merchant-lr.tsv"), lr, with_bundle=False, with_shipping=False)
    print(f"Herbalife: {len(hl)} rânduri ({sum(1 for r in hl if r['is_bundle'])} pachete), "
          f"{'in_stock' if hl_activ else 'preorder'}; transport 0 lei pe {sum(1 for r in hl if r['shipping(country:price)'])}")
    print(f"LR: {len(lr)} rânduri, {'in_stock' if lr_activ else 'preorder'}")
    for e in excluse:
        print("   exclus:", e)
    for e in fara_text:
        print("   fără text descriptiv pe pagină:", e)
    n_g = sum(1 for r in hl + lr if r["gtin"])
    print(f"GTIN: {n_g} rânduri cu cod din scripts/gtin.json")
    for e in gtin_bad:
        print("   GTIN INVALID, ignorat:", e)


if __name__ == "__main__":
    sys.exit(main())
