from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=2)
def get_embedder(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


def embed_texts(model_name: str, texts: list[str]) -> list[list[float]]:
    model = get_embedder(model_name)
    vectors = model.encode(texts, show_progress_bar=len(texts) > 20)
    return [vector.tolist() for vector in vectors]
