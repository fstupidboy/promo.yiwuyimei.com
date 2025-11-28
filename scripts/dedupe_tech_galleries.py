#!/usr/bin/env python3
import re
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
MD_DIR = ROOT / 'content' / 'products' / 'tech-items'

frontmatter_re = re.compile(r"^---\n(.*?)\n---\n", re.S)
image_re = re.compile(r"^image:\s*(?:\"([^\"]+)\"|(\S+))", re.M)
gallery_start_re = re.compile(r"^gallery:\s*$", re.M)
gallery_item_re = re.compile(r"^\s*-\s*(?:\"([^\"]+)\"|(\S+))\s*$")

def dedupe_gallery(items, preferred_ext=None):
    # items: list of paths (strings)
    by_stem = {}
    order = []
    for p in items:
        stem = os.path.splitext(os.path.basename(p))[0]
        ext = os.path.splitext(p)[1].lower()
        if stem not in by_stem:
            by_stem[stem] = {}
            order.append(stem)
        by_stem[stem][ext] = p
    out = []
    for stem in order:
        opts = by_stem[stem]
        chosen = None
        if preferred_ext:
            pe = preferred_ext.lower()
            if pe in opts:
                chosen = opts[pe]
        if not chosen:
            # prefer .jpg, .png, .webp in that order
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                if ext in opts:
                    chosen = opts[ext]
                    break
        if not chosen:
            # fallback to any
            chosen = next(iter(opts.values()))
        out.append(chosen)
    return out


def process_file(path: Path):
    text = path.read_text(encoding='utf-8')
    m = frontmatter_re.search(text)
    if not m:
        return False, 'no frontmatter'
    fm = m.group(1)
    # find image
    im = None
    mi = image_re.search(fm)
    if mi:
        im = mi.group(1) or mi.group(2)
    preferred_ext = None
    if im:
        preferred_ext = os.path.splitext(im)[1].lower()
    # find gallery block start
    gstart = gallery_start_re.search(fm)
    if not gstart:
        return False, 'no gallery'
    # get lines after gallery: in fm
    lines = fm.splitlines()
    gallery_idx = None
    for i,l in enumerate(lines):
        if l.strip() == 'gallery:':
            gallery_idx = i
            break
    if gallery_idx is None:
        return False, 'no gallery idx'
    # collect gallery items starting at gallery_idx+1 while lines start with whitespace and '-'
    items = []
    i = gallery_idx + 1
    while i < len(lines):
        line = lines[i]
        if line.strip() == '':
            i += 1
            continue
        if re.match(r"^\s*-\s*", line):
            m_item = gallery_item_re.match(line)
            if m_item:
                val = m_item.group(1) or m_item.group(2)
                items.append(val)
                i += 1
                continue
            else:
                break
        else:
            break
    if not items:
        return False, 'no items'
    new_items = dedupe_gallery(items, preferred_ext)
    if len(new_items) == len(items):
        return False, 'no change'
    # Reconstruct the gallery block text
    # Determine indentation from original gallery items
    indent = None
    for j in range(gallery_idx+1, gallery_idx+6):
        if j < len(lines):
            if lines[j].strip().startswith('-') or re.match(r"^\s*-\s*", lines[j]):
                indent = lines[j][:lines[j].find('-')]
                break
    if indent is None:
        indent = '  '
    new_block_lines = ['gallery:']
    for it in new_items:
        # keep same quoting style as original (use double quotes)
        new_block_lines.append(f"{indent}- \"{it}\"")
    # replace the original gallery section in fm with new_block
    # find start index in fm string
    fm_lines = fm.splitlines()
    start = gallery_idx
    end = i  # one past last gallery item
    new_fm_lines = fm_lines[:start] + new_block_lines + fm_lines[end:]
    new_fm = '\n'.join(new_fm_lines)
    # replace frontmatter in text
    new_text = text[:m.start(1)] + new_fm + text[m.end(1):]
    path.write_text(new_text, encoding='utf-8')
    return True, f'changed {len(items)}->{len(new_items)}'


if __name__ == '__main__':
    md_files = sorted(MD_DIR.glob('*.md'))
    total = 0
    changed = 0
    for p in md_files:
        total += 1
        ok, msg = process_file(p)
        if ok:
            changed += 1
            print(f'Updated: {p.name} -> {msg}')
        else:
            print(f'Skipped: {p.name} ({msg})')
    print(f'Done. Processed {total} files, updated {changed}.')
