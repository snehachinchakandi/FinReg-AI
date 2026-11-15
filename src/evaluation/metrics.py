"""
Evaluation Metrics calculation for FinReg AI.
Implements Hit Rate@K, Mean Reciprocal Rank (MRR), Citation Accuracy,
Correct Refusal Rate (CRR), False Refusal Rate (FRR), Answerable Coverage (AQC),
and Semantic Correctness.
"""

import re
from typing import List, Dict, Any, Optional

def compute_passage_overlap(chunk_text: str, golden_passage: str) -> float:
    """Computes normalized word unigram overlap between retrieved chunk and golden text."""
    c_words = set(re.findall(r"\b\w{3,}\b", chunk_text.lower()))
    g_words = set(re.findall(r"\b\w{3,}\b", golden_passage.lower()))
    if not g_words:
        return 0.0
    return len(c_words.intersection(g_words)) / len(g_words)

def compute_hit_at_k(
    retrieved_chunks: List[Dict[str, Any]],
    golden_passages: List[str],
    k: int = 5,
    threshold: float = 0.4
) -> float:
    """
    Returns 1.0 if any chunk in the top-k retrieved list satisfies the golden passage overlap threshold, else 0.0.
    """
    if not golden_passages:
        return 0.0

    for chunk in retrieved_chunks[:k]:
        chunk_text = chunk.get("text", "")
        for gp in golden_passages:
            if compute_passage_overlap(chunk_text, gp) >= threshold:
                return 1.0
    return 0.0

def compute_reciprocal_rank(
    retrieved_chunks: List[Dict[str, Any]],
    golden_passages: List[str],
    threshold: float = 0.4
) -> float:
    """
    Computes reciprocal rank: 1 / rank of first relevant chunk.
    Returns 0.0 if not found in retrieved chunks.
    """
    if not golden_passages:
        return 0.0

    for rank, chunk in enumerate(retrieved_chunks, 1):
        chunk_text = chunk.get("text", "")
        for gp in golden_passages:
            if compute_passage_overlap(chunk_text, gp) >= threshold:
                return 1.0 / rank
    return 0.0

TOTAL_NEGATIVE_QUESTIONS = 15
TOTAL_ANSWERABLE_QUESTIONS = 35

def is_genuine_policy_refusal(record: Dict[str, Any]) -> bool:
    """
    Determines if a record represents a genuine policy refusal.
    Execution errors (API failures, exceptions) are strictly excluded.
    """
    if record.get("is_error") is True or record.get("execution_mode") == "api_error":
        return False
    ans = (record.get("generated_answer") or record.get("answer") or "").strip()
    if ans.startswith("ERROR:"):
        return False
    if record.get("is_policy_refusal") is not None:
        return bool(record.get("is_policy_refusal"))
    return bool(record.get("is_refusal", False))

def is_successful_answer(record: Dict[str, Any]) -> bool:
    """
    Determines if a record represents a successfully generated compliance answer.
    Policy refusals and execution errors are strictly excluded.
    """
    if record.get("is_error") is True or record.get("execution_mode") == "api_error":
        return False
    if is_genuine_policy_refusal(record):
        return False
    ans = (record.get("generated_answer") or record.get("answer") or "").strip()
    if ans.startswith("ERROR:") or ans.startswith("REFUSAL:"):
        return False
    if ans == "" and ("generated_answer" in record or "answer" in record):
        return False
    return True

