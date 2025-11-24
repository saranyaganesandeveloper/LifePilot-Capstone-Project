# memory/vector_memory.py

from typing import List
import numpy as np

from gen_client import embed


class VectorMemory:
    """
    Super-simple in-memory vector store using cosine similarity.
    """

    def __init__(self) -> None:
        self.vectors: List[np.ndarray] = []
        self.texts: List[str] = []

    def add(self, text: str) -> None:
        if not text:
            return
        vec_list = embed(text)
        vec = np.array(vec_list, dtype="float32")
        if vec.size == 0:
            return
        self.vectors.append(vec)
        self.texts.append(text)

    def search(self, query: str, k: int = 5) -> List[str]:
        if not self.vectors or not query:
            return []

        qvec_list = embed(query)
        qvec = np.array(qvec_list, dtype="float32")
        if qvec.size == 0:
            return []

        sims = []
        for idx, v in enumerate(self.vectors):
            denom = (np.linalg.norm(v) * np.linalg.norm(qvec)) + 1e-9
            sims.append((float(np.dot(v, qvec) / denom), idx))

        sims.sort(key=lambda x: x[0], reverse=True)
        sims = sims[: max(1, k)]

        return [self.texts[i] for _, i in sims]
