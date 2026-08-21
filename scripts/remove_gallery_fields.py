#!/usr/bin/env python3
"""Remove gallery fields from product markdown for specified categories.

Targets categories: Apparel, Bags, Headwear, Ceramic Mugs
"""
from __future__ import annotations
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "products"
TARGET = {"Apparel","Bags","Headwear","Ceramic Mugs"}

def split_front_matter(text: str):
    if not text.startswith("---\n"): return None, text
    parts = text.split("\n---\n", 1)
    if len(parts) != 2: return None, text
    fm = parts[0][4:]
    body = parts[1]
    return fm, body

def main():
    changed = 0
    scanned = 0
    for md in CONTENT.rglob("*.md"):
        txt = md.read_text(encoding="utf-8")
        fm_text, body = split_front_matter(txt)
        if fm_text is None:
            scanned += 1
            continue
        data = yaml.safe_load(fm_text) or {}
        cat = data.get("category")
        if cat not in TARGET or "gallery" not in data:
            scanned += 1
            continue
        del data["gallery"]
        new_fm = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip()
        md.write_text("---\n" + new_fm + "\n---\n" + body, encoding="utf-8")
        changed += 1
        scanned += 1
    print(f"Scanned {scanned} files; removed gallery from {changed}.")

if __name__ == "__main__":
    main()
