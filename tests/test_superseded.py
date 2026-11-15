"""
Unit tests for Date-Specific Historical Retrieval, Staggered Commencement, and
Tri-Temporal Regulatory Versioning (Phase B2.1).
Verifies:
1. Correct 2023 circular identifier (RBI/2023-24/41 DOR.CRE.REC.21/21.07.001/2023-24).
2. Staggered commencement dates in 2025 Directions (Para 6 eff. 2025-11-01, Para 17 eff. 2025-06-15, others eff. 2025-05-08).
3. Paragraph 6 multi-lender arrangements before vs after 2025-11-01.
4. Paragraph 17 CIMS reporting before vs after 2025-06-15.
5. Example A: "What was the DLG cap in October 2024?" -> Retrieves RBI_DLG_2023 (5%), excludes RBI_DL_2025.
6. Example B: "What was the DLG cap in October 2025?" -> Retrieves RBI_DL_2025 Para 23 (5%), excludes RBI_DLG_2023.
7. Example C: "What were the RBI digital lending requirements in June 2025?" -> Respects staggered commencement.
8. Example D: "Compare the DLG rules in 2022, 2024 and 2026." -> Multi-era comparison with distinct dates/citations.
9. Example E: "What is the current DLG cap?" -> Current mode retrieves RBI_DL_2025 Para 23.
10. Source & pagination descriptions: Local rendered PDF distinction & paragraph anchor citations.
11. Current digital lending loan disbursements retrieve RBI_DL_2025 Paragraph 9.
12. Historical pre-June-2023 FLDG queries retrieve RBI_DL_2022 Clause 15 (synthetic securitisation).
13. 2025 repeal provisions (Paragraph 30 & Annex III) are correctly indexed and represented.
14. Unrelated regulatory documents remain unaffected and active.
15. Ambiguous or missing dates are safely handled.
16. Hybrid retrieval verifies date-aware selection across dense and BM25.
"""

import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import json
import pytest
from pathlib import Path
from src.config import INDEXES_DIR, SECTION_CHUNKS_FILE, FIXED_CHUNKS_FILE, METADATA_FILE
from src.versioning.temporal_filter import (
    RegulatoryVersionManager,
    parse_date_query,
    is_chunk_valid_on_date,
    SUPERSEDED_REGISTRY,
    CURRENT_SYSTEM_DATE
)
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.dense import DenseRetriever
from src.retrieval.hybrid import HybridRetriever
from src.generation.rag_engine import FinRegRAGEngine

# ---------------------------------------------------------------------------
# 1. Identifier & Metadata Verification Tests
# ---------------------------------------------------------------------------

