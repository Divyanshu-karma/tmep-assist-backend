# backup
# import torch
# from transformers import AutoTokenizer, AutoModel

# MODEL_NAME = "intfloat/e5-base-v2"

# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# model = AutoModel.from_pretrained(MODEL_NAME)
# model.eval()


# def mean_pooling(last_hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
#     mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
#     summed = torch.sum(last_hidden_state * mask, dim=1)
#     counts = torch.clamp(mask.sum(dim=1), min=1e-9)
#     return summed / counts


from sentence_transformers import SentenceTransformer

_MODEL = None


def get_embedding_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(
            "intfloat/e5-base-v2",
            device="cpu"
        )
    return _MODEL
