#!/usr/bin/env bash
set -uo pipefail

# Generate one product per JPG (primary) for ceramic mugs with sequential slugs.
# Range derived from recovered history CM806..CM825 => 20 items.

IMGDIR="static/images/products/ceramic-mugs"
OUTDIR="content/products/ceramic-mugs"
BASE="/images/products/ceramic-mugs"
START=806
END=825

mkdir -p "$OUTDIR"

seq_index=0
for code in $(seq $START $END); do
  jpg=$(ls "$IMGDIR"/*${code}_2.jpg 2>/dev/null || true)
  echo "Debug: code=$code jpg='$jpg'" >&2
  if [[ -z "$jpg" ]]; then
    continue
  fi
  ((seq_index++))
  printf -v seq_slug "%03d" "$seq_index"  # 001,002,...
  file_slug="ceramic-mugs-${seq_slug}"
  mdfile="$OUTDIR/${file_slug}.md"
  [[ -f "$mdfile" ]] && continue

  title="Ceramic Mugs ${seq_slug}"
  sku="CERAMIC_MUGS_${seq_slug}"
  old_slug="cm${code}"  # old lowercase path
  img_file="$(basename "$jpg")"

  echo "Debug: writing $mdfile" >&2
  {
    echo "---"
    echo "title: \"$title\""
    echo "category: \"Ceramic Mugs\""
    echo "categories: [\"Ceramic Mugs\"]"
    echo "description: \"$title product item\""
    echo "image: \"$BASE/$img_file\""
    echo "specifications:"
    echo "  - name: \"Material\""
    echo "    value: \"Ceramic\""
    echo "  - name: \"SKU\""
    echo "    value: \"$sku\""
    echo "aliases: [\"/products/ceramic-mugs/${old_slug}/\"]"
    echo "---"
    echo "$title — sequential ceramic mug (original code CM${code})."
    echo
    echo "---"
  } > "$mdfile"
  echo "Created $mdfile (from CM${code})"
done

echo "Generated $seq_index ceramic mug markdown files into $OUTDIR"
