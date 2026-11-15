"""
Configuration module for FinReg AI.
Centralizes paths, model configurations, retrieval hyperparameters, and evaluation settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Data directories
DATA_DIR = BASE_DIR / "data"
RAW_DOCS_DIR = DATA_DIR / "raw_documents"
PROCESSED_DOCS_DIR = DATA_DIR / "processed_documents"
CHUNKS_DIR = DATA_DIR / "chunks"
METADATA_DIR = DATA_DIR / "metadata"

# Index directories
INDEXES_DIR = BASE_DIR / "indexes"
EVALUATION_DIR = BASE_DIR / "evaluation"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
for path in [
    RAW_DOCS_DIR,
    PROCESSED_DOCS_DIR,
    CHUNKS_DIR,
    METADATA_DIR,
    INDEXES_DIR,
    EVALUATION_DIR,
    REPORTS_DIR,
    EVALUATION_DIR / "results",
]:
    path.mkdir(parents=True, exist_ok=True)

# File paths
METADATA_FILE = METADATA_DIR / "documents_metadata.json"
FIXED_CHUNKS_FILE = CHUNKS_DIR / "fixed_chunks.json"
SECTION_CHUNKS_FILE = CHUNKS_DIR / "section_chunks.json"
EVAL_DATASET_FILE = EVALUATION_DIR / "eval_dataset.jsonl"
RESULTS_TABLE_FILE = REPORTS_DIR / "results_table.csv"

# Models
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Chunking Hyperparameters
FIXED_CHUNK_SIZE = 512       # Approximate tokens / characters
FIXED_CHUNK_OVERLAP = 100
SECTION_MAX_TOKENS = 800
SECTION_MIN_TOKENS = 150

# Retrieval Hyperparameters
TOP_K_DENSE = 10
TOP_K_BM25 = 10
TOP_K_FINAL = 5
RRF_K = 60                   # Reciprocal Rank Fusion constant

# Evidence sufficiency thresholds (Retrieval-Mode Aware)
# Dense retrieval: cosine similarity on BGE embeddings (below 0.40 indicates out-of-domain / no evidence)
DENSE_REFUSAL_THRESHOLD = 0.40

# Sparse retrieval: BM25 score threshold
BM25_REFUSAL_THRESHOLD = 1.5

# Hybrid RRF: minimum fused score (an item ranked in top ranks has ~0.015 - 0.033; below 0.010 indicates no strong rank)
HYBRID_RRF_MIN_SCORE = 0.010

# API Pricing (Gemini 2.5 Flash / 1.5 Flash rates)
COST_PER_MILLION_INPUT_TOKENS = 0.075
COST_PER_MILLION_OUTPUT_TOKENS = 0.30
