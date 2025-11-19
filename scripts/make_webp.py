#!/usr/bin/env python3
"""Generate .webp copies for images under static/images.

Priority conversion tool chain:
1. Use `cwebp` if available (fast, good quality)
2. Fallback to Pillow (requires pillow + pillow-avif-plugin for AVIF) if cwebp missing

Skips targets that already exist and are newer than source.
Quality default 80 for cwebp; Pillow uses quality=80 and method=6.
Converts: .jpg, .jpeg, .png, .avif
"""
from __future__ import annotations
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Optional

try:
    from PIL import Image  # type: ignore
except ImportError:  # Pillow not installed; fallback will be disabled
    Image = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
IMG_ROOT = ROOT / "static" / "images"
SRC_EXT = {".jpg",".jpeg",".png",".avif"}

def has_cwebp() -> bool:
    return shutil.which("cwebp") is not None

def convert_cwebp(src: Path, dst: Path, quality: int = 80) -> bool:
    cmd = ["cwebp", "-quiet", "-q", str(quality), str(src), "-o", str(dst)]
    r = subprocess.run(cmd)
    return r.returncode == 0

def convert_pillow(src: Path, dst: Path, quality: int = 80) -> bool:
    if Image is None:
        return False
    try:
        with Image.open(src) as im:
            im.save(dst, "WEBP", quality=quality, method=6)
        return True
    except Exception as e:  # pragma: no cover
        print(f"[warn] Pillow conversion failed for {src.name}: {e}")
        return False

def convert(src: Path, dst: Path, quality: int = 80) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if has_cwebp():
        return convert_cwebp(src, dst, quality)
    return convert_pillow(src, dst, quality)

def main():
    if not IMG_ROOT.exists():
        print(f"Not found: {IMG_ROOT}")
        sys.exit(2)
    converted = 0
    skipped = 0
    mode = "cwebp" if has_cwebp() else ("pillow" if Image else "none")
    if mode == "none":
        print("No conversion backend (install webp tools or Pillow + pillow-avif-plugin).")
        sys.exit(1)
    print(f"Using backend: {mode}")
    for p in IMG_ROOT.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in SRC_EXT:
            continue
        dst = p.with_suffix(".webp")
        if dst.exists() and dst.stat().st_mtime >= p.stat().st_mtime:
            skipped += 1
            continue
        ok = convert(p, dst)
        if ok:
            converted += 1
        else:
            skipped += 1
    print(f"webp converted: {converted}, skipped: {skipped}")

if __name__ == "__main__":
    main()
