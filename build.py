import re
from pathlib import Path
import subprocess
import shutil

CHAPTERS_DIR = Path("chapters")
TEMPLATE_FILE = Path("template.yaml")
CHAPTER_PATTERN = re.compile(r"^c_(\d+)(_(.*))?$", re.IGNORECASE)
OUTPUT_DIR = Path("output")
OUTPUT_MD = OUTPUT_DIR / "full_doc.md"
OUTPUT_PDF = OUTPUT_DIR / "full_doc.pdf"

def get_chapter_dirs():
    return sorted(
        [d for d in CHAPTERS_DIR.iterdir() if d.is_dir() and CHAPTER_PATTERN.match(d.name)],
        key=lambda p: int(CHAPTER_PATTERN.match(p.name).group(1))
    )


def copy_images_and_process_chapter(chapter_number: int, content: str, chapter_path: Path) -> str:
    lines = content.splitlines()
    result_lines = []
    title_found = False

    chapter_prefix_regex = re.compile(r"^chapter\s+\d+\s*:\s*", re.IGNORECASE)
    image_regex = re.compile(r'!\[([^\]]*)\]\(resources/([^)]+)\)')

    # Create images directory in output
    images_dir = OUTPUT_DIR / "images"
    images_dir.mkdir(exist_ok=True)

    for line in lines:
        stripped = line.strip()
        if not title_found and stripped.startswith("#"):
            # Strip all leading #
            raw_title = stripped.lstrip("#").strip()

            # Remove "Chapter X:" if already present
            cleaned_title = chapter_prefix_regex.sub("", raw_title)

            # Add our consistent prefix
            result_lines.append(f"# {cleaned_title}")
            title_found = True
        else:
            # Handle image references
            def replace_image(match):
                alt_text = match.group(1)
                image_file = match.group(2)
                source_image = chapter_path / "resources" / image_file
                
                if source_image.exists():
                    # Copy image to output/images with chapter prefix
                    dest_image = images_dir / f"c_{chapter_number:02d}_{image_file}"
                    shutil.copy2(source_image, dest_image)
                    # Return markdown with new path relative to where pandoc runs
                    return f"![{alt_text}](output/images/{dest_image.name})"
                else:
                    print(f"[WARNING] Image not found: {source_image}")
                    return match.group(0)  # Return original if image not found
            
            line = image_regex.sub(replace_image, line)
            result_lines.append(line)

    return "\n".join(result_lines)


def concatenate_markdown(chapter_dirs):
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_MD, "w", encoding="utf-8") as outfile:
        for chapter_path in chapter_dirs:
            match = CHAPTER_PATTERN.match(chapter_path.name)
            chapter_number = int(match.group(1))
            content_file = chapter_path / "content.md"

            if content_file.exists():
                content = content_file.read_text(encoding="utf-8")
                processed = copy_images_and_process_chapter(chapter_number, content, chapter_path)
                outfile.write(processed + "\n\n")
            else:
                print(f"[Warning] {content_file} not found.")

def convert_to_pdf():
    cmd = [
        "pandoc",
        str(OUTPUT_MD),
        "-o", str(OUTPUT_PDF),
        "--defaults", str(TEMPLATE_FILE),
    ]
    subprocess.run(cmd, check=True)
    print(f"✅ PDF generated at {OUTPUT_PDF}")

if __name__ == "__main__":
    print("📚 Building document from chapters...")
    chapters = get_chapter_dirs()
    concatenate_markdown(chapters)
    convert_to_pdf()