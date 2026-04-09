import os
from pathlib import Path

# ============================================
#  CONFIGURARE
# ============================================

# Folderul cu fisierele HTML (. = acelasi folder ca scriptul)
FOLDER = "."

# ============================================

def sterge_frontmatter(cale_fisier):
    """Sterge frontmatter-ul --- ... --- de la inceputul fisierului"""
    with open(cale_fisier, "r", encoding="utf-8", errors="ignore") as f:
        continut = f.read()

    # Verifica daca incepe cu ---
    if not continut.strip().startswith("---"):
        return "sarit"

    linii = continut.split("\n")
    
    # Gaseste primul --- (linia 0)
    # Gaseste al doilea --- (sfarsitul frontmatter)
    sfarsit_frontmatter = None
    for i in range(1, len(linii)):
        if linii[i].strip() == "---":
            sfarsit_frontmatter = i
            break

    if sfarsit_frontmatter is None:
        return "eroare"  # Nu am gasit al doilea ---

    # Sterge frontmatter-ul si liniile goale de dupa
    continut_nou = "\n".join(linii[sfarsit_frontmatter + 1:]).lstrip("\n")

    with open(cale_fisier, "w", encoding="utf-8") as f:
        f.write(continut_nou)

    return "ok"

def main():
    folder = Path(FOLDER).resolve()
    print(f"\n Curat frontmatter din: {folder}")
    print("=" * 50)

    # Cauta HTML in folder si subfoldere
    fisiere_html = list(folder.rglob("*.html"))

    if not fisiere_html:
        print(" Nu am gasit fisiere HTML.")
        input("\nApasa Enter pentru a inchide...")
        return

    ok = 0
    sarite = 0
    erori = 0

    for fisier in sorted(fisiere_html):
        try:
            rezultat = sterge_frontmatter(fisier)
            if rezultat == "ok":
                print(f"  OK  {fisier.name}")
                ok += 1
            elif rezultat == "sarit":
                print(f"  --  {fisier.name} (fara frontmatter, sarit)")
                sarite += 1
            elif rezultat == "eroare":
                print(f"  !!  {fisier.name} (frontmatter incomplet?)")
                erori += 1
        except Exception as e:
            print(f"  ERR {fisier.name} - {e}")
            erori += 1

    print("=" * 50)
    print(f"\n Curatate: {ok} fisiere")
    print(f"-- Sarite:  {sarite} fisiere (nu aveau frontmatter)")
    if erori:
        print(f"!! Erori:   {erori} fisiere - verifica manual")

    print("\n Gata! Verifica site-ul in browser.")
    input("\nApasa Enter pentru a inchide...")

if __name__ == "__main__":
    main()
