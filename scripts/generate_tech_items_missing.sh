#!/usr/bin/env bash
set -euo pipefail

ROOT="static/images/products/tech-items"
OUT="content/products/tech-items"
BASE="/images/products/tech-items"
mkdir -p "$OUT"

# Extensions priority for main image
exts=(avif png jpg jpeg webp)

has_md() { local slug="$1"; [[ -f "$OUT/$slug.md" ]]; }

pick_main() {
  local dir="$1"; for e in "${exts[@]}"; do
    local f=("$dir"/*."$e"); if [[ -f "${f[0]:-}" ]]; then echo "$(basename "${f[0]}")"; return 0; fi; done; return 1;
}

gather_gallery() {
  local dir="$1" main="$2"; local g=();
  for f in "$dir"/*; do
    [[ -f "$f" ]] || continue
    bn="$(basename "$f")"
    [[ "$bn" == "$main" ]] && continue
    case "$bn" in *.avif|*.png|*.jpg|*.jpeg|*.webp) g+=("$bn");; esac
  done
  printf '%s\n' "${g[@]}"
}

slugify() { echo "$1" | tr 'A-Z ' 'a-z-' | sed 's/--\+/-/g' | sed 's/[^a-z0-9-]//g'; }

create_md() {
  local dir="$1"; local base_dir="$(basename "$dir")"; local slug
  slug="$(slugify "$base_dir")"
  # preserve existing hyphenated numeric slug exactly if already proper
  if [[ "$base_dir" =~ ^[a-z0-9-]+$ ]]; then slug="$base_dir"; fi
  has_md "$slug" && return
  main="$(pick_main "$dir" || true)" || true
  [[ -z "$main" ]] && echo "Skip $base_dir (no image)" && return
  mapfile -t gallery < <(gather_gallery "$dir" "$main")
  sku="$(echo "$slug" | tr 'a-z-' 'A-Z_')"
  title="$(echo "$base_dir" | sed 's/-/ /g' | sed 's/\b\([a-z]\)/\u\1/g')"
  file="$OUT/$slug.md"
  {
    echo '---'
    echo "title: \"$title\""
    echo 'category: "Tech Items"'
    echo 'categories: ["Tech Items"]'
    echo "description: \"$title promotional tech item\""
    echo "image: \"$BASE/$base_dir/$main\""
    echo 'specifications:'
    echo '  - name: "SKU"'
    echo "    value: \"$sku\""
    if ((${#gallery[@]})); then
      echo 'gallery:'
      for g in "${gallery[@]}"; do
        echo "  - \"$BASE/$base_dir/$g\""
      done
    fi
    echo '---'
    echo "$title tech item page generated from directory $base_dir."
    echo; echo '---'
  } > "$file"
  echo "Created $file"
}

while IFS= read -r -d '' d; do
  create_md "$d"
done < <(find "$ROOT" -maxdepth 1 -mindepth 1 -type d -print0)

echo 'Done generating missing tech-items markdown.'
