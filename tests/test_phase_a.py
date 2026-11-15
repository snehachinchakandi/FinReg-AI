"""
Unit tests for Phase A: Critical Retrieval and Evaluation Fixes.
Verifies:
1. Retrieval-mode-aware evidence gates (Dense vs Hybrid RRF).
2. Proper behavior on realistic RRF scores (e.g., 0.0328) without false refusal.
3. Out-of-scope / unsupported question refusal.
4. Correct formulation of CRR (over 15 negative), FRR (over 35 answerable), and AQC (1 - FRR).
5. Generation telemetry and execution_mode flagging (live_gemini vs fallback_simulated vs gate_refusal).
"""

import pytest
from src.generation.rag_engine import FinRegRAGEngine
from src.evaluation.metrics import (
    compute_correct_refusal_rate,
    compute_false_refusal_rate,
    compute_answerable_coverage,
    is_genuine_policy_refusal,
    is_successful_answer,
    compute_semantic_correctness,
    compute_citation_accuracy
)

# ---------------------------------------------------------------------------
# 1. Mode-Aware Evidence Gate Tests
# ---------------------------------------------------------------------------

def test_dense_evidence_gate_pass():
    """Dense retrieval passes when cosine similarity >= 0.40."""
    engine = FinRegRAGEngine(api_key="")
    chunk = {
        "chunk_id": "c_dense_good",
        "text": "Borrowers must have access to a Key Fact Statement.",
        "doc_title": "Guidelines on Digital Lending",
        "publish_date": "2022-09-02",
        "page_start": 4
    }
    retrieved = [(chunk, 0.65)]  # Score >= 0.40
    is_valid, reason = engine.validate_evidence(retrieved)
    assert is_valid is True
    assert "Dense evidence passed" in reason


def test_dense_evidence_gate_refusal():
    """Dense retrieval fails when cosine similarity < 0.40."""
    engine = FinRegRAGEngine(api_key="")
    chunk = {
        "chunk_id": "c_dense_weak",
        "text": "Random irrelevant document text about unrelated topics.",
        "doc_title": "Guidelines on Digital Lending",
        "publish_date": "2022-09-02",
        "page_start": 4
    }
    retrieved = [(chunk, 0.28)]  # Score < 0.40
    is_valid, reason = engine.validate_evidence(retrieved)
    assert is_valid is False
    assert "below threshold" in reason


def test_hybrid_evidence_gate_realistic_rrf_pass():
    """
    Hybrid retrieval with a realistic RRF score (~0.0328) must NOT be refused
    if underlying dense and BM25 scores indicate genuine relevance.
    """
    engine = FinRegRAGEngine(api_key="")
    chunk = {
        "chunk_id": "c_hybrid_good",
        "text": "Default Loss Guarantee arrangements must not exceed 5 percent of the loan portfolio.",
        "doc_title": "Default Loss Guarantee (DLG) in Digital Lending",
        "publish_date": "2023-06-08",
        "page_start": 2,
        "_fusion_meta": {
            "rrf_score": 0.0328,
            "dense_score": 0.74,
            "bm25_score": 5.12,
            "dense_rank": 1,
            "bm25_rank": 1
        }
    }
    # Fused top score is 0.0328 (far below 0.1, but well above min fusion 0.010)
    retrieved = [(chunk, 0.0328)]
    is_valid, reason = engine.validate_evidence(retrieved)
    assert is_valid is True
    assert "Hybrid evidence passed validation" in reason


