import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import json

BASE = os.path.dirname(os.path.dirname(__file__))
INDEX_PATH = os.getenv("FAISS_INDEX_PATH", os.path.join(BASE, "data", "jobs_index.faiss"))
IDS_PATH = os.getenv("FAISS_IDS_PATH", os.path.join(BASE, "data", "job_ids.npy"))
MODEL_NAME = os.getenv("SENTENCE_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")

class Recommender:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        if not os.path.exists(INDEX_PATH) or not os.path.exists(IDS_PATH):
            raise FileNotFoundError("FAISS index or ids not found. Run data/build_index.py first.")
        self.index = faiss.read_index(INDEX_PATH)
        self.ids = np.load(IDS_PATH, allow_pickle=True)
    def embed(self, text: str):
        emb = self.model.encode([text], convert_to_numpy=True)
        faiss.normalize_L2(emb)
        return emb
    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[str,float]]:
        q_emb = self.embed(query)
        D, I = self.index.search(q_emb, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0:
                continue
            job_id = self.ids[idx].item() if hasattr(self.ids[idx], "item") else self.ids[idx]
            results.append((str(job_id), float(score)))
        return results

# match score utility
def compute_match_score(similarity: float, skill_ratio: float = 0.0, salary_score: float = 0.0, experience_score: float = 0.0, recency_score: float = 0.0):
    score = 0.6 * similarity + 0.2 * skill_ratio + 0.1 * salary_score + 0.05 * experience_score + 0.05 * recency_score
    return max(0.0, min(1.0, score))
