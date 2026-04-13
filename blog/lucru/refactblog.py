#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================
  NUTRISIB — Script refactorizare batch articole blog
  Versiunea 1.0 · 2026 · dr.ing. Radu Pascu
=============================================================
  Utilizare:
    python refactorizare_nutrisib.py

  Configurare (editează secțiunea CONFIG de mai jos):
    - API_KEY      : cheia Anthropic sk-ant-...
    - INPUT_DIR    : folderul cu fișierele HTML originale
    - OUTPUT_DIR   : folderul unde se salvează rezultatele
    - MODEL        : modelul Claude (implicit Haiku 4.5 — rapid + ieftin)
    - CONCURRENCY  : câte fișiere procesează în paralel (implicit 3)
    - SKIP_EXISTING: True = sare peste fișierele deja procesate

  Structura output:
    output/
      ✓ articol1.html   ← refactorizat
      ✓ articol2.html
      refactorizare_log.txt  ← log complet cu costuri
=============================================================
"""

import os
import sys
import time
import json
import re
import logging
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("❌ Lipsește librăria 'anthropic'. Instalează cu: pip install anthropic")
    sys.exit(1)

# =============================================================
#  CONFIG — editează aici
# =============================================================

API_KEY       = "cheia api"
INPUT_DIR     = r"D:\_site-uri\nutrisib\blog\lucru"      # folderul cu HTML originale
OUTPUT_DIR    = r"D:\_site-uri\nutrisib\blog\gata"  # output
MODEL         = "claude-haiku-4-5-20251001"        # Haiku 4.5 — rapid + ieftin
MAX_TOKENS    = 20000                              # suficient pentru orice articol
CONCURRENCY   = 2                                  # fișiere paralel
DELAY_BETWEEN = 0.5                                # secunde între batch-uri
SKIP_EXISTING = True                               # sare peste fișiere deja în output
STYLE_THRESHOLD  = 3 * 1024                        # 3KB — strip selectiv style
SCRIPT_THRESHOLD = 2 * 1024                        # 2KB — strip selectiv script

# =============================================================
#  SYSTEM PROMPT
# =============================================================

SYSTEM_PROMPT = """Ești un procesor tehnic de fișiere HTML pentru site-ul nutrisib.club.

SARCINA TA: Convertești complet structura și stilul unui articol de blog vechi la standardul vizual NutriSib definit de celos.css.

NU generezi conținut nou. NU schimbi textul, imaginile, tabelele sau listele originale.
Returnează DOAR codul HTML complet de la <!DOCTYPE html> până la </html>, fără explicații, fără markdown, fără backtick-uri.

STRUCTURA EXACTĂ PE CARE O PRODUCI:

<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[titlul original]</title>
    [toate meta tags originale: description, keywords, og:*, author — NEATINSE]
    <link rel="stylesheet" href="../celos.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Lora:ital,wght@0,400..700;1,400..700&family=Montserrat:wght@700;800;900&display=swap" rel="stylesheet">
    <style>
        .nav-bar { width: 100%; box-sizing: border-box; }
        /* Pastreaza DOAR clasele cu prefix unic ale articolului (ex: .zwp-, .ztabs-) */
        /* Elimina: body{}, header{}, .container{}, .section-wrapper{}, section{}, main{} */
        /* Inlocuieste variabile locale: #0A2463 cu var(--color-navy), #3E92CC cu var(--color-brand-medium), #1f2937 cu var(--color-text-dark), #4b5563 cu var(--color-text-light), #f8f9fa/#f3f4f6 cu var(--color-pearl), #e5e7eb cu var(--color-border), #C5A021 cu var(--color-gold) */
    </style>
</head>
<body>
<div class="container-main">

    <header class="nav-bar">
        <a href="../index.html" class="nav-brand"><img src="https://nutrisib.club/logo/logo_navy_pearl.png" alt="Sigla Nutrisib" class="logo-image" onerror="this.style.display='none'"></a>
        <div class="nav-links">
            <a href="../index.html">Acasa</a>
            <a href="../index.html#povestea">Povestea</a>
            <a href="../index.html#metoda">Metoda</a>
            <a href="../blog/index.html" class="active">Blog</a>
            <a href="../contact.html">Contact</a>
        </div>
        <button class="mobile-menu-btn" onclick="const nav=document.querySelector('.nav-links');nav.style.display=(nav.style.display==='flex'?'none':'flex')">☰</button>
    </header>

    <div class="hero-card">
        <h1>[titlul principal al articolului — din h1 sau header original]</h1>
        <p>[subtitlul sau descrierea — din p descriptiv din header sau meta description]</p>
    </div>

    <div class="art-card" id="[slug-sectiune-1]">
        <div class="section-anchor-header">
            <h2>[titlul primei sectiuni — din h3 sau h2 original]</h2>
            <a href="#" class="back-top">↑ Sus</a>
        </div>
        [continut original NEATINS: paragrafe, liste, tabele, imagini, h4, h5]
    </div>

    [... cate art-card cate sectiuni are articolul original ...]

    <div id="footer-placeholder"></div>