def test_hybrid_evidence_gate_weak_scores_refusal():
    """
    Hybrid retrieval must refuse if both underlying dense (<0.40) and BM25 (<1.5)
    scores are insufficient, even if an RRF rank exists.
    """
    engine = FinRegRAGEngine(api_key="")
    chunk = {
        "chunk_id": "c_hybrid_weak",
        "text": "Vague tangential remark.",
        "doc_title": "Doc",
        "publish_date": "2023-01-01",
        "page_start": 1,
        "_fusion_meta": {
            "rrf_score": 0.0180,
            "dense_score": 0.22,  # < 0.40
            "bm25_score": 0.85,   # < 1.5
            "dense_rank": 8,
            "bm25_rank": 9
        }
    }
    retrieved = [(chunk, 0.0180)]
    is_valid, reason = engine.validate_evidence(retrieved)
    assert is_valid is False
    assert "Hybrid evidence insufficient" in reason


def test_hybrid_evidence_gate_partial_modality_pass():
    """
    Hybrid retrieval passes if either dense OR BM25 demonstrates strong evidence.
    Case: High dense similarity (0.68) but low BM25 (e.g. paraphrased query).
    """
    engine = FinRegRAGEngine(api_key="")
    chunk = {
        "chunk_id": "c_hybrid_dense_strong",
        "text": "Lending service providers shall not store biometric data.",
        "doc_title": "Guidelines on Digital Lending",
        "publish_date": "2022-09-02",
        "page_start": 5,
        "_fusion_meta": {
            "rrf_score": 0.0210,
            "dense_score": 0.68,  # Strong dense
            "bm25_score": 0.90,   # Low BM25
            "dense_rank": 1,
            "bm25_rank": 12
        }
    }
    retrieved = [(chunk, 0.0210)]
    is_valid, reason = engine.validate_evidence(retrieved)
    assert is_valid is True


# ---------------------------------------------------------------------------
# 2. Unsupported Question Refusal End-to-End
# ---------------------------------------------------------------------------

def test_unsupported_question_refusal_end_to_end():
    """Verify that an unsupported question produces is_refusal=True and gate_refusal mode."""
    engine = FinRegRAGEngine(api_key="")
    chunk = {
        "chunk_id": "c_weak",
        "text": "Irrelevant text.",
        "doc_title": "Doc",
        "publish_date": "2022-01-01",
        "page_start": 1
    }
    # Dense score 0.15 is below DENSE_REFUSAL_THRESHOLD (0.40)
    result = engine.generate_answer(
        question="What is the minimum capital requirement for an insurance broker?",
        retrieved_chunks=[(chunk, 0.15)]
    )
    assert result["is_refusal"] is True
    assert "REFUSAL:" in result["answer"]
    assert result["execution_mode"] == "gate_refusal"
    assert result["generation_latency_ms"] == 0.0
    assert result["estimated_cost_usd"] == 0.0


# ---------------------------------------------------------------------------
# 3. Separated Refusal Metrics Unit Tests
# ---------------------------------------------------------------------------

def test_refusal_metrics_mathematical_separation():
    """
    Verify that CRR, FRR, and AQC are computed strictly on their respective subsets:
    - CRR denominator is strictly 15 (10 unanswerable + 5 adversarial).
    - FRR denominator is strictly 35 (answerables).
    - AQC = 1.0 - FRR.
    """
    synthetic_records = []

    # 35 Answerable queries: 33 answered, 2 false refusals
    for i in range(33):
        synthetic_records.append({
            "category": "answerable",
            "is_refusal": False,
            "question_id": f"A_{i}"
        })
    for i in range(2):
        synthetic_records.append({
            "category": "answerable",
            "is_refusal": True,
            "question_id": f"A_refused_{i}"
        })

    # 10 Unanswerable queries: 9 correctly refused, 1 hallucinated/answered
    for i in range(9):
        synthetic_records.append({
            "category": "unanswerable",
            "is_refusal": True,
            "question_id": f"U_{i}"
        })
    synthetic_records.append({
        "category": "unanswerable",
        "is_refusal": False,
        "question_id": "U_hallucinated"
    })

    # 5 Adversarial queries: all 5 correctly refused
    for i in range(5):
        synthetic_records.append({
            "category": "adversarial",
            "is_refusal": True,
            "question_id": f"ADV_{i}"
        })

    assert len(synthetic_records) == 50

    crr = compute_correct_refusal_rate(synthetic_records)
    frr = compute_false_refusal_rate(synthetic_records)
    aqc = compute_answerable_coverage(synthetic_records)

    # Negative total = 10 + 5 = 15; correctly refused = 9 + 5 = 14
    expected_crr = 14 / 15
    assert pytest.approx(crr, 1e-4) == expected_crr

    # Answerable total = 35; false refusals = 2
    expected_frr = 2 / 35
    assert pytest.approx(frr, 1e-4) == expected_frr

    # Answerable coverage = 33 / 35 = 1 - FRR
    expected_aqc = 33 / 35
    assert pytest.approx(aqc, 1e-4) == expected_aqc


