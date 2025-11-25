#!/usr/bin/env bash
set -euo pipefail

IMGDIR="static/images/products/toys"
OUTDIR="content/products/toys"
BASE="/images/products/toys"
mkdir -p "$OUTDIR"
shopt -s nullglob

# Generate one product per JPG/PNG; pair webp ignored to avoid duplicates.

slugify() {
  local s="$1"
  s="$(echo "$s" | tr 'A-Z' 'a-z' | sed 's/ /-/g')"
  s="$(echo "$s" | sed 's/[^a-z0-9-]//g' | sed 's/--\+/-/g' | sed 's/^-//;s/-$//')"
  echo "$s"
}

for img in "$IMGDIR"/*.{jpg,JPG,jpeg,JPEG,png,PNG}; do
  [[ -f "$img" ]] || continue
  bn="$(basename "$img")"
  stem="${bn%.*}"
  slug="toy-$(slugify "$stem")"
  mdfile="$OUTDIR/${slug}.md"
  title="${stem}"  # Keep original capitalization
  sku="TOY_$(echo "$slug" | tr 'a-z-' 'A-Z_')"

  if [[ -f "$mdfile" ]]; then
    # Repair front matter if first line is not '---'
    if ! head -n1 "$mdfile" | grep -q '^---$'; then
      {
        echo '---'
        echo "title: \"$title\""
        echo 'category: "Toys"'
        echo 'categories: ["Toys"]'
        echo "description: \"$title single-image toy product\""
        echo "image: \"$BASE/$bn\""
        echo 'specifications:'
        echo '  - name: "SKU"'
        echo "    value: \"$sku\""
        echo '---'
        echo
        echo '---'
      } > "$mdfile"
      echo "Repaired $mdfile"
    fi
    continue
  fi

  {
    echo '---'
    echo "title: \"$title\""
    echo 'category: "Toys"'
    echo 'categories: ["Toys"]'
    echo "description: \"$title single-image toy product\""
    echo "image: \"$BASE/$bn\""
    echo 'specifications:'
    echo '  - name: "SKU"'
    echo "    value: \"$sku\""
    echo '---'
    echo
    echo '---'
  } > "$mdfile"
  echo "Created $mdfile"
done

echo "Done generating per-image toy products into $OUTDIR"
