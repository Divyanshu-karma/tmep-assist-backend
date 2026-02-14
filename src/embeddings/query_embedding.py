from src.embeddings.model import get_embedding_model


def embed_query(query: str) -> list[float]:
    """
    Embed a search query using E5.
    """
    model = get_embedding_model()

    vector = model.encode(
        "query: " + query,
        normalize_embeddings=True
    )

    return vector.tolist()



# from typing import List
# import torch
# from .model import tokenizer, model, mean_pooling


# def embed_query(query: str) -> List[float]:
#     text = f"query: {query}"

#     inputs = tokenizer(
#         text,
#         padding=True,
#         truncation=True,
#         max_length=512,
#         return_tensors="pt"
#     )

#     with torch.no_grad():
#         outputs = model(**inputs)
#         embedding = mean_pooling(
#             outputs.last_hidden_state,
#             inputs["attention_mask"]
#         )

#     return embedding[0].tolist()

