#!/usr/bin/env bash
set -euo pipefail

OUTDIR="content/products/drinkware"
IMAGEDIR="static/images/products/drinkware"
BASE="/images/products/drinkware"

mkdir -p "$OUTDIR"
shopt -s nullglob

slugify() {
  local name="$1"
  # try extract a 3+ digit code (e.g., 815) for stable IDs
  local code
  code="$(echo "$name" | grep -oE '[0-9]{3,}' | head -n1 || true)"
  if [[ -n "${code:-}" ]]; then
    echo "drinkware-${code}"
    return
  fi
  # fallback: ascii-lower, spaces to -, strip invalids
  local s
  s="$(echo "$name" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')"
  s="$(echo "$s" | sed 's/[^a-z0-9_-]/-/g' | sed 's/--\+/-/g' | sed 's/^-\+//; s/-\+$//')"
  if [[ -z "$s" ]]; then
    # ultimate fallback: timestamp-based unique slug
    s="drinkware-$(date +%s%N)"
  fi
  echo "$s"
}

for img in "$IMAGEDIR"/*.{jpg,JPG,jpeg,JPEG,png,PNG}; do
  [[ -f "$img" ]] || continue
  bn="$(basename "$img")"
  stem="${bn%.*}"
  slug="$(slugify "$stem")"
  file="$OUTDIR/${slug}.md"
  [[ -f "$file" ]] && continue

  title="$stem"
  sku="DRINKWARE_$(echo "$slug" | tr '[:lower:]' '[:upper:]' | tr '-' '_')"

  {
    echo "---"
    echo "title: \"$title\""
    echo "category: \"Drinkware\""
    echo "categories: [\"Drinkware\"]"
    echo "description: \"$title single-image product\""
    echo "image: \"$BASE/$bn\""
    echo "specifications:"
    echo "  - name: \"SKU\""
    echo "    value: \"$sku\""
    echo "---"
    echo "$title — one product per image."
    echo
    echo "---"
  } > "$file"
  echo "Created $file"
done

echo "Done generating per-image drinkware products into $OUTDIR"
