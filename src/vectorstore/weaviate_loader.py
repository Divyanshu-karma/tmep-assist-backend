
# import json
# from pathlib import Path

# from .weaviate_client import get_client, create_schema, CLASS_NAME


# EMBEDDINGS_PATH = Path("data/embeddings/tmep_e5_embeddings.json")


# def load_embeddings(embeddings_path: Path) -> None:
#     if not embeddings_path.exists():
#         raise FileNotFoundError(
#             f"Embeddings file not found: {embeddings_path}"
#         )

#     client = get_client()

#     try:
#         create_schema(client)
#         collection = client.collections.get(CLASS_NAME)

#         data = json.loads(
#             embeddings_path.read_text(encoding="utf-8")
#         )

#         print(f"⏳ Ingesting {len(data)} chunks into Weaviate...")

#         with collection.batch.dynamic() as batch:
#             for item in data:
#                 batch.add_object(
#                     properties={
#                         "chunk_id": item["chunk_id"],   # ✅ store as property
#                         "text": item["text"],
#                         "section_id": item["section_id"],
#                         "section_path": item["section_path"],
#                         "source_file": item.get("source_file"),
#                         "doc_version": item["doc_version"],
#                         "source": item["source"],
#                     },
#                     vector=item["embedding"],
#                 )


#         print("✅ All chunks ingested successfully")

#     finally:
#         client.close()


# # ✅ THIS WAS MISSING
# def main():
#     load_embeddings(EMBEDDINGS_PATH)


# if __name__ == "__main__":
#     main()
import json
import uuid
from pathlib import Path

from .weaviate_client import (
    get_client,
    create_schema,
    CLASS_NAME,
    EXPECTED_EMBEDDING_DIM,
)


EMBEDDINGS_PATH = Path("data/embeddings/tmep_e5_embeddings.json")


def load_embeddings(embeddings_path: Path) -> None:
    if not embeddings_path.exists():
        raise FileNotFoundError(
            f"Embeddings file not found: {embeddings_path}"
        )

    client = get_client()

    try:
        create_schema(client)
        collection = client.collections.get(CLASS_NAME)

        data = json.loads(
            embeddings_path.read_text(encoding="utf-8")
        )

        if not data:
            raise ValueError("Embeddings file is empty.")

        # ✅ Dataset-level embedding dimension validation
        embedding_dim = len(data[0]["embedding"])
        if embedding_dim != EXPECTED_EMBEDDING_DIM:
            raise ValueError(
                f"Embedding dimension mismatch. "
                f"Expected {EXPECTED_EMBEDDING_DIM}, got {embedding_dim}"
            )

        # ✅ doc_version consistency validation
        doc_versions = {item["doc_version"] for item in data}
        if len(doc_versions) != 1:
            raise ValueError(
                f"Multiple doc_version values detected: {doc_versions}"
            )

        print(f"⏳ Ingesting {len(data)} chunks into Weaviate...")

        with collection.batch.dynamic() as batch:
            for item in data:
                chunk_id = item["chunk_id"]
                vector = item["embedding"]

                # ✅ Per-item embedding validation
                if len(vector) != EXPECTED_EMBEDDING_DIM:
                    raise ValueError(
                        f"Embedding dimension mismatch for chunk {chunk_id}"
                    )

                # ✅ Deterministic UUID for idempotent ingestion
                uuid_str = str(
                    uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id)
                )

                batch.add_object(
                    uuid=uuid_str,
                    properties={
                        "chunk_id": chunk_id,
                        "text": item["text"],
                        "section_id": item["section_id"],
                        "section_path": item["section_path"],
                        "source_file": item.get("source_file"),
                        "doc_version": item["doc_version"],
                        "source": item["source"],
                    },
                    vector=vector,
                )

            # ✅ Fail hard on ingestion errors
            if batch.number_errors > 0:
                raise RuntimeError(
                    f"Batch ingestion failed for "
                    f"{batch.number_errors} objects."
                )

        print("✅ All chunks ingested successfully")
        print(f"📌 Ingested TMEP version: {list(doc_versions)[0]}")
        print(f"📐 Embedding dimension: {EXPECTED_EMBEDDING_DIM}")

    finally:
        client.close()


def main():
    load_embeddings(EMBEDDINGS_PATH)


if __name__ == "__main__":
    main()
