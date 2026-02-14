# from pathlib import Path
# import json
# from typing import List, Dict


# CHUNK_SIZE = 800  # approx words per chunk


# def chunk_sections(
#     sections: List[Dict]
# ) -> List[Dict]:
#     """
#     Chunk normalized TMEP sections into NON-overlapping chunks.
#     """

#     chunks: List[Dict] = []

#     for section in sections:
#         words = section["text"].split()
#         chunk_index = 0

#         for start in range(0, len(words), CHUNK_SIZE):
#             end = start + CHUNK_SIZE
#             chunk_words = words[start:end]

#             chunk_text = " ".join(chunk_words).strip()

#             if not chunk_text:
#                 continue

#             chunks.append({
#                 "chunk_id": f"{section['section_id']}_{chunk_index:04d}",
#                 "section_id": section["section_id"],
#                 "section_title": section["section_title"],
#                 "section_path": section["section_path"],
#                 "chunk_text": chunk_text,
#                 "chunk_index": chunk_index,
#                 "source": section["source"],
#                 "doc_version": section["doc_version"]
#             })

#             chunk_index += 1

#     return chunks


# def save_chunks(
#     chunks: List[Dict],
#     output_path: Path
# ) -> None:
#     output_path.parent.mkdir(parents=True, exist_ok=True)

#     with output_path.open("w", encoding="utf-8") as f:
#         json.dump(chunks, f, indent=2, ensure_ascii=False)

from pathlib import Path
import json
from typing import List, Dict


def chunk_sections(sections: List[Dict], source_file: str) -> List[Dict]:
    """
    LEGAL-GRADE chunking with globally unique IDs.

    - section_id: legal citation (e.g. 109.03)
    - chunk_id: globally unique (file + section + ordinal)
    """

    chunks: List[Dict] = []

    # Counter per section_id to avoid collisions
    section_counter: dict[str, int] = {}

    for section in sections:
        text = section["text"].strip()
        if not text:
            continue

        sid = section["section_id"]

        # Increment counter for repeated section IDs
        count = section_counter.get(sid, 0)
        section_counter[sid] = count + 1

        chunk_id = f"{source_file}::{sid}::{count}"

        chunks.append({
            # ✅ TECHNICAL identity (unique)
            "chunk_id": chunk_id,

            # ✅ LEGAL identity
            "section_id": sid,
            "section_title": section["section_title"],
            "section_path": section["section_path"],

            "chunk_text": text,

            "source": section["source"],
            "doc_version": section["doc_version"],
            "order": section["order"],
            "source_file": source_file,
        })

    return chunks


def save_chunks(chunks: List[Dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
