#!/usr/bin/env bash
set -uo pipefail

OUTDIR="content/products/vase"
IMAGEDIR="static/images/products/vase"
BASE="/images/products/vase"

mkdir -p "$OUTDIR"
shopt -s nullglob

process_series() {
  local series_glob="$1"   # e.g., ceramic-vase-V* or glass-vase-V*
  local material="$2"      # Ceramic or Glass
  local sku_prefix="$3"    # CERAMIC_VASE or GLASS_VASE

  for d in "$IMAGEDIR"/$series_glob; do
    [[ -d "$d" ]] || continue
    bn="$(basename "$d")"               # ceramic-vase-V### or glass-vase-V###
    num="${bn##*-V}"                      # ###

    # Collect images
    mapfile -t imgs < <(ls -1 "$d"/*.{jpg,JPG,jpeg,JPEG,png,PNG} 2>/dev/null || true)
    if (( ${#imgs[@]} == 0 )); then
      continue
    fi

    idx=0
    for img in "${imgs[@]}"; do
      ((idx++))
      imgbase="$(basename "$img")"
      # zero-pad index to two digits
      printf -v idx2 "%02d" "$idx"
      slug_base="${bn}-${idx2}"
      file="$OUTDIR/${slug_base}.md"
      [[ -f "$file" ]] && continue

      title="${material} Vase ${num} – ${idx2}"
      sku="${sku_prefix}_${num}_${idx2}"

      {
        echo "---"
        echo "title: \"$title\""
        echo "category: \"Vase\""
        echo "categories: [\"Vase\"]"
        echo "description: \"$title single-image product\""
        echo "image: \"$BASE/$bn/$imgbase\""
        echo "specifications:"
        echo "  - name: \"Material\""
        echo "    value: \"$material\""
        echo "  - name: \"SKU\""
        echo "    value: \"$sku\""
        echo "---"
        echo "$title — one product per image from $bn."
        echo
        echo "---"
      } > "$file"
      echo "Created $file"
    done
  done
}

process_series "ceramic-vase-V*" "Ceramic" "CERAMIC_VASE"
process_series "glass-vase-V*" "Glass" "GLASS_VASE"

echo "Done generating per-image vase products into $OUTDIR"
