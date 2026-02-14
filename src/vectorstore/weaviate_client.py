

# import os
# import weaviate
# from weaviate.auth import AuthApiKey
# from dotenv import load_dotenv

# load_dotenv()

# WEAVIATE_URL = os.getenv("WEAVIATE_URL")
# WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

# if not WEAVIATE_URL or not WEAVIATE_API_KEY:
#     raise RuntimeError(
#         "WEAVIATE_URL and WEAVIATE_API_KEY must be set in .env"
#     )

# CLASS_NAME = "TmepChunk"
# EXPECTED_EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))


# def get_client() -> weaviate.WeaviateClient:
#     """
#     Connect to Weaviate Cloud using Python client v4.
#     """
#     return weaviate.connect_to_weaviate_cloud(
#         cluster_url=WEAVIATE_URL,
#         auth_credentials=AuthApiKey(WEAVIATE_API_KEY),
#     )


# def create_schema(client: weaviate.WeaviateClient) -> None:
#     """
#     Create collection if it does not exist.
#     Vectorizer is disabled (we bring our own vectors).
#     """
#     if client.collections.exists(CLASS_NAME):
#         return

#     client.collections.create(
#         name=CLASS_NAME,
#         vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none(),
#         vector_index_config=weaviate.classes.config.Configure.VectorIndex.hnsw(
#         distance_metric="cosine",
#         vector_cache_max_objects=200000,
#         ),
#         properties=[
#     weaviate.classes.config.Property(
#         name="chunk_id",
#         data_type=weaviate.classes.config.DataType.TEXT,
#         tokenization=weaviate.classes.config.Tokenization.FIELD
#     ),
#     weaviate.classes.config.Property(
#         name="text",
#         data_type=weaviate.classes.config.DataType.TEXT
#     ),
#     weaviate.classes.config.Property(
#         name="section_id",
#         data_type=weaviate.classes.config.DataType.TEXT
#     ),
#     weaviate.classes.config.Property(
#         name="section_path",
#         data_type=weaviate.classes.config.DataType.TEXT
#     ),
#     weaviate.classes.config.Property(
#         name="source_file",
#         data_type=weaviate.classes.config.DataType.TEXT
#     ),
#     weaviate.classes.config.Property(
#         name="doc_version",
#         data_type=weaviate.classes.config.DataType.TEXT
#     ),
#     weaviate.classes.config.Property(
#         name="source",
#         data_type=weaviate.classes.config.DataType.TEXT
#     ),
# ],

#     )

#     print(f"✅ Schema '{CLASS_NAME}' created")

import os
import weaviate
from weaviate.auth import AuthApiKey




WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

if not WEAVIATE_URL or not WEAVIATE_API_KEY:
    raise RuntimeError(
        "WEAVIATE_URL and WEAVIATE_API_KEY must be set in .env"
    )

CLASS_NAME = "TmepChunk"
EXPECTED_EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))


def get_client() -> weaviate.WeaviateClient:
    """
    Connect to Weaviate Cloud using Python client v4.
    """
    return weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_URL,
        auth_credentials=AuthApiKey(WEAVIATE_API_KEY),
    )


def create_schema(client: weaviate.WeaviateClient) -> None:
    """
    Create collection if it does not exist.
    Vectorizer is disabled (we bring our own vectors).
    """
    if client.collections.exists(CLASS_NAME):
        collection = client.collections.get(CLASS_NAME)
        config = collection.config.get()

        if config.vector_index_config.distance_metric != "cosine":
            raise RuntimeError("Vector index distance metric mismatch.")

        if config.vector_index_config.vector_dimensions != EXPECTED_EMBEDDING_DIM:
            raise RuntimeError("Vector dimension mismatch.")

        return


    client.collections.create(
        name=CLASS_NAME,
        vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none(),
        vector_index_config=weaviate.classes.config.Configure.VectorIndex.hnsw(
        distance_metric="cosine",
        vector_cache_max_objects=200000,
        vector_dimensions=EXPECTED_EMBEDDING_DIM,
         ef_construction=128,
        max_connections=64,
        ),
        properties=[
    weaviate.classes.config.Property(
        name="chunk_id",
        data_type=weaviate.classes.config.DataType.TEXT,
        tokenization=weaviate.classes.config.Tokenization.FIELD
    ),
    weaviate.classes.config.Property(
        name="text",
        data_type=weaviate.classes.config.DataType.TEXT
    ),
    weaviate.classes.config.Property(
        name="section_id",
        data_type=weaviate.classes.config.DataType.TEXT
    ),
    weaviate.classes.config.Property(
        name="section_path",
        data_type=weaviate.classes.config.DataType.TEXT
    ),
    weaviate.classes.config.Property(
        name="source_file",
        data_type=weaviate.classes.config.DataType.TEXT
    ),
    weaviate.classes.config.Property(
        name="doc_version",
        data_type=weaviate.classes.config.DataType.TEXT
    ),
    weaviate.classes.config.Property(
        name="source",
        data_type=weaviate.classes.config.DataType.TEXT
    ),
],

    )

    print(f"✅ Schema '{CLASS_NAME}' created")
