#!/usr/bin/env python3
"""Generic script: group product images by subdirectory into one Hugo content file.

Each immediate subdirectory under the given images root becomes a single product
markdown file whose gallery contains all images (except the first which is main).

Example:
  python3 scripts/group_by_directory.py \
    --images-root static/images/products/resin-ornaments-n-snow-globes \
    --category "Resin Ornaments & Snow Globes" \
    --output-dir content/products/resin-ornaments-n-snow-globes \
    --material Resin
"""

from __future__ import annotations
import argparse
import re
from pathlib import Path

VALID_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

def kebab_case(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-")
    return name.lower()

def title_case(name: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[\s_-]+", name) if part)

def list_subdirs(root: Path) -> list[Path]:
    return sorted([p for p in root.iterdir() if p.is_dir()], key=lambda p: p.name.lower())

def list_images(dir_path: Path) -> list[Path]:
    return sorted([p for p in dir_path.iterdir() if p.is_file() and p.suffix.lower() in VALID_EXT], key=lambda p: p.name.lower())

def build_markdown(category: str, material: str, dir_path: Path, images_root: Path, images: list[Path]) -> str:
    if not images:
        return ""
    title = title_case(dir_path.name)
    slug = kebab_case(dir_path.name)
    rel_main = "/" + "/".join((images_root.name, dir_path.name, images[0].name))
    gallery = ["/" + "/".join((images_root.name, dir_path.name, img.name)) for img in images[1:]]
    sku = kebab_case(title).upper()
    fm = [
        "---",
        f"title: \"{title}\"",
        f"category: \"{category}\"",
        f"categories: [\"{category}\"]",
        f"description: \"{title} promotional {category} item\"",
        f"image: \"/images/products/{images_root.name}/{dir_path.name}/{images[0].name}\"",
        "specifications:",
        f"  - name: \"Material\"",
        f"    value: \"{material}\"",
        "  - name: \"SKU\"",
        f"    value: \"{sku}\"",
    ]
    if gallery:
        fm.append("gallery:")
        for g in gallery:
            # Adjust path to include /images/products prefix for consistency
            gm = g.replace(f"/{images_root.name}/", f"/images/products/{images_root.name}/")
            fm.append(f"  - \"{gm}\"")
    fm.append("---")
    body = f"\n{title} – grouped {category} product comprising {len(images)} images.\n\n---\n"
    return "\n".join(fm) + body

def main():
    parser = argparse.ArgumentParser(description="Group product images into one markdown per subdirectory.")
    parser.add_argument("--images-root", required=True, help="Path under static/images/products/... e.g. static/images/products/resin-ornaments-n-snow-globes")
    parser.add_argument("--category", required=True, help="Category name to use in front matter")
    parser.add_argument("--output-dir", required=True, help="Content output directory, e.g. content/products/resin-ornaments-n-snow-globes")
    parser.add_argument("--material", default="Mixed", help="Material specification value")
    parser.add_argument("--clean", action="store_true", help="Remove existing markdown files in output before writing")
    args = parser.parse_args()

    images_root = Path(args.images_root).resolve()
    if not images_root.is_dir():
        raise SystemExit(f"Images root not found: {images_root}")
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.clean:
        removed = 0
        for md in output_dir.glob("*.md"):
            md.unlink(); removed += 1
        print(f"Removed {removed} existing markdown files.")

    dirs = list_subdirs(images_root)
    created = 0
    skipped = []
    for d in dirs:
        imgs = list_images(d)
        md = build_markdown(args.category, args.material, d, images_root, imgs)
        if not md:
            skipped.append(d.name); continue
        slug = kebab_case(d.name)
        (output_dir / f"{slug}.md").write_text(md, encoding="utf-8")
        created += 1
    print(f"Created {created} markdown files for category '{args.category}'.")
    if skipped:
        print("Skipped empty directories:", ", ".join(skipped))

if __name__ == "__main__":
    main()
