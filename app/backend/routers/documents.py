"""
Document Intelligence Router for FinReg AI.
Provides endpoints for listing regulatory circulars, inspecting metadata, retrieving structured text, and streaming raw PDFs.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from src.config import (
    METADATA_FILE,
    RAW_DOCS_DIR,
    PROCESSED_DOCS_DIR
)

router = APIRouter(prefix="/api/documents", tags=["Documents"])

def _load_metadata() -> List[Dict[str, Any]]:
    if not METADATA_FILE.exists():
        return []
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("", response_model=List[Dict[str, Any]])
def list_documents():
    """Returns the full catalog of 12 authentic regulatory documents."""
    return _load_metadata()

@router.get("/summary")
def get_corpus_summary():
    """Returns aggregated corpus metrics (total docs, pages, active/superseded counts)."""
    docs = _load_metadata()
    total_docs = len(docs)
    total_pages = sum(d.get("pages", 0) for d in docs)
    active_docs = sum(1 for d in docs if d.get("is_active", False))
    superseded_docs = total_docs - active_docs
    return {
        "total_documents": total_docs,
        "total_pages": total_pages,
        "active_documents": active_docs,
        "superseded_documents": superseded_docs,
        "regulator": "Reserve Bank of India (RBI)"
    }

@router.get("/{doc_id}")
def get_document_details(doc_id: str):
    """Retrieves metadata for a specific regulatory circular by doc_id."""
    docs = _load_metadata()
    for doc in docs:
        if doc.get("doc_id") == doc_id:
            return doc
    raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found in corpus metadata.")

@router.get("/{doc_id}/content")
def get_document_content(doc_id: str):
    """Retrieves parsed structured JSON content for a document."""
    processed_path = PROCESSED_DOCS_DIR / f"{doc_id}.json"
    if not processed_path.exists():
        raise HTTPException(status_code=404, detail=f"Processed content for '{doc_id}' not found.")
    with open(processed_path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/{doc_id}/pdf")
def stream_document_pdf(doc_id: str):
    """Streams the raw PDF file for in-browser PDF viewer rendering."""
    pdf_path = RAW_DOCS_DIR / f"{doc_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"Raw PDF for '{doc_id}' not found.")
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"{doc_id}.pdf"
    )
