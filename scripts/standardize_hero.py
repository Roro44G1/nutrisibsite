#!/usr/bin/env python3
"""Apply unified NutriSib hero color/shape to existing static HTML pages.

First recognized hero section only, preserving every page's layout/content.
Injects one shared stylesheet after the page's other CSS. Idempotent.
Run on the construction branch only.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {".git", "node_modules", "dist", "build", ".netlify", ".venv", "venv"}
SELECTORS = {
    "hero-full", "hero-card", "pv-hero", "hero-journal",
    "ns-services-hero", "asistent-hero", "hero-enc",
    "infographic-header-page", "blog-hero", "page-hero",
    "hero-banner", "biohack-hero", "article-hero",
}
START_TAG = re.compile(r"<(?:section|div)\b[^>]*>", re.I | re.S)
CLASS_ATTR = re.compile(r'(\bclass\s*=\s*)(["\'])(.*?)\2', re.I | re.S)
HEAD_END = re.compile(r"</head\s*>", re.I)


def unify(html: str, prefix: str) -> str:
    """Tag the first known top-level hero and link common CSS."""
    if not HEAD_END.search(html):
        return html
    chosen = None
    for match in START_TAG.finditer(html):
        klass = CLASS_ATTR.search(match.group(0))
        if not klass:
            continue
        existing = set(klass.group(3).split())
        if existing & SELECTORS:
            chosen = match
            break
    if chosen is None:
        return html
    tag = chosen.group(0)
    klass = CLASS_ATTR.search(tag)
    if "ns-uniform-hero" not in klass.group(3).split():
        new_value = klass.group(3) + " ns-uniform-hero"
        updated_tag = tag[:klass.start(3)] + new_value + tag[klass.end(3):]
        html = html[:chosen.start()] + updated_tag + html[chosen.end():]
    if "hero-uniform.css" not in html:
        link = '<link rel="stylesheet" href="' + prefix + 'hero-uniform.css">\n'
        html = HEAD_END.sub(lambda m: link + m.group(0), html, count=1)
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
        if any(piece in EXCLUDE for piece in relative.parts):
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        amended = unify(original, "../" * (len(relative.parts) - 1))
        if amended != original:
            changed.append(str(relative))
            if not args.dry_run:
                path.write_text(amended, encoding="utf-8")
    print(f"Unified hero sections: {len(changed)} pages")
    for filename in changed:
        print(filename)


if __name__ == "__main__":
    main()
