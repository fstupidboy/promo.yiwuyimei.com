#!/usr/bin/env bash
set -euo pipefail

OUTDIR="content/products/ceramic-vase"
IMAGEDIR="static/images/products/vase"
BASE="/images/products/vase"

mkdir -p "$OUTDIR"
shopt -s nullglob

for d in "$IMAGEDIR"/ceramic-vase-V*; do
  bn="$(basename "$d")"          # ceramic-vase-V###
  num="${bn##ceramic-vase-V}"      # ### part
  slug="$bn"                       # keep full
  file="$OUTDIR/$slug.md"
  [[ -f "$file" ]] && continue

  # Collect images (jpg/png only)
  imgs=("$d"/*.{jpg,JPG,jpeg,JPEG,png,PNG})
  if [[ "${imgs[0]}" == "$d/*.{jpg,JPG,jpeg,JPEG,png,PNG}" ]]; then
    unset imgs[0]
  fi
  main=""
  gallery=()
  if (( ${#imgs[@]} > 0 )); then
    main="$(basename "${imgs[0]}")"
    if (( ${#imgs[@]} > 1 )); then
      for ((i=1;i<${#imgs[@]};i++)); do
        gallery+=("$(basename "${imgs[$i]}")")
      done
    fi
  fi

  # Title: Ceramic Vase V###
  title="Ceramic Vase ${num}"
  sku="CERAMIC_VASE_${num}"

  {
    echo "---"
    echo "title: \"$title\""
    echo "category: \"Vase\""
    echo "categories: [\"Vase\"]"
    echo "description: \"$title promotional ceramic vase item\""
    if [[ -n "$main" ]]; then
      echo "image: \"$BASE/$slug/$main\""
    fi
    echo "specifications:"
    echo "  - name: \"Material\""
    echo "    value: \"Ceramic\""
    echo "  - name: \"SKU\""
    echo "    value: \"$sku\""
    if (( ${#gallery[@]} > 0 )); then
      echo "gallery:"
      for g in "${gallery[@]}"; do
        echo "  - \"$BASE/$slug/$g\""
      done
    fi
    echo "---"
    echo "$title – grouped Ceramic Vase product comprising ${#imgs[@]} images."
    echo
    echo "---"
  } > "$file"
  echo "Created $file"
done
