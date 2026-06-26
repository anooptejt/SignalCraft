from pathlib import Path


def collect_manual_linkedin_examples(input_dir: Path) -> list[dict]:
    if not input_dir.exists():
        return []

    items: list[dict] = []
    for path in sorted(input_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        first_line = next((line.strip("# ").strip() for line in text.splitlines() if line.strip()), path.stem)
        items.append(
            {
                "title": first_line,
                "platform": "linkedin",
                "url": None,
                "author": None,
                "summary": text[:320],
                "raw_text": text,
                "metadata_json": {"input_file": str(path)},
            }
        )
    return items
