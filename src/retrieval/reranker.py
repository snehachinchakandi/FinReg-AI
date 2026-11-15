"""
Cross-Encoder Reranker module for FinReg AI.
Used to experimentally determine if neural cross-attention improves Hit Rate@5 and MRR
over pure dense and hybrid RRF retrieval.
"""

import time
from typing import List, Dict, Any, Tuple
from sentence_transformers import CrossEncoder
from src.config import RERANKER_MODEL_NAME

class CrossEncoderReranker:
    """Neural cross-encoder reranker."""

    def __init__(self, model_name: str = RERANKER_MODEL_NAME):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """Lazy loader for CrossEncoder model."""
        if self._model is None:
            print(f"Loading Cross-Encoder reranker: {self.model_name}...")
            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(
        self,
        query: str,
        candidates: List[Tuple[Dict[str, Any], float]],
        top_k: int = 5
    ) -> Tuple[List[Tuple[Dict[str, Any], float]], float]:
        """
        Reranks a list of candidate chunks against the query.
        Returns:
            fused_results: List of (chunk, reranker_score)
            latency_ms: Milliseconds elapsed during reranking
        """
        if not candidates:
            return [], 0.0

        start_time = time.perf_counter()
        pairs = [[query, item[0]["text"]] for item in candidates]
        
        scores = self.model.predict(pairs)
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        reranked_results = []
        for idx in ranked_indices[:top_k]:
            chunk = dict(candidates[idx][0])
            chunk["_rerank_score"] = float(scores[idx])
            reranked_results.append((chunk, float(scores[idx])))

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return reranked_results, latency_ms
