#!/usr/bin/env python3
"""Generate bag product markdown files from image filenames.

Creates one markdown per image base name group (e.g. Backpack1/2/3 -> Backpack 1, Backpack 2 ...).
Title rules:
  - Separate trailing digits and capitalize words.
SKU rules:
  - Remove spaces, uppercase, digits kept (e.g. BACKPACK1).
Category fixed to "Bags".
Skips existing markdown files (by slug) and duplicate SKUs.
"""
from __future__ import annotations
import re, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "static" / "images" / "products" / "bags"
CONTENT_DIR = ROOT / "content" / "products" / "bags"
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

def make_title(stem: str) -> str:
    stem = re.sub(r"[_]+", " ", stem)
    stem = re.sub(r"(?<=\D)(\d+)$", r" \1", stem)
    words = [w.capitalize() for w in stem.split()]
    return " ".join(words)

def make_slug(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9 ]+", "", s)
    return re.sub(r"\s+", "-", s)

def make_sku(stem: str) -> str:
    return re.sub(r"[\s_]+", "", stem).upper()

existing = {p.stem for p in CONTENT_DIR.glob("*.md")}
existing_sku = set()
for p in CONTENT_DIR.glob("*.md"):
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"SKU"+r".*?([A-Z0-9]{3,})", txt)
    if m: existing_sku.add(m.group(1))

created = 0
for img in sorted(IMAGE_DIR.iterdir()):
    if not img.is_file():
        continue
    if img.suffix.lower() not in {".jpg",".jpeg",".png",".gif"}: continue
    stem = img.stem
    title = make_title(stem)
    slug = make_slug(title)
    sku = make_sku(stem)
    md_path = CONTENT_DIR / f"{slug}.md"
    if md_path.exists() or sku in existing_sku:
        continue
    image_rel = f"/images/products/bags/{img.name}"
    fm = (
        "---\n"
        f"title: \"{title}\"\n"
        "category: \"Bags\"\n"
        "categories: [\"Bags\"]\n"
        f"description: \"{title} promotional bag item\"\n"
        f"image: \"{image_rel}\"\n"
        "specifications:\n"
        "  - name: \"Material\"\n"
        "    value: \"Polyester\"\n"
        "  - name: \"SKU\"\n"
        f"    value: \"{sku}\"\n"
        "---\n\n"
        f"{title} – promotional bag product variant.\n\n---\n"
    )
    md_path.write_text(fm, encoding="utf-8")
    created += 1
    existing_sku.add(sku)

print(f"Created {created} bag markdown files.")
