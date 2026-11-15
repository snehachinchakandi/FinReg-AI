"""
BM25 Keyword Retrieval module for FinReg AI using rank-bm25.
Features a domain-specific tokenizer for Indian financial and banking regulation terms.
"""

import re
import pickle
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from rank_bm25 import BM25Okapi

class BM25Retriever:
    """Okapi BM25 keyword search engine for regulatory chunks."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.bm25: Optional[BM25Okapi] = None
        self.chunks: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Tokenizer that lowercases, removes punctuation, but strictly preserves
        regulatory acronyms and clause identifiers (e.g., 'fldg', 'dlg', 'kfs', '3.1').
        """
        # Replace punctuation except hyphen and period inside numbers
        text = text.lower()
        # Extract alphanumeric words and dotted numbers
        tokens = re.findall(r"\b[a-z0-9]+(?:\.[a-z0-9]+)*\b", text)
        
        # Financial stopwords to filter
        stopwords = {
            "the", "and", "or", "of", "to", "in", "for", "with", "on", "at", "by",
            "an", "be", "this", "that", "from", "as", "is", "are", "was", "were",
            "shall", "such", "any", "other", "under", "all", "which", "thereof"
        }
        return [t for t in tokens if t not in stopwords and len(t) > 1]

    def build_index(self, chunks: List[Dict[str, Any]]):
        """Tokenizes chunks and builds BM25Okapi index."""
        self.chunks = chunks
        self.tokenized_corpus = [self.tokenize(c["text"]) for c in chunks]
        self.bm25 = BM25Okapi(self.tokenized_corpus, k1=self.k1, b=self.b)
        print(f"BM25 index built with {len(self.chunks)} documents.")

    def save(self, index_path: str, chunks_path: str):
        """Persists BM25 model and chunks."""
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        with open(index_path, "wb") as f:
            pickle.dump({
                "bm25": self.bm25,
                "tokenized_corpus": self.tokenized_corpus
            }, f)
        with open(chunks_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)
        print(f"Saved BM25 index to {index_path} and chunks to {chunks_path}")

    def load(self, index_path: str, chunks_path: str):
        """Loads BM25 model and chunks."""
        with open(index_path, "rb") as f:
            data = pickle.load(f)
            self.bm25 = data["bm25"]
            self.tokenized_corpus = data["tokenized_corpus"]
        with open(chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)
        print(f"Loaded BM25 index with {len(self.chunks)} documents from {index_path}")

    def search(
        self,
        query: str,
        top_k: int = 10,
        filter_active_only: Optional[bool] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Executes BM25 query search.
        Returns list of (chunk_dict, bm25_score).
        If filter_active_only=None, automatically infers based on whether query is historical.
        """
        if self.bm25 is None:
            raise ValueError("BM25 index not built or loaded.")

        from src.versioning.temporal_filter import RegulatoryVersionManager, is_chunk_valid_on_date, CURRENT_SYSTEM_DATE
        version_mgr = RegulatoryVersionManager()

        tokens = self.tokenize(query)
        if not tokens:
            return []

        doc_scores = self.bm25.get_scores(tokens)
        ranked_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)

        results: List[Tuple[Dict[str, Any], float]] = []
        for idx in ranked_indices:
            score = doc_scores[idx]
            if score <= 0.0:
                break
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
