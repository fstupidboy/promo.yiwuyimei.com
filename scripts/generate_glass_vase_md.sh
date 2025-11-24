#!/usr/bin/env bash
set -euo pipefail

OUTDIR="content/products/glass-vase"
IMAGEDIR="static/images/products/vase"
BASE="/images/products/vase"

mkdir -p "$OUTDIR"
shopt -s nullglob

for d in "$IMAGEDIR"/glass-vase-V*; do
  bn="$(basename "$d")"          # glass-vase-V###
  num="${bn##glass-vase-V}"        # ### part
  slug="$bn"
  file="$OUTDIR/$slug.md"
  [[ -f "$file" ]] && continue

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

  title="Glass Vase ${num}"
  sku="GLASS_VASE_${num}"

  {
    echo "---"
    echo "title: \"$title\""
    echo "category: \"Glass Vase\""
    echo "categories: [\"Glass Vase\"]"
    echo "description: \"$title promotional glass vase item\""
    if [[ -n "$main" ]]; then
      echo "image: \"$BASE/$slug/$main\""
    fi
    echo "specifications:"
    echo "  - name: \"Material\""
    echo "    value: \"Glass\""
    echo "  - name: \"SKU\""
    echo "    value: \"$sku\""
    if (( ${#gallery[@]} > 0 )); then
      echo "gallery:"
      for g in "${gallery[@]}"; do
        echo "  - \"$BASE/$slug/$g\""
      done
    fi
    echo "---"
    echo "$title – grouped Glass Vase product comprising ${#imgs[@]} images."
    echo
    echo "---"
  } > "$file"
  echo "Created $file"
done
