#!/usr/bin/env python3
"""Normalize *header brand logos only* across static HTML pages of NutriSib.
Does not touch images inside articles, footers, products, scripts or CSS.
Idempotent; safe to run again from repository root.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = re.compile(r"<header\b[^>]*>[\s\S]*?<\/header\s*>", re.I)
IMAGE = re.compile(r"<img\b[^>]*>", re.I | re.S)
SRC = re.compile(r"(\bsrc\s*=\s*)([\"'])(.*?)\2", re.I | re.S)
ALT = re.compile(r"\balt\s*=\s*[\"']([^\"']*)[\"']", re.I)
BRAND = re.compile(r"logo_navy_pearl|logo_alb|logo_nutrisib", re.I)
EXCLUDE = {".git", "node_modules", "dist", "build", ".netlify", "venv", ".venv"}

def update_image(tag: str, prefix: str) -> str:
    src_match = SRC.search(tag)
    alt_match = ALT.search(tag)
    src = src_match.group(3) if src_match else ""
    alt = alt_match.group(1) if alt_match else ""
    is_brand = bool(BRAND.search(src)) or (
        bool(re.search(r"nutrisib", alt, re.I))
        and bool(re.search(r"sigla|logo", alt, re.I))
    )
    if not is_brand:
        return tag
    if src_match:
        filename = re.search(r"(?:^|/)(logo_navy_pearl\.png|logo_alb\.png)$", src, re.I)
        if filename:
            target = prefix + "logo/" + filename.group(1)
            tag = SRC.sub(lambda m: m.group(1) + m.group(2) + target + m.group(2), tag, count=1)
    for attribute in ("width", "height"):
        expr = re.compile(r"(\b" + attribute + r"\s*=\s*)([\"'])(.*?)\2", re.I | re.S)
        if expr.search(tag):
            tag = expr.sub(lambda m: m.group(1) + m.group(2) + "52" + m.group(2), tag, count=1)
        else:
            tag = tag[:-1] + ' ' + attribute + '="52">'
    return tag

def convert(html: str, prefix: str) -> str:
    has_logo = [False]
    def update_header(match: re.Match[str]) -> str:
        fragment = match.group(0)
        def update_tag(tag: re.Match[str]) -> str:
            old = tag.group(0)
            new = update_image(old, prefix)
            if new != old or BRAND.search(old):
                has_logo[0] = True
            return new
        return IMAGE.sub(update_tag, fragment)
    html = HEADER.sub(update_header, html)
    if has_logo[0] and "header-brand.css" not in html and re.search(r"</head\s*>", html, re.I):
        html = re.sub(r"</head\s*>",
            '<link rel="stylesheet" href="' + prefix + 'header-brand.css">\n</head>',
            html, count=1, flags=re.I)
    return html

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    changed = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".html", ".htm"}:
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDE for part in relative.parts):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = convert(content, "../" * (len(relative.parts) - 1))
        if new != content:
            changed.append(str(relative))
            if not args.dry_run:
                path.write_text(new, encoding="utf-8")
    print(f"Normalized header branding: {len(changed)} pages")
    for filename in changed:
        print(filename)

if __name__ == "__main__":
    main()
