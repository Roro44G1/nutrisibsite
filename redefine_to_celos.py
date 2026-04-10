#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║   NUTRISIB — Script de rebranduire terminologică                    ║
║   ReDefine / Re-Define / Protocolul ReDefine → C.E.L.O.S.          ║
║   © 2026 dr.ing. Radu Pascu — NUTRISIB Sibiu                       ║
╚══════════════════════════════════════════════════════════════════════╝

UTILIZARE:
  python redefine_to_celos.py --folder /calea/spre/folderul/tau
  python redefine_to_celos.py --folder ./site --dry-run
  python redefine_to_celos.py --folder ./site --ext .html .htm .js .css .txt

OPȚIUNI:
  --folder    Folderul rădăcină (obligatoriu). Caută recursiv în toate subdirectoarele.
  --dry-run   Simulează fără să modifice nimic. Arată ce ar fi schimbat.
  --ext       Extensii de fișiere procesate (implicit: .html .htm .js .css .txt .md .php .xml)
  --backup    Creează copii .bak înainte de modificare (recomandat la prima rulare)
  --log       Salvează raportul într-un fișier .txt (implicit: redefine_audit.txt)
"""

import os
import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# ══════════════════════════════════════════════════════════════
# DICȚIONAR DE ÎNLOCUIRI
# Ordinea contează: mai specific → mai general
# ══════════════════════════════════════════════════════════════
REPLACEMENTS = [
    # ── Cu semn de exclamare ──────────────────────────────────
    (r'[Pp]rotocolul\s+ReDefine\s*!',       'protocolul C.E.L.O.S.'),
    (r'[Pp]rogramul\s+ReDefine\s*!',        'programul C.E.L.O.S.'),
    (r'[Mm]etoda\s+ReDefine\s*!',           'metoda C.E.L.O.S.'),
    (r'[Ss]istemul\s+ReDefine\s*!',         'sistemul C.E.L.O.S.'),
    (r'ReDefine\s*!',                        'C.E.L.O.S.'),

    # ── Cu cratimă Re-Define ──────────────────────────────────
    (r'[Pp]rotocolul\s+Re-Define',          'protocolul C.E.L.O.S.'),
    (r'[Pp]rogramul\s+Re-Define',           'programul C.E.L.O.S.'),
    (r'[Mm]etoda\s+Re-Define',              'metoda C.E.L.O.S.'),
    (r'[Ss]istemul\s+Re-Define',            'sistemul C.E.L.O.S.'),
    (r'Re-Define',                           'C.E.L.O.S.'),

    # ── Cu context explicit (fără cratimă, fără !) ────────────
    (r'[Pp]rotocolul\s+ReDefine',           'protocolul C.E.L.O.S.'),
    (r'[Pp]rogramul\s+ReDefine',            'programul C.E.L.O.S.'),
    (r'[Mm]etoda\s+ReDefine',               'metoda C.E.L.O.S.'),
    (r'[Ss]istemul\s+ReDefine',             'sistemul C.E.L.O.S.'),
    (r'[Cc]ursul\s+ReDefine',               'cursul C.E.L.O.S.'),
    (r'[Pp]achetul\s+ReDefine',             'pachetul C.E.L.O.S.'),
    (r'[Cc]omanda\s+ReDefine',              'comanda C.E.L.O.S.'),

    # ── Standalone — ultimul, cel mai general ─────────────────
    (r'\bReDefine\b',                        'C.E.L.O.S.'),
    (r'\bREDEFINE\b',                        'C.E.L.O.S.'),
    (r'\bRedefine\b',                        'C.E.L.O.S.'),
    (r'\bRe-define\b',                       'C.E.L.O.S.'),
    (r'\bRE-DEFINE\b',                       'C.E.L.O.S.'),
]

# Pre-compilare pentru performanță
COMPILED = [(re.compile(pattern, re.UNICODE), replacement)
            for pattern, replacement in REPLACEMENTS]

# Extensii procesate implicit
DEFAULT_EXTENSIONS = {'.html', '.htm', '.js', '.css', '.txt', '.md', '.php', '.xml', '.json'}

# ══════════════════════════════════════════════════════════════
# LOGICĂ PRINCIPALĂ
# ══════════════════════════════════════════════════════════════

def process_text(content: str) -> tuple[str, list[str]]:
    """Aplică toate înlocuirile pe conținut. Returnează (text_nou, lista_modificari)."""
    changes = []
    result = content

    for pattern, replacement in COMPILED:
        matches = pattern.findall(result)
        if matches:
            for m in matches:
                changes.append(f'  "{m}" → "{replacement}"')
            result = pattern.sub(replacement, result)

    return result, changes


def process_file(filepath: Path, dry_run: bool, backup: bool) -> dict:
    """Procesează un fișier. Returnează dict cu statistici."""
    report = {
        'path': str(filepath),
        'status': 'unchanged',
        'changes': [],
        'error': None
    }

    try:
        raw = filepath.read_bytes()
        # Detectare encoding
        try:
            content = raw.decode('utf-8')
            encoding = 'utf-8'
        except UnicodeDecodeError:
            try:
                content = raw.decode('latin-1')
                encoding = 'latin-1'
            except UnicodeDecodeError:
                report['status'] = 'skip'
                report['error'] = 'Encoding necunoscut — fișier sărit'
                return report

        new_content, changes = process_text(content)

        if changes:
            report['status'] = 'modified'
            report['changes'] = changes

            if not dry_run:
                if backup:
                    shutil.copy2(filepath, str(filepath) + '.bak')
                filepath.write_text(new_content, encoding=encoding)

    except PermissionError:
        report['status'] = 'error'
        report['error'] = 'Acces refuzat'
    except Exception as e:
        report['status'] = 'error'
        report['error'] = str(e)

    return report


def scan_folder(folder: Path, extensions: set, dry_run: bool, backup: bool) -> list[dict]:
    """Scanează recursiv folderul și procesează fișierele cu extensiile selectate."""
    results = []
    files = [f for f in folder.rglob('*') if f.is_file() and f.suffix.lower() in extensions]

    total = len(files)
    print(f'\n🔍 Fișiere găsite cu extensiile selectate: {total}')
    print('─' * 60)

    for i, filepath in enumerate(sorted(files), 1):
        # Sari fișierele .bak create de acest script
        if filepath.suffix == '.bak':
            continue

        result = process_file(filepath, dry_run, backup)
        results.append(result)

        status_icon = {'modified': '✅', 'unchanged': '·', 'error': '❌', 'skip': '⚠️'}.get(result['status'], '?')
        rel_path = filepath.relative_to(folder)

        if result['status'] == 'modified':
            print(f'{status_icon} [{i:>4}/{total}] {rel_path}  ({len(result["changes"])} înlocuiri)')
            for ch in result['changes']:
                print(f'         {ch}')
        elif result['status'] in ('error', 'skip'):
            print(f'{status_icon} [{i:>4}/{total}] {rel_path}  → {result["error"]}')

    return results


def generate_report(results: list[dict], dry_run: bool, folder: str, log_path: str):
    """Generează raportul final și îl salvează."""
    modified  = [r for r in results if r['status'] == 'modified']
    unchanged = [r for r in results if r['status'] == 'unchanged']
    errors    = [r for r in results if r['status'] in ('error', 'skip')]
    total_changes = sum(len(r['changes']) for r in modified)

    mode_label = '🔵 MOD SIMULARE (dry-run) — niciun fișier nu a fost modificat' if dry_run else '🟢 MOD LIVE — fișierele au fost modificate'

    lines = [
        '═' * 60,
        'RAPORT REBRANDUIRE: ReDefine → C.E.L.O.S.',
        f'Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'Folder: {folder}',
        mode_label,
        '═' * 60,
        f'Fișiere scanate total:    {len(results)}',
        f'Fișiere modificate:       {len(modified)}',
        f'Fișiere nemodificate:     {len(unchanged)}',
        f'Erori / sărite:           {len(errors)}',
        f'Total înlocuiri efectuate: {total_changes}',
        '─' * 60,
    ]

    if modified:
        lines.append('\nFIȘIERE MODIFICATE:')
        for r in modified:
            lines.append(f'\n  📄 {r["path"]}')
            for ch in r['changes']:
                lines.append(f'      {ch}')

    if errors:
        lines.append('\nERRORI:')
        for r in errors:
            lines.append(f'  ❌ {r["path"]}: {r["error"]}')

    report_text = '\n'.join(lines)

    # Print în consolă
    print('\n' + report_text)

    # Salvare în fișier log
    try:
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f'\n📋 Raport salvat în: {log_path}')
    except Exception as e:
        print(f'\n⚠️  Nu s-a putut salva raportul: {e}')


# ══════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='NUTRISIB — Rebranduire ReDefine → C.E.L.O.S. în fișiere HTML și alte tipuri',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--folder',  required=True,  help='Folderul rădăcină (scanare recursivă)')
    parser.add_argument('--dry-run', action='store_true', help='Simulare — nu modifică nimic')
    parser.add_argument('--backup',  action='store_true', help='Creează .bak înainte de modificare')
    parser.add_argument('--ext',     nargs='+', default=None,
                        help='Extensii procesate (ex: .html .js .css). Implicit: toate tipurile web comune.')
    parser.add_argument('--log',     default='redefine_audit.txt',
                        help='Fișier raport (implicit: redefine_audit.txt)')

    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists() or not folder.is_dir():
        print(f'❌ Eroare: folderul "{folder}" nu există sau nu este un director.')
        sys.exit(1)

    extensions = set(args.ext) if args.ext else DEFAULT_EXTENSIONS

    print('╔══════════════════════════════════════════════════════════╗')
    print('║  NUTRISIB — Rebranduire ReDefine → C.E.L.O.S.          ║')
    print('╚══════════════════════════════════════════════════════════╝')
    print(f'📁 Folder:     {folder.resolve()}')
    print(f'📄 Extensii:   {", ".join(sorted(extensions))}')
    print(f'🔵 Mod:        {"DRY-RUN (simulare)" if args.dry_run else "LIVE (modifică fișierele)"}')
    print(f'💾 Backup:     {"DA" if args.backup else "NU"}')

    if not args.dry_run:
        print('\n⚠️  ATENȚIE: Fișierele vor fi modificate direct.')
        if args.backup:
            print('   Copii .bak vor fi create înainte de fiecare modificare.')
        confirm = input('   Continui? (da/nu): ').strip().lower()
        if confirm not in ('da', 'yes', 'y', 'd'):
            print('Anulat.')
            sys.exit(0)

    results = scan_folder(folder, extensions, args.dry_run, args.backup)
    generate_report(results, args.dry_run, str(folder.resolve()), args.log)


if __name__ == '__main__':
    main()
