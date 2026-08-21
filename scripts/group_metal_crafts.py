#!/usr/bin/env python3
"""Group Metal Crafts products by image subdirectory.

For each subdirectory under static/images/products/metal-crafts/, create a
single markdown file in content/products/metal-crafts/ representing one
product whose gallery consists of all images in that subdirectory.

Existing per-image markdown files in the target content directory are removed.

Usage:
  python scripts/group_metal_crafts.py
"""

from __future__ import annotations
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGE_ROOT = ROOT / "static" / "images" / "products" / "metal-crafts"
OUTPUT_DIR = ROOT / "content" / "products" / "metal-crafts"

VALID_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

def kebab_case(name: str) -> str:
    # Replace non-alphanumeric with dash, collapse repeats, lower-case.
    name = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-")
    return name.lower()

def title_case(name: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[\s_-]+", name) if part)

def gather_directories() -> list[Path]:
    if not IMAGE_ROOT.is_dir():
        raise SystemExit(f"Image root not found: {IMAGE_ROOT}")
    dirs = [p for p in IMAGE_ROOT.iterdir() if p.is_dir()]
    return sorted(dirs, key=lambda p: p.name.lower())

def list_images(dir_path: Path) -> list[Path]:
    files = [p for p in dir_path.iterdir() if p.is_file() and p.suffix.lower() in VALID_EXT]
    # Sort by name for deterministic ordering.
    return sorted(files, key=lambda p: p.name.lower())

def remove_existing_markdown():
    if not OUTPUT_DIR.exists():
        return
    removed = 0
    for md in OUTPUT_DIR.glob("*.md"):
        md.unlink()
        removed += 1
    return removed

def make_markdown(dir_path: Path, images: list[Path]) -> str:
    title = title_case(dir_path.name)
    slug = kebab_case(dir_path.name)
    if not images:
        return ""  # Skip empty directories.
    # Use first image as main image.
    main_image_rel = "/images/products/metal-crafts/" + "/".join(dir_path.relative_to(IMAGE_ROOT).parts + (images[0].name,))
    gallery_paths = [
        "/images/products/metal-crafts/" + "/".join(dir_path.relative_to(IMAGE_ROOT).parts + (img.name,))
        for img in images[1:]  # Exclude main image from gallery list.
    ]
    sku = kebab_case(title).upper()
    front_matter_lines = [
        "---",
        f"title: \"{title}\"",
        "category: \"Metal Crafts\"",
        "categories: [\"Metal Crafts\"]",
        f"description: \"{title} promotional metal crafts item\"",
        f"image: \"{main_image_rel}\"",
        "specifications:",
        "  - name: \"Material\"",
        "    value: \"Alloy\"",
        "  - name: \"SKU\"",
        f"    value: \"{sku}\"",
    ]
    if gallery_paths:
        front_matter_lines.append("gallery:")
        for g in gallery_paths:
            front_matter_lines.append(f"  - \"{g}\"")
    front_matter_lines.append("---")
    body = f"\n{title} – grouped Metal Crafts product comprising {len(images)} images.\n\n---\n"
    return "\n".join(front_matter_lines) + body

def write_markdown(slug: str, content: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{slug}.md"
    path.write_text(content, encoding="utf-8")
    return path

def main():
    dirs = gather_directories()
    removed = remove_existing_markdown()
    created = 0
    skipped = []
    for d in dirs:
        images = list_images(d)
        md = make_markdown(d, images)
        if not md:
            skipped.append(d.name)
            continue
        slug = kebab_case(d.name)
        write_markdown(slug, md)
        created += 1
    print(f"Removed {removed} old markdown files.")
    print(f"Created {created} grouped markdown files.")
    if skipped:
        print("Skipped empty directories:", ", ".join(skipped))

if __name__ == "__main__":
    main()
