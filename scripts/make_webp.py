#!/usr/bin/env python3
"""Generate .webp copies for images under static/images.

Uses `cwebp` if available. Skips targets that already exist and newer.
Quality default 80. Converts: .jpg, .jpeg, .png, .avif
"""
from __future__ import annotations
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
IMG_ROOT = ROOT / "static" / "images"
SRC_EXT = {".jpg",".jpeg",".png",".avif"}

def has_cwebp() -> bool:
    return shutil.which("cwebp") is not None

def convert(src: Path, dst: Path, quality: int=80) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not has_cwebp():
        return False
    cmd = ["cwebp", "-quiet", "-q", str(quality), str(src), "-o", str(dst)]
    r = subprocess.run(cmd)
    return r.returncode == 0

def main():
    if not IMG_ROOT.exists():
        print(f"Not found: {IMG_ROOT}")
        sys.exit(2)
    converted = 0
    skipped = 0
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
