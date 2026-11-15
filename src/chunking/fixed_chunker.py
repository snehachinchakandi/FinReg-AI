"""
Strategy A: Fixed-size chunking with overlap for FinReg AI.
Generates uniform sliding-window chunks while preserving document title, circular number,
date, estimated section heading, and page ranges.
"""

from typing import List, Dict, Any
from src.chunking.base_chunker import BaseChunker, RegulatoryChunk

class FixedSizeChunker(BaseChunker):
    """
    Fixed-size sliding window chunker.
    Uses word-level windows (approx. 400 words = ~512 tokens) with 75-word overlap (~100 tokens).
    """

    def __init__(self, chunk_size_words: int = 400, overlap_words: int = 75):
        self.chunk_size = chunk_size_words
        self.overlap = overlap_words

    def chunk_document(self, parsed_doc: Dict[str, Any]) -> List[RegulatoryChunk]:
        chunks: List[RegulatoryChunk] = []
        doc_id = parsed_doc.get("doc_id", "DOC")
        doc_title = parsed_doc.get("title", "Unknown")
        circular_no = parsed_doc.get("circular_no", "")
        publish_date = parsed_doc.get("publish_date", "")
        effective_date = parsed_doc.get("effective_date", publish_date)
        is_active = parsed_doc.get("is_active", True)
        superseded_by = parsed_doc.get("superseded_by")
        supersedes = parsed_doc.get("supersedes")

        # Flatten pages while tracking word-to-page mappings
        words_with_meta = []
        for page in parsed_doc.get("pages", []):
            page_no = page.get("page_number", 1)
            text = page.get("text", "")
            for word in text.split():
                words_with_meta.append((word, page_no))

        if not words_with_meta:
            return chunks

        step = max(1, self.chunk_size - self.overlap)
        total_words = len(words_with_meta)
        chunk_idx = 1

        for i in range(0, total_words, step):
            window = words_with_meta[i : i + self.chunk_size]
            if not window:
                break

            chunk_text = " ".join([w[0] for w in window])
            page_start = window[0][1]
            page_end = window[-1][1]
            
            # Identify heuristic section heading from first line or document title
            first_line = chunk_text.split(". ")[0][:80]
            section_heading = f"Part near page {page_start} ({first_line}...)"

            # Clause-level supersession and validity metadata defaults
            chunk_is_active = is_active
            chunk_effective_date = effective_date
            chunk_valid_until = parsed_doc.get("valid_until")
            chunk_superseded_by = superseded_by
            chunk_supersedes = supersedes
            superseded_clause = None
            superseding_clause = None
            supersession_date = None
            supersession_reason = None
            source_type = parsed_doc.get("source_type", "official_gazette")
            primary_source_url = parsed_doc.get("primary_source_url")
            local_pdf_page = None

            # Tri-temporal supersession logic for Digital Lending Directions
            if doc_id == "RBI_DL_2025":
                chunk_is_active = True
                chunk_valid_until = None
                chunk_superseded_by = None
                chunk_supersedes = "RBI_DL_2022 and RBI_DLG_2023 (Repealed under Para 30 and Annex III)"
                source_type = "local_rendered_pdf"
                primary_source_url = "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12848&Mode=0"
                local_pdf_page = page_start
                # Staggered commencement:
                if "arrangements involving multiple lenders" in chunk_text.lower() or "para 6" in chunk_text.lower():
                    chunk_effective_date = "2025-11-01"
                elif "cims portal" in chunk_text.lower() or "para 17" in chunk_text.lower() or "reporting on cims" in chunk_text.lower():
                    chunk_effective_date = "2025-06-15"
                else:
                    chunk_effective_date = "2025-05-08"

            elif doc_id == "RBI_DL_2022":
                chunk_is_active = False
                circular_no = parsed_doc.get("circular_no") or "RBI/2022-23/111 DOR.CRE.REC.66/21.07.001/2022-23"
                if (
                    "first loss default guarantee" in chunk_text.lower() or 
                    "loss sharing arrangement in case of default" in chunk_text.lower()
                ):
                    chunk_effective_date = "2022-09-02"
                    chunk_valid_until = "2023-06-07"
                    chunk_superseded_by = "RBI_DLG_2023"
                    superseded_clause = "Para 6 / Item 15 (Synthetic Securitisation & FLDG)"
                    superseding_clause = "RBI Circular RBI/2023-24/41 DOR.CRE.REC.21/21.07.001/2023-24 (DLG 5% cap) and RBI_DL_2025 Para 23"
                    supersession_date = "2023-06-08"
                    supersession_reason = (
                        "Superseded initially on June 8, 2023 by RBI_DLG_2023 (permitting DLG up to 5%), "
                        "and subsequently repealed on May 8, 2025 by RBI_DL_2025 (Chapter VI, Para 23)."
                    )
                else:
                    chunk_effective_date = "2022-09-02"
                    chunk_valid_until = "2025-05-07"
                    chunk_superseded_by = "RBI_DL_2025"
                    superseded_clause = f"Guidelines on Digital Lending (Page {page_start})"
                    superseding_clause = "Reserve Bank of India (Digital Lending) Directions, 2025 (RBI/2025-26/36)"
                    supersession_date = "2025-05-08"
                    supersession_reason = (
                        "Repealed under Paragraph 30 and Annex III of RBI (Digital Lending) Directions, 2025 "
                        "(DOR.STR.REC.19/21.07.001/2025-26 dated May 8, 2025)."
                    )
            elif doc_id == "RBI_DLG_2023":
                chunk_is_active = False
                circular_no = "RBI/2023-24/41 DOR.CRE.REC.21/21.07.001/2023-24"
                chunk_effective_date = "2023-06-08"
                chunk_valid_until = "2025-05-07"
                chunk_superseded_by = "RBI_DL_2025"
                superseded_clause = f"Default Loss Guarantee (DLG) Guidelines (Page {page_start})"
                superseding_clause = "Reserve Bank of India (Digital Lending) Directions, 2025 Chapter VI (Paras 18-28)"
                supersession_date = "2025-05-08"
                supersession_reason = (
                    "Repealed and consolidated into Chapter VI under Paragraph 30 and Annex III of "
                    "RBI (Digital Lending) Directions, 2025."
                )

            chunk_id = f"{doc_id}_fix_{chunk_idx:04d}"
            chunks.append(RegulatoryChunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                doc_title=doc_title,
                circular_no=circular_no,
                regulator=parsed_doc.get("regulator", "Reserve Bank of India (RBI)"),
                publish_date=publish_date,
                effective_date=chunk_effective_date,
                valid_until=chunk_valid_until,
                is_active=chunk_is_active,
                superseded_by=chunk_superseded_by,
                supersedes=chunk_supersedes,
                superseded_clause=superseded_clause,
                superseding_clause=superseding_clause,
                supersession_date=supersession_date,
                supersession_reason=supersession_reason,
                source_type=source_type,
                primary_source_url=primary_source_url,
                section_heading=section_heading,
                clause_no=None,
                page_start=page_start,
                page_end=page_end,
                local_pdf_page=local_pdf_page,
                chunk_strategy="fixed_size",
                text=chunk_text,
                token_count=self.estimate_tokens(chunk_text)
            ))
            chunk_idx += 1

            if i + self.chunk_size >= total_words:
                break

        return chunks
