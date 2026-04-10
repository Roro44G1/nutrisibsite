import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime

# ============================================
#  AGENT NUTRISIB - Restructurare Eleventy
#  Pune acest script in folderul radacina
#  al repo-ului tau (langa index.html)
# ============================================

FOLDER = Path(".").resolve()
OUTPUT = FOLDER / "_eleventy_nou"
TEMPLATES = OUTPUT / "_includes"
CONTINUT = OUTPUT / "pagini"
BLOG_OUT = OUTPUT / "blog"

IGNORA = [
    "footer.html", "success.html", "eval_bia.html", "eval_bio.html",
    "acord_EN.html", "acord_RO.html", "acord_RO1.html",
    "celos - Copie.html", "povestea - Copie.html",
    "cheicaptcha", "components.json"
]

IGNORA_FOLDERE = ["_eleventy_nou", "_site", "node_modules", "admin"]

# ============================================
#  UTILITARE
# ============================================

def titlu_din_html(continut, nume_fisier):
    match = re.search(r'<title[^>]*>(.*?)</title>', continut, re.IGNORECASE | re.DOTALL)
    if match:
        titlu = match.group(1).strip().split("|")[0].strip()
        return titlu
    match = re.search(r'<h1[^>]*>(.*?)</h1>', continut, re.IGNORECASE | re.DOTALL)
    if match:
        return re.sub(r'<[^>]+>', '', match.group(1)).strip()
    return Path(nume_fisier).stem.replace("-", " ").replace("_", " ").title()

