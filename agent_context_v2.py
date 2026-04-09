import os
import re
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup, Comment

# ============================================
#  GENERATOR CONTEXT NUTRISIB v2
#  Rezumate inteligente ~200 cuvinte per pagina
#  Necesita: pip install anthropic beautifulsoup4
# ============================================

FOLDER = Path(__file__).parent.resolve()
OUTPUT_FILE = FOLDER / "netlify" / "functions" / "context_site.js"

IGNORA_FOLDERE = {
    "en", "admin", "_site", "node_modules",
    "_eleventy_nou", ".git", "logo", "imagini",
    "cards", "patches", "netlify", "wellness",
    "video", "nutritrack", "essent"
}

IGNORA_FISIERE = {
    "footer.html", "success.html", 
    "acord_EN.html", "acord_RO.html",
    "disclaimer_EN.html", "disclaimer_RO.html",
}

# Max caractere text brut trimis la rezumat
MAX_TEXT_BRUT = 6000
# Delay intre requesturi API
DELAY = 0.5

# API KEY
API_KEY = "sk-ant-CHEIA_TA_AICI"

# ============================================
#  EXTRAGERE TEXT DIN HTML
# ============================================

def extrage_text(fisier):
    try:
        with open(fisier, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")

        for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
            c.extract()
        for tag in soup.find_all(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        titlu = ""
        title_tag = soup.find("title")
        if title_tag:
            titlu = title_tag.get_text().split("|")[0].strip()

        descriere = ""
        meta = soup.find("meta", attrs={"name": "description"})
        if meta:
            descriere = meta.get("content", "").strip()

        main = soup.find("main") or soup.find("article") or soup.find("body")
        text = main.get_text(separator=" ", strip=True) if main else ""
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) > MAX_TEXT_BRUT:
            text = text[:MAX_TEXT_BRUT]

        return titlu, descriere, text

    except Exception as e:
        print(f"    Eroare extragere {fisier.name}: {e}")
        return "", "", ""

# ============================================
#  REZUMAT INTELIGENT CU CLAUDE
# ============================================

def genereaza_rezumat(titlu, descriere, text, url, client):
    if not text or len(text) < 50:
        return descriere or ""

    prompt = f"""Ești un asistent care rezumă pagini web pentru un chatbot de nutriție (NutriSib).

Pagina: {titlu}
URL: {url}
Descriere: {descriere}

Conținut:
{text}

Generează un rezumat în română de maxim 200 de cuvinte care:
- Acoperă toate informațiile importante din pagină
- Menționează servicii, produse, prețuri dacă există
- Menționează module, lecții, structura dacă e un curs
- Este util pentru a răspunde întrebărilor clienților
- Nu folosește formatare Markdown
- Scrie natural, concis, informativ

Rezumat:"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f"    Eroare rezumat: {e}")
        # Fallback: primele 200 cuvinte din text
        cuvinte = text.split()[:200]
        return " ".join(cuvinte)

# ============================================
#  SCANARE FISIERE
# ============================================

def scaneaza_site():
    fisiere = []

    for fisier in sorted(FOLDER.rglob("*.html")):
        parti = fisier.relative_to(FOLDER).parts
        if any(parte in IGNORA_FOLDERE for parte in parti):
            continue
        if fisier.name in IGNORA_FISIERE:
            continue
        fisiere.append(fisier)

    return fisiere

def construieste_url(fisier):
    relativ = fisier.relative_to(FOLDER)
    url = "/" + str(relativ).replace("\\", "/")
    if url.endswith("/index.html"):
        url = url[:-10] or "/"
    elif url == "/index.html":
        url = "/"
    return url

# ============================================
#  MAIN
# ============================================

def main():
    print("\n" + "="*55)
    print("  GENERATOR CONTEXT v2 — Rezumate inteligente")
    print("="*55)
    print(f"\n  Folder: {FOLDER}")

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("\n  EROARE: pip install beautifulsoup4")
        input("\nApasa Enter...")
        return

    try:
        import anthropic
    except ImportError:
        print("\n  EROARE: pip install anthropic")
        input("\nApasa Enter...")
        return

    api_key = API_KEY
    if "CHEIA_TA" in api_key:
        api_key = input("\n  Introdu API key-ul Anthropic: ").strip()

    import anthropic as ant
    client = ant.Anthropic(api_key=api_key)

    fisiere = scaneaza_site()
    print(f"\n  Fisiere gasite: {len(fisiere)}")
    print(f"  Cost estimat: ~${len(fisiere) * 0.001:.2f} (Haiku)")

    if input("\n  Continui? (d/n): ").strip().lower() not in ["d", "da", "y"]:
        print("  Anulat.")
        input("\nApasa Enter...")
        return

    pagini = []
    erori = 0

    for i, fisier in enumerate(fisiere, 1):
        url = construieste_url(fisier)
        print(f"\n  [{i}/{len(fisiere)}] {url}")

        titlu, descriere, text = extrage_text(fisier)

        if not text:
            print(f"    -> Sarit (fara continut)")
            continue

        print(f"    Text brut: {len(text)} caractere → rezumez...")
        rezumat = genereaza_rezumat(titlu, descriere, text, url, client)
        cuvinte = len(rezumat.split())
        print(f"    Rezumat: {cuvinte} cuvinte ✓")

        pagini.append({
            "url": url,
            "titlu": titlu,
            "rezumat": rezumat
        })

        time.sleep(DELAY)

    # Construieste contextul final
    context_text = "INFORMATII COMPLETE SITE NUTRISIB:\n\n"
    for pagina in pagini:
        context_text += f"--- {pagina['titlu'] or pagina['url']} ({pagina['url']}) ---\n"
        context_text += f"{pagina['rezumat']}\n\n"

    # Statistici
    size_kb = len(context_text) / 1024
    print(f"\n  Pagini procesate: {len(pagini)}")
    print(f"  Dimensiune context: {size_kb:.1f} KB")
    print(f"  Erori: {erori}")

    if size_kb > 200:
        print(f"\n  ATENTIE: Contextul e inca mare ({size_kb:.0f}KB).")
        print(f"  Considera sa reduci MAX_TEXT_BRUT sau sa ignori mai multe foldere.")

    # Genereaza JS
    context_escaped = json.dumps(context_text)
    js_content = f"""// ============================================
// CONTEXT SITE NUTRISIB - GENERAT AUTOMAT
// Nu edita manual - regenereaza cu agent_context_v2.py
// Generat: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}
// Pagini indexate: {len(pagini)}
// Dimensiune: {size_kb:.1f} KB
// ============================================

const SITE_CONTEXT = {context_escaped};

module.exports = {{ SITE_CONTEXT }};
"""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"\n  Salvat: netlify/functions/context_site.js")
    print(f"\n  Pasi urmatori:")
    print(f"  1. Verifica fisierul generat")
    print(f"  2. Commit + push pe GitHub (branch dev)")
    print(f"  3. Netlify redeploy automat")

    input("\n  Apasa Enter pentru a inchide...")

if __name__ == "__main__":
    main()
