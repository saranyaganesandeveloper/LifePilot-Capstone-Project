# memory/vector_memory.py
import numpy as np
from gen_client import embed

class VectorMemory:

    def __init__(self):
        self.vectors = []
        self.texts = []

    def add(self, text: str):
        vec = np.array(embed(text), dtype="float32")
        self.vectors.append(vec)
        self.texts.append(text)

    def search(self, query: str, k=5):
        if not self.vectors:
            return []

        qvec = np.array(embed(query), dtype="float32")

        sims = []
        for idx, v in enumerate(self.vectors):
            denom = (np.linalg.norm(v) * np.linalg.norm(qvec)) + 1e-9
            sims.append((np.dot(v, qvec) / denom, idx))

        sims = sorted(sims, key=lambda x: x[0], reverse=True)
        sims = sims[:k]

        return [self.texts[i] for _, i in sims]