def extrage_sectiune(continut, tag_start, tag_end):
    pattern = f'{re.escape(tag_start)}(.*?){re.escape(tag_end)}'
    match = re.search(pattern, continut, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(0)
    return None

def extrage_body(continut):
    match = re.search(r'<body[^>]*>(.*?)</body>', continut, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return continut

def extrage_head(continut):
    match = re.search(r'<head[^>]*>(.*?)</head>', continut, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

def confirma(mesaj, default="d"):
    suffix = " [D/n]: " if default == "d" else " [d/N]: "
    raspuns = input(mesaj + suffix).strip().lower()
    if not raspuns:
        return default == "d"
    return raspuns in ["d", "da", "y", "yes"]

def afiseaza_preview(text, max_linii=15):
    linii = text.strip().split("\n")
    for linie in linii[:max_linii]:
        print("  " + linie)
    if len(linii) > max_linii:
        print(f"  ... (+{len(linii) - max_linii} linii)")

# ============================================
#  PASUL 1 - ANALIZA SITE
# ============================================

def analizeaza_site():
    print("\n" + "="*55)
    print("  PASUL 1 — Analiza structurii site-ului")
    print("="*55)

    fisiere_html = [
        f for f in FOLDER.glob("*.html")
        if f.name not in IGNORA
    ]
    fisiere_blog = []
    folder_blog = FOLDER / "blog"
    if folder_blog.exists():
        fisiere_blog = list(folder_blog.glob("*.html"))

    print(f"\n  Pagini principale gasite:  {len(fisiere_html)}")
    for f in sorted(fisiere_html):
        print(f"    - {f.name}")

    print(f"\n  Articole blog gasite:      {len(fisiere_blog)}")
    for f in sorted(fisiere_blog)[:5]:
        print(f"    - {f.name}")
    if len(fisiere_blog) > 5:
        print(f"    ... si inca {len(fisiere_blog)-5} articole")

    return fisiere_html, fisiere_blog

# ============================================
#  PASUL 2 - EXTRAGE TEMPLATE DIN FISIER MODEL
# ============================================

def alege_fisier_model(fisiere_html):
    print("\n" + "="*55)
    print("  PASUL 2 — Alegere fisier model pentru template")
    print("="*55)
    print("\n  Pe care fisier sa il folosesc ca model pentru")
    print("  a extrage header-ul, meniul si footer-ul?")
    print("\n  Fisiere disponibile:")

    lista = sorted(fisiere_html)
    for i, f in enumerate(lista):
        print(f"    {i+1}. {f.name}")

    while True:
        try:
            alegere = int(input("\n  Numarul fisierului model: ")) - 1
            if 0 <= alegere < len(lista):
                return lista[alegere]
            print("  Numar invalid, incearca din nou.")
        except ValueError:
            print("  Introduceti un numar.")

def extrage_template(fisier_model):
    print(f"\n  Analizez: {fisier_model.name} ...")

    with open(fisier_model, "r", encoding="utf-8", errors="ignore") as f:
        continut = f.read()

    head = extrage_head(continut)
    body = extrage_body(continut)

    # Incearca sa gaseasca nav/header
    nav = extrage_sectiune(body, "<nav", "</nav>")
    header = extrage_sectiune(body, "<header", "</header>")
    footer = extrage_sectiune(body, "<footer", "</footer>")

    print("\n  Am identificat:")
    print(f"    <head>  : {'DA' if head else 'NU'}")
    print(f"    <nav>   : {'DA' if nav else 'NU'}")
    print(f"    <header>: {'DA' if header else 'NU'}")
    print(f"    <footer>: {'DA' if footer else 'NU'}")

    # Construieste template-ul de baza
    template_layout = f"""<!DOCTYPE html>
<html lang="ro">
<head>
{head}
</head>
<body>
"""
    if header:
        template_layout += f"{header}\n"
    if nav:
        template_layout += f"{nav}\n"

    template_layout += """\n<main>
  {{ content }}
</main>
"""
    if footer:
        template_layout += f"\n{footer}\n"

    template_layout += """
</body>
</html>"""

    print("\n  Preview template generat (primele 20 linii):")
    afiseaza_preview(template_layout, 20)

    if confirma("\n  Folosim acest template?"):
        return template_layout, continut
    else:
        print("\n  Ok, poti edita manual template-ul dupa ce agentul termina.")
        return template_layout, continut

# ============================================
#  PASUL 3 - EXTRAGE CONTINUT DIN PAGINI
# ============================================

def extrage_continut_pagina(fisier, continut_model):
    with open(fisier, "r", encoding="utf-8", errors="ignore") as f:
        continut = f.read()

    titlu = titlu_din_html(continut, fisier.name)
    body = extrage_body(continut)

    # Elimina nav, header, footer din body (sunt deja in template)
    nav = extrage_sectiune(body, "<nav", "</nav>")
    header_tag = extrage_sectiune(body, "<header", "</header>")
    footer_tag = extrage_sectiune(body, "<footer", "</footer>")

    continut_curat = body
    if nav:
        continut_curat = continut_curat.replace(nav, "")
    if header_tag:
        continut_curat = continut_curat.replace(header_tag, "")
    if footer_tag:
        continut_curat = continut_curat.replace(footer_tag, "")

    continut_curat = continut_curat.strip()

    return titlu, continut_curat

def proceseaza_pagini(fisiere_html, fisier_model):
    print("\n" + "="*55)
    print("  PASUL 3 — Extragere continut din pagini")
    print("="*55)

    pagini_procesate = []

    for fisier in sorted(fisiere_html):
        if fisier.name == fisier_model.name:
            continue  # sarim peste modelul deja procesat

        print(f"\n  Procesez: {fisier.name}")

        try:
            with open(fisier, "r", encoding="utf-8", errors="ignore") as f:
                continut_model = f.read()

            titlu, continut_curat = extrage_continut_pagina(fisier, continut_model)
            print(f"    Titlu detectat: {titlu}")
            print(f"    Continut extras: {len(continut_curat)} caractere")

            pagini_procesate.append({
                "fisier": fisier,
                "titlu": titlu,
                "continut": continut_curat,
                "slug": fisier.stem
            })
        except Exception as e:
            print(f"    EROARE: {e}")

    print(f"\n  Total pagini procesate: {len(pagini_procesate)}")
    return pagini_procesate

# ============================================
#  PASUL 4 - ARTICOLE NOI DE BLOG
# ============================================

def creeaza_articol_nou():
    print("\n" + "-"*45)
    print("  Articol nou de blog")
    print("-"*45)

    titlu = input("  Titlul articolului: ").strip()
    if not titlu:
        return None

    slug = titlu.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = slug[:50]

    data = datetime.now().strftime("%Y-%m-%d")
    print(f"  Data: {data}")
    print(f"  Slug (nume fisier): {slug}.html")

    descriere = input("  Descriere scurta: ").strip()

    print("  Introdu continutul articolului (HTML).")
    print("  Scrie 'GATA' pe o linie noua cand termini:")
    linii = []
    while True:
        linie = input()
        if linie.strip() == "GATA":
            break
        linii.append(linie)
    continut = "\n".join(linii)

    return {
        "titlu": titlu,
        "slug": slug,
        "data": data,
        "descriere": descriere,
        "continut": continut
    }

def gestioneaza_blog(fisiere_blog):
    print("\n" + "="*55)
    print("  PASUL 4 — Articole de blog")
    print("="*55)
    print(f"\n  Ai {len(fisiere_blog)} articole existente in /blog")

    articole_noi = []

    while confirma("\n  Vrei sa adaugi un articol nou de blog?", default="n"):
        articol = creeaza_articol_nou()
        if articol:
            articole_noi.append(articol)
            print(f"  Articol adaugat: {articol['titlu']}")

    return articole_noi

# ============================================
#  PASUL 5 - GENEREAZA FISIERELE ELEVENTY
# ============================================

def genereaza_fisiere(template_layout, pagini_procesate, articole_noi, fisiere_blog):
    print("\n" + "="*55)
    print("  PASUL 5 — Generare fisiere Eleventy")
    print("="*55)

    # Creeaza structura de foldere
    OUTPUT.mkdir(exist_ok=True)
    TEMPLATES.mkdir(exist_ok=True)
    CONTINUT.mkdir(exist_ok=True)
    BLOG_OUT.mkdir(exist_ok=True)

    # 1. Salveaza template-ul principal
    layout_path = TEMPLATES / "base.html"
    with open(layout_path, "w", encoding="utf-8") as f:
        f.write(template_layout)
    print(f"\n  Template salvat: _includes/base.html")

    # 2. Genereaza paginile
    for pagina in pagini_procesate:
        continut_md = f"""---
layout: base.html
title: "{pagina['titlu']}"
---

{pagina['continut']}
"""
        cale = CONTINUT / f"{pagina['slug']}.html"
        with open(cale, "w", encoding="utf-8") as f:
            f.write(continut_md)
        print(f"  Pagina: pagini/{pagina['slug']}.html")

    # 3. Copiaza articolele existente din blog
    for fisier in fisiere_blog:
        dest = BLOG_OUT / fisier.name
        shutil.copy2(fisier, dest)
    print(f"  Blog: {len(fisiere_blog)} articole copiate")

    # 4. Adauga articolele noi
    for articol in articole_noi:
        continut_articol = f"""---
layout: base.html
title: "{articol['titlu']}"
date: {articol['data']}
description: "{articol['descriere']}"
---

{articol['continut']}
"""
        cale = BLOG_OUT / f"{articol['slug']}.html"
        with open(cale, "w", encoding="utf-8") as f:
            f.write(continut_articol)
        print(f"  Articol nou: blog/{articol['slug']}.html")

    # 5. Genereaza package.json pentru Eleventy
    package_json = {
        "name": "nutrisibsite",
        "version": "1.0.0",
        "scripts": {
            "build": "eleventy",
            "start": "eleventy --serve"
        },
        "devDependencies": {
            "@11ty/eleventy": "^2.0.0"
        }
    }
    with open(OUTPUT / "package.json", "w", encoding="utf-8") as f:
        json.dump(package_json, f, indent=2)
    print("  package.json generat")

    # 6. Genereaza .eleventy.js config
    eleventy_config = """module.exports = function(eleventyConfig) {
  // Copiaza folderul imagini
  eleventyConfig.addPassthroughCopy("imagini");
  // Copiaza CSS-urile
  eleventyConfig.addPassthroughCopy("*.css");
  // Copiaza JS-urile
  eleventyConfig.addPassthroughCopy("*.js");

  return {
    dir: {
      input: ".",
      output: "_site",
      includes: "_includes"
    }
  };
};
"""
    with open(OUTPUT / ".eleventy.js", "w", encoding="utf-8") as f:
        f.write(eleventy_config)
    print("  .eleventy.js generat")

    # 7. Genereaza netlify.toml
    netlify_toml = """[build]
  command = "npm run build"
  publish = "_site"

[context.dev]
  command = "npm run build"
  publish = "_site"
"""
    with open(OUTPUT / "netlify.toml", "w", encoding="utf-8") as f:
        f.write(netlify_toml)
    print("  netlify.toml generat")

    print(f"\n  Toate fisierele sunt in: {OUTPUT}")

# ============================================
#  MAIN
# ============================================

def main():
    print("\n" + "="*55)
    print("  AGENT NUTRISIB — Restructurare pentru Eleventy")
    print("="*55)
    print(f"\n  Folder de lucru: {FOLDER}")
    print("\n  Agentul va:")
    print("  1. Analiza structura site-ului tau")
    print("  2. Extrage template (header, nav, footer)")
    print("  3. Separa continutul fiecarei pagini")
    print("  4. Permite adaugarea de articole noi")
    print("  5. Genera structura completa Eleventy")
    print("\n  IMPORTANT: Nu modifica fisierele originale!")
    print("  Rezultatul va fi in folderul: _eleventy_nou/")

    if not confirma("\n  Continuam?"):
        print("\n  Anulat. La revedere!")
        return

    # Pasul 1 - Analiza
    fisiere_html, fisiere_blog = analizeaza_site()

    if not fisiere_html:
        print("\n  Nu am gasit fisiere HTML. Verifica folderul.")
        input("\nApasa Enter pentru a inchide...")
        return

    # Pasul 2 - Template
    fisier_model = alege_fisier_model(fisiere_html)
    template_layout, _ = extrage_template(fisier_model)

    # Pasul 3 - Pagini
    pagini_procesate = proceseaza_pagini(fisiere_html, fisier_model)

    # Pasul 4 - Blog
    articole_noi = gestioneaza_blog(fisiere_blog)

    # Pasul 5 - Generare
    if confirma("\n  Generam fisierele Eleventy acum?"):
        genereaza_fisiere(template_layout, pagini_procesate, articole_noi, fisiere_blog)

        print("\n" + "="*55)
        print("  GATA! Ce urmează:")
        print("="*55)
        print("\n  1. Verifica folderul _eleventy_nou/")
        print("  2. Corecteaza _includes/base.html daca e nevoie")
        print("  3. Copiaza continutul in repo-ul tau (branch dev)")
        print("  4. Ruleaza: npm install")
        print("  5. Ruleaza: npm run build")
        print("  6. Verifica _site/ si fa push pe GitHub")
        print("\n  Netlify va rula automat 'npm run build' la fiecare deploy.")
    else:
        print("\n  Anulat. Fisierele nu au fost generate.")

    input("\nApasa Enter pentru a inchide...")

if __name__ == "__main__":
    main()
