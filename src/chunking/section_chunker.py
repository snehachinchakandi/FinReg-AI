"""
Strategy B: Section-Heading & Clause-Aware Hierarchical Chunking for FinReg AI.
Preserves the legal hierarchy of RBI circulars (Chapters, Sections, Sub-clauses, Annexures)
and keeps definitions, conditions, and exceptions unified in self-contained contexts.
"""

import re
from typing import List, Dict, Any, Tuple
from src.chunking.base_chunker import BaseChunker, RegulatoryChunk

class SectionAwareChunker(BaseChunker):
    """
    Heading- and clause-aware hierarchical chunker tailored for Indian regulatory circulars.
    """

    def __init__(self, min_words: int = 100, max_words: int = 600):
        self.min_words = min_words
        self.max_words = max_words

        # Regex patterns for RBI circular structure
        self.chapter_pattern = re.compile(
            r"^(CHAPTER\s+[IVX\d]+|Chapter\s+[IVX\d]+|PART\s+[IVX\d]+)[\s\:\.\-]+(.*)",
            re.IGNORECASE
        )
        self.section_pattern = re.compile(
            r"^(\d{1,2}(\.\d{1,2}){0,2})\.?\s+([A-Z][\w\s\,\-\(\)\/\:]{3,80})[:\.\-]?$",
            re.IGNORECASE
        )
        self.clause_pattern = re.compile(
            r"^(\d{1,2}(\.\d{1,2}){1,3})\.?\s+(.*)"
        )
        self.annexure_pattern = re.compile(
            r"^(ANNEXURE|SCHEDULE|Annexure|Schedule)\s*([IVX\d\-]*)[\s\:\.\-]*(.*)",
            re.IGNORECASE
        )

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

        # Extract structured sections by walking through pages and blocks
        raw_sections = self._extract_raw_sections(parsed_doc)
        
        # Merge tiny sections and split oversized sections
        normalized_sections = self._normalize_sections(raw_sections)

        chunk_idx = 1
        for sec in normalized_sections:
            chunk_id = f"{doc_id}_sec_{chunk_idx:04d}"
            sec_text = sec["text"].strip()
            sec_clause = sec.get("clause_no")
            sec_heading = sec["section_heading"]

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

            # Tri-temporal supersession and staggered commencement logic for Digital Lending Directions
            if doc_id == "RBI_DL_2025":
                chunk_is_active = True
                chunk_valid_until = None
                chunk_superseded_by = None
                chunk_supersedes = "RBI_DL_2022 and RBI_DLG_2023 (Repealed under Para 30 and Annex III)"
                source_type = "local_rendered_pdf"
                primary_source_url = "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12848&Mode=0"
                local_pdf_page = sec["page_start"]
                # Staggered commencement per Para 2(ii) of RBI Directions 2025:
                # - Para 6 comes into effect from November 1, 2025
                # - Para 17 comes into effect from June 15, 2025
                # - All other provisions come into force immediately (May 8, 2025)
                if sec_clause == "6" or "multiple lenders" in sec_heading.lower():
                    chunk_effective_date = "2025-11-01"
                elif sec_clause == "17" or "cims portal" in sec_heading.lower() or "reporting on cims" in sec_text.lower():
                    chunk_effective_date = "2025-06-15"
                else:
                    chunk_effective_date = "2025-05-08"

            elif doc_id == "RBI_DL_2022":
                chunk_is_active = False
                circular_no = parsed_doc.get("circular_no") or "RBI/2022-23/111 DOR.CRE.REC.66/21.07.001/2022-23"
                is_fldg_superseded = (
                    sec_clause == "15" or 
                    "loss sharing arrangement" in sec_heading.lower() or 
                    ("first loss default guarantee" in sec_text.lower() and "securitisation" in sec_text.lower())
                )
                if is_fldg_superseded:
                    chunk_effective_date = "2022-09-02"
                    chunk_valid_until = "2023-06-07"
                    chunk_superseded_by = "RBI_DLG_2023"
                    superseded_clause = "Para 6 / Clause 15 (Loss sharing arrangement / FLDG)"
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
                    superseded_clause = f"Clause {sec_clause}: {sec_heading}" if sec_clause else sec_heading
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
                superseded_clause = f"Clause {sec_clause}: {sec_heading}" if sec_clause else sec_heading
                superseding_clause = "Reserve Bank of India (Digital Lending) Directions, 2025 Chapter VI (Paras 18-28)"
                supersession_date = "2025-05-08"
                supersession_reason = (
                    "Repealed and consolidated into Chapter VI under Paragraph 30 and Annex III of "
                    "RBI (Digital Lending) Directions, 2025."
                )

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
                section_heading=sec_heading,
                clause_no=sec_clause,
                page_start=sec["page_start"],
                page_end=sec["page_end"],
                local_pdf_page=local_pdf_page,
                chunk_strategy="section_aware",
                text=sec_text,
                token_count=self.estimate_tokens(sec_text)
            ))
            chunk_idx += 1

        return chunks

    def _extract_raw_sections(self, parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw_sections: List[Dict[str, Any]] = []
        current_heading = "Preamble / Introduction"
        current_clause = None
        current_text_parts = []
        current_page_start = 1
        current_page_end = 1

        for page in parsed_doc.get("pages", []):
            page_no = page.get("page_number", 1)
            
            # Incorporate extracted tables as discrete markdown units
            for table in page.get("tables", []):
                md_tab = table.get("markdown", "")
                if md_tab:
                    current_text_parts.append(f"\n[Regulatory Table]\n{md_tab}\n")

            for block in page.get("blocks", []):
                text = block.get("text", "").strip()
                if not text:
                    continue

                lines = text.splitlines()
                first_line = lines[0].strip()

                # Check for structural heading
                matched_heading, matched_clause = self._detect_heading(first_line)

                if matched_heading:
                    # Save current accumulated section if it has content
                    accumulated = "\n".join(current_text_parts).strip()
                    if accumulated:
                        raw_sections.append({
                            "section_heading": current_heading,
                            "clause_no": current_clause,
                            "page_start": current_page_start,
                            "page_end": current_page_end,
                            "text": accumulated
                        })
                        current_text_parts = []

                    current_heading = matched_heading
                    current_clause = matched_clause
                    current_page_start = page_no

                current_text_parts.append(text)
                current_page_end = page_no

        # Flush final accumulated section
        accumulated = "\n".join(current_text_parts).strip()
        if accumulated:
            raw_sections.append({
                "section_heading": current_heading,
                "clause_no": current_clause,
                "page_start": current_page_start,
                "page_end": current_page_end,
                "text": accumulated
            })

        return raw_sections

    def _detect_heading(self, line: str) -> Tuple[str, str]:
        """Checks if a text line represents a regulatory heading or clause."""
        if len(line) > 120:
            return None, None

        # Chapter / Part match
        m_chap = self.chapter_pattern.match(line)
        if m_chap:
            heading = f"{m_chap.group(1)}: {m_chap.group(2).strip()}"
            return heading.strip(": "), None

        # Annexure match
        m_ann = self.annexure_pattern.match(line)
        if m_ann:
            heading = f"{m_ann.group(1)} {m_ann.group(2)}: {m_ann.group(3).strip()}"
            return heading.strip(": "), None

        # Numbered Section match (e.g. "3. Disbursement of Loan")
        m_sec = self.section_pattern.match(line)
        if m_sec:
            clause = m_sec.group(1)
            title = m_sec.group(3).strip()
            return f"Section {clause}: {title}", clause

        # Numbered Clause match (e.g. "4.2 Key Fact Statement")
        m_cl = self.clause_pattern.match(line)
        if m_cl and len(line) < 90:
            clause = m_cl.group(1)
            title = m_cl.group(3).strip()
            return f"Clause {clause}: {title}", clause

        return None, None

    def _normalize_sections(self, raw_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merges small fragments and splits oversized sections."""
        normalized: List[Dict[str, Any]] = []
        buffer_sec = None

        for sec in raw_sections:
            words = sec["text"].split()
            word_count = len(words)

            if word_count < self.min_words:
                if buffer_sec is None:
                    buffer_sec = dict(sec)
                else:
                    # Merge with existing buffer
                    buffer_sec["text"] += "\n\n" + sec["text"]
                    buffer_sec["page_end"] = sec["page_end"]
                    if sec.get("clause_no") and not buffer_sec.get("clause_no"):
                        buffer_sec["clause_no"] = sec["clause_no"]
                    if len(buffer_sec["text"].split()) >= self.min_words:
                        normalized.append(buffer_sec)
                        buffer_sec = None
            else:
                if buffer_sec is not None:
                    normalized.append(buffer_sec)
                    buffer_sec = None

                # Check if oversized
                if word_count > self.max_words:
                    sub_chunks = self._split_oversized(sec)
                    normalized.extend(sub_chunks)
                else:
                    normalized.append(sec)

        if buffer_sec is not None:
            normalized.append(buffer_sec)

        return normalized

    def _split_oversized(self, sec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Splits an oversized section on paragraph boundaries."""
        paragraphs = sec["text"].split("\n\n")
        chunks = []
        current_paras = []
        current_words = 0
        part_idx = 1

        for p in paragraphs:
            p_words = len(p.split())
            if current_words + p_words > self.max_words and current_paras:
                chunks.append({
                    "section_heading": f"{sec['section_heading']} (Part {part_idx})",
                    "clause_no": sec.get("clause_no"),
                    "page_start": sec["page_start"],
                    "page_end": sec["page_end"],
                    "text": "\n\n".join(current_paras)
                })
                part_idx += 1
                current_paras = [p]
                current_words = p_words
            else:
                current_paras.append(p)
                current_words += p_words

        if current_paras:
            chunks.append({
                "section_heading": f"{sec['section_heading']} (Part {part_idx})" if part_idx > 1 else sec['section_heading'],
                "clause_no": sec.get("clause_no"),
                "page_start": sec["page_start"],
                "page_end": sec["page_end"],
                "text": "\n\n".join(current_paras)
            })

        return chunks
