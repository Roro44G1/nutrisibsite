import os
import re
import time
import json
from pathlib import Path
from datetime import datetime, timezone
from bs4 import BeautifulSoup, Comment

# ============================================
#  AGENT INDEXARE INCREMENTALA SUPABASE
#  Indexeaza DOAR fisierele modificate recent
#  Necesita: py -m pip install anthropic beautifulsoup4 supabase
# ============================================

FOLDER = Path(__file__).parent.resolve()

# ── Configurare ──
SUPABASE_URL = "https://cwdbejilkbgdolywnozi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3ZGJlamlsa2JnZG9seXdub3ppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU4MTUyMDIsImV4cCI6MjA5MTM5MTIwMn0.-HW2XAyYh9wkZde2zOpXQ9G-ogCLllfuB_sKzrO_h8I"
ANTHROPIC_KEY = "sk-ant-CHEIA_TA_AICI"

# Fisier care tine minte ultima indexare
ULTIMA_INDEXARE_FILE = FOLDER / ".ultima_indexare.json"

IGNORA_FOLDERE = {
    "en", "admin", "_site", "node_modules",
    ".git", "logo", "imagini",
    "cards", "patches", "nutritrack"
}

IGNORA_FISIERE = {
    "footer.html", "success.html", "acord_EN.html",
    "acord_RO.html", "acord_RO1.html",
    "disclaimer_EN.html", "disclaimer_RO.html",
}

MAX_FRAGMENT = 1500
DELAY = 0.3

# ============================================
#  GESTIONARE ULTIMA INDEXARE
# ============================================

def citeste_ultima_indexare():
    """Citeste timestamp-ul ultimei indexari"""
    try:
        if ULTIMA_INDEXARE_FILE.exists():
            with open(ULTIMA_INDEXARE_FILE, "r") as f:
                data = json.load(f)
                return datetime.fromisoformat(data["ultima_indexare"])
    except:
        pass
    return None

def salveaza_ultima_indexare():
    """Salveaza timestamp-ul curent ca ultima indexare"""
    with open(ULTIMA_INDEXARE_FILE, "w") as f:
        json.dump({
            "ultima_indexare": datetime.now().isoformat(),
            "folder": str(FOLDER)
        }, f)

# ============================================
#  EXTRAGERE TEXT
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
        main = soup.find("main") or soup.find("article") or soup.find("body")
        text = main.get_text(separator=" ", strip=True) if main else ""
        text = re.sub(r'\s+', ' ', text).strip()
        return titlu, text
    except Exception as e:
        print(f"    Eroare: {e}")
        return "", ""

def imparte_in_fragmente(text, max_len=MAX_FRAGMENT):
    if len(text) <= max_len:
        return [text]
    fragmente = []
    propozitii = re.split(r'(?<=[.!?])\s+', text)
    fragment_curent = ""
    for prop in propozitii:
        if len(fragment_curent) + len(prop) < max_len:
            fragment_curent += " " + prop
        else:
            if fragment_curent:
                fragmente.append(fragment_curent.strip())
            fragment_curent = prop
    if fragment_curent:
        fragmente.append(fragment_curent.strip())
    return fragmente

def construieste_url(fisier):
    relativ = fisier.relative_to(FOLDER)
    url = "/" + str(relativ).replace("\\", "/")
    if url.endswith("/index.html"):
        url = url[:-10] or "/"
    elif url == "/index.html":
        url = "/"
    return url

def genereaza_embedding(text):
    import hashlib
    hash_bytes = hashlib.sha512(text.encode()).digest()
    vector = []
    for i in range(1536):
        byte_idx = i % 64
        val = (hash_bytes[byte_idx] - 128) / 128.0
        val = val * (1 + (i % 10) * 0.01)
        vector.append(round(val, 6))
    return vector

# ============================================
#  MAIN
# ============================================

