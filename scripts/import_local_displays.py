#!/usr/bin/env python3
import argparse
import os
import shutil
import json
import re
from pathlib import Path


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\-\s]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value or "item"


def main():
    parser = argparse.ArgumentParser(
        description="Import local display images into Hugo static folder and build a manifest"
    )
    parser.add_argument(
        "src_root",
        help="Source root folder containing per-category subfolders (e.g., /home/user/photos/displays)",
    )
    parser.add_argument(
        "--out-dir",
        default="static/images/displays",
        help="Destination root under Hugo static (default: static/images/displays)",
    )
    parser.add_argument(
        "--out-json",
        default="scripts/display_assets_local.json",
        help="Manifest JSON output path",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of symlink (default: symlink if possible)",
    )
    args = parser.parse_args()

    exts = {".jpg", ".jpeg", ".png", ".webp"}
    src_root = Path(args.src_root).expanduser().resolve()
    out_root = Path(args.out_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    items = []
    for cat_dir in sorted(p for p in src_root.iterdir() if p.is_dir()):
        category = cat_dir.name
        cat_slug = slugify(category)
        dest_cat = out_root / cat_slug
        dest_cat.mkdir(parents=True, exist_ok=True)

        for fp in sorted(cat_dir.rglob("*")):
            if not fp.is_file() or fp.suffix.lower() not in exts:
                continue
            dest_file = dest_cat / fp.name
            if dest_file.exists():
                # Deduplicate by filename; skip if already exists
                continue
            try:
                if args.copy:
                    shutil.copy2(fp, dest_file)
                else:
                    # Use relative symlink if possible; fallback to copy on Windows
                    rel = os.path.relpath(fp, start=dest_cat)
                    try:
                        os.symlink(rel, dest_file)
                    except OSError:
                        shutil.copy2(fp, dest_file)
            except Exception as e:
                print(f"[skip] {fp} -> {dest_file}: {e}")
                continue

            web_path = f"/images/displays/{cat_slug}/{dest_file.name}"
            items.append(
                {
                    "category": category,
                    "site": "local",
                    "title": dest_file.name,
                    "author_name": "",
                    "page_url": "",
                    "download_url": web_path,
                    "width": None,
                    "height": None,
                    "license": "User-provided (verify commercial rights)",
                }
            )

    manifest = Path(args.out_json)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"Imported {len(items)} images. Manifest: {manifest}")


if __name__ == "__main__":
    main()
