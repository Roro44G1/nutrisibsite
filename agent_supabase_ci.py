import os
import re
import time
from pathlib import Path
from bs4 import BeautifulSoup, Comment

# ============================================
#  AGENT INDEXARE SUPABASE — GITHUB ACTIONS
#  Citeste variabilele din environment (secrets)
#  Nu modifica manual — configureaza in GitHub Secrets
# ============================================

FOLDER = Path(__file__).parent.resolve()

# Citeste din GitHub Secrets (environment variables)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

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
        print(f"  Eroare {fisier.name}: {e}")
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

def main():
    print("\n" + "="*55)
    print("  AGENT INDEXARE SUPABASE — GitHub Actions")
    print("="*55)

    # Verifica variabilele
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("  EROARE: SUPABASE_URL sau SUPABASE_KEY lipsesc din Secrets!")
        exit(1)
    if not ANTHROPIC_KEY:
        print("  EROARE: ANTHROPIC_API_KEY lipseste din Secrets!")
        exit(1)

    from supabase import create_client

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Scaneaza fisierele
    fisiere = []
    for fisier in sorted(FOLDER.rglob("*.html")):
        parti = fisier.relative_to(FOLDER).parts
        if any(parte in IGNORA_FOLDERE for parte in parti):
            continue
        if fisier.name in IGNORA_FISIERE:
            continue
        fisiere.append(fisier)

    print(f"\n  Fisiere gasite: {len(fisiere)}")

    # Sterge indexul vechi
    print("  Sterg indexul vechi...")
    try:
        supabase.table("nutrisib_context").delete().neq("id", 0).execute()
        print("  Index sters.")
    except Exception as e:
        print(f"  Eroare stergere: {e}")

    total_fragmente = 0
    erori = 0

    for i, fisier in enumerate(fisiere, 1):
        url = construieste_url(fisier)
        titlu, text = extrage_text(fisier)

        if not text or len(text) < 50:
            continue

        fragmente = imparte_in_fragmente(text)
        print(f"  [{i}/{len(fisiere)}] {url} → {len(fragmente)} fragmente")

        # Sterge URL existent
        try:
            supabase.table("nutrisib_context").delete().eq("url", url).execute()
        except:
            pass

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
                print(f"    Eroare insert: {e}")
                erori += 1
            time.sleep(DELAY)

    print("\n" + "="*55)
    print(f"  GATA! Fragmente indexate: {total_fragmente} | Erori: {erori}")
    print("="*55)

if __name__ == "__main__":
    main()
