"""
Unit tests for Dual Chunking Strategies (Fixed-size vs. Section-aware).
Verifies that document title, circular number, publication date, and section headings
remain strictly attached to every generated chunk.
"""

import pytest
from src.chunking.fixed_chunker import FixedSizeChunker
from src.chunking.section_chunker import SectionAwareChunker

@pytest.fixture
def sample_parsed_doc():
    return {
        "doc_id": "RBI_DL_2022",
        "title": "Guidelines on Digital Lending",
        "circular_no": "DOR.CRE.REC.66/21.07.001/2022-23",
        "regulator": "Reserve Bank of India (RBI)",
        "publish_date": "2022-09-02",
        "effective_date": "2022-09-02",
        "is_active": True,
        "superseded_by": None,
        "supersedes": None,
        "pages": [
            {
                "page_number": 1,
                "text": "Reserve Bank of India\nGuidelines on Digital Lending\n\n1. Introduction\nDigital lending has gathered momentum in India. Regulated Entities shall ensure compliance.",
                "blocks": [
                    {"text": "1. Introduction\nDigital lending has gathered momentum in India.", "block_id": 1}
                ],
                "tables": []
            },
            {
                "page_number": 2,
                "text": "3. Disbursement of Loan and Repayments\nAll loan servicing, repayments, etc., shall be executed by the borrower directly into the RE's bank account without any pass-through account or pool account of any third party.\n\n4. Key Fact Statement\nA standardised Key Fact Statement (KFS) must be provided to the borrower before the execution of the contract.",
                "blocks": [
                    {"text": "3. Disbursement of Loan and Repayments\nAll loan servicing, repayments, etc., shall be executed by the borrower directly into the RE's bank account.", "block_id": 2},
                    {"text": "4. Key Fact Statement\nA standardised Key Fact Statement (KFS) must be provided to the borrower.", "block_id": 3}
                ],
                "tables": []
            }
        ]
    }

def test_fixed_size_chunking_metadata(sample_parsed_doc):
    chunker = FixedSizeChunker(chunk_size_words=30, overlap_words=10)
    chunks = chunker.chunk_document(sample_parsed_doc)

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.doc_title == "Guidelines on Digital Lending"
        assert chunk.publish_date == "2022-09-02"
        assert chunk.circular_no == "DOR.CRE.REC.66/21.07.001/2022-23"
        assert chunk.section_heading is not None and len(chunk.section_heading) > 0
        assert chunk.page_start >= 1
        assert chunk.chunk_strategy == "fixed_size"
        assert len(chunk.text) > 0

def test_section_aware_chunking_metadata(sample_parsed_doc):
    chunker = SectionAwareChunker(min_words=10, max_words=100)
    chunks = chunker.chunk_document(sample_parsed_doc)

    assert len(chunks) > 0
    headings = [c.section_heading for c in chunks]
    
    # Assert that structural headings were detected
    assert any("Disbursement" in h or "Key Fact" in h or "Introduction" in h for h in headings)
    for chunk in chunks:
        assert chunk.doc_title == "Guidelines on Digital Lending"
        assert chunk.publish_date == "2022-09-02"
        assert chunk.chunk_strategy == "section_aware"
        assert chunk.page_start in (1, 2)