def compute_citation_accuracy(
    answer: str,
    retrieved_chunks: List[Dict[str, Any]],
    is_refusal: bool = False,
    execution_mode: str = "live_gemini"
) -> Optional[float]:
    """
    Checks if citations present in the answer correspond to actual chunks retrieved.
    Returns 1.0 for valid policy refusals.
    Returns 0.0 for API execution errors or factual answers without citations.
    """
    if execution_mode == "api_error" or answer.strip().startswith("ERROR:"):
        return 0.0

    if is_refusal or answer.strip().startswith("REFUSAL:"):
        return 1.0

    # Pattern: [Doc: <title>, Date: <date>, Clause: <clause>, Page: <page>]
    pattern = r"\[Doc:\s*([^,]+),\s*Date:\s*([^,]+),\s*Clause:\s*([^,]+),\s*Page:\s*([^\]]+)\]"
    found_citations = re.findall(pattern, answer)

    if not found_citations:
        # Factual answer without citations is non-compliant
        return 0.0

    valid_count = 0
    retrieved_titles = {c.get("doc_title", "").lower() for c in retrieved_chunks}

    for cite in found_citations:
        cite_title = cite[0].strip().lower()
        if any(cite_title in rt or rt in cite_title for rt in retrieved_titles):
            valid_count += 1

    return valid_count / len(found_citations)

def compute_semantic_correctness(
    generated_answer: str,
    golden_answer: str,
    is_refusal: bool,
    category: str,
    execution_mode: str = "live_gemini"
) -> float:
    """
    Evaluates semantic correctness score (0.0 to 1.0).
    - Execution errors (API errors): 0.0 regardless of category.
    - Unanswerable / Adversarial: 1.0 if genuine policy refusal, 0.0 if hallucinated answer or error.
    - Answerable: 0.0 if refused or execution failure; otherwise unigram overlap with golden answer.
    """
    if execution_mode == "api_error" or generated_answer.strip().startswith("ERROR:"):
        return 0.0

    if category in ("unanswerable", "adversarial"):
        return 1.0 if is_refusal else 0.0

    if is_refusal:
        return 0.0  # False refusal on answerable query

    gen_words = set(re.findall(r"\b\w{3,}\b", generated_answer.lower()))
    gold_words = set(re.findall(r"\b\w{3,}\b", golden_answer.lower()))
    if not gold_words:
        return 0.0

    overlap = len(gen_words.intersection(gold_words)) / len(gold_words)
    return min(1.0, overlap * 1.3)

def compute_correct_refusal_rate(
    records: List[Dict[str, Any]],
    total_negative: int = TOTAL_NEGATIVE_QUESTIONS
) -> float:
    """
    Correct Refusal Rate (CRR):
    Genuine policy refusals on negative queries divided strictly by fixed denominator (15).
    API execution errors are never credited as correct refusals.
    """
    if total_negative <= 0:
        return 0.0
    negative_records = [
        r for r in records 
        if (r.get("category") or r.get("question_type")) in ("unanswerable", "adversarial")
    ]
    genuine_refusals = sum(1 for r in negative_records if is_genuine_policy_refusal(r))
    return genuine_refusals / total_negative

def compute_false_refusal_rate(
    records: List[Dict[str, Any]],
    total_answerable: int = TOTAL_ANSWERABLE_QUESTIONS
) -> float:
    """
    False Refusal Rate (FRR):
    Genuine policy refusals on answerable queries divided strictly by fixed denominator (35).
    API execution errors are never counted as false policy refusals.
    """
    if total_answerable <= 0:
        return 0.0
    answerable_records = [
        r for r in records 
        if (r.get("category") or r.get("question_type")) == "answerable"
    ]
    genuine_false_refusals = sum(1 for r in answerable_records if is_genuine_policy_refusal(r))
    return genuine_false_refusals / total_answerable

def compute_answerable_coverage(
    records: List[Dict[str, Any]],
    total_answerable: int = TOTAL_ANSWERABLE_QUESTIONS
) -> float:
    """
    Answerable Question Coverage (AQC):
    Successfully answered answerable queries divided strictly by fixed denominator (35).
    API execution failures and policy refusals both reduce coverage.
    AQC is NOT calculated as 1 - FRR.
    """
    if total_answerable <= 0:
        return 0.0
    answerable_records = [
        r for r in records 
        if (r.get("category") or r.get("question_type")) == "answerable"
    ]
    successful_answers = sum(1 for r in answerable_records if is_successful_answer(r))
    return successful_answers / total_answerable
