import re
from pathlib import Path

INPUT_FILE = "untranslated_chapters.txt"
OUTPUT_DIR = "cn_chapters"

# ==========================
# LOAD RAW TEXT
# ==========================
raw_text = Path(INPUT_FILE).read_text(encoding="utf-8")

# Normalize line endings (important)
raw_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

# ==========================
# SPLIT BY CHAPTER MARKER
# ==========================
# This regex keeps the chapter title in the result
chapter_blocks = re.split(r"(?=第\d+章)", raw_text)

# Remove any text before the first chapter
chapter_blocks = [blk.strip() for blk in chapter_blocks if blk.strip().startswith("第")]

# ==========================
# OUTPUT DIRECTORY
# ==========================
output_path = Path(OUTPUT_DIR)
output_path.mkdir(exist_ok=True)

# ==========================
# PROCESS EACH CHAPTER
# ==========================
for block in chapter_blocks:
    # Extract chapter number
    match = re.search(r"第(\d+)章", block)
    if not match:
        continue

    chapter_number = match.group(1)

    # Remove duplicated chapter titles (common in EPUBs)
    lines = block.split("\n")
    cleaned_lines = []

    seen_title = False
    for line in lines:
        if re.match(r"第\d+章", line):
            if seen_title:
                continue
            seen_title = True
        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines).strip()

    # Save chapter file
    output_file = output_path / f"ch_{chapter_number}.txt"
    output_file.write_text(cleaned_text, encoding="utf-8")

    print(f"Saved chapter {chapter_number}")

print("Done! All chapters split.")