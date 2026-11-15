"""
Hybrid Retrieval with Reciprocal Rank Fusion (RRF) for FinReg AI.
Combines dense semantic vector retrieval (FAISS) with lexical keyword retrieval (BM25).
"""

from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
from src.retrieval.dense import DenseRetriever
from src.retrieval.bm25 import BM25Retriever
from src.config import RRF_K

class HybridRetriever:
    """
    Hybrid retriever fusing dense and sparse search via Reciprocal Rank Fusion.
    """

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        bm25_retriever: BM25Retriever,
        rrf_k: int = RRF_K
    ):
        self.dense = dense_retriever
        self.bm25 = bm25_retriever
        self.rrf_k = rrf_k

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_active_only: Optional[bool] = None,
        dense_k: int = 15,
        bm25_k: int = 15
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Executes dense and BM25 queries in parallel, applies RRF scoring,
        and returns the top_k fused results.
        If filter_active_only=None, automatically infers based on whether query is historical.
        """
        # Pass filter_active_only directly to dense and bm25 (None triggers date-aware auto-selection)
        dense_results = self.dense.search(query, top_k=dense_k, filter_active_only=filter_active_only)
        bm25_results = self.bm25.search(query, top_k=bm25_k, filter_active_only=filter_active_only)

        # Map chunk_id to chunk data and rank positions
        rrf_scores = defaultdict(float)
        chunk_map = {}
        rank_details = defaultdict(dict)

        # Dense ranks (1-indexed)
        for rank, (chunk, score) in enumerate(dense_results, 1):
            cid = chunk["chunk_id"]
            chunk_map[cid] = chunk
            rrf_scores[cid] += 1.0 / (self.rrf_k + rank)
            rank_details[cid]["dense_rank"] = rank
            rank_details[cid]["dense_score"] = score

        # BM25 ranks (1-indexed)
        for rank, (chunk, score) in enumerate(bm25_results, 1):
            cid = chunk["chunk_id"]
            chunk_map[cid] = chunk
            rrf_scores[cid] += 1.0 / (self.rrf_k + rank)
            rank_details[cid]["bm25_rank"] = rank
            rank_details[cid]["bm25_score"] = score

        # Sort chunks by fused RRF score descending
        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        fused_results: List[Tuple[Dict[str, Any], float]] = []
        for cid in sorted_cids[:top_k]:
            chunk = dict(chunk_map[cid])
            # Attach fusion debug metadata
            chunk["_fusion_meta"] = {
                "rrf_score": rrf_scores[cid],
                "dense_rank": rank_details[cid].get("dense_rank"),
                "dense_score": rank_details[cid].get("dense_score"),
                "bm25_rank": rank_details[cid].get("bm25_rank"),
                "bm25_score": rank_details[cid].get("bm25_score"),
            }
            fused_results.append((chunk, rrf_scores[cid]))

        return fused_results