</div>
<script>fetch('https://nutrisib.club/footer.html').then(r=>r.text()).then(data=>{const c=document.getElementById('footer-placeholder');if(c)c.innerHTML=data;}).catch(err=>console.error('Footer error:',err));</script>
<script src="https://nutrisib.club/script_protect.js" defer></script>
</body>
</html>

REGULI DE CONVERSIE:

R1 — WRAPPER: Inveleste tot body-ul in <div class="container-main">. Elimina orice <div class="container"> sau wrapper propriu.

R2 — NAV: Inlocuieste orice header/nav/meniu cu nav-ul standard de mai sus.

R3 — HERO CARD: Converteste <header> cu gradient (titlu+subtitlu) in <div class="hero-card">. Extrage h1 si primul p descriptiv. Elimina header-ul original.

R4 — SECTIUNI: Fiecare <div class="section-wrapper"><section> sau <section> devine:
<div class="art-card" id="[slug-din-titlu]">
  <div class="section-anchor-header"><h2>[titlul sectiunii]</h2><a href="#" class="back-top">↑ Sus</a></div>
  [continut NEATINS]
</div>
Elimina: <div class="section-wrapper">, <section>, <main>, orice wrapper de sectiune propriu.

R5 — TITLURI: h3 titlu de sectiune devine h2 in section-anchor-header. h4 si h5 raman NEATINSE in interiorul art-card.

R6 — CSS: Inlocuieste link-urile CSS cu celos.css + Google Fonts. In <style> intern elimina clasele globale. Pastreaza DOAR clasele cu prefix unic ale articolului.

R7 — FOOTER: Elimina orice <footer> hardcodat. Adauga footer-placeholder si scripturile standard. Elimina scripturi inline de protectie (contextmenu, keydown, F12).

R8 — CONTINUT NEATINS: Fiecare paragraf, lista, tabel, imagine — 100% neatins.

