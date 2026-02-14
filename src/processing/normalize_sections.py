from pathlib import Path
import json
import re


DOC_VERSION = "TMEP Nov 2025"
SOURCE_NAME = "USPTO TMEP"


def normalize_sections(
    sections: list[dict]
) -> list[dict]:
    """
    Normalize and validate parsed TMEP sections.
    Returns a clean list of sections ready for chunking.
    """

    normalized: list[dict] = []

    for idx, section in enumerate(sections):
        section_id = _normalize_section_id(section.get("section_id"))
        if not section_id:
            continue
        section_title = _normalize_title(section.get("section_title"))
        text = _normalize_text(section.get("full_text"))

        # Validation: skip empty or broken sections
        if not text or len(text) < 50:
            continue

        normalized.append({
            "section_id": section_id,
            "section_title": section_title,
            "section_path": _build_section_path(section_id, section_title),
            "text": text,
            "source": SOURCE_NAME,
            "doc_version": DOC_VERSION,
            "order": idx
        })

    return normalized


def _normalize_section_id(section_id: str | None) -> str | None:
    if not section_id:
        return None

    section_id = section_id.strip()

    # Ensure consistent formatting (no trailing dots/spaces)
    section_id = re.sub(r"\s+", "", section_id)

    return section_id


def _normalize_title(title: str | None) -> str:
    if not title:
        return ""

    title = title.strip()
    title = re.sub(r"\s+", " ", title)

    return title


def _normalize_text(text: str | None) -> str:
    if not text:
        return ""

    # Normalize whitespace
    text = text.replace("\xa0", " ")
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def _build_section_path(section_id: str | None, title: str) -> str:
    if section_id:
        return f"{section_id} {title}".strip()
    return title


def save_normalized_sections(
    sections: list[dict],
    output_path: Path
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)
