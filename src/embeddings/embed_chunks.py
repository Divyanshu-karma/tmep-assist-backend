# from pathlib import Path
# from typing import List, Dict
# import json
# import torch

# from .model import tokenizer, model, mean_pooling


# def embed_chunks(
#     chunks: List[Dict],
#     batch_size: int = 16
# ) -> List[Dict]:
#     """
#     Generate embeddings for NON-overlapping TMEP chunks.

#     Assumptions:
#     - chunk_id is stable and deterministic
#     - chunk_text is the single source of semantic truth
#     - embeddings are regenerated whenever chunks change
#     """

#     embedded_chunks: List[Dict] = []

#     for i in range(0, len(chunks), batch_size):
#         batch = chunks[i:i + batch_size]

#         # E5 passage-format prompting (correct)
#         texts = [f"passage: {c['chunk_text']}" for c in batch]

#         inputs = tokenizer(
#             texts,
#             padding=True,
#             truncation=True,
#             max_length=512,
#             return_tensors="pt"
#         )

#         with torch.no_grad():
#             outputs = model(**inputs)
#             embeddings = mean_pooling(
#                 outputs.last_hidden_state,
#                 inputs["attention_mask"]
#             )

#         for chunk, emb in zip(batch, embeddings):
#             embedded_chunks.append({
#                 "chunk_id": chunk["chunk_id"],
#                 "embedding": emb.tolist(),

#                 # 🔒 Store exact embedded text for legal traceability
#                 "text": chunk["chunk_text"],

#                 "metadata": {
#                     "section_id": chunk["section_id"],
#                     "section_title": chunk["section_title"],
#                     "section_path": chunk["section_path"],
#                     "source": chunk["source"],
#                     "doc_version": chunk["doc_version"],
#                     "chunk_index": chunk["chunk_index"]
#                 }
#             })

#     return embedded_chunks


# def save_embeddings(
#     embeddings: List[Dict],
#     output_path: Path
# ) -> None:
#     output_path.parent.mkdir(parents=True, exist_ok=True)

#     with output_path.open("w", encoding="utf-8") as f:
#         json.dump(embeddings, f, indent=2, ensure_ascii=False)


from pathlib import Path
import json
from tqdm import tqdm

from src.embeddings.model import get_embedding_model


# -----------------------------
# Paths
# -----------------------------
CHUNKS_PATH = Path("data/chunks/tmep_chunks.json")
OUTPUT_PATH = Path("data/embeddings/tmep_e5_embeddings.json")


def main():
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"Chunks file not found: {CHUNKS_PATH}"
        )

    chunks = json.loads(
        CHUNKS_PATH.read_text(encoding="utf-8")
    )

    model = get_embedding_model()

    embeddings = []

    print(f"🔢 Embedding {len(chunks)} chunks")

    for chunk in tqdm(chunks):
        text = chunk["chunk_text"].strip()
        if not text:
            continue

        # 🔑 E5 rule: passage prefix
        vector = model.encode(
            "passage: " + text,
            normalize_embeddings=True
        ).tolist()

        embeddings.append({
            "chunk_id": chunk["chunk_id"],
            "section_id": chunk["section_id"],
            "section_path": chunk["section_path"],
            "source_file": chunk.get("source_file"),

            "embedding": vector,

            # keep text for debugging / reload safety
            "text": text,
            "doc_version": chunk["doc_version"],
            "source": chunk["source"],
        })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(embeddings, indent=2),
        encoding="utf-8"
    )

    print("=" * 60)
    print(f"✅ Embeddings saved: {OUTPUT_PATH}")
    print(f"📦 Total vectors: {len(embeddings)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
