import os
import re
from pathlib import Path
from datetime import datetime

# ============================================
#  CONFIGURARE - modifică doar aici dacă vrei
# ============================================

# Folderul cu fișierele HTML (. = același folder ca scriptul)
FOLDER = "."

# Fișiere de ignorat (nu li se adaugă frontmatter)
IGNORA = [
    "footer.html",
    "success.html",
    
]

# ============================================

def are_frontmatter(continut):
    """Verifică dacă fișierul are deja frontmatter"""
    return continut.strip().startswith("---")

def extrage_titlu(continut, nume_fisier):
    """Încearcă să extragă titlul din tag-ul <title> sau <h1>"""
    match = re.search(r'<title[^>]*>(.*?)</title>', continut, re.IGNORECASE | re.DOTALL)
    if match:
        titlu = match.group(1).strip()
        # Elimină pipe și ce urmează (ex. "Povestea | NutriSib" -> "Povestea")
        titlu = titlu.split("|")[0].strip()
        return titlu
    match = re.search(r'<h1[^>]*>(.*?)</h1>', continut, re.IGNORECASE | re.DOTALL)
    if match:
        return re.sub(r'<[^>]+>', '', match.group(1)).strip()
    # Fallback: numele fișierului
    return Path(nume_fisier).stem.replace("-", " ").replace("_", " ").title()

def adauga_frontmatter(cale_fisier):
    """Adaugă frontmatter la un fișier HTML"""
    with open(cale_fisier, "r", encoding="utf-8", errors="ignore") as f:
        continut = f.read()

    if are_frontmatter(continut):
        return "sarit"  # Are deja frontmatter

    titlu = extrage_titlu(continut, cale_fisier.name)
    data_azi = datetime.now().strftime("%Y-%m-%d")

    frontmatter = f"""---
title: "{titlu}"
date: {data_azi}
description: ""
thumbnail: ""
---

"""
    continut_nou = frontmatter + continut

    with open(cale_fisier, "w", encoding="utf-8") as f:
        f.write(continut_nou)

    return "ok"

# ============================================
#  RULARE
# ============================================

def main():
    folder = Path(FOLDER).resolve()
    print(f"\n📁 Procesez folderul: {folder}")
    print("=" * 50)

    fisiere_html = [f for f in folder.glob("*.html") if f.name not in IGNORA]

    if not fisiere_html:
        print("❌ Nu am găsit fișiere HTML în acest folder.")
        input("\nApasă Enter pentru a închide...")
        return

    ok = 0
    sarite = 0
    erori = 0

    for fisier in sorted(fisiere_html):
        try:
            rezultat = adauga_frontmatter(fisier)
            if rezultat == "ok":
                print(f"  ✅ {fisier.name}")
                ok += 1
            elif rezultat == "sarit":
                print(f"  ⏭️  {fisier.name} (are deja frontmatter)")
                sarite += 1
        except Exception as e:
            print(f"  ❌ {fisier.name} - Eroare: {e}")
            erori += 1

    print("=" * 50)
    print(f"\n✅ Procesate: {ok} fișiere")
    print(f"⏭️  Sărite (aveau deja): {sarite} fișiere")
    if erori:
        print(f"❌ Erori: {erori} fișiere")

    print("\n💡 Verifică fișierele și completează câmpurile 'description' și 'thumbnail' unde vrei.")
    input("\nApasă Enter pentru a închide...")

if __name__ == "__main__":
    main()
