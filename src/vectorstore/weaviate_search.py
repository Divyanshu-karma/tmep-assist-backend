# from typing import List, Dict, Optional
# from .weaviate_client import get_client, CLASS_NAME
# from src.embeddings.query_embedding import embed_query


# def similarity_search(
#     query: str,
#     top_k: int = 5,
#     doc_version: Optional[str] = None,
#     debug: bool = False,
# ) -> List[Dict]:
#     """
#     Perform vector similarity search over TMEP chunks.

#     - Uses E5 query embedding ("query: " prefix handled in embed_query)
#     - Supports optional doc_version filtering
#     - Converts cosine distance -> similarity
#     """

#     client = get_client()

#     try:
#         collection = client.collections.get(CLASS_NAME)

#         # ✅ Correct E5 query embedding
#         query_vector = embed_query(query)

#         # ✅ Optional version filter (prevents cross-version contamination)
#         filters = None
#         if doc_version:
#             filters = Filter.by_property("doc_version").equal(doc_version)


#         # ✅ Vector search
#         response = collection.query.near_vector(
#             near_vector=query_vector,
#             limit=top_k,
#             filters=filters,
#             return_metadata=["distance"],
#         )

#         results: List[Dict] = []

#         for obj in response.objects:
#             distance = obj.metadata.distance

#             # Weaviate cosine distance → similarity
#             similarity = 1 - distance if distance is not None else None

#             result_obj = {
#                 "text": obj.properties["text"],
#                 "section_id": obj.properties["section_id"],
#                 "section_path": obj.properties["section_path"],
#                 "source_file": obj.properties.get("source_file"),
#                 "doc_version": obj.properties["doc_version"],
#                 "source": obj.properties["source"],
#                 "distance": distance,
#                 "similarity": similarity,
#             }

#             results.append(result_obj)

#         # ✅ Optional retrieval debug output
#         if debug:
#             print("\n--- Retrieval Debug ---")
#             for r in results:
#                 print(
#                     f"{r['section_id']} | "
#                     f"Similarity: {round(r['similarity'], 4) if r['similarity'] else None} | "
#                     f"Distance: {round(r['distance'], 4) if r['distance'] else None}"
#                 )
#             print("-----------------------\n")

#         return results

#     finally:
#         client.close()

from weaviate.classes.query import Filter
from typing import List, Dict
from .weaviate_client import get_client, CLASS_NAME


MIN_SIMILARITY = 0.70


def similarity_search(
    query: str,
    top_k: int = 5,
    doc_version: str = None,
    debug: bool = False,
) -> List[Dict]:

    if not doc_version:
        raise ValueError("doc_version must be provided.")

    client = get_client()

    try:
        collection = client.collections.get(CLASS_NAME)

        filters = Filter.by_property("doc_version").equal(doc_version)

        # 🔥 Auto-embedding query search
        response = collection.query.near_text(
            query=query,
            limit=top_k,
            filters=filters,
            return_metadata=["distance"],
        )

        results: List[Dict] = []

        for obj in response.objects:
            distance = obj.metadata.distance
            similarity = max(0.0, 1 - distance) if distance is not None else None

            results.append({
                "chunk_id": obj.properties["chunk_id"],
                "text": obj.properties["text"],
                "section_id": obj.properties["section_id"],
                "section_path": obj.properties["section_path"],
                "source_file": obj.properties.get("source_file"),
                "doc_version": obj.properties["doc_version"],
                "source": obj.properties["source"],
                "distance": distance,
                "similarity": similarity,
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)

        results = [
            r for r in results
            if r["similarity"] is not None and r["similarity"] >= MIN_SIMILARITY
        ]

        if not results:
            raise ValueError("No sufficiently relevant TMEP sections found.")

        if debug:
            print("\n--- Retrieval Debug ---")
            for r in results:
                print(
                    f"{r['section_id']} | "
                    f"Similarity: {round(r['similarity'], 4)}"
                )
            print("-----------------------\n")

        return results

    finally:
        client.close()

