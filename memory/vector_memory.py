# memory/vector_memory.py
import numpy as np
import faiss
from gen_client import embed
import traceback

class VectorMemory:
    def __init__(self):
        try:
            sample = embed("init")
            self.dim = len(sample)
        except:
            self.dim = 768

        self.index = faiss.IndexFlatL2(self.dim)
        self.data = []

    def add(self, text: str):
        try:
            vec = np.array([embed(text)], dtype="float32")
            self.index.add(vec)
            self.data.append(text)
        except Exception:
            print("[VectorMemory Error]", traceback.format_exc())

    def search(self, query: str, k=3):
        if not self.data:
            return []

        try:
            qvec = np.array([embed(query)], dtype="float32")
            scores, idx = self.index.search(qvec, k)
            return [self.data[i] for i in idx[0] if i < len(self.data)]
        except Exception:
            print("[VectorMemory Search Error]", traceback.format_exc())
            return []