def main():
    print("\n" + "="*55)
    print("  AGENT INDEXARE INCREMENTALA — NUTRISIB")
    print("="*55)
    print(f"\n  Folder: {FOLDER}")

    try:
        from supabase import create_client
    except ImportError:
        print("\n  EROARE: py -m pip install supabase beautifulsoup4")
        input("\nApasa Enter...")
        return

    api_key = ANTHROPIC_KEY
    if "CHEIA_TA" in api_key:
        api_key = input("\n  Introdu API key-ul Anthropic: ").strip()

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Citeste ultima indexare
    ultima_indexare = citeste_ultima_indexare()

    print("\n  Mod de indexare:")
    print("  1. Doar fisierele modificate de la ultima indexare")
    print("  2. Reindexeaza TOT de la zero")
    mod = input("\n  Alegere (1/2): ").strip()

    if mod == "2":
        print("\n  Sterg indexul complet...")
        try:
            supabase.table("nutrisib_context").delete().neq("id", 0).execute()
            print("  Index sters.")
        except Exception as e:
            print(f"  Eroare: {e}")
        ultima_indexare = None

    # Scaneaza fisierele
    toate_fisierele = []
    for fisier in sorted(FOLDER.rglob("*.html")):
        parti = fisier.relative_to(FOLDER).parts
        if any(parte in IGNORA_FOLDERE for parte in parti):
            continue
        if fisier.name in IGNORA_FISIERE:
            continue
        toate_fisierele.append(fisier)

    # Filtreaza fisierele modificate
    if ultima_indexare and mod == "1":
        fisiere_de_indexat = []
        for fisier in toate_fisierele:
            modificat_la = datetime.fromtimestamp(fisier.stat().st_mtime)
            if modificat_la > ultima_indexare:
                fisiere_de_indexat.append(fisier)

        print(f"\n  Ultima indexare: {ultima_indexare.strftime('%d.%m.%Y %H:%M')}")
        print(f"  Fisiere modificate: {len(fisiere_de_indexat)} din {len(toate_fisierele)}")

        if len(fisiere_de_indexat) == 0:
            print("\n  Niciun fisier modificat de la ultima indexare!")
            print("  Totul e la zi. 🙂")
            salveaza_ultima_indexare()
            input("\nApasa Enter...")
            return

        print("\n  Fisiere de reindexat:")
        for f in fisiere_de_indexat:
            print(f"    - {construieste_url(f)}")
    else:
        fisiere_de_indexat = toate_fisierele
        print(f"\n  Total fisiere de indexat: {len(fisiere_de_indexat)}")

    if input("\n  Continui? (d/n): ").strip().lower() not in ["d", "da", "y"]:
        print("  Anulat.")
        input("\nApasa Enter...")
        return

    total_fragmente = 0
    erori = 0

    for i, fisier in enumerate(fisiere_de_indexat, 1):
        url = construieste_url(fisier)
        titlu, text = extrage_text(fisier)

        if not text or len(text) < 50:
            continue

        fragmente = imparte_in_fragmente(text)
        print(f"\n  [{i}/{len(fisiere_de_indexat)}] {url} → {len(fragmente)} fragmente")

        # Sterge fragmentele vechi pentru acest URL
        try:
            supabase.table("nutrisib_context").delete().eq("url", url).execute()
        except:
            pass

        # Indexeaza fragmentele noi
        for fragment in fragmente:
            embedding = genereaza_embedding(fragment)
            try:
                supabase.table("nutrisib_context").insert({
                    "url": url,
                    "titlu": titlu,
                    "continut": fragment,
                    "embedding": embedding
                }).execute()
                total_fragmente += 1
            except Exception as e:
                print(f"    Eroare: {e}")
                erori += 1
            time.sleep(DELAY)

        print(f"    Indexat ✓")

    # Salveaza timestamp-ul indexarii
    salveaza_ultima_indexare()

    print("\n" + "="*55)
    print(f"  GATA!")
    print(f"  Fragmente indexate: {total_fragmente}")
    if erori:
        print(f"  Erori: {erori}")
    print(f"  Urmatoarea indexare incrementala va procesa")
    print(f"  doar fisierele modificate dupa acum.")
    print("="*55)

    input("\n  Apasa Enter pentru a inchide...")

if __name__ == "__main__":
    main()
