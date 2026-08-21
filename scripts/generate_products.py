#!/usr/bin/env python3
"""Generic product markdown generator for Hugo site.

Usage:
  python3 scripts/generate_products.py --category "Headwear" --images static/images/products/headwear --out content/products/headwear

Arguments:
  --category   Display category name (stored in front matter fields `category` and `categories`).
  --images     Path to directory containing product images (absolute or relative to repo root).
  --out        Output directory for generated markdown files (default: derive from category under content/products/<slug>). If it does not exist it will be created.
  --material   Optional material value (default Polyester).
  --dry-run    Only show summary, do not write files.

Generation Rules:
  Title: From image filename stem, underscores/spaces collapsed, trailing digits separated with space, words capitalized.
  Slug: Lowercase alphanumeric hyphenated from title.
  SKU: Uppercase filename stem without spaces/underscores.
  Image path: preserved with original filename, prefixed with /images/... for Hugo.
  Skips existing markdown (same slug) and duplicate SKU.

This script unifies previous category-specific generators.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path
from typing import Set

ROOT = Path(__file__).resolve().parents[1]

IMG_EXT = {".jpg",".jpeg",".png",".gif",".webp",".avif"}

def normalize_title(stem: str) -> str:
    stem = re.sub(r"[_]+", " ", stem)
    # separate trailing digits attached to word
    stem = re.sub(r"(?<=\D)(\d+)$", r" \1", stem)
    words = [w.capitalize() for w in stem.split()]
    return " ".join(words)

def make_slug(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9 ]+", "", s)
    return re.sub(r"\s+", "-", s)

def make_sku(stem: str) -> str:
    return re.sub(r"[\s_]+", "", stem).upper()

def collect_existing(out_dir: Path) -> tuple[Set[str], Set[str]]:
    slugs = {p.stem for p in out_dir.glob("*.md")}
    skus: Set[str] = set()
    for md in out_dir.glob("*.md"):
        try:
            txt = md.read_text(encoding="utf-8")
        except Exception:
            continue
        m = re.search(r"SKU\"?\s*:?\s*\"?([A-Z0-9]{3,})\"?", txt)
        if m:
            skus.add(m.group(1))
    return slugs, skus

def build_front_matter(title: str, category: str, sku: str, image_rel: str, material: str) -> str:
    return (
        "---\n"
        f"title: \"{title}\"\n"
        f"category: \"{category}\"\n"
        f"categories: [\"{category}\"]\n"
        f"description: \"{title} promotional {category.lower()} item\"\n"
        f"image: \"{image_rel}\"\n"
        "specifications:\n"
        f"  - name: \"Material\"\n    value: \"{material}\"\n"
        "  - name: \"SKU\"\n"
        f"    value: \"{sku}\"\n"
        "---\n\n"
        f"{title} – promotional {category.lower()} product variant.\n\n---\n"
    )

def generate(category: str, images_dir: Path, out_dir: Path, material: str, dry_run: bool=False) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    existing_slugs, existing_skus = collect_existing(out_dir)
    created = 0
    static_root = ROOT / "static"
    for img in sorted(images_dir.iterdir()):
        if not img.is_file():
            continue
        if img.suffix.lower() not in IMG_EXT:
            continue
        img_abs = img.resolve()
        stem = img_abs.stem
        title = normalize_title(stem)
        slug = make_slug(title)
        sku = make_sku(stem)
        md_path = out_dir / f"{slug}.md"
        if md_path.stem in existing_slugs or sku in existing_skus:
            continue
        # Build web path relative to static/images root
        try:
            rel_from_static = img_abs.relative_to(static_root)
        except ValueError:
            # If image not under static, skip
            continue
        rel_str = rel_from_static.as_posix()
        if rel_str.startswith("images/"):
            image_rel = "/" + rel_str  # already begins with images/
        else:
            image_rel = "/images/" + rel_str
        fm = build_front_matter(title, category, sku, image_rel, material)
        if not dry_run:
            md_path.write_text(fm, encoding="utf-8")
        existing_slugs.add(md_path.stem)
        existing_skus.add(sku)
        created += 1
    return created

def main():
    ap = argparse.ArgumentParser(description="Generic product markdown generator")
    ap.add_argument("--category", required=True, help="Category display name")
    ap.add_argument("--images", required=True, help="Path to images directory")
    ap.add_argument("--out", help="Output directory for markdown files")
    ap.add_argument("--material", default="Polyester", help="Default material spec value")
    ap.add_argument("--dry-run", action="store_true", help="Do not write files; show summary only")
    args = ap.parse_args()

    images_dir = Path(args.images)
    if not images_dir.is_dir():
        print(f"Images dir not found: {images_dir}")
        raise SystemExit(2)
    out_dir = Path(args.out) if args.out else (ROOT / "content" / "products" / make_slug(args.category))
    created = generate(args.category, images_dir, out_dir, args.material, args.dry_run)
    print(f"Generated {created} markdown files in {out_dir}")

if __name__ == "__main__":
    main()