Returnează DOAR HTML complet, fără niciun text sau explicație înainte sau după."""

# =============================================================
#  STRIP SELECTIV CSS + JS
# =============================================================

def strip_selective(html: str):
    """
    Scoate blocurile <style> mari (>3KB) și <script> inline mari (>2KB).
    Blocurile mici rămân la Claude: R6/R7 le procesează.
    Returnează (html_stripped, styles[], scripts[])
    """
    styles = []
    scripts = []

    def replace_style(m):
        block = m.group(0)
        if len(block) > STYLE_THRESHOLD:
            idx = len(styles)
            styles.append(block)
            return f"<!--STYLE_PH_{idx}-->"
        return block  # mic → rămâne la Claude

    def replace_script(m):
        block = m.group(0)
        if re.search(r'src\s*=', block, re.I):
            return block  # extern → rămâne la Claude (R7 îl elimină)
        if len(block) > SCRIPT_THRESHOLD:
            idx = len(scripts)
            scripts.append(block)
            return f"<!--SCRIPT_PH_{idx}-->"
        return block  # mic → rămâne la Claude

    stripped = re.sub(r'<style[\s\S]*?</style>', replace_style, html, flags=re.I)
    stripped = re.sub(r'<script[\s\S]*?</script>', replace_script, stripped, flags=re.I)
    return stripped, styles, scripts


def reinject_selective(html: str, styles: list, scripts: list) -> str:
    """Reinjectează blocurile mari la pozițiile lor originale."""
    result = html
    for i, s in enumerate(styles):
        result = result.replace(f"<!--STYLE_PH_{i}-->", s)
    for i, s in enumerate(scripts):
        result = result.replace(f"<!--SCRIPT_PH_{i}-->", s)
    # Curăță placeholdere rămase (Claude le-a eliminat intenționat — correct)
    result = re.sub(r'<!--STYLE_PH_\d+-->', '', result)
    result = re.sub(r'<!--SCRIPT_PH_\d+-->', '', result)
    return result

# =============================================================
#  PROCESARE UN FIȘIER
# =============================================================

def process_file(client: anthropic.Anthropic, filepath: Path, output_dir: Path, stats: dict, lock: threading.Lock) -> dict:
    name = filepath.name
    result = {"file": name, "status": "error", "tokens_in": 0, "tokens_out": 0, "cost": 0.0, "error": ""}

    try:
        html_original = filepath.read_text(encoding='utf-8')
        size_kb = len(html_original) / 1024

        # Strip selectiv
        stripped, styles, scripts = strip_selective(html_original)
        stripped_kb = len(stripped) / 1024

        placeholder_note = ""
        if styles or scripts:
            placeholder_note = (
                f"\n\nIMPORTANT: Placeholder-ele <!--STYLE_PH_N--> si <!--SCRIPT_PH_N--> "
                f"reprezinta blocuri CSS/JS mari extrase local — pastreaza-le EXACT in pozitia lor din output."
            )

        # Apel API
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Procesează tehnic fișierul HTML. Fisier: {name}{placeholder_note}\n\n{stripped}"
            }]
        )

        tokens_in  = message.usage.input_tokens
        tokens_out = message.usage.output_tokens

        # Cost estimativ Haiku 4.5: $0.80/M input, $4.00/M output
        cost = (tokens_in / 1_000_000 * 0.80) + (tokens_out / 1_000_000 * 4.00)

        # Extrage text răspuns
        raw = "".join(b.text for b in message.content if hasattr(b, 'text')).strip()
        # Curăță eventuale markdown fences
        raw = re.sub(r'^```html\s*', '', raw, flags=re.I)
        raw = re.sub(r'\s*```$', '', raw)
        raw = raw.strip()

        if len(raw) < 200:
            raise ValueError(f"Răspuns prea scurt ({len(raw)} chars). stop_reason={message.stop_reason}")

        # Reinjectează blocurile mari
        final_html = reinject_selective(raw, styles, scripts)

        # Salvează
        out_path = output_dir / name
        out_path.write_text(final_html, encoding='utf-8')

        result.update({
            "status": "ok",
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost": cost,
            "size_in_kb": round(size_kb, 1),
            "size_stripped_kb": round(stripped_kb, 1),
            "size_out_kb": round(len(final_html) / 1024, 1),
        })

        with lock:
            stats["done"] += 1
            stats["total_cost"] += cost
            stats["total_tokens_in"] += tokens_in
            stats["total_tokens_out"] += tokens_out

        print(f"  ✓  {name:<40} {size_kb:>5.1f}KB → {stripped_kb:>5.1f}KB stripped  |  {tokens_in}+{tokens_out} tok  |  ${cost:.4f}")

    except Exception as e:
        result["error"] = str(e)
        with lock:
            stats["errors"] += 1
        print(f"  ✗  {name:<40} EROARE: {e}")

    return result

# =============================================================
#  MAIN
# =============================================================

def main():
    print("=" * 65)
    print("  NUTRISIB — Refactorizare batch articole blog")
    print(f"  Model: {MODEL}  |  Concurență: {CONCURRENCY}")
    print("=" * 65)

    # Validări
    if "PUNE_CHEIA_TA_AICI" in API_KEY:
        print("\n❌ Configurează API_KEY în secțiunea CONFIG din script!")
        sys.exit(1)

    input_path  = Path(INPUT_DIR)
    output_path = Path(OUTPUT_DIR)

    if not input_path.exists():
        print(f"\n❌ Folderul INPUT nu există: {INPUT_DIR}")
        sys.exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    # Colectează fișierele HTML
    all_files = sorted(input_path.glob("*.html"))
    if not all_files:
        print(f"\n❌ Niciun fișier .html găsit în: {INPUT_DIR}")
        sys.exit(1)

    # Filtrează fișierele deja procesate
    if SKIP_EXISTING:
        files = [f for f in all_files if not (output_path / f.name).exists()]
        skipped = len(all_files) - len(files)
        if skipped:
            print(f"\n  ⏭  {skipped} fișiere deja procesate — sărite (SKIP_EXISTING=True)")
    else:
        files = all_files

    if not files:
        print("\n✅ Toate fișierele sunt deja procesate!")
        sys.exit(0)

    print(f"\n  📂 Input:   {INPUT_DIR}")
    print(f"  📁 Output:  {OUTPUT_DIR}")
    print(f"  📄 Fișiere de procesat: {len(files)}")
    print(f"  💰 Cost estimat: ${len(files) * 0.03:.2f} – ${len(files) * 0.08:.2f}\n")
    print("-" * 65)

    # Configurare logging
    log_path = output_path / "refactorizare_log.json"
    client = anthropic.Anthropic(api_key=API_KEY)

    stats = {"done": 0, "errors": 0, "total_cost": 0.0, "total_tokens_in": 0, "total_tokens_out": 0}
    lock  = threading.Lock()
    results = []
    start_time = time.time()

    # Procesare paralelă
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = {
            executor.submit(process_file, client, f, output_path, stats, lock): f
            for f in files
        }
        for future in as_completed(futures):
            results.append(future.result())
            # Delay mic între completări pentru rate limit
            time.sleep(DELAY_BETWEEN)

    elapsed = time.time() - start_time

    # Raport final
    print("\n" + "=" * 65)
    print(f"  ✅ Gata: {stats['done']} reușite  |  ✗ {stats['errors']} erori")
    print(f"  ⏱  Timp total: {elapsed:.1f}s  ({elapsed/len(files):.1f}s/fișier)")
    print(f"  🔢 Tokens: {stats['total_tokens_in']:,} input + {stats['total_tokens_out']:,} output")
    print(f"  💰 Cost total: ${stats['total_cost']:.4f}")
    print("=" * 65)

    if stats["errors"] > 0:
        print("\n  ⚠️  Fișiere cu erori:")
        for r in results:
            if r["status"] == "error":
                print(f"     ✗ {r['file']}: {r['error']}")

    # Salvează log JSON
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "total_files": len(files),
        "done": stats["done"],
        "errors": stats["errors"],
        "elapsed_seconds": round(elapsed, 1),
        "total_cost_usd": round(stats["total_cost"], 4),
        "total_tokens_in": stats["total_tokens_in"],
        "total_tokens_out": stats["total_tokens_out"],
        "results": results
    }
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    print(f"\n  📋 Log salvat: {log_path}")

    print(f"\n  📁 Fișierele refactorizate sunt în: {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()
