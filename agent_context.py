import os
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup, Comment

# ============================================
#  GENERATOR CONTEXT SITE NUTRISIB
#  Parcurge toate folderele si extrage textul
#  Necesita: pip install beautifulsoup4
# ============================================

FOLDER = Path(__file__).parent.resolve()
OUTPUT_FILE = FOLDER / "netlify" / "functions" / "context_site.js"

# Foldere de ignorat
IGNORA_FOLDERE = {
    "en", "admin", "_site", "node_modules",
    "_eleventy_nou", ".git", "logo", "imagini"
}

# Fisiere de ignorat
IGNORA_FISIERE = {
    "footer.html", "success.html", "acord_EN.html",
    "acord_RO.html", "acord_RO1.html",
    "celos - Copie.html", "povestea - Copie.html",
}

# Lungime maxima text per pagina (caractere)
MAX_TEXT_PER_PAGINA = 3000

# ============================================

def extrage_text_din_html(fisier):
    """Extrage textul vizibil dintr-un fisier HTML"""
    try:
        with open(fisier, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")

        # Elimina comentarii
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()

        # Elimina script, style, nav, footer, header (nu contin continut util)
        for tag in soup.find_all(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        # Extrage titlul
        titlu = ""
        title_tag = soup.find("title")
        if title_tag:
            titlu = title_tag.get_text().split("|")[0].strip()

        # Extrage meta description
        descriere = ""
        meta = soup.find("meta", attrs={"name": "description"})
        if meta:
            descriere = meta.get("content", "").strip()

        # Extrage textul principal
        main = soup.find("main") or soup.find("article") or soup.find("body")
        if main:
            text = main.get_text(separator=" ", strip=True)
        else:
            text = soup.get_text(separator=" ", strip=True)

        # Curata spatiile multiple
        text = re.sub(r'\s+', ' ', text).strip()

        # Trunchiaza daca e prea lung
        if len(text) > MAX_TEXT_PER_PAGINA:
            text = text[:MAX_TEXT_PER_PAGINA] + "..."

        return titlu, descriere, text

    except Exception as e:
        print(f"    Eroare la {fisier.name}: {e}")
        return "", "", ""


def construieste_url(fisier, folder_radacina):
    """Construieste URL-ul relativ al fisierului"""
    relativ = fisier.relative_to(folder_radacina)
    url = "/" + str(relativ).replace("\\", "/")
    # Simplifica index.html
    if url.endswith("/index.html"):
        url = url[:-10]
    elif url == "/index.html":
        url = "/"
    return url


def scaneaza_site():
    """Scaneaza recursiv toate fisierele HTML din site"""
    pagini = []

    for fisier in sorted(FOLDER.rglob("*.html")):
        # Verifica daca e intr-un folder ignorat
        parti_path = fisier.relative_to(FOLDER).parts
        if any(parte in IGNORA_FOLDERE for parte in parti_path):
            continue
        if fisier.name in IGNORA_FISIERE:
            continue

        titlu, descriere, text = extrage_text_din_html(fisier)

        if not text:
            continue

        url = construieste_url(fisier, FOLDER)

        pagini.append({
            "url": url,
            "titlu": titlu,
            "descriere": descriere,
            "text": text
        })

        print(f"  ✓ {url} ({len(text)} caractere)")

    return pagini


def genereaza_js(pagini):
    """Genereaza fisierul JS cu contextul site-ului"""

    # Construieste contextul ca text structurat
    context_text = "INFORMATII COMPLETE SITE NUTRISIB:\n\n"

    for pagina in pagini:
        context_text += f"--- PAGINA: {pagina['titlu'] or pagina['url']} ---\n"
        context_text += f"URL: {pagina['url']}\n"
        if pagina['descriere']:
            context_text += f"Descriere: {pagina['descriere']}\n"
        context_text += f"Continut: {pagina['text']}\n\n"

    # Escape pentru JS
    context_escaped = json.dumps(context_text)

    js_content = f"""// ============================================
// CONTEXT SITE NUTRISIB - GENERAT AUTOMAT
// Nu edita manual - regenereaza cu agent_context.py
// Generat: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}
// Pagini indexate: {len(pagini)}
// ============================================

const SITE_CONTEXT = {context_escaped};

module.exports = {{ SITE_CONTEXT }};
"""
    return js_content, len(context_text)


def main():
    print("\n" + "="*55)
    print("  GENERATOR CONTEXT SITE NUTRISIB")
    print("="*55)
    print(f"\n  Folder: {FOLDER}")
    print("\n  Scanez toate paginile HTML...\n")

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("  EROARE: pip install beautifulsoup4")
        input("\n  Apasa Enter...")
        return

    pagini = scaneaza_site()

    print(f"\n  Total pagini indexate: {len(pagini)}")

    js_content, lungime_context = genereaza_js(pagini)

    # Creeaza folderul daca nu exista
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"\n  Context generat: {lungime_context:,} caractere")
    print(f"  Salvat in: netlify/functions/context_site.js")
    print("\n  Acum actualizeaza claude-proxy.js sa foloseasca acest context.")
    print("  (fisierul claude-proxy.js actualizat e in acelasi folder)")

    input("\n  Apasa Enter pentru a inchide...")


if __name__ == "__main__":
    main()