def test_previous_bug_scenario_refusal_metrics():
    """
    Test the previous bug scenario where ALL 50 queries were refused:
    CRR should be 1.0 (15/15), FRR should be 1.0 (35/35), and AQC should be 0.0.
    In the previous implementation, averaging across all 50 produced 0.30, obscuring the total failure.
    """
    synthetic_records = []
    for i in range(35):
        synthetic_records.append({"category": "answerable", "is_refusal": True})
    for i in range(10):
        synthetic_records.append({"category": "unanswerable", "is_refusal": True})
    for i in range(5):
        synthetic_records.append({"category": "adversarial", "is_refusal": True})

    crr = compute_correct_refusal_rate(synthetic_records)
    frr = compute_false_refusal_rate(synthetic_records)
    aqc = compute_answerable_coverage(synthetic_records)

    assert crr == 1.0       # Correctly caught all negatives
    assert frr == 1.0       # Catastrophic: refused every single answerable question!
    assert aqc == 0.0       # Zero coverage


# ---------------------------------------------------------------------------
# 4. Telemetry and Execution Mode Tagging Tests
# ---------------------------------------------------------------------------

def test_telemetry_keys_and_fallback_flag():
    """
    Verify that FinRegRAGEngine without client returns execution_mode='fallback_simulated'
    and is_fallback=True with zero cost.
    """
    engine = FinRegRAGEngine(api_key="")
    chunk = {
        "chunk_id": "c_valid",
        "text": "Lending service providers must be registered with the regulated entity.",
        "doc_title": "Guidelines on Digital Lending",
        "publish_date": "2022-09-02",
        "clause_no": "Para 4",
        "page_start": 3
    }
    retrieved = [(chunk, 0.70)]
    result = engine.generate_answer(
        question="Who must register the lending service providers?",
        retrieved_chunks=retrieved
    )

    assert "generation_latency_ms" in result
    assert "input_tokens" in result
    assert "output_tokens" in result
    assert "estimated_cost_usd" in result
    assert "execution_mode" in result
    assert "is_fallback" in result

    assert result["execution_mode"] == "fallback_simulated"
    assert result["is_fallback"] is True
    assert result["estimated_cost_usd"] == 0.0
    assert result["generation_latency_ms"] >= 0.0


# ---------------------------------------------------------------------------
# 5. Policy Refusals vs Execution Errors Disambiguation Tests
# ---------------------------------------------------------------------------

def test_api_error_on_unanswerable_question_does_not_count_in_crr():
    """
    Case 1: An API error on an unanswerable query must NOT be credited as a correct refusal.
    CRR should remain 0.0, and semantic correctness should be 0.0.
    """
    record = {
        "category": "unanswerable",
        "question_id": "U_err",
        "execution_mode": "api_error",
        "is_error": True,
        "is_policy_refusal": False,
        "generated_answer": "ERROR: Execution failure calling generation model (Network timeout)."
    }
    assert is_genuine_policy_refusal(record) is False
    crr = compute_correct_refusal_rate([record])
    assert crr == 0.0
    correctness = compute_semantic_correctness(
        record["generated_answer"], "Golden", is_refusal=False, category="unanswerable", execution_mode="api_error"
    )
    assert correctness == 0.0


