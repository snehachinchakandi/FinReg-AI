"""
FastAPI Backend API for FinReg AI.
Provides REST endpoints for querying, version comparison, and evaluation analytics.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import pandas as pd

from src.config import (
    FIXED_CHUNKS_FILE,
    SECTION_CHUNKS_FILE,
    INDEXES_DIR,
    RESULTS_TABLE_FILE,
    BASE_DIR
)
from src.retrieval.dense import DenseRetriever
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.hybrid import HybridRetriever
from src.retrieval.reranker import CrossEncoderReranker
from src.generation.rag_engine import FinRegRAGEngine
from src.versioning.temporal_filter import RegulatoryVersionManager
from app.backend.routers.documents import router as documents_router
from app.backend.routers.evolution import router as evolution_router
from app.backend.routers.compliance import router as compliance_router
from app.backend.routers.export import router as export_router

app = FastAPI(
    title="FinReg AI API",
    description="Regulatory RAG Assistant for Indian Digital Payments & Lending (RBI)",
    version="1.0.0"
)

# CORS middleware for modern frontend development (React / Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount additive modular routers
app.include_router(documents_router)
app.include_router(evolution_router)
app.include_router(compliance_router)
app.include_router(export_router)

# Global instances (lazy initialized)
rag_engine = FinRegRAGEngine()
version_manager = RegulatoryVersionManager()
retrievers = {}

class QueryRequest(BaseModel):
    query: str
    config_id: str = "C4"  # C1, C2, C3, C4
    top_k: int = 5
    allow_superseded: bool = False

class QueryResponse(BaseModel):
    query: str
    config_id: str
    answer: str
    is_refusal: bool
    citations: List[Dict[str, str]]
    retrieved_chunks: List[str]
    latency_ms: float
    estimated_cost_usd: float

class CompareRequest(BaseModel):
    topic: str  # e.g., "FLDG", "Penal Interest"

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "FinReg AI Regulatory Assistant",
        "version": "1.0.0"
    }

@app.post("/query", response_model=QueryResponse)
def query_finreg(request: QueryRequest):
    """Answers a compliance query using the selected RAG configuration."""
    query = request.query
    config_id = request.config_id.upper()

    # Determine chunk strategy and retrieval mode
    use_section = config_id in ("C3", "C4")
    use_hybrid = config_id in ("C2", "C4")

    # Select indexes
    prefix = "section" if use_section else "fixed"
    dense_path = INDEXES_DIR / f"{prefix}_dense.faiss"
    bm25_path = INDEXES_DIR / f"{prefix}_bm25.pkl"
    chunks_path = SECTION_CHUNKS_FILE if use_section else FIXED_CHUNKS_FILE

    # Load retrievers if not cached
    if prefix not in retrievers:
        d_ret = DenseRetriever()
        b_ret = BM25Retriever()
        if dense_path.exists() and chunks_path.exists():
            d_ret.load(str(dense_path), str(chunks_path))
        if bm25_path.exists() and chunks_path.exists():
            b_ret.load(str(bm25_path), str(chunks_path))
        retrievers[prefix] = {"dense": d_ret, "bm25": b_ret}

    d_ret = retrievers[prefix]["dense"]
    b_ret = retrievers[prefix]["bm25"]

    # Temporal filtering
    filter_active = not request.allow_superseded

    if use_hybrid:
        hybrid = HybridRetriever(d_ret, b_ret)
        retrieved = hybrid.search(query, top_k=request.top_k, filter_active_only=filter_active)
    else:
        retrieved = d_ret.search(query, top_k=request.top_k, filter_active_only=filter_active)

    result = rag_engine.generate_answer(query, retrieved)

    latency = float(result.get("generation_latency_ms", result.get("latency_ms", 0.0)))
    cost = float(result.get("estimated_cost_usd", 0.0))

    return QueryResponse(
        query=query,
        config_id=config_id,
        answer=result.get("answer", ""),
        is_refusal=bool(result.get("is_refusal", False)),
        citations=result.get("citations", []),
        retrieved_chunks=result.get("retrieved_chunks", []),
        latency_ms=latency,
        estimated_cost_usd=cost
    )

@app.post("/compare_regulations")
def compare_regulations(request: CompareRequest):
    """Compares outdated vs current regulatory positions."""
    diff = version_manager.get_version_diff(request.topic)
    if not diff:
        return {"found": False, "message": "No superseded regulation mapped for this topic."}
    return {"found": True, "comparison": diff}

@app.get("/eval_summary")
def get_evaluation_summary():
    """Returns the benchmark results across all 4 configurations."""
    if not RESULTS_TABLE_FILE.exists():
        raise HTTPException(status_code=404, detail="Results table not yet generated.")
    df = pd.read_csv(RESULTS_TABLE_FILE)
    return df.to_dict(orient="records")

# Mount compiled modern React SPA if built
from fastapi.staticfiles import StaticFiles
CLIENT_DIST_DIR = BASE_DIR / "app" / "frontend" / "client" / "dist"
if CLIENT_DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(CLIENT_DIST_DIR), html=True), name="client-spa")