def test_2023_circular_number_correction():
    """
    Item 1: Verify the 2023 DLG circular identifier is strictly corrected to:
    RBI/2023-24/41 DOR.CRE.REC.21/21.07.001/2023-24 across metadata, chunks, and registry.
    Confirm that the incorrect identifier (DOR.CRE.REC.20/21.04.048/2023-24) does not appear.
    """
    expected_circ = "RBI/2023-24/41 DOR.CRE.REC.21/21.07.001/2023-24"
    incorrect_circ = "21.04.048"

    # Check documents_metadata.json
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        meta_list = json.load(f)
    dlg_meta = [m for m in meta_list if m["doc_id"] == "RBI_DLG_2023"][0]
    assert dlg_meta["circular_no"] == expected_circ
    assert incorrect_circ not in dlg_meta["circular_no"]

    # Check chunks in section_chunks.json
    with open(SECTION_CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    dlg_chunks = [c for c in chunks if c["doc_id"] == "RBI_DLG_2023"]
    assert len(dlg_chunks) > 0
    for c in dlg_chunks:
        assert c["circular_no"] == expected_circ
        assert incorrect_circ not in c["circular_no"]

    # Check SUPERSEDED_REGISTRY in temporal_filter.py
    fldg_reg = SUPERSEDED_REGISTRY["FLDG_SYNTHETIC_SECURITISATION"]
    assert fldg_reg["intermediate_circular_no"] == expected_circ
    assert incorrect_circ not in fldg_reg["intermediate_circular_no"]


def test_staggered_commencement_metadata():
    """
    Item 2: Verify provision-level staggered commencement dates in RBI_DL_2025:
    - Paragraph 6: effective 2025-11-01
    - Paragraph 17: effective 2025-06-15
    - General provisions (Paras 8, 9, 23): effective 2025-05-08
    """
    with open(SECTION_CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    dl_2025_chunks = [c for c in chunks if c["doc_id"] == "RBI_DL_2025"]

    para6_chunks = [c for c in dl_2025_chunks if c.get("clause_no") == "6" or "multiple lenders" in c.get("section_heading", "").lower()]
    para17_chunks = [c for c in dl_2025_chunks if c.get("clause_no") == "17" or "cims portal" in c.get("section_heading", "").lower()]
    para23_chunks = [c for c in dl_2025_chunks if c.get("clause_no") == "23" or "cap on dlg" in c.get("section_heading", "").lower()]
    para9_chunks  = [c for c in dl_2025_chunks if c.get("clause_no") == "9" or "disbursal" in c.get("section_heading", "").lower()]

    assert len(para6_chunks) > 0
    assert para6_chunks[0]["effective_date"] == "2025-11-01"

    assert len(para17_chunks) > 0
    assert para17_chunks[0]["effective_date"] == "2025-06-15"

    assert len(para23_chunks) > 0
    assert para23_chunks[0]["effective_date"] == "2025-05-08"

    assert len(para9_chunks) > 0
    assert para9_chunks[0]["effective_date"] == "2025-05-08"


def test_source_and_pagination_descriptions():
    """
    Item 4: Verify that the 2025 PDF is clearly designated as a local rendered representation,
    the primary source URL points to the official RBI notification, and citations anchor on paragraphs.
    """
    with open(SECTION_CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    dl_2025_chunks = [c for c in chunks if c["doc_id"] == "RBI_DL_2025"]
    assert len(dl_2025_chunks) > 0

    c0 = dl_2025_chunks[0]
    assert c0.get("source_type") == "local_rendered_pdf"
    assert "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12848" in c0.get("primary_source_url", "")

    # Citation anchors on Paragraph / Clause and notes Local Rendered PDF Page
    para23 = [c for c in dl_2025_chunks if c.get("clause_no") == "23"][0]
    citation = para23.get("citation_str") or f"[{para23['doc_title']} | Paragraph/Clause: {para23['clause_no']}]"
    assert "23" in citation
    assert "Local Rendered PDF Page" in citation or "Paragraph/Clause" in citation


# ---------------------------------------------------------------------------
# 2. Date-Specific Retrieval & Commencement Tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def section_bm25_retriever():
    """Fixture loading section BM25 index with date-aware metadata."""
    retriever = BM25Retriever()
    idx_path = INDEXES_DIR / "section_bm25.pkl"
    chunks_path = INDEXES_DIR / "section_bm25_chunks.json"
    if idx_path.exists() and chunks_path.exists():
        retriever.load(str(idx_path), str(chunks_path))
    else:
        with open(SECTION_CHUNKS_FILE, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        retriever.build_index(chunks)
    return retriever


@pytest.fixture(scope="module")
def section_hybrid_retriever(section_bm25_retriever):
    """Fixture loading section Hybrid retriever."""
    dense = DenseRetriever()
    dense.load(str(INDEXES_DIR / "section_dense.faiss"), str(INDEXES_DIR / "section_chunks_index.json"))
    return HybridRetriever(dense, section_bm25_retriever)


def test_staggered_commencement_para_6_before_and_after_nov_2025(section_bm25_retriever):
    """
    Test Paragraph 6 (multi-lender RE-LSP arrangements) before and after November 1, 2025.
    - October 15, 2025: Not yet effective -> must be excluded.
    - November 15, 2025: Effective -> must be retrievable.
    """
    version_mgr = RegulatoryVersionManager()
    
    # Before commencement: October 15, 2025
    q_before = "What are the RE-LSP requirements for multiple lenders on October 15, 2025?"
    anchor_before = version_mgr.extract_temporal_anchor(q_before)
    assert anchor_before["intent"] == "HISTORICAL_DATE"
    assert anchor_before["target_date"] == "2025-10-15"

    results_before = section_bm25_retriever.search(q_before, top_k=10)
    for chunk, _ in results_before:
        if chunk.get("doc_id") == "RBI_DL_2025":
            assert chunk.get("clause_no") != "6", "Paragraph 6 cannot be active on October 15, 2025!"

    # After commencement: November 15, 2025
    q_after = "What are the RE-LSP requirements for multiple lenders as of November 15, 2025?"
    anchor_after = version_mgr.extract_temporal_anchor(q_after)
    assert anchor_after["intent"] == "HISTORICAL_DATE"
    assert anchor_after["target_date"] == "2025-11-15"

    results_after = section_bm25_retriever.search(q_after, top_k=10)
    para6_after = [c for c, _ in results_after if c.get("doc_id") == "RBI_DL_2025" and c.get("clause_no") == "6"]
    assert len(para6_after) > 0, "Paragraph 6 should be active and retrievable on November 15, 2025!"


def test_staggered_commencement_para_17_before_and_after_june_2025(section_bm25_retriever):
    """
    Test Paragraph 17 (CIMS portal reporting) before and after June 15, 2025.
    - June 1, 2025: Not yet effective -> excluded.
    - June 20, 2025: Effective -> retrievable.
    """
    version_mgr = RegulatoryVersionManager()

    # Before commencement: June 1, 2025
    q_before = "What were the CIMS reporting requirements for DLAs on June 1, 2025 before commencement?"
    anchor_before = version_mgr.extract_temporal_anchor(q_before)
    assert anchor_before["intent"] == "HISTORICAL_DATE"
    assert anchor_before["target_date"] == "2025-06-01"

    results_before = section_bm25_retriever.search(q_before, top_k=10)
    for chunk, _ in results_before:
        if chunk.get("doc_id") == "RBI_DL_2025":
            assert chunk.get("clause_no") != "17", "Paragraph 17 cannot be active on June 1, 2025!"

    # After commencement: June 20, 2025
    q_after = "What were the CIMS reporting requirements for DLAs on June 20, 2025?"
    anchor_after = version_mgr.extract_temporal_anchor(q_after)
    assert anchor_after["intent"] == "HISTORICAL_DATE"
    assert anchor_after["target_date"] == "2025-06-20"

    results_after = section_bm25_retriever.search(q_after, top_k=10)
    para17_after = [c for c, _ in results_after if c.get("doc_id") == "RBI_DL_2025" and (c.get("clause_no") == "17" or "cims" in c["text"].lower())]
    assert len(para17_after) > 0, "Paragraph 17 should be active on June 20, 2025!"


def test_date_specific_retrieval_example_a_october_2024(section_bm25_retriever):
    """
    Example A: "What was the DLG cap in October 2024?"
    Expected: 2023 DLG circular (RBI_DLG_2023), 5% cap, historically applicable.
    RBI_DL_2025 MUST NOT be retrieved as applicable on October 2024!
    """
    query = "What was the DLG cap in October 2024?"
    version_mgr = RegulatoryVersionManager()
    anchor = version_mgr.extract_temporal_anchor(query)
    assert anchor["intent"] == "HISTORICAL_DATE"
    assert anchor["target_date"] == "2024-10-15"

    results = section_bm25_retriever.search(query, top_k=10)
    assert len(results) > 0

    # Every retrieved chunk must be legally valid on 2024-10-15
    for chunk, _ in results:
        assert is_chunk_valid_on_date(chunk, "2024-10-15") is True
        assert chunk["doc_id"] != "RBI_DL_2025", "RBI_DL_2025 was not in force in October 2024!"

    dlg_2023_chunks = [c for c, _ in results if c["doc_id"] == "RBI_DLG_2023"]
    assert len(dlg_2023_chunks) > 0
    text_content = " ".join(c["text"].lower() for c in dlg_2023_chunks)
    assert "5%" in text_content or "5 per cent" in text_content or "five" in text_content


def test_date_specific_retrieval_example_b_october_2025(section_bm25_retriever):
    """
    Example B: "What was the DLG cap in October 2025?"
    Expected: 2025 Directions (RBI_DL_2025), Paragraph 23, 5% cap.
    Repealed 2023 circular MUST NOT be retrieved as applicable on October 2025!
    """
    query = "What was the DLG cap in October 2025?"
    version_mgr = RegulatoryVersionManager()
    anchor = version_mgr.extract_temporal_anchor(query)
    assert anchor["intent"] == "HISTORICAL_DATE"
    assert anchor["target_date"] == "2025-10-15"

    results = section_bm25_retriever.search(query, top_k=10)
    assert len(results) > 0

    # Every retrieved chunk must be legally valid on 2025-10-15
    for chunk, _ in results:
        assert is_chunk_valid_on_date(chunk, "2025-10-15") is True
        assert chunk["doc_id"] != "RBI_DLG_2023", "RBI_DLG_2023 was repealed before October 2025!"
        assert chunk["doc_id"] != "RBI_DL_2022", "RBI_DL_2022 was repealed before October 2025!"

    dlg_2025_chunks = [c for c, _ in results if c["doc_id"] == "RBI_DL_2025"]
    assert len(dlg_2025_chunks) > 0

    para23_chunks = [c for c in dlg_2025_chunks if c.get("clause_no") == "23" or "cap on dlg" in c.get("section_heading", "").lower()]
    assert len(para23_chunks) > 0
    assert "5" in para23_chunks[0]["text"] or "five" in para23_chunks[0]["text"].lower()


def test_date_specific_retrieval_example_c_june_2025(section_bm25_retriever):
    """
    Example C: "What were the RBI digital lending requirements in June 2025?"
    Month-level query crossing commencement date of June 15, 2025.
    Must NOT automatically resolve to an arbitrary single date.
    Must identify TRANSITION_PERIOD and demarcate June 1–14 from June 15–30.
    """
    query = "What were the RBI digital lending requirements in June 2025?"
    version_mgr = RegulatoryVersionManager()
    anchor = version_mgr.extract_temporal_anchor(query)
    assert anchor["intent"] == "TRANSITION_PERIOD"
    assert anchor["month_year"] == "2025-06"
    assert len(anchor["periods"]) == 2
    assert anchor["periods"][0]["label"] == "June 1 – June 14, 2025"
    assert anchor["periods"][1]["label"] == "June 15 – June 30, 2025"
    assert anchor["periods"][0]["para17_in_force"] is False
    assert anchor["periods"][1]["para17_in_force"] is True

    results = section_bm25_retriever.search(query, top_k=10)
    assert len(results) > 0
    top_docs = [c["doc_id"] for c, _ in results]
    assert "RBI_DL_2025" in top_docs
    assert "RBI_DL_2022" not in top_docs
    assert "RBI_DLG_2023" not in top_docs

    # In June 2025, Paragraph 6 MUST NOT be in force in either sub-period
    for chunk, _ in results:
        if chunk.get("doc_id") == "RBI_DL_2025":
            assert chunk.get("clause_no") != "6", "Paragraph 6 was not yet in force in June 2025!"


def test_comparison_query_example_d_2022_2024_2026(section_bm25_retriever):
    """
    Example D: "Compare the DLG rules in 2022, 2024 and 2026."
    Expected: Comparison across 2022, 2023, and 2025 provisions, each clearly dated and labeled.
    """
    query = "Compare the DLG rules in 2022, 2024 and 2026."
    version_mgr = RegulatoryVersionManager()
    anchor = version_mgr.extract_temporal_anchor(query)
    assert anchor["intent"] == "COMPARISON"
    assert 2022 in anchor["comparison_years"]
    assert 2024 in anchor["comparison_years"]
    assert 2026 in anchor["comparison_years"]

    diff = version_mgr.get_version_diff(query)
    assert diff["rule_key"] == "FLDG_SYNTHETIC_SECURITISATION"
    assert diff["old_version"]["doc_id"] == "RBI_DL_2022"
    assert diff["intermediate_version"]["doc_id"] == "RBI_DLG_2023"
    assert diff["current_version"]["doc_id"] == "RBI_DL_2025"

    assert "2022-09-02" in diff["old_version"]["effective_date"]
    assert "2023-06-08" in diff["intermediate_version"]["effective_date"]
    assert "2025-05-08" in diff["current_version"]["effective_date"]

    assert diff["old_version"]["status"] == "SUPERSEDED / REPEALED"
    assert diff["intermediate_version"]["status"] == "SUPERSEDED / REPEALED"
    assert diff["current_version"]["status"] == "ACTIVE & CURRENT"


def test_current_query_example_e_dlg_cap(section_bm25_retriever):
    """
    Example E: "What is the current DLG cap?"
    Expected: 2025 Directions (RBI_DL_2025), Paragraph 23 (5% cap).
    Strictly excludes repealed 2022 and 2023 circulars.
    """
    query = "What is the current DLG cap?"
    version_mgr = RegulatoryVersionManager()
    anchor = version_mgr.extract_temporal_anchor(query)
    assert anchor["intent"] == "CURRENT"

    results = section_bm25_retriever.search(query, top_k=10, filter_active_only=True)
    assert len(results) > 0

    for chunk, _ in results:
        assert chunk["is_active"] is True
        assert chunk["doc_id"] not in ["RBI_DL_2022", "RBI_DLG_2023"]

    para23_chunks = [
        c for c, _ in results 
        if c.get("doc_id") == "RBI_DL_2025" and (c.get("clause_no") == "23" or "cap on dlg" in c.get("section_heading", "").lower())
    ]
    assert len(para23_chunks) > 0
    assert "5" in para23_chunks[0]["text"] or "five" in para23_chunks[0]["text"].lower()


# ---------------------------------------------------------------------------
# 3. Regression & General Retrieval Tests
# ---------------------------------------------------------------------------

def test_current_digital_lending_disbursement_retrieves_2025_paragraph_9(section_bm25_retriever):
    """Current digital lending disbursement query retrieves RBI_DL_2025 Paragraph 9."""
    query = "Where must digital lending loan disbursements and repayments be executed?"
    results = section_bm25_retriever.search(query, top_k=5, filter_active_only=True)
    
    assert len(results) > 0
    assert results[0][0].get("doc_id") == "RBI_DL_2025"
    assert results[0][0].get("is_active") is True

    clause9_chunks = [
        c for c, _ in results 
        if c.get("doc_id") == "RBI_DL_2025" and (c.get("clause_no") == "9" or "disbursal" in c.get("section_heading", "").lower())
    ]
    assert len(clause9_chunks) > 0
    assert "bank account" in clause9_chunks[0]["text"].lower()


def test_historical_pre_june_2023_fldg_query_retrieves_2022_clause_15(section_bm25_retriever):
    """Historical pre-June-2023 FLDG query retrieves RBI_DL_2022 Clause 15 (synthetic securitisation)."""
    version_mgr = RegulatoryVersionManager()
    query = "Under the original 2022 Digital Lending Guidelines, what was the position on First Loss Default Guarantee (FLDG) prior to the 2023 circular?"
    
    anchor = version_mgr.extract_temporal_anchor(query)
    assert anchor["intent"] == "HISTORICAL_DATE"
    assert anchor["target_date"] in ("2023-06-07", "2022-10-01", "2022-09-02")

    results = section_bm25_retriever.search(query, top_k=10)
    
    historical_fldg_chunks = [
        c for c, _ in results 
        if c.get("doc_id") == "RBI_DL_2022" and (c.get("clause_no") == "15" or "synthetic securitisation" in c["text"].lower())
    ]
    assert len(historical_fldg_chunks) > 0
    hist_chunk = historical_fldg_chunks[0]
    assert "RBI_DLG_2023" in str(hist_chunk.get("superseded_by"))
    assert "securitisation" in hist_chunk["text"].lower()


def test_2025_repeal_provisions_represented(section_bm25_retriever):
    """Verify that 2025 repeal provisions (Paragraph 30 & Annex III) are correctly indexed and represented."""
    query = "Which earlier digital lending circulars were repealed under Paragraph 30 and Annex III of the Directions 2025?"
    results = section_bm25_retriever.search(query, top_k=10, filter_active_only=True)
    
    assert len(results) > 0
    rbi_2025_chunks = [c for c, _ in results if c.get("doc_id") == "RBI_DL_2025"]
    assert len(rbi_2025_chunks) > 0
    
    repeal_chunks = [
        c for c in rbi_2025_chunks 
        if c.get("clause_no") == "30" or "repeal" in c.get("section_heading", "").lower()
    ]
    assert len(repeal_chunks) > 0
    text = repeal_chunks[0]["text"].lower()
    assert "repeal" in text
    assert "annex" in text or "circulars" in text or "directions" in text


def test_unrelated_regulatory_documents_unaffected():
    """Verify unrelated regulatory documents (Penal charges, PPI, P2P, CoFT) maintain is_active=True."""
    with open(SECTION_CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    unrelated_doc_ids = ["RBI_PENAL_2023", "RBI_PPI_MD_2021", "RBI_COFT_2021", "RBI_P2P_MD_2017", "RBI_PA_PG_2020"]
    for doc_id in unrelated_doc_ids:
        doc_chunks = [c for c in chunks if c.get("doc_id") == doc_id]
        assert len(doc_chunks) > 0, f"Expected chunks for {doc_id}"
        for c in doc_chunks:
            assert c.get("is_active", True) is True, f"Chunk {c['chunk_id']} should remain active!"


def test_missing_or_ambiguous_date_information_handled_safely():
    """Missing or ambiguous date / status fields are handled safely without raising exceptions."""
    version_mgr = RegulatoryVersionManager()
    
    sparse_chunk = {
        "chunk_id": "c_sparse",
        "text": "Regulatory clause text.",
        "doc_title": "Generic Circular"
    }
    
    filtered = version_mgr.filter_chunks([(sparse_chunk, 0.5)], allow_superseded=False)
    assert len(filtered) == 1

    status = version_mgr.format_chunk_temporal_status(sparse_chunk)
    assert "CURRENT & ACTIVE" in status

    assert version_mgr.is_historical_query("") is False
    assert version_mgr.is_historical_query(None) is False


def test_hybrid_retrieval_date_aware(section_hybrid_retriever):
    """Hybrid retrieval applies date-aware auto-selection across dense and BM25."""
    # 1. October 2024: retrieves 2023 DLG circular
    res_2024 = section_hybrid_retriever.search("What was the DLG cap in October 2024?", top_k=5)
    assert len(res_2024) > 0
    for chunk, _ in res_2024:
        assert chunk["doc_id"] != "RBI_DL_2025"
    assert any(c["doc_id"] == "RBI_DLG_2023" for c, _ in res_2024)

    # 2. October 2025: retrieves 2025 Directions
    res_2025 = section_hybrid_retriever.search("What was the DLG cap in October 2025?", top_k=5)
    assert len(res_2025) > 0
    for chunk, _ in res_2025:
        assert chunk["doc_id"] != "RBI_DLG_2023"
        assert chunk["doc_id"] != "RBI_DL_2022"
    assert any(c["doc_id"] == "RBI_DL_2025" for c, _ in res_2025)


# ---------------------------------------------------------------------------
# 4. Phase B2.2 Ambiguous Temporal Query & Exact Cutoff Regression Tests
# ---------------------------------------------------------------------------

def test_ambiguous_june_2025_query_separates_sub_periods(section_bm25_retriever):
    """
    Phase B2.2 Test 1: "What were the digital lending requirements in June 2025?"
    Verifies that the RAG pipeline does not pick an arbitrary single date, but separates
    June 1–14 from June 15–30, correctly noting the commencement of Paragraph 17.
    """
    query = "What were the digital lending requirements in June 2025?"
    version_mgr = RegulatoryVersionManager()
    anchor = version_mgr.extract_temporal_anchor(query)
    
    # 1. Structural parser assertions
    assert anchor["intent"] == "TRANSITION_PERIOD"
    assert anchor["month_year"] == "2025-06"
    assert anchor["transition_date"] == "2025-06-15"
    assert len(anchor["periods"]) == 2
    assert anchor["periods"][0]["para17_in_force"] is False
    assert anchor["periods"][1]["para17_in_force"] is True

    # 2. Retrieval assertions
    results = section_bm25_retriever.search(query, top_k=10)
    assert len(results) > 0
    top_docs = [c["doc_id"] for c, _ in results]
    assert "RBI_DL_2025" in top_docs
    assert "RBI_DL_2022" not in top_docs
    assert "RBI_DLG_2023" not in top_docs

    # Paragraph 6 (multi-lenders) must NOT be in force in June 2025
    for chunk, _ in results:
        if chunk.get("doc_id") == "RBI_DL_2025":
            assert chunk.get("clause_no") != "6"

    # 3. Grounded generation separation test with separate citations
    engine = FinRegRAGEngine(api_key="test_dummy_key")
    gen_result = engine.generate_answer(query, results)
    ans = gen_result["answer"]

    assert ("June 1–14" in ans or "June 1-14" in ans or ("June 1" in ans and "14" in ans))
    assert ("June 15–30" in ans or "June 15-30" in ans or ("June 15" in ans and "30" in ans))
    assert "Paragraph 17" in ans or "CIMS" in ans
    
    # Must contain separate citations for each period
    assert len(gen_result["citations"]) >= 2
    cited_clauses = [str(c.get("clause", "")) for c in gen_result["citations"]]
    assert "17" in cited_clauses, "Period 2 must cite Paragraph 17"
    assert any(cl in ["8", "9", "23", "None", "General"] for cl in cited_clauses), "Period 1 must cite active general provision"


def test_what_changed_on_june_15_2025(section_bm25_retriever):
    """
    Phase B2.2 Test 2: "What changed on June 15, 2025?"
    Identifies transition event on June 15, 2025 when Paragraph 17 of 2025 Directions came into force.
    """
    query = "What changed on June 15, 2025?"
    version_mgr = RegulatoryVersionManager()
    anchor = version_mgr.extract_temporal_anchor(query)

    assert anchor["intent"] == "TRANSITION_EVENT"
    assert anchor["transition_date"] == "2025-06-15"
    assert anchor["event_info"]["clause_no"] == "17"

    results = section_bm25_retriever.search(query, top_k=10)
    assert len(results) > 0
    
    # Retrieved chunks must include Paragraph 17 or CIMS portal reporting
    para17_chunks = [
        c for c, _ in results 
        if c.get("doc_id") == "RBI_DL_2025" and (c.get("clause_no") == "17" or "cims portal" in c.get("section_heading", "").lower())
    ]
    assert len(para17_chunks) > 0
    assert "cims" in para17_chunks[0]["text"].lower()


def test_what_applied_before_june_15_2025(section_bm25_retriever):
    """
    Phase B2.2 Test 3: "What applied before June 15, 2025?"
    Evaluates on exact cutoff 2025-06-14:
    - Paragraph 17 is strictly NOT yet effective (excluded).
    - Paragraph 6 is strictly NOT yet effective (excluded).
    - Active 2025 provisions (Paras 8, 9, 23) ARE in force.
    - Repealed 2022/2023 circulars are excluded.
    """
    query = "What applied before June 15, 2025?"
    version_mgr = RegulatoryVersionManager()
    anchor = version_mgr.extract_temporal_anchor(query)

    assert anchor["intent"] == "HISTORICAL_DATE"
    assert anchor["target_date"] == "2025-06-14"
    assert anchor["cutoff_date"] == "2025-06-14"

    results = section_bm25_retriever.search(query, top_k=10)
    assert len(results) > 0

    for chunk, _ in results:
        assert is_chunk_valid_on_date(chunk, "2025-06-14") is True
        if chunk.get("doc_id") == "RBI_DL_2025":
            assert chunk.get("clause_no") != "17", "Paragraph 17 cannot be active before June 15, 2025!"
            assert chunk.get("clause_no") != "6", "Paragraph 6 cannot be active before June 15, 2025!"
        assert chunk.get("doc_id") not in ["RBI_DL_2022", "RBI_DLG_2023"]


def test_what_applied_after_june_15_2025(section_bm25_retriever):
    """
    Phase B2.2.1: "What applied after June 15, 2025?"
    Strictly resolves to from June 16, 2025 (2025-06-16), excluding the commencement date itself:
    - Paragraph 17 IS in force and retrievable.
    - Paragraph 6 is NOT yet in force (effective Nov 1, 2025).
    - General 2025 provisions are in force.
    """
    query = "What applied after June 15, 2025?"
    version_mgr = RegulatoryVersionManager()
    anchor = version_mgr.extract_temporal_anchor(query)

    assert anchor["intent"] == "HISTORICAL_DATE"
    assert anchor["target_date"] == "2025-06-16"

    results = section_bm25_retriever.search(query, top_k=10)
    assert len(results) > 0

    for chunk, _ in results:
        assert is_chunk_valid_on_date(chunk, "2025-06-16") is True
        if chunk.get("doc_id") == "RBI_DL_2025":
            assert chunk.get("clause_no") != "6", "Paragraph 6 cannot be active after June 15, 2025!"

    # Verify applicability: Para 17 is applicable; Para 6 is not
    with open(SECTION_CHUNKS_FILE, "r", encoding="utf-8") as f:
        all_chunks = json.load(f)
    para17_chunk = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2025" and c.get("clause_no") == "17"][0]
    para6_chunk = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2025" and c.get("clause_no") == "6"][0]
    assert version_mgr.is_chunk_applicable(para17_chunk, query) is True
    assert version_mgr.is_chunk_applicable(para6_chunk, query) is False

    # And when querying specifically for CIMS portal reporting post-June 15, Para 17 is retrieved
    cims_results = section_bm25_retriever.search("What CIMS portal reporting requirements applied after June 15, 2025?", top_k=5)
    assert len(cims_results) > 0
    assert cims_results[0][0].get("clause_no") == "17"


def test_what_was_applicable_before_the_june_2023_dlg_circular(section_bm25_retriever):
    """
    Phase B2.2 Test 5: "What was applicable before the June 2023 DLG circular?"
    Derives exact cutoff date 2023-06-07 (day before June 8, 2023 DLG circular):
    - Retrieves RBI_DL_2022 Clause 15 (synthetic securitisation / FLDG).
    - Excludes RBI_DLG_2023 (effective June 8, 2023).
    - Excludes RBI_DL_2025 (effective May 8, 2025).
    """
    query = "What was applicable before the June 2023 DLG circular?"
    version_mgr = RegulatoryVersionManager()
    anchor = version_mgr.extract_temporal_anchor(query)

    assert anchor["intent"] == "HISTORICAL_DATE"
    assert anchor["target_date"] == "2023-06-07"
    assert anchor["cutoff_date"] == "2023-06-07"

    results = section_bm25_retriever.search(query, top_k=10)
    assert len(results) > 0

    for chunk, _ in results:
        assert is_chunk_valid_on_date(chunk, "2023-06-07") is True
        assert chunk["doc_id"] != "RBI_DLG_2023"
        assert chunk["doc_id"] != "RBI_DL_2025"

    # Confirm RBI_DL_2022 synthetic securitisation is retrieved
    hist_fldg = [
        c for c, _ in results 
        if c.get("doc_id") == "RBI_DL_2022" and (c.get("clause_no") == "15" or "synthetic securitisation" in c["text"].lower())
    ]
    assert len(hist_fldg) > 0


def test_what_applied_under_the_original_2022_guidelines(section_bm25_retriever):
    """
    Phase B2.2 Test 6: "What applied under the original 2022 guidelines?"
    Derives exact commencement date 2022-09-02:
    - Retrieves RBI_DL_2022.
    - Excludes subsequent circulars (RBI_DLG_2023, RBI_DL_2025).
    """
    query = "What applied under the original 2022 guidelines?"
    version_mgr = RegulatoryVersionManager()
    anchor = version_mgr.extract_temporal_anchor(query)

    assert anchor["intent"] == "HISTORICAL_DATE"
    assert anchor["target_date"] == "2022-09-02"

    results = section_bm25_retriever.search(query, top_k=10)
    assert len(results) > 0

    for chunk, _ in results:
        assert is_chunk_valid_on_date(chunk, "2022-09-02") is True
        assert chunk["doc_id"] != "RBI_DLG_2023"
        assert chunk["doc_id"] != "RBI_DL_2025"

    dl_2022_chunks = [c for c, _ in results if c["doc_id"] == "RBI_DL_2022"]
    assert len(dl_2022_chunks) > 0


def test_what_were_the_rules_before_november_1_2025(section_bm25_retriever):
    """
    Phase B2.2 Test 7: "What were the rules before November 1, 2025?"
    Derives exact cutoff date 2025-10-31:
    - Paragraph 6 (multi-lenders) is strictly EXCLUDED.
    - Paragraph 17 (CIMS reporting) IS INCLUDED.
    - General 2025 provisions ARE INCLUDED.
    - Repealed 2022 and 2023 circulars are EXCLUDED.
    """
    query = "What were the rules before November 1, 2025?"
    version_mgr = RegulatoryVersionManager()
    anchor = version_mgr.extract_temporal_anchor(query)

    assert anchor["intent"] == "HISTORICAL_DATE"
    assert anchor["target_date"] == "2025-10-31"
    assert anchor["cutoff_date"] == "2025-10-31"

    results = section_bm25_retriever.search(query, top_k=10)
    assert len(results) > 0

    for chunk, _ in results:
        assert is_chunk_valid_on_date(chunk, "2025-10-31") is True
        if chunk.get("doc_id") == "RBI_DL_2025":
            assert chunk.get("clause_no") != "6", "Paragraph 6 cannot be active before November 1, 2025!"
        assert chunk["doc_id"] not in ["RBI_DL_2022", "RBI_DLG_2023"]

    # Verify applicability: Para 6 is excluded, while Para 17 and general provisions are applicable
    with open(SECTION_CHUNKS_FILE, "r", encoding="utf-8") as f:
        all_chunks = json.load(f)
    para6_chunk = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2025" and c.get("clause_no") == "6"][0]
    para17_chunk = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2025" and c.get("clause_no") == "17"][0]
    assert version_mgr.is_chunk_applicable(para6_chunk, query) is False
    assert version_mgr.is_chunk_applicable(para17_chunk, query) is True

    # And querying for multiple lenders before Nov 1, 2025 strictly excludes Paragraph 6
    multi_res = section_bm25_retriever.search("What rules on multiple lenders applied before November 1, 2025?", top_k=5)
    assert all(c.get("clause_no") != "6" for c, _ in multi_res)

    # While querying for CIMS reporting retrieves Paragraph 17
    cims_res = section_bm25_retriever.search("What CIMS portal reporting rules applied before November 1, 2025?", top_k=5)
    assert len(cims_res) > 0
    assert cims_res[0][0].get("clause_no") == "17"


# ---------------------------------------------------------------------------
# 5. Phase B2.2.1 Natural Language Date Semantics & Grounded Transition Tests
# ---------------------------------------------------------------------------

def test_from_and_on_june_15_2025():
    """
    Phase B2.2.1: Verify "From June 15, 2025" and "On June 15, 2025" resolve to 2025-06-15,
    whereas "After June 15, 2025" resolves to 2025-06-16.
    """
    version_mgr = RegulatoryVersionManager()
    
    # "From June 15, 2025" (starting on June 15)
    anchor_from = version_mgr.extract_temporal_anchor("What requirements applied from June 15, 2025?")
    assert anchor_from["intent"] == "HISTORICAL_DATE"
    assert anchor_from["target_date"] == "2025-06-15"

    # "On June 15, 2025" (exact commencement date)
    anchor_on = version_mgr.extract_temporal_anchor("What took effect on June 15, 2025?")
    assert anchor_on["intent"] in ("HISTORICAL_DATE", "TRANSITION_EVENT")
    assert anchor_on["target_date"] == "2025-06-15"

    # "After June 15, 2025" (starting from June 16)
    anchor_after = version_mgr.extract_temporal_anchor("What requirements applied after June 15, 2025?")
    assert anchor_after["intent"] == "HISTORICAL_DATE"
    assert anchor_after["target_date"] == "2025-06-16"


def test_calendar_month_prior_to_june_2023_vs_circular_commencement():
    """
    Phase B2.2.1: Verify calendar-month "Prior to June 2023" resolves to before June 1, 2023 (2023-05-31),
    whereas "Before the June 8, 2023 DLG circular took effect" resolves to June 7, 2023 (2023-06-07).
    """
    version_mgr = RegulatoryVersionManager()

    # Calendar month expression: Prior to June 2023 -> cutoff is 2023-05-31
    anchor_month = version_mgr.extract_temporal_anchor("What was the FLDG position prior to June 2023?")
    assert anchor_month["intent"] == "HISTORICAL_DATE"
    assert anchor_month["target_date"] == "2023-05-31"
    assert anchor_month["cutoff_date"] == "2023-05-31"

    # Circular commencement reference: Before June 8, 2023 DLG circular -> cutoff is 2023-06-07
    anchor_circ = version_mgr.extract_temporal_anchor("What was the rule before the June 8, 2023 DLG circular took effect?")
    assert anchor_circ["intent"] == "HISTORICAL_DATE"
    assert anchor_circ["target_date"] == "2023-06-07"
    assert anchor_circ["cutoff_date"] == "2023-06-07"


def test_under_2023_circular_preserves_complete_interval():
    """
    Phase B2.2.1: Verify "Under the 2023 circular" preserves the complete applicable interval
    (2023-06-08 through 2025-05-07), recognizes both co-existing regulatory documents
    (RBI_DLG_2023 and surviving provisions of RBI_DL_2022), and correctly evaluates validity boundaries.
    """
    version_mgr = RegulatoryVersionManager()
    query = "What was the DLG cap under the 2023 circular?"
    anchor = version_mgr.extract_temporal_anchor(query)

    assert anchor["intent"] == "HISTORICAL_DATE"
    assert anchor["target_date"] == "2023-06-08"
    assert anchor["cutoff_date"] == "2025-05-07"
    assert anchor["date_interval"] == ("2023-06-08", "2025-05-07")
    assert anchor.get("applicable_docs") == ["RBI_DLG_2023", "RBI_DL_2022"]

    with open(SECTION_CHUNKS_FILE, "r", encoding="utf-8") as f:
        all_chunks = json.load(f)
    dlg_chunk = [c for c in all_chunks if c.get("doc_id") == "RBI_DLG_2023"][0]
    dl_2022_clause3 = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2022" and c.get("clause_no") == "3"][0]
    dl_2022_clause15 = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2022" and c.get("clause_no") == "15"][0]

    # Valid within the interval for both DLG 2023 and surviving 2022 provisions
    assert is_chunk_valid_on_date(dlg_chunk, "2023-06-08") is True
    assert is_chunk_valid_on_date(dlg_chunk, "2024-10-15") is True
    assert is_chunk_valid_on_date(dlg_chunk, "2025-05-07") is True

    assert is_chunk_valid_on_date(dl_2022_clause3, "2023-06-08") is True
    assert is_chunk_valid_on_date(dl_2022_clause3, "2024-10-15") is True
    assert is_chunk_valid_on_date(dl_2022_clause3, "2025-05-07") is True

    # Invalid outside the interval (before commencement or after repeal)
    assert is_chunk_valid_on_date(dlg_chunk, "2023-06-07") is False
    assert is_chunk_valid_on_date(dlg_chunk, "2025-05-08") is False
    assert is_chunk_valid_on_date(dl_2022_clause3, "2025-05-08") is False

    # Clause 15 of 2022 (superseded on 2023-06-08) is strictly invalid during the 2023 circular regime
    assert is_chunk_valid_on_date(dl_2022_clause15, "2023-06-08") is False


def test_2023_regime_retrieves_both_2022_and_2023_provisions(section_bm25_retriever):
    """
    Phase B Final Checklist Item 10.1:
    Verify that queries under the 2023 circular regime (June 8, 2023 - May 7, 2025)
    can retrieve BOTH applicable 2022 provisions (e.g. Clause 3 loan disbursements)
    and 2023 DLG provisions without incorrectly restricting the regime to a single document.
    """
    # 1. Query for loan disbursements under the 2023 regime -> retrieves surviving 2022 Clause 3
    q_disb = "Under the 2023 circular regime, where must digital lending loan disbursements be executed?"
    res_disb = section_bm25_retriever.search(q_disb, top_k=5)
    assert len(res_disb) > 0
    top_disb = res_disb[0][0]
    assert top_disb.get("doc_id") == "RBI_DL_2022"
    assert top_disb.get("clause_no") == "3"
    assert "bank account" in top_disb.get("text", "").lower()

    # 2. Query for DLG cap under the 2023 circular -> retrieves 2023 DLG circular
    q_dlg = "What was the DLG cap under the 2023 circular?"
    res_dlg = section_bm25_retriever.search(q_dlg, top_k=5)
    assert len(res_dlg) > 0
    top_dlg = res_dlg[0][0]
    assert top_dlg.get("doc_id") == "RBI_DLG_2023"

    # 3. Neither query retrieves repealed 2022 Clause 15 or 2025 Directions
    for c, _ in res_disb:
        assert not (c.get("doc_id") == "RBI_DL_2022" and c.get("clause_no") == "15")
        assert c.get("doc_id") != "RBI_DL_2025"
    for c, _ in res_dlg:
        assert not (c.get("doc_id") == "RBI_DL_2022" and c.get("clause_no") == "15")
        assert c.get("doc_id") != "RBI_DL_2025"


def test_june_2025_citation_grounding_rejects_unrelated_chunks_for_para_17_and_para_6():
    """
    Phase B Final Checklist Item 10.2:
    Verify that the system requires actual Paragraph 17 / Paragraph 6 evidence before
    making claims about those provisions, and does NOT substitute unrelated chunks (e.g. Paragraph 9)
    as citations for Paragraph 17 or Paragraph 6 claims.
    """
    engine = FinRegRAGEngine(api_key="test_dummy_key")
    query = "What were the digital lending requirements in June 2025?"

    with open(SECTION_CHUNKS_FILE, "r", encoding="utf-8") as f:
        all_chunks = json.load(f)

    c9 = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2025" and c.get("clause_no") == "9"][0]
    c17 = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2025" and c.get("clause_no") == "17"][0]
    c6 = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2025" and c.get("clause_no") == "6"][0]

    # Test Case A: Only Paragraph 9 is provided (no Paragraph 17 or Paragraph 6 chunks)
    only_gen = [(c9, 0.90)]
    res_gen = engine.generate_answer(query, only_gen, force_refusal_threshold=False)
    ans_gen = res_gen["answer"]

    # Must describe general provisions and cite Clause 9
    assert "Clause: 9" in ans_gen
    # Must NOT claim Paragraph 17 came into force or cite Clause 9 for Paragraph 17!
    assert "Paragraph 17 came into force" not in ans_gen
    assert "making reporting on the CIMS portal mandatory" not in ans_gen
    assert "Paragraph 6 (multiple lenders) remained prospective" not in ans_gen

    # Test Case B: Both Paragraph 9 and Paragraph 17 are provided
    gen_and_p17 = [(c9, 0.90), (c17, 0.85)]
    res_p17 = engine.generate_answer(query, gen_and_p17, force_refusal_threshold=False)
    ans_p17 = res_p17["answer"]

    # Period 2 must ground Paragraph 17 specifically with Clause: 17
    assert "Paragraph 17 came into force on June 15, 2025" in ans_p17
    assert "Clause: 17" in ans_p17
    # General provisions cite Clause: 9
    assert "Clause: 9" in ans_p17
    # Paragraph 6 chunk is still absent, so no Paragraph 6 claim should be asserted
    assert "Paragraph 6 (multiple lenders) remained prospective" not in ans_p17

    # Test Case C: Paragraph 9, Paragraph 17, and Paragraph 6 are provided
    all_three = [(c9, 0.90), (c17, 0.85), (c6, 0.80)]
    res_all = engine.generate_answer(query, all_three, force_refusal_threshold=False)
    ans_all = res_all["answer"]

    # All three provisions are grounded in their respective clauses
    assert "Clause: 17" in ans_all
    assert "Clause: 9" in ans_all
    assert "Clause: 6" in ans_all
    assert "Paragraph 6" in ans_all


def test_unrelated_document_clause_17_rejected_for_transition_event():
    """
    Phase B2.2.1: Verify that an unrelated document with clause_no == '17'
    is NOT admitted for the June 15, 2025 digital lending transition event.
    """
    version_mgr = RegulatoryVersionManager()
    query = "What changed on June 15, 2025?"

    # Legitimate Paragraph 17 of RBI_DL_2025
    valid_p17 = {
        "chunk_id": "c_valid_17",
        "doc_id": "RBI_DL_2025",
        "clause_no": "17",
        "effective_date": "2025-06-15",
        "is_active": True
    }
    assert version_mgr.is_chunk_applicable(valid_p17, query) is True

    # Unrelated document with clause_no == "17" (e.g. from PPI Master Directions)
    unrelated_p17 = {
        "chunk_id": "c_unrelated_17",
        "doc_id": "RBI_PPI_MD_2021",
        "clause_no": "17",
        "effective_date": "2021-08-27",
        "is_active": True
    }
    assert version_mgr.is_chunk_applicable(unrelated_p17, query) is False, "Unrelated document Paragraph 17 must be rejected!"


def test_missing_evidence_in_transition_period_does_not_generate_unsupported_claim():
    """
    Phase B2.2.1: Verify that if evidence is missing for a transition period,
    the pipeline does not generate an unsupported claim, but reports insufficient evidence.
    """
    engine = FinRegRAGEngine(api_key="test_dummy_key")
    query = "What were the digital lending requirements in June 2025?"

    # Create dummy retrieved chunks that only have Period 2 evidence (Para 17)
    with open(SECTION_CHUNKS_FILE, "r", encoding="utf-8") as f:
        all_chunks = json.load(f)
    p17_chunk = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2025" and c.get("clause_no") == "17"][0]

    # Only Period 2 chunk provided (no Period 1 chunk)
    only_p2_chunks = [(p17_chunk, 0.85)]
    res = engine.generate_answer(query, only_p2_chunks, force_refusal_threshold=False)
    ans = res["answer"]

    # Period 1 should state insufficient evidence
    assert ("June 1–14" in ans or "Period 1" in ans) and "Insufficient evidence" in ans
    # Period 2 should cite Paragraph 17
    assert ("June 15–30" in ans or "Period 2" in ans) and "Paragraph 17" in ans

# ---------------------------------------------------------------------------
# 6. Final Audit: Document-Identity Verification & 2023 Regime Consumption
# ---------------------------------------------------------------------------

def test_paragraph_evidence_document_identity_audit_seven_cases():
    """
    Phase B Final Audit Cases 1-7:
    Strictly verifies that Paragraph 17 and Paragraph 6 claims require authentic
    evidence from RBI_DL_2025, rejects unrelated documents, rejects substitution
    of general paragraphs, and produces explicit evidence limitations when missing.
    """
    engine = FinRegRAGEngine(api_key="test_dummy_key")
    query = "What were the digital lending requirements in June 2025?"

    with open(SECTION_CHUNKS_FILE, "r", encoding="utf-8") as f:
        all_chunks = json.load(f)

    c9 = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2025" and c.get("clause_no") == "9"][0]
    c17_dl2025 = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2025" and c.get("clause_no") == "17"][0]
    c6_dl2025 = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2025" and c.get("clause_no") == "6"][0]

    # Dummy unrelated documents containing Clause 17 and Clause 6
    unrelated_c17 = {
        "chunk_id": "c_unrelated_17",
        "doc_id": "RBI_PPI_MD_2021",
        "doc_title": "Master Directions on Prepaid Payment Instruments",
        "clause_no": "17",
        "publish_date": "2021-08-27",
        "effective_date": "2021-08-27",
        "page_start": 25,
        "text": "17. Cross-border outward transactions shall not be permitted under these directions.",
        "is_active": True
    }
    unrelated_c6 = {
        "chunk_id": "c_unrelated_6",
        "doc_id": "RBI_PA_PG_2020",
        "doc_title": "Guidelines on Regulation of Payment Aggregators",
        "clause_no": "6",
        "publish_date": "2020-03-17",
        "effective_date": "2020-03-17",
        "page_start": 8,
        "text": "6. Escrow account operation and settlement of payment aggregator funds.",
        "is_active": True
    }

    # Case 1: Unrelated RBI document containing Clause 17 must NOT support Paragraph 17 claim
    res_case1 = engine.generate_answer(query, [(c9, 0.90), (unrelated_c17, 0.85)], force_refusal_threshold=False)
    ans_case1 = res_case1["answer"]
    assert "Paragraph 17 came into force" not in ans_case1, "Unrelated Clause 17 must not trigger Paragraph 17 claim!"
    assert "RBI_PPI_MD_2021" not in ans_case1
    assert "Prepaid Payment Instruments" not in ans_case1

    # Case 2: Unrelated RBI document containing Clause 6 must NOT support Paragraph 6 claim
    res_case2 = engine.generate_answer(query, [(c9, 0.90), (unrelated_c6, 0.85)], force_refusal_threshold=False)
    ans_case2 = res_case2["answer"]
    assert "Paragraph 6 (multiple lenders) remained prospective" not in ans_case2, "Unrelated Clause 6 must not trigger Paragraph 6 claim!"
    assert "Payment Aggregators" not in ans_case2

    # Case 3: General 2025 Directions paragraph must NOT substitute for Paragraph 17 evidence
    res_case3 = engine.generate_answer(query, [(c9, 0.90)], force_refusal_threshold=False)
    ans_case3 = res_case3["answer"]
    assert "Clause: 9" in ans_case3
    assert "Paragraph 17" not in ans_case3, "General Clause 9 must not substitute for Paragraph 17!"
    assert "CIMS portal" not in ans_case3

    # Case 4: General 2025 Directions paragraph must NOT substitute for Paragraph 6 evidence
    assert "Paragraph 6" not in ans_case3, "General Clause 9 must not substitute for Paragraph 6!"

    # Case 5: Actual Paragraph 17 evidence from RBI_DL_2025 supports the relevant claim
    res_case5 = engine.generate_answer(query, [(c9, 0.90), (c17_dl2025, 0.85)], force_refusal_threshold=False)
    ans_case5 = res_case5["answer"]
    assert "Paragraph 17 came into force on June 15, 2025" in ans_case5
    assert "Clause: 17" in ans_case5
    assert "Reserve Bank of India (Digital Lending) Directions, 2025" in ans_case5

    # Case 6: Actual Paragraph 6 evidence from RBI_DL_2025 supports the relevant claim
    res_case6 = engine.generate_answer(query, [(c9, 0.90), (c6_dl2025, 0.85)], force_refusal_threshold=False)
    ans_case6 = res_case6["answer"]
    assert "Paragraph 6 (multiple lenders) remained prospective until November 1, 2025" in ans_case6
    assert "Clause: 6" in ans_case6

    # Case 7: Missing paragraph-specific evidence produces explicit limitation
    q_specific_cims = "What were the digital lending CIMS portal reporting requirements in June 2025?"
    res_case7 = engine.generate_answer(q_specific_cims, [(c9, 0.90)], force_refusal_threshold=False)
    ans_case7 = res_case7["answer"]
    assert "Insufficient evidence in retrieved documents regarding Paragraph 17" in ans_case7


def test_2023_regime_applicable_docs_actively_consumed(section_bm25_retriever):
    """
    Phase B Final Audit Item 4:
    Confirms that `applicable_docs` is actively consumed by the filtering and retrieval implementation.
    Verifies that:
    - Applicable 2022 provisions are retrievable.
    - Applicable 2023 DLG provisions are retrievable.
    - Superseded 2022 Clause 15 is excluded.
    - 2025 Directions are excluded for dates before May 8, 2025.
    """
    version_mgr = RegulatoryVersionManager()
    query = "What was the DLG cap under the 2023 circular?"
    anchor = version_mgr.extract_temporal_anchor(query)

    # 1. Verify applicable_docs is present on the anchor
    assert "applicable_docs" in anchor
    assert set(anchor["applicable_docs"]) == {"RBI_DLG_2023", "RBI_DL_2022"}

    with open(SECTION_CHUNKS_FILE, "r", encoding="utf-8") as f:
        all_chunks = json.load(f)

    c_2022_para3 = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2022" and c.get("clause_no") == "3"][0]
    c_2022_para15 = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2022" and c.get("clause_no") == "15"][0]
    c_2023_dlg = [c for c in all_chunks if c.get("doc_id") == "RBI_DLG_2023"][0]
    c_2025_para23 = [c for c in all_chunks if c.get("doc_id") == "RBI_DL_2025" and c.get("clause_no") == "23"][0]

    # 2. Direct filter applicability
    assert version_mgr.is_chunk_applicable(c_2022_para3, query) is True, "2022 surviving clause 3 must be applicable!"
    assert version_mgr.is_chunk_applicable(c_2023_dlg, query) is True, "2023 DLG chunk must be applicable!"
    assert version_mgr.is_chunk_applicable(c_2022_para15, query) is False, "Superseded clause 15 must be excluded!"
    assert version_mgr.is_chunk_applicable(c_2025_para23, query) is False, "2025 Directions must be excluded prior to May 8, 2025!"

    # 3. filter_chunks actively filters candidate pool
    candidates = [
        (c_2022_para3, 0.9),
        (c_2023_dlg, 0.85),
        (c_2022_para15, 0.8),
        (c_2025_para23, 0.75)
    ]
    filtered = version_mgr.filter_chunks(candidates, query=query)
    filtered_cids = [c["chunk_id"] for c, _ in filtered]
    assert c_2022_para3["chunk_id"] in filtered_cids
    assert c_2023_dlg["chunk_id"] in filtered_cids
    assert c_2022_para15["chunk_id"] not in filtered_cids
    assert c_2025_para23["chunk_id"] not in filtered_cids

    # 4. End-to-end BM25 retrieval consumes applicable_docs
    q_disb = "Under the 2023 circular regime, where must digital lending loan disbursements be executed?"
    res_disb = section_bm25_retriever.search(q_disb, top_k=5)
    assert len(res_disb) > 0
    assert res_disb[0][0].get("doc_id") == "RBI_DL_2022"
    assert res_disb[0][0].get("clause_no") == "3"
    for c, _ in res_disb:
        assert c.get("doc_id") in ("RBI_DL_2022", "RBI_DLG_2023")
        assert not (c.get("doc_id") == "RBI_DL_2022" and c.get("clause_no") == "15")
        assert c.get("doc_id") != "RBI_DL_2025"



