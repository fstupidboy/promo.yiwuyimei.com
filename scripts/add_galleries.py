#!/usr/bin/env python3
"""Populate gallery arrays in product markdown from static images.

Rule:
- Use the directory of the main image (front matter `image`) under `static/`.
- Add all images in that directory except the main image to `gallery` list (as web paths starting with `/images/`).
- Supports extensions: jpg, jpeg, png, webp, avif.
- Skips files if gallery already exists.
"""
from __future__ import annotations
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "products"
STATIC = ROOT / "static"
IMG_EXT = {".jpg",".jpeg",".png",".webp",".avif"}

def split_front_matter(text: str):
    if not text.startswith("---\n"):
        return None, text
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return None, text
    fm = parts[0][4:]
    body = parts[1]
    return fm, body

def main():
    count = 0
    updated = 0
    for md in CONTENT.rglob("*.md"):
        txt = md.read_text(encoding="utf-8")
        fm_text, body = split_front_matter(txt)
        if fm_text is None:
            continue
        data = yaml.safe_load(fm_text) or {}
        image = data.get("image")
        if not image or data.get("gallery"):
            count += 1
            continue
        # map web path to disk path
        rel = image.lstrip("/")
        img_path = STATIC / rel
        if not img_path.exists():
            count += 1
            continue
        folder = img_path.parent
        files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMG_EXT]
        # exclude main image
        gallery = []
        for f in sorted(files):
            if f.samefile(img_path):
                continue
            web = "/" + str(f.relative_to(STATIC)).replace("\\", "/")
            gallery.append(web)
        if gallery:
            data["gallery"] = gallery
            # write back
            new_fm = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip()
            md.write_text("---\n" + new_fm + "\n---\n" + body, encoding="utf-8")
            updated += 1
        count += 1
    print(f"Processed {count} products; updated {updated} with gallery images.")

if __name__ == "__main__":
    main()
