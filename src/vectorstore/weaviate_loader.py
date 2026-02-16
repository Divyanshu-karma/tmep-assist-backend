
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
)

CHUNKS_PATH = Path("data/chunks/tmep_chunks.json")


def load_chunks(chunks_path: Path) -> None:
    if not chunks_path.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_path}")

    client = get_client()

    try:
        create_schema(client)
        collection = client.collections.get(CLASS_NAME)

        data = json.loads(
            chunks_path.read_text(encoding="utf-8")
        )

        if not data:
            raise ValueError("Chunks file is empty.")

        print(f"⏳ Ingesting {len(data)} chunks into Weaviate...")

        with collection.batch.dynamic() as batch:
            for item in data:
                chunk_id = item["chunk_id"]

                uuid_str = str(
                    uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id)
                )

                batch.add_object(
                    uuid=uuid_str,
                    properties={
                        "chunk_id": chunk_id,
                        "text": item["chunk_text"],  # 🔥 important
                        "section_id": item["section_id"],
                        "section_path": item["section_path"],
                        "source_file": item.get("source_file"),
                        "doc_version": item["doc_version"],
                        "source": item["source"],
                    }
                )

            if batch.number_errors > 0:
                raise RuntimeError(
                    f"Batch ingestion failed for "
                    f"{batch.number_errors} objects."
                )

        print("✅ All chunks ingested successfully")

    finally:
        client.close()


def main():
    load_chunks(CHUNKS_PATH)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