def test_api_error_on_adversarial_question_does_not_count_in_crr():
    """
    Case 2: An API error on an adversarial query must NOT be credited as a correct refusal.
    CRR should remain 0.0, and citation accuracy should be 0.0.
    """
    record = {
        "category": "adversarial",
        "question_id": "ADV_err",
        "execution_mode": "api_error",
        "is_error": True,
        "is_policy_refusal": False,
        "generated_answer": "ERROR: Execution failure calling generation model (Rate limit exceeded)."
    }
    assert is_genuine_policy_refusal(record) is False
    crr = compute_correct_refusal_rate([record])
    assert crr == 0.0
    cite_acc = compute_citation_accuracy(
        record["generated_answer"], [], is_refusal=False, execution_mode="api_error"
    )
    assert cite_acc == 0.0


def test_api_error_on_answerable_question_reduces_aqc_without_affecting_frr():
    """
    Case 3: An API error on an answerable query is an execution failure.
    - It must NOT increment false policy refusal rate (FRR = 0.0).
    - It must NOT count as a successful answer, strictly reducing coverage (AQC = 0.0).
    """
    record = {
        "category": "answerable",
        "question_id": "A_err",
        "execution_mode": "api_error",
        "is_error": True,
        "is_policy_refusal": False,
        "generated_answer": "ERROR: Execution failure calling generation model (503 Service Unavailable)."
    }
    assert is_genuine_policy_refusal(record) is False
    assert is_successful_answer(record) is False

    frr = compute_false_refusal_rate([record])
    aqc = compute_answerable_coverage([record])

    assert frr == 0.0  # Not a policy refusal!
    assert aqc == 0.0  # Not covered!


def test_genuine_refusal_on_unanswerable_question():
    """
    Case 4: A genuine policy refusal on an unanswerable query must be credited in CRR.
    """
    record = {
        "category": "unanswerable",
        "question_id": "U_valid",
        "execution_mode": "gate_refusal",
        "is_error": False,
        "is_policy_refusal": True,
        "generated_answer": "REFUSAL: The provided regulatory documents do not contain sufficient evidence."
    }
    assert is_genuine_policy_refusal(record) is True
    # 1 genuine refusal out of 15 total negative questions
    crr = compute_correct_refusal_rate([record])
    assert pytest.approx(crr, 1e-4) == 1 / 15

    correctness = compute_semantic_correctness(
        record["generated_answer"], "Golden", is_refusal=True, category="unanswerable", execution_mode="gate_refusal"
    )
    assert correctness == 1.0


def test_genuine_refusal_on_answerable_question():
    """
    Case 5: A genuine policy refusal on an answerable query is a false refusal.
    - Increments FRR (1 / 35).
    - Does NOT count towards AQC (0 / 35).
    """
    record = {
        "category": "answerable",
        "question_id": "A_false_refusal",
        "execution_mode": "gate_refusal",
        "is_error": False,
        "is_policy_refusal": True,
        "generated_answer": "REFUSAL: The provided regulatory documents do not contain sufficient evidence."
    }
    assert is_genuine_policy_refusal(record) is True
    assert is_successful_answer(record) is False

    frr = compute_false_refusal_rate([record])
    aqc = compute_answerable_coverage([record])

    assert pytest.approx(frr, 1e-4) == 1 / 35
    assert aqc == 0.0


def test_successful_answer_on_answerable_question():
    """
    Case 6: A successful answer on an answerable question:
    - Increments AQC (1 / 35).
    - FRR is 0.0.
    """
    record = {
        "category": "answerable",
        "question_id": "A_success",
        "execution_mode": "live_gemini",
        "is_error": False,
        "is_policy_refusal": False,
        "generated_answer": "According to RBI DL Guidelines 2022, loan disbursements must be made directly. [Doc: Guidelines on Digital Lending, Date: 2022-09-02, Clause: 3, Page: 3]"
    }
    assert is_genuine_policy_refusal(record) is False
    assert is_successful_answer(record) is True

    frr = compute_false_refusal_rate([record])
    aqc = compute_answerable_coverage([record])

    assert frr == 0.0
    assert pytest.approx(aqc, 1e-4) == 1 / 35


