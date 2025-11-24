#!/usr/bin/env bash
set -euo pipefail

OUTDIR="content/products/metal-crafts"
BASE="/images/products/metal-crafts"

shopt -s nullglob
for d in static/images/products/metal-crafts/car-vent-clip-*; do
  bn="$(basename "$d")"
  slug="$bn"
  file="$OUTDIR/$slug.md"
  if [[ -f "$file" ]]; then
    continue
  fi
  # Build title by capitalizing each hyphen-separated part
  raw="${slug//-/ }"
  title=""
  for w in $raw; do
    # capitalize first letter
    first="${w:0:1}"
    rest="${w:1}"
    title+="${first^^}${rest} "
  done
  title="${title%% }"

  # Select main image (first jpg/png) and gallery (remaining jpg/png)
  images=("$d"/*.{jpg,JPG,jpeg,JPEG,png,PNG})
  # Remove any literal pattern if no match
  if [[ "${images[0]}" == "$d/*.{jpg,JPG,jpeg,JPEG,png,PNG}" ]]; then
    unset images[0]
  fi
  main=""
  gallery=()
  if (( ${#images[@]} > 0 )); then
    main="$(basename "${images[0]}")"
    if (( ${#images[@]} > 1 )); then
      for ((i=1;i<${#images[@]};i++)); do
        gallery+=("$(basename "${images[$i]}")")
      done
    fi
  fi

  sku="$(echo "$slug" | tr '[:lower:]' '[:upper:]' | tr '-' '_')"

  {
    echo "---"
    echo "title: \"$title\""
    echo "category: \"Metal Crafts\""
    echo "categories: [\"Metal Crafts\"]"
    echo "description: \"$slug promotional Metal Crafts item\""
    if [[ -n "$main" ]]; then
      echo "image: \"$BASE/$slug/$main\""
    fi
    echo "specifications:"
    echo "  - name: \"Material\""
    echo "    value: \"Metal\""
    echo "  - name: \"SKU\""
    echo "    value: \"$sku\""
    if (( ${#gallery[@]} > 0 )); then
      echo "gallery:"
      for g in "${gallery[@]}"; do
        echo "  - \"$BASE/$slug/$g\""
      done
    fi
    echo "---"
    echo "$title – grouped Metal Crafts product."
    echo
    echo "---"
  } > "$file"
  echo "Created $file"
done
