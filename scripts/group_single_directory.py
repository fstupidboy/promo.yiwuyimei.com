#!/usr/bin/env python3
"""Create a single Hugo product from all images in one directory.

Usage:
  python3 scripts/group_single_directory.py \
    --images-dir static/images/products/gift-set \
    --category "Gift Set" \
    --output-file content/products/gift-set/gift-set.md \
    --title "Gift Set" \
    --material Mixed
"""

from __future__ import annotations
import argparse
from pathlib import Path

VALID_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

def list_images(dir_path: Path) -> list[Path]:
    return sorted([p for p in dir_path.iterdir() if p.is_file() and p.suffix.lower() in VALID_EXT], key=lambda p: p.name.lower())

def build_markdown(images_dir: Path, category: str, title: str, material: str, images: list[Path]) -> str:
    if not images:
        raise SystemExit(f"No images found in: {images_dir}")
    main = images[0]
    # Build paths relative to /images/products/... (strip leading static)
    def to_public_path(p: Path) -> str:
        # Expect 'static/...' prefix
        parts = p.resolve().parts
        try:
            idx = parts.index('static')
            rel = Path(*parts[idx+1:])
            return '/' + str(rel).replace('\\', '/')
        except ValueError:
            # Fallback to absolute-like
            return '/' + str(p).replace('\\', '/')

    main_src = to_public_path(main)
    gallery = [to_public_path(p) for p in images[1:]]
    fm = [
        '---',
        f'title: "{title}"',
        f'category: "{category}"',
        f'categories: ["{category}"]',
        f'description: "{title} promotional {category} item"',
        f'image: "{main_src}"',
        'specifications:',
        '  - name: "Material"',
        f'    value: "{material}"',
        '  - name: "SKU"',
        f'    value: "{title.replace(" ", "-").upper()}"',
    ]
    if gallery:
        fm.append('gallery:')
        for g in gallery:
            fm.append(f'  - "{g}"')
    fm.append('---')
    body = f"\n{title} – grouped {category} product comprising {len(images)} images.\n\n---\n"
    return "\n".join(fm) + body

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--images-dir', required=True)
    ap.add_argument('--category', required=True)
    ap.add_argument('--output-file', required=True)
    ap.add_argument('--title', required=True)
    ap.add_argument('--material', default='Mixed')
    args = ap.parse_args()

    images_dir = Path(args.images_dir).resolve()
    images = list_images(images_dir)
    md = build_markdown(images_dir, args.category, args.title, args.material, images)
    out = Path(args.output_file).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding='utf-8')
    print(f"Wrote {out}")

if __name__ == '__main__':
    main()