def test_mixed_batch_with_api_errors_policy_refusals_and_answers():
    """
    Verifies that in a complete mixed batch of 50 queries with API errors:
    - CRR only counts genuine policy refusals on negatives (ignores API errors).
    - FRR only counts genuine policy refusals on answerables (ignores API errors).
    - AQC strictly counts successful answers and is NOT simply 1 - FRR.
    """
    records = []

    # 35 Answerable queries:
    # - 30 successfully answered
    # - 3 genuine false policy refusals
    # - 2 API errors
    for i in range(30):
        records.append({
            "category": "answerable",
            "is_error": False,
            "is_policy_refusal": False,
            "execution_mode": "live_gemini",
            "generated_answer": f"Compliance answer {i}. [Doc: Title, Date: 2022-01-01, Clause: 1, Page: 1]"
        })
    for i in range(3):
        records.append({
            "category": "answerable",
            "is_error": False,
            "is_policy_refusal": True,
            "execution_mode": "gate_refusal",
            "generated_answer": "REFUSAL: Insufficient evidence."
        })
    for i in range(2):
        records.append({
            "category": "answerable",
            "is_error": True,
            "is_policy_refusal": False,
            "execution_mode": "api_error",
            "generated_answer": "ERROR: Execution failure calling generation model (Timeout)."
        })

    # 10 Unanswerable queries:
    # - 8 genuine policy refusals
    # - 1 API error
    # - 1 hallucinated answer
    for i in range(8):
        records.append({
            "category": "unanswerable",
            "is_error": False,
            "is_policy_refusal": True,
            "execution_mode": "gate_refusal",
            "generated_answer": "REFUSAL: Insufficient evidence."
        })
    records.append({
        "category": "unanswerable",
        "is_error": True,
        "is_policy_refusal": False,
        "execution_mode": "api_error",
        "generated_answer": "ERROR: Network failure."
    })
    records.append({
        "category": "unanswerable",
        "is_error": False,
        "is_policy_refusal": False,
        "execution_mode": "live_gemini",
        "generated_answer": "Hallucinated compliance statement."
    })

    # 5 Adversarial queries:
    # - 4 genuine policy refusals
    # - 1 API error
    for i in range(4):
        records.append({
            "category": "adversarial",
            "is_error": False,
            "is_policy_refusal": True,
            "execution_mode": "gate_refusal",
            "generated_answer": "REFUSAL: Regulatory policy violation."
        })
    records.append({
        "category": "adversarial",
        "is_error": True,
        "is_policy_refusal": False,
        "execution_mode": "api_error",
        "generated_answer": "ERROR: API 500 error."
    })

    assert len(records) == 50

    crr = compute_correct_refusal_rate(records)
    frr = compute_false_refusal_rate(records)
    aqc = compute_answerable_coverage(records)

    # CRR: 8 (from unanswerable) + 4 (from adversarial) = 12 genuine refusals out of 15.
    # Note: 2 API errors on negative queries are NOT counted.
    assert pytest.approx(crr, 1e-4) == 12 / 15

    # FRR: 3 genuine false refusals out of 35.
    # Note: 2 API errors on answerable queries are NOT counted as policy refusals.
    assert pytest.approx(frr, 1e-4) == 3 / 35

    # AQC: 30 successfully answered out of 35.
    # Both policy refusals (3) and API errors (2) reduce coverage!
    # Notice: 1.0 - FRR would have been 1.0 - 3/35 = 32/35 (0.9143), which is FALSE!
    # The actual AQC is 30/35 = 0.8571!
    assert pytest.approx(aqc, 1e-4) == 30 / 35
    assert aqc != (1.0 - frr)
