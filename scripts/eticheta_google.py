"""Eticheta Google (Google Tag Manager, container GTM-K8J357CV, creat din Merchant Center) pe toate paginile.

Modul de consimțământ (decizia lui Radu, 17.11.2026): eticheta se încarcă pe orice pagină, cu consimțământ
implicit „refuzat”. Dacă vizitatorul a ales deja în bannerul de cookie-uri (cookies.js, cookie-ul
`nutrisib_consent`), alegerea lui e aplicată înainte de încărcarea etichetei:
  analytics  → analytics_storage
  marketing  → ad_storage, ad_user_data, ad_personalization
La o alegere nouă în banner, cookies.js trimite `gtag('consent', 'update', …)`.

Folosire:
  python3 scripts/eticheta_google.py            # inserează / actualizează fragmentul în toate paginile HTML
  python3 scripts/eticheta_google.py --verifica # doar raportează paginile fără fragment sau cu fragment vechi

Fragmentul stă imediat după <head>, între markerii INCEPUT și SFARSIT, deci rularea repetată îl înlocuiește,
nu îl dublează. Generatorul magazinului (scripts/magazin_comun.py) îl include din acest fișier (GOOGLE_TAG).
"""
import os
import re
import subprocess
import sys

GTM_ID = "GTM-K8J357CV"
INCEPUT = "<!-- NutriSib: eticheta Google -->"
SFARSIT = "<!-- /NutriSib: eticheta Google -->"

GOOGLE_TAG = f"""{INCEPUT}
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  (function(){{var c=null;try{{var m=document.cookie.match(/(?:^|; )nutrisib_consent=([^;]+)/);if(m)c=JSON.parse(decodeURIComponent(m[1]));}}catch(e){{}}
  var a=c&&c.analytics?'granted':'denied',k=c&&c.marketing?'granted':'denied';
  gtag('consent','default',{{analytics_storage:a,ad_storage:k,ad_user_data:k,ad_personalization:k}});
  gtag('set','ads_data_redaction',true);}})();
</script>
<script async src="https://www.googletagmanager.com/gtm.js?id={GTM_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
</script>
{SFARSIT}"""

# Fișiere care nu sunt pagini publice ale site-ului.
EXCLUSE_PREFIX = ("produse/", "scripts/", "netlify/", "node_modules/", "admin/")
HEAD = re.compile(r"<head(?:\s[^>]*)?>", re.I)
BLOC = re.compile(re.escape(INCEPUT) + r".*?" + re.escape(SFARSIT), re.S)


def pagini(root):
    out = subprocess.run(["git", "-C", root, "-c", "core.quotepath=off", "ls-files", "*.html", "*.htm"],
                         capture_output=True, text=True, check=True).stdout.split("\n")
    return [f for f in out if f and not f.startswith(EXCLUSE_PREFIX)]


def aplica(text):
    """Întoarce (text_nou, stare): stare ∈ {'adaugat', 'actualizat', 'neschimbat', 'fara_head'}."""
    if INCEPUT in text:
        nou = BLOC.sub(lambda _: GOOGLE_TAG, text, count=1)
        return nou, ("neschimbat" if nou == text else "actualizat")
    m = HEAD.search(text)  # primul <head> e cel real; alte apariții sunt în șiruri JS / exemple
    if not m:
        return text, "fara_head"
    return text[:m.end()] + "\n" + GOOGLE_TAG + text[m.end():], "adaugat"


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    doar_verifica = "--verifica" in sys.argv
    stari = {}
    for rel in pagini(root):
        cale = os.path.join(root, rel)
        with open(cale, encoding="utf-8", newline="") as fh:
            text = fh.read()
        nou, stare = aplica(text)
        stari.setdefault(stare, []).append(rel)
        if not doar_verifica and nou != text:
            with open(cale, "w", encoding="utf-8", newline="") as fh:
                fh.write(nou)
    for stare in ("adaugat", "actualizat", "neschimbat", "fara_head"):
        lst = stari.get(stare, [])
        eticheta = {"adaugat": "de adăugat" if doar_verifica else "adăugat",
                    "actualizat": "de actualizat" if doar_verifica else "actualizat",
                    "neschimbat": "la zi", "fara_head": "fără <head> (sărite)"}[stare]
        print(f"{eticheta}: {len(lst)}")
        if stare == "fara_head" and lst:
            print("   " + ", ".join(lst))
    if doar_verifica and (stari.get("adaugat") or stari.get("actualizat")):
        sys.exit(1)


if __name__ == "__main__":
    main()
