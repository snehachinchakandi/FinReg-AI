"""
Dense Vector Retrieval module for FinReg AI using Sentence Transformers and FAISS.
Computes normalized embeddings for exact inner-product (cosine) similarity.
Supports bi-temporal metadata filtering (active vs superseded circulars).
"""

import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import faiss
from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_MODEL_NAME

class DenseRetriever:
    """FAISS-based dense semantic retriever."""

    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.index: Optional[faiss.IndexFlatIP] = None
        self.chunks: List[Dict[str, Any]] = []

    def build_index(self, chunks: List[Dict[str, Any]], batch_size: int = 32):
        """Encodes chunks and builds FAISS IndexFlatIP (cosine similarity)."""
        self.chunks = chunks
        texts = [c["text"] for c in chunks]

        print(f"Encoding {len(texts)} chunks using {self.model_name}...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True
        )
        embeddings = np.array(embeddings, dtype=np.float32)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)
        print(f"FAISS index built with {self.index.ntotal} vectors of dimension {dimension}.")

    def save(self, index_path: str, chunks_path: str):
        """Persists FAISS index binary and metadata chunks JSON."""
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_path))
        with open(chunks_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)
        print(f"Saved dense index to {index_path} and chunks to {chunks_path}")

    def load(self, index_path: str, chunks_path: str):
        """Loads FAISS index and associated chunks."""
        self.index = faiss.read_index(str(index_path))
        with open(chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)
        print(f"Loaded dense index with {self.index.ntotal} vectors from {index_path}")

    def search(
        self,
        query: str,
        top_k: int = 10,
        filter_active_only: Optional[bool] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches the vector index for query.
        Returns list of (chunk_dict, cosine_similarity_score).
        Applies active circular filtering if filter_active_only=True.
        If filter_active_only=None, automatically infers based on whether query is historical.
        """
        if self.index is None:
            raise ValueError("Index not built or loaded.")

        from src.versioning.temporal_filter import RegulatoryVersionManager, is_chunk_valid_on_date, CURRENT_SYSTEM_DATE
        version_mgr = RegulatoryVersionManager()

        # BGE models benefit from instruction prefix for queries
        if "bge" in self.model_name.lower():
            query_text = f"Represent this sentence for searching relevant passages: {query}"
        else:
            query_text = query

        q_emb = self.model.encode([query_text], normalize_embeddings=True)
        q_emb = np.array(q_emb, dtype=np.float32)

        # Retrieve a broader candidate pool (top_k * 4) to allow post-filtering
        fetch_k = min(len(self.chunks), top_k * 4)
        scores, indices = self.index.search(q_emb, fetch_k)

        results: List[Tuple[Dict[str, Any], float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx]

            # Date-aware temporal validity filter
            if filter_active_only is True:
                if not (chunk.get("is_active", True) and is_chunk_valid_on_date(chunk, CURRENT_SYSTEM_DATE)):
                    continue
            elif filter_active_only is False:
                pass  # Caller explicitly disabled filtering
            else:
                # Automatic date-aware filtering based on query
                if not version_mgr.is_chunk_applicable(chunk, query):
                    continue

            results.append((chunk, float(score)))
            if len(results) >= top_k:
                break

        return results
