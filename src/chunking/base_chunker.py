"""
Base Chunker and Schema definitions for FinReg AI.
Ensures every chunk strictly preserves document title, circular number, date, section heading,
clause number, and temporal validity metadata.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class RegulatoryChunk(BaseModel):
    """Schema for every chunk across all chunking strategies."""
    chunk_id: str
    doc_id: str
    doc_title: str
    circular_no: str
    regulator: str = "Reserve Bank of India (RBI)"
    publish_date: str
    effective_date: str
    valid_until: Optional[str] = None
    is_active: bool = True
    superseded_by: Optional[str] = None
    supersedes: Optional[str] = None
    superseded_clause: Optional[str] = None
    superseding_clause: Optional[str] = None
    supersession_date: Optional[str] = None
    supersession_reason: Optional[str] = None
    source_type: str = "official_gazette"
    primary_source_url: Optional[str] = None
    section_heading: str
    clause_no: Optional[str] = None
    page_start: int
    page_end: int
    local_pdf_page: Optional[int] = None
    chunk_strategy: str  # "fixed_size" or "section_aware"
    text: str
    token_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def get_citation_str(self) -> str:
        """Returns standard regulatory citation format anchored by authoritative paragraph/clause."""
        clause_part = f", Paragraph/Clause: {self.clause_no}" if self.clause_no else ""
        page_info = f" | Local Rendered PDF Page: {self.local_pdf_page or self.page_start}" if self.source_type == "local_rendered_pdf" else f" | Page: {self.page_start}"
        return f"[{self.doc_title} | Circular: {self.circular_no} | Date: {self.publish_date} | Section: {self.section_heading}{clause_part}{page_info}]"


class BaseChunker(ABC):
    """Abstract interface for document chunking."""

    @abstractmethod
    def chunk_document(self, parsed_doc: Dict[str, Any]) -> List[RegulatoryChunk]:
        """Splits a structured parsed document into a list of RegulatoryChunks."""
        pass

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Heuristic estimation: ~1 token per 4 characters / 0.75 words."""
        words = text.split()
        return max(1, int(len(words) * 1.3))
