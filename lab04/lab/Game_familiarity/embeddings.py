from __future__ import annotations

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

CHECKPOINT = "distiluse-base-multilingual-cased-v2"


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer(CHECKPOINT)


def generate_embeddings(text: str) -> list[float]:
    embedding = _model().encode(text)
    if isinstance(embedding, np.ndarray):
        return embedding.tolist()
    return list(embedding)