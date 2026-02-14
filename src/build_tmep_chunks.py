from pathlib import Path
import json

from src.parsing.parse_tmep_html import parse_tmep_html
from src.processing.normalize_sections import normalize_sections
from src.processing.chunk_sections import chunk_sections



# ---------------------------------------
# Paths (MATCH YOUR PROJECT STRUCTURE)
# ---------------------------------------
RAW_HTML_DIR = Path(
    "data/raw/tmep-nov2025-html/TMEP"
)
OUTPUT_CHUNKS = Path(
    "data/chunks/tmep_chunks.json"
)


def main():
    all_chunks = []
    seen_chunk_ids = set()

    html_files = sorted(RAW_HTML_DIR.glob("*.html"))

    print(f"📄 Found {len(html_files)} TMEP HTML files")

    for html_file in html_files:
        print(f"→ Processing {html_file.name}")

        # 1️⃣ Parse
        parsed = parse_tmep_html(html_file)

        # 2️⃣ Normalize
        normalized = normalize_sections(parsed)

        # 3️⃣ Chunk (1 section = 1 chunk)
        source_file = html_file.name
        chunks = chunk_sections(normalized, source_file)


        # 4️⃣ Validate + collect
        for chunk in chunks:
            cid = chunk["chunk_id"]
            if cid in seen_chunk_ids:
                raise ValueError(
                    f"Duplicate chunk_id detected: {cid}"
                )
            seen_chunk_ids.add(cid)
            all_chunks.append(chunk)

    # 5️⃣ Save output
    OUTPUT_CHUNKS.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_CHUNKS.write_text(
        json.dumps(all_chunks, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("=" * 60)
    print(f"✅ Total chunks created: {len(all_chunks)}")
    print(f"📁 Output file: {OUTPUT_CHUNKS}")
    print("=" * 60)


if __name__ == "__main__":
    main()
