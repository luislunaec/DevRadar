from sentence_transformers import SentenceTransformer
from typing import List

# Debe ser EL MISMO modelo que usaste para poblar jobs_clean.embedding
_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed_text(text: str) -> List[float]:
    """
    Genera embedding normalizado para un texto.
    Retorna un vector de 384 dimensiones.
    """
    embedding = _MODEL.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()
