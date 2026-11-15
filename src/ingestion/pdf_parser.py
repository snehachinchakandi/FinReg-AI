"""
PDF Parser for FinReg AI using PyMuPDF (fitz).
Extracts text, structural blocks, tables, and page metadata from regulatory PDFs.
Handles repeated headers/footers and multi-column formatting.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any
import fitz  # PyMuPDF

class RegulatoryPDFParser:
    """Parser tailored for RBI and financial regulatory circulars."""

    def __init__(self, remove_headers_footers: bool = True):
        self.remove_headers_footers = remove_headers_footers

    def parse_pdf(self, pdf_path: str, doc_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses a single regulatory PDF document into structured pages and text blocks.
        """
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        pages_data = []
        full_text_list = []

        # First pass: identify common repeating headers / footers across pages
        header_patterns = [
            r"भारतीय\s+रिज़र्व\s+बैंक",
            r"RESERVE\s+BANK\s+OF\s+INDIA",
            r"www\.rbi\.org\.in",
            r"^\s*-\s*\d+\s*-\s*$",
            r"^\s*Page\s+\d+\s+of\s+\d+\s*$"
        ]

        for page_num in range(total_pages):
            page = doc[page_num]
            page_text = page.get_text("text")
            
            # Extract tables if present
            tables_data = []
            try:
                tables = page.find_tables()
                for tab in tables:
                    table_rows = tab.extract()
                    if table_rows:
                        # Convert to clean markdown table string
                        md_table = self._format_table_markdown(table_rows)
                        tables_data.append({
                            "bbox": tab.bbox,
                            "markdown": md_table,
                            "rows": table_rows
                        })
            except Exception:
                pass  # Fallback if table extraction fails

            # Extract text blocks with bounding boxes and font sizes
            blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, block_type)
            clean_blocks = []

            for b in blocks:
                # b[4] is the text content, b[6] is block type (0 = text, 1 = image)
                if b[6] == 0:
                    text = b[4].strip()
                    if not text:
                        continue
                    
                    # Filter out standard recurring header/footer noise if enabled
                    if self.remove_headers_footers:
                        is_noise = False
                        for pat in header_patterns:
                            if re.search(pat, text, re.IGNORECASE):
                                # If short header/footer line, skip from chunking text
                                if len(text.splitlines()) <= 2 and len(text) < 100:
                                    is_noise = True
                                    break
                        if is_noise:
                            continue

                    clean_blocks.append({
                        "bbox": [b[0], b[1], b[2], b[3]],
                        "text": text,
                        "block_id": b[5]
                    })

            page_combined_text = "\n\n".join([b["text"] for b in clean_blocks])
            pages_data.append({
                "page_number": page_num + 1,
                "text": page_combined_text,
                "blocks": clean_blocks,
                "tables": tables_data
            })
            full_text_list.append(page_combined_text)

        doc.close()

        return {
            "doc_id": doc_metadata.get("doc_id"),
            "title": doc_metadata.get("title"),
            "circular_no": doc_metadata.get("circular_no"),
            "regulator": doc_metadata.get("regulator"),
            "publish_date": doc_metadata.get("publish_date"),
            "effective_date": doc_metadata.get("effective_date"),
            "is_active": doc_metadata.get("is_active", True),
            "superseded_by": doc_metadata.get("superseded_by"),
            "supersedes": doc_metadata.get("supersedes"),
            "total_pages": total_pages,
            "source_file": str(pdf_path),
            "pages": pages_data,
            "full_document_text": "\n\n--- PAGE BREAK ---\n\n".join(full_text_list)
        }

    def _format_table_markdown(self, rows: List[List[Any]]) -> str:
        """Converts raw table rows into Markdown format."""
        if not rows or len(rows) < 1:
            return ""
        
        # Clean cell text
        clean_rows = []
        for row in rows:
            clean_row = [str(cell).replace("\n", " ").strip() if cell is not None else "" for cell in row]
            clean_rows.append(clean_row)
            
        header = clean_rows[0]
        md_lines = ["| " + " | ".join(header) + " |"]
        md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        
        for row in clean_rows[1:]:
            # Pad row if shorter than header
            padded = row + [""] * (len(header) - len(row))
            md_lines.append("| " + " | ".join(padded[:len(header)]) + " |")
            
        return "\n".join(md_lines)
