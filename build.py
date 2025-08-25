import re
from pathlib import Path
import subprocess

CHAPTERS_DIR = Path("chapters")
TEMPLATE_FILE = Path("template.yaml")
CHAPTER_PATTERN = re.compile(r"^c_(\d+)$", re.IGNORECASE)
OUTPUT_DIR = Path("output")
OUTPUT_MD = OUTPUT_DIR / "full_doc.md"
OUTPUT_PDF = OUTPUT_DIR / "full_doc.pdf"

def get_chapter_dirs():
    return sorted(
        [d for d in CHAPTERS_DIR.iterdir() if d.is_dir() and CHAPTER_PATTERN.match(d.name)],
        key=lambda p: int(CHAPTER_PATTERN.match(p.name).group(1))
    )


def process_chapter(chapter_number: int, content: str, chapter_path: Path) -> str:
    lines = content.splitlines()
    result_lines = []
    title_found = False

    chapter_prefix_regex = re.compile(r"^chapter\s+\d+\s*:\s*", re.IGNORECASE)

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
            result_lines.append(line)

    result = "\n".join(result_lines)
    result = result.replace("resources/", f"../{chapter_path}/resources/")
    return result


def concatenate_markdown(chapter_dirs):
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_MD, "w", encoding="utf-8") as outfile:
        for chapter_path in chapter_dirs:
            match = CHAPTER_PATTERN.match(chapter_path.name)
            chapter_number = int(match.group(1))
            content_file = chapter_path / "content.md"

            if content_file.exists():
                content = content_file.read_text(encoding="utf-8")
                processed = process_chapter(chapter_number, content, chapter_path)
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