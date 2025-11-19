#!/usr/bin/env python3
import os
import re
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any
from urllib.parse import quote_plus

try:
    import requests
except ImportError:
    requests = None


CATEGORIES: Dict[str, List[str]] = {
    "Roll-up banner stand": [
        "roll up banner stand",
        "retractable banner stand",
        "易拉宝",
    ],
    "X banner stand": [
        "x banner stand",
        "x display stand",
        "X展架",
    ],
    "Fabric pop-up display / pop up backdrop": [
        "fabric pop up display",
        "pop up backdrop",
        "拉网展架",
    ],
    "Acrylic display stand / holder": [
        "acrylic display stand",
        "acrylic brochure holder",
        "亚克力展示架",
    ],
    "Wooden display stand / shelf": [
        "wooden display stand",
        "wooden shelf display",
        "木质展示架",
    ],
    "Metal display rack / stand": [
        "metal display rack",
        "metal display stand",
        "金属展示架",
    ],
    "Cardboard display stand / corrugated POS": [
        "cardboard display stand",
        "corrugated pos display",
        "纸质展示架",
    ],
    "PVC foam board stand / KT board": [
        "kt board stand",
        "pvc foam board sign stand",
        "KT板 展架",
        "PVC 展架",
    ],
    "Gridwall display / wire grid": [
        "gridwall display",
        "wire grid display",
        "网片展示架",
    ],
    "Tabletop display stand": [
        "tabletop display stand",
        "countertop display stand",
        "桌面展示架",
    ],
    "Brochure holder / literature rack": [
        "brochure holder",
        "literature rack",
        "资料架",
    ],
    "Rotating display stand": [
        "rotating display stand",
        "spinner display rack",
        "旋转展示架",
    ],
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\-\s]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value or "item"


def ensure_requests():
    if requests is None:
        raise SystemExit(
            "Python 'requests' is required. Install with: pip install requests"
        )


def pexels_search(api_key: str, query: str, per_page: int) -> List[Dict[str, Any]]:
    ensure_requests()
    url = f"https://api.pexels.com/v1/search?query={quote_plus(query)}&per_page={per_page}&page=1"
    headers = {"Authorization": api_key}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    results = []
    for p in data.get("photos", []):
        results.append(
            {
                "site": "Pexels",
                "title": p.get("alt") or "",
                "author_name": p.get("photographer") or "",
                "page_url": p.get("url") or "",
                "download_url": (p.get("src") or {}).get("original") or "",
                "width": p.get("width"),
                "height": p.get("height"),
                "license": "Pexels License (free commercial use)",
            }
        )
    return results


def pixabay_search(api_key: str, query: str, per_page: int) -> List[Dict[str, Any]]:
    ensure_requests()
    base = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": query,
        "image_type": "photo",
        "safesearch": "true",
        "per_page": per_page,
        "order": "popular",
    }
    r = requests.get(base, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    results = []
    for h in data.get("hits", []):
        results.append(
            {
                "site": "Pixabay",
                "title": h.get("tags") or "",
                "author_name": h.get("user") or "",
                "page_url": h.get("pageURL") or "",
                "download_url": h.get("largeImageURL") or h.get("webformatURL") or "",
                "width": h.get("imageWidth"),
                "height": h.get("imageHeight"),
                "license": "Pixabay License (free commercial use)",
            }
        )
    return results


def dedupe(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for it in items:
        key = (it.get("page_url") or "") + "|" + (it.get("download_url") or "")
        if key not in seen and it.get("download_url"):
            seen.add(key)
            out.append(it)
    return out


def download_file(url: str, dest: Path, retries: int = 2):
    ensure_requests()
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(retries + 1):
        try:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            return
        except Exception:
            if attempt == retries:
                raise
            time.sleep(1 + attempt)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch free commercial-use display stand images from Pexels/Pixabay"
    )
    parser.add_argument(
        "--per-category", type=int, default=8, help="Images per category (default 8)"
    )
    parser.add_argument(
        "--sites",
        default="pexels,pixabay",
        help="Comma list of sites to use: pexels,pixabay",
    )
    parser.add_argument(
        "--out-json",
        default="scripts/display_assets.json",
        help="Where to write JSON manifest",
    )
    parser.add_argument(
        "--out-dir",
        default="static/images/displays",
        help="Directory to download images into",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Also download image files into --out-dir/category",
    )
    args = parser.parse_args()

    sites = [s.strip().lower() for s in args.sites.split(",") if s.strip()]
    use_pexels = "pexels" in sites
    use_pixabay = "pixabay" in sites

    pexels_key = os.getenv("PEXELS_API_KEY") if use_pexels else None
    pixabay_key = os.getenv("PIXABAY_API_KEY") if use_pixabay else None

    if use_pexels and not pexels_key:
        print("[warn] PEXELS_API_KEY not set; skipping Pexels")
        use_pexels = False
    if use_pixabay and not pixabay_key:
        print("[warn] PIXABAY_API_KEY not set; skipping Pixabay")
        use_pixabay = False

    if not (use_pexels or use_pixabay):
        raise SystemExit(
            "No image sites enabled. Set API keys and/or adjust --sites."
        )

    all_items: List[Dict[str, Any]] = []

    for category, queries in CATEGORIES.items():
        collected: List[Dict[str, Any]] = []
        needed = args.per_category
        # Try queries in order to bias results
        for q in queries:
            if use_pexels and len(collected) < needed:
                try:
                    res = pexels_search(pexels_key, q, per_page=max(needed, 10))
                    collected.extend(res)
                except Exception as e:
                    print(f"[pexels] {category} '{q}': {e}")
            if use_pixabay and len(collected) < needed:
                try:
                    res = pixabay_search(pixabay_key, q, per_page=max(needed, 20))
                    collected.extend(res)
                except Exception as e:
                    print(f"[pixabay] {category} '{q}': {e}")
            if len(collected) >= needed:
                break

        # Dedupe and trim to needed
        collected = dedupe(collected)[:needed]

        # Attach category label
        for it in collected:
            it["category"] = category

        print(f"[ok] {category}: {len(collected)} images")
        all_items.extend(collected)

    # Write manifest
    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    print(f"Wrote manifest: {out_json}")

    # Download if requested
    if args.download:
        out_dir = Path(args.out_dir)
        for it in all_items:
            cat_slug = slugify(it["category"])[:60]
            site = it.get("site", "site")
            # Stable filename from page_url or download_url
            base = it.get("page_url") or it.get("download_url") or "asset"
            base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-")
            base = base[-80:]
            filename = f"{site.lower()}-{base}.jpg"
            dest = out_dir / cat_slug / filename
            try:
                download_file(it["download_url"], dest)
            except Exception as e:
                print(f"[skip] {dest.name}: {e}")
        print(f"Images saved under: {args.out_dir}")


if __name__ == "__main__":
    main()
