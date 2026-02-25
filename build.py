import re
from pathlib import Path
import subprocess
import shutil
import yaml

SECTIONS_DIR = Path("sections")
TEMPLATE_FILE = Path("template.yaml")
SECTION_PATTERN = re.compile(r"^s_(\d+)(_(.*))?$", re.IGNORECASE)
CHAPTER_PATTERN = re.compile(r"^c_(\d+)(_(.*))?$", re.IGNORECASE)
OUTPUT_DIR = Path("output")
OUTPUT_MD = OUTPUT_DIR / "full_doc.md"
FINAL_RESULTS_DIR = Path.home() / "Downloads"


def get_metadata_title() -> str:
    """Read metadata.title from template.yaml using a safe YAML parser."""
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as template_file:
        template_data = yaml.safe_load(template_file) or {}

    metadata = template_data.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError(f"Missing or invalid 'metadata' in {TEMPLATE_FILE}")

    md_title = metadata.get("title")
    if not isinstance(md_title, str) or not md_title.strip():
        raise ValueError(f"Missing or invalid 'metadata.title' in {TEMPLATE_FILE}")

    return md_title.strip() + ".pdf"


md_title = get_metadata_title()
OUTPUT_PDF = FINAL_RESULTS_DIR / md_title


def get_section_dirs():
    """Get all section directories sorted by number."""
    return sorted(
        [
            d
            for d in SECTIONS_DIR.iterdir()
            if d.is_dir() and SECTION_PATTERN.match(d.name)
        ],
        key=lambda p: int(SECTION_PATTERN.match(p.name).group(1)),
    )


def get_chapter_dirs(section_path):
    """Get all chapter directories within a section, sorted by number."""
    return sorted(
        [
            d
            for d in section_path.iterdir()
            if d.is_dir() and CHAPTER_PATTERN.match(d.name)
        ],
        key=lambda p: int(CHAPTER_PATTERN.match(p.name).group(1)),
    )


def copy_images_and_process_content(
    content: str,
    source_path: Path,
    prefix: str,
    is_section: bool = False,
    section_num: int = 0,
    chapter_num: int = 0,
) -> str:
    """Process content: handle title and copy images."""
    lines = content.splitlines()
    result_lines = []
    title_found = False
    subchapter_counter = 0
    topic_counter = 0

    image_regex = re.compile(r"!\[([^\]]*)\]\(resources/([^)]+)\)")

    # Create images directory in output
    images_dir = OUTPUT_DIR / "images"
    images_dir.mkdir(exist_ok=True)

    for line in lines:
        stripped = line.strip()

        # Handle headings
        if stripped.startswith("#"):
            raw_title = stripped.lstrip("#").strip()
            heading_level = len(stripped) - len(stripped.lstrip("#"))

            if not title_found:
                # First heading is the main title
                if is_section:
                    # Section titles - level 1 with manual numbering (no .unnumbered to keep in bookmarks)
                    result_lines.append(f"# {section_num}. {raw_title}")
                else:
                    # Chapter titles - level 2 with manual numbering (no .unnumbered to keep in bookmarks)
                    result_lines.append(f"## {section_num}.{chapter_num} {raw_title}")
                title_found = True
            elif heading_level == 2 and not is_section:
                # Sub-chapters within a chapter (original ## headings become ###)
                subchapter_counter += 1
                topic_counter = 0
                result_lines.append(
                    f"### {section_num}.{chapter_num}.{subchapter_counter} {raw_title}"
                )
            else:
                # All other headings - shift down by 1 level (add one #) and mark unnumbered
                shifted_level = heading_level + 1

                # Number original ### headings (now ####) under the current sub-chapter.
                if not is_section and heading_level == 3:
                    topic_counter += 1
                    current_subchapter = (
                        subchapter_counter if subchapter_counter > 0 else 1
                    )
                    shifted_heading = (
                        "#" * shifted_level
                        + f" {section_num}.{chapter_num}.{current_subchapter}.{topic_counter} {raw_title} {{.unnumbered}}"
                    )
                else:
                    shifted_heading = (
                        "#" * shifted_level + " " + raw_title + " {.unnumbered}"
                    )
                result_lines.append(shifted_heading)
        else:
            # Handle image references
            def replace_image(match):
                alt_text = match.group(1)
                image_file = match.group(2)
                source_image = source_path / "resources" / image_file

                if source_image.exists():
                    # Copy image to output/images with prefix
                    dest_image = images_dir / f"{prefix}_{image_file}"
                    shutil.copy2(source_image, dest_image)
                    return f"![{alt_text}](output/images/{dest_image.name})"
                else:
                    print(f"[WARNING] Image not found: {source_image}")
                    return match.group(0)

            line = image_regex.sub(replace_image, line)
            result_lines.append(line)

    return "\n".join(result_lines)


def concatenate_markdown():
    """Build the full document from sections and chapters."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(OUTPUT_MD, "w", encoding="utf-8") as outfile:
        section_dirs = get_section_dirs()

        for section_idx, section_path in enumerate(section_dirs, start=1):
            section_match = SECTION_PATTERN.match(section_path.name)
            section_number = int(section_match.group(1))

            # Process section's main content.md (the part header)
            section_content_file = section_path / "content.md"
            if section_content_file.exists():
                content = section_content_file.read_text(encoding="utf-8")
                processed = copy_images_and_process_content(
                    content,
                    section_path,
                    f"s_{section_number:02d}",
                    is_section=True,
                    section_num=section_idx,
                )
                outfile.write(processed + "\n\n")
                outfile.write("\\newpage\n\n")
            else:
                print(f"[Warning] {section_content_file} not found.")

            # Process chapters within this section
            chapter_dirs = get_chapter_dirs(section_path)
            for chapter_idx, chapter_path in enumerate(chapter_dirs, start=1):
                chapter_match = CHAPTER_PATTERN.match(chapter_path.name)
                chapter_number = int(chapter_match.group(1))

                chapter_content_file = chapter_path / "content.md"
                if chapter_content_file.exists():
                    content = chapter_content_file.read_text(encoding="utf-8")
                    processed = copy_images_and_process_content(
                        content,
                        chapter_path,
                        f"s_{section_number:02d}_c_{chapter_number:02d}",
                        is_section=False,
                        section_num=section_idx,
                        chapter_num=chapter_idx,
                    )
                    outfile.write(processed + "\n\n")
                else:
                    print(f"[Warning] {chapter_content_file} not found.")


def convert_to_pdf():
    """Convert the markdown to PDF using pandoc."""
    cmd = [
        "pandoc",
        str(OUTPUT_MD),
        "-o",
        str(OUTPUT_PDF),
        "--defaults",
        str(TEMPLATE_FILE),
    ]
    subprocess.run(cmd, check=True)
    print(f"✅ PDF generated at {OUTPUT_PDF}")


if __name__ == "__main__":
    print("📚 Building document from sections and chapters...")
    concatenate_markdown()
    convert_to_pdf()
