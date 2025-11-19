#!/usr/bin/env python3
"""
Find all references to .avif images in content files and replace them
with .webp or .jpg if they exist.
"""
import os
from pathlib import Path

def fix_avif_references(content_dir="content/products"):
    content_path = Path(content_dir)
    static_images_path = Path("static/images/products")
    markdown_files = list(content_path.rglob("*.md"))
    total_fixed = 0
    not_found = []

    for md_file in markdown_files:
        try:
            original_content = md_file.read_text(encoding="utf-8")
            new_content = original_content
            
            lines = new_content.splitlines()
            modified_lines = []
            file_modified = False

            for line in lines:
                if ".avif" in line:
                    # Extract image path
                    start = line.find("/images/products/")
                    if start != -1:
                        # Find the end of the path, which could be " or '
                        end_quote = line.find('"', start)
                        if end_quote == -1:
                            end_quote = len(line)

                        avif_rel_path_str = line[start:end_quote]
                        # remove leading slash for path joining
                        avif_fs_path = Path("static") / avif_rel_path_str.lstrip('/')
                        
                        # Check for .webp
                        webp_path = avif_fs_path.with_suffix(".webp")
                        if webp_path.exists():
                            line = line.replace(".avif", ".webp")
                            file_modified = True
                        else:
                            # Check for .jpg
                            jpg_path = avif_fs_path.with_suffix(".jpg")
                            if jpg_path.exists():
                                line = line.replace(".avif", ".jpg")
                                file_modified = True
                            else:
                                # Check for .jpeg
                                jpeg_path = avif_fs_path.with_suffix(".jpeg")
                                if jpeg_path.exists():
                                    line = line.replace(".avif", ".jpeg")
                                    file_modified = True
                                else:
                                    # Check for .png
                                    png_path = avif_fs_path.with_suffix(".png")
                                    if png_path.exists():
                                        line = line.replace(".avif", ".png")
                                        file_modified = True
                                    else:
                                        not_found.append(avif_fs_path)
                modified_lines.append(line)
            
            if file_modified:
                new_content = "\\n".join(modified_lines)
                md_file.write_text(new_content + "\\n", encoding="utf-8")
                total_fixed += 1

        except Exception as e:
            print(f"Error processing {md_file}: {e}")

    print(f"Processed {len(markdown_files)} files.")
    print(f"Fixed {total_fixed} files with AVIF references.")
    if not_found:
        print("\\nWarning: The following AVIF files had no replacement found:")
        for item in not_found:
            print(f"  - {item}")

if __name__ == "__main__":
    fix_avif_references()
