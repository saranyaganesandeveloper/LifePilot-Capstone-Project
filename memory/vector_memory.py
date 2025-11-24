# memory/vector_memory.py

from typing import List
from gen_client import embed


class VectorMemory:
    """
    Simple in-memory vector store.
    Stores user texts and their embeddings.
    """

    def __init__(self):
        self.texts: List[str] = []
        self.embeddings: List[List[float]] = []

    def add(self, text: str):
        if not text:
            return
        vec = embed(text)
        self.texts.append(text)
        self.embeddings.append(vec)

    def _cosine(self, a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = sum(x * x for x in a) ** 0.5
        nb = sum(x * x for x in b) ** 0.5
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb + 1e-9)

    def search(self, query: str, k: int = 5) -> List[str]:
        if not self.texts:
            return []
        qv = embed(query)
        scores = [
            (self._cosine(qv, ev), txt)
            for txt, ev in zip(self.texts, self.embeddings)
        ]
        scores.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scores[:k]]

    def clear(self):
        """Clear all stored texts and embeddings."""
        self.texts = []
        self.embeddings = []
