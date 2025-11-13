#!/usr/bin/env python3
"""Generate headwear product markdown files from image filenames.

Rules:
 - Title: derived from filename, digits separated (e.g., "Baseball Cap1" -> "Baseball Cap 1").
 - Slug: lowercase, hyphen-separated.
 - SKU: uppercase filename base without spaces (e.g., "BaseballCap1").
 - Image path stored as original (spaces retained) under /images/products/headwear/.
 - Creates file only if missing to avoid overwriting manual edits.
"""

from __future__ import annotations
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "static" / "images" / "products" / "headwear"
CONTENT_DIR = ROOT / "content" / "products" / "headwear"

CONTENT_DIR.mkdir(parents=True, exist_ok=True)

def make_title(base: str) -> str:
    # Separate trailing digits if stuck to last word
    base = re.sub(r"(?<=\D)(\d+)$", r" \1", base)
    # Normalize multiple spaces
    base = re.sub(r"[ _]+", " ", base).strip()
    # Title case each word
    words = [w.capitalize() for w in base.split()]
    return " "+" ".join(words) if False else " ".join(words)

def make_slug(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9 ]+", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug

def make_sku(base: str) -> str:
    sku = re.sub(r"[\s_]+", "", base).upper()
    return sku

def existing_skus() -> set[str]:
    skus = set()
    for md in CONTENT_DIR.glob("*.md"):
        with md.open("r", encoding="utf-8") as f:
            head = f.read().split("---", 2)
            if len(head) >= 3:
                front = head[1]
                m = re.search(r"SKU"+r"\"?\s*:?\s*\"?([A-Z0-9]+)\"?", front)
                if m:
                    skus.add(m.group(1))
    return skus

def main():
    created = 0
    skus = existing_skus()
    for entry in sorted(IMAGE_DIR.iterdir()):
        if not entry.is_file():
            continue
        if entry.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        base = entry.stem  # filename without extension
        title = make_title(base)
        slug = make_slug(title)
        sku = make_sku(base)
        md_path = CONTENT_DIR / f"{slug}.md"
        if sku in skus or md_path.exists():
            continue
        image_rel = f"/images/products/headwear/{entry.name}"
        front_matter = (
            "---\n"
            f"title: \"{title}\"\n"
            "category: \"Headwear\"\n"
            "categories: [\"Headwear\"]\n"
            f"description: \"{title} promotional headwear item\"\n"
            f"image: \"{image_rel}\"\n"
            "specifications:\n"
            "  - name: \"Material\"\n"
            "    value: \"Cotton\"\n"
            "  - name: \"SKU\"\n"
            f"    value: \"{sku}\"\n"
            "---\n\n"
            f"{title} – promotional headwear product variant.\n\n---\n"
        )
        md_path.write_text(front_matter, encoding="utf-8")
        created += 1
    print(f"Created {created} new headwear markdown files.")

if __name__ == "__main__":
    main()
