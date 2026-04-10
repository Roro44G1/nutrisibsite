from pathlib import Path

FOLDER = Path(__file__).parent.resolve()

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

fisiere = []
for f in sorted(FOLDER.rglob("*.html")):
    parti = f.relative_to(FOLDER).parts
    if any(p in IGNORA_FOLDERE for p in parti):
        continue
    if f.name in IGNORA_FISIERE:
        continue
    fisiere.append(f)

print(f"\nTotal fisiere gasite: {len(fisiere)}\n")

# Grupeaza pe foldere
foldere = {}
for f in fisiere:
    parti = f.relative_to(FOLDER).parts
    folder = parti[0] if len(parti) > 1 else "/"
    if folder not in foldere:
        foldere[folder] = []
    foldere[folder].append(f.name)

for folder, fisiere_folder in sorted(foldere.items()):
    print(f"  [{folder}] — {len(fisiere_folder)} fisiere")
    for nume in fisiere_folder[:5]:
        print(f"    - {nume}")
    if len(fisiere_folder) > 5:
        print(f"    ... si inca {len(fisiere_folder)-5}")

input("\nApasa Enter pentru a inchide...")
