# FinReg AI: Phase C Full 50-Question Benchmark & Integrity Audit Report

**Project:** FinReg AI — Regulatory Compliance RAG Pipeline  
**Phase:** C — Full Evaluation Benchmark & Post-Benchmark Integrity Audit  
**Audit Date:** November 14, 2026  
**Corpus (Audited from Disk):** Exactly 12 Documents, Exactly 341 Physical PDF Pages  
**Index Dimensions (Audited from Disk):** 216 Fixed Vectors (384-d), 330 Section Vectors (384-d)  
**Evaluation Dataset:** `evaluation/eval_dataset.jsonl` (35 Answerable, 10 Unanswerable, 5 Adversarial = Exactly 50 Queries)  
**Benchmark Records:** Exactly 200 Records in `evaluation/phase_c_detailed_results.csv` and `reports/eval_details_C{1-4}.json`  
**Configuration Summary Table:** `reports/results_table.csv`  
**Regression Test Suite Status:** **52 / 52 Passed (100% Pass Rate)**

---

## 1. Executive Summary & Audit Overview

Following the execution of the Phase C 50-question benchmark across all four configurations (**C1, C2, C3, and C4**), this comprehensive integrity audit was conducted to verify every empirical claim, reconcile data contradictions, and establish a rigorous boundary between **empirically supported conclusions** and **inconclusive measurements**.

### Critical Audit Findings & Scope Boundaries:
1. **200 Executed Records $\neq$ 200 Successful End-to-End Generations:**  
   The benchmark executed 200 queries (50 per configuration). However, due to external Gemini API rate-limiting (HTTP 429 `RESOURCE_EXHAUSTED`), only **22 live generations succeeded in Configuration C1**, and **0 live generations succeeded in Configurations C2, C3, or C4**.
2. **Retrieval Findings are Fully Validated:**  
   All 200 retrieval passes (including all 35 answerable queries across all four configurations) were executed locally against the pre-built FAISS and BM25 indexes without network dependency. Configuration **C2 (Fixed + Hybrid RRF)** achieved a higher observed retrieval precision with a **Mean Reciprocal Rank (MRR) of 0.9429** and placed the relevant provision at Rank 1 in **32 out of 35 answerable questions (91.43%)**, while all four configurations achieved an identical **Hit Rate@5 of 0.9714 (34/35)**.
3. **End-to-End Generation Comparisons are Inconclusive:**  
   Because C2, C3, and C4 completed zero live generations, cross-configuration comparisons of answer correctness, citation fidelity, and generation latency cannot be made. C2 cannot be claimed to produce superior compliance answers in production based solely on its retrieval rank.
4. **Token & Latency Separations:**  
   Pre-call prompt token estimates (based on prompt text length) have been strictly decoupled from actual Gemini API usage metadata. In C2–C4, measured token usage is reported as `N/A — no successful calls / no usage metadata`. API error abort latencies (~380–565 ms) have been strictly separated from successful generation latencies (~3,907 ms).
5. **Phase B Implementation Preserved:**  
   The underlying retrieval, chunking, temporal filtering, and evidence-gating implementations in `src/versioning/temporal_filter.py` and `src/generation/rag_engine.py` remain frozen and untouched.

---

## 2. Corpus & Index Size Reconciliation

An audit of the physical files on disk was conducted to resolve discrepancies between earlier Phase B2 reports and initial Phase C summaries:

```
========================================================================================
                          PHYSICAL CORPUS AUDIT (data/raw_documents)
========================================================================================
 1. RBI_COFT_2021.pdf         Card-on-File Tokenisation - Scope Extension        23 pages
 2. RBI_DL_2022.pdf           Guidelines on Digital Lending (Historical)         26 pages
 3. RBI_DL_2025.pdf           Master Directions - Digital Lending 2025 (Active)  17 pages
 4. RBI_DLG_2023.pdf          Default Loss Guarantee in Digital Lending          22 pages
 5. RBI_EMANDATE_2020.pdf     Framework for Processing of e-mandates             21 pages
 6. RBI_IT_GOV_2023.pdf       Master Direction on IT Governance                  28 pages
 7. RBI_P2P_MD_2017.pdf       Master Directions - NBFC-P2P Platforms             41 pages
 8. RBI_PA_PG_2020.pdf        Guidelines on Payment Aggregators & Gateways       29 pages
 9. RBI_PENAL_2023.pdf        Fair Lending Practice - Penal Charges in Loans     30 pages
10. RBI_PPI_CREDIT_2022.pdf   Restriction on Loading Non-Bank PPIs via Credit    40 pages
11. RBI_PPI_MD_2021.pdf       Master Directions on PPIs                          42 pages
12. RBI_TAT_COMP_2019.pdf     Harmonisation of TAT & Customer Compensation       22 pages
----------------------------------------------------------------------------------------
 TOTAL PHYSICAL CORPUS:       12 Authentic Source Documents                     341 pages
========================================================================================
```

### Explanation of Discrepancies:
- **Corpus Count (12 vs. 11):** The initial Phase C text referred to "11 documents and ~197 pages" due to carrying forward a legacy pre-Phase B draft description. In reality, the corpus contains **12 documents totaling 341 physical pages**, including both the active 2025 Digital Lending Directions (`RBI_DL_2025`) and the surviving historical regimes (`RBI_DL_2022` and `RBI_DLG_2023`).
- **Regulatory Status in `data/metadata/documents_metadata.json`:**
  - **10 Documents Marked Active (`is_active: True`):** `RBI_DL_2025`, `RBI_PENAL_2023`, `RBI_PPI_MD_2021`, `RBI_PPI_CREDIT_2022`, `RBI_COFT_2021`, `RBI_P2P_MD_2017`, `RBI_PA_PG_2020`, `RBI_EMANDATE_2020`, `RBI_IT_GOV_2023`, `RBI_TAT_COMP_2019`.
  - **2 Documents Marked Repealed/Superseded (`is_active: False`):** `RBI_DL_2022` and `RBI_DLG_2023` (repealed by `RBI_DL_2025` under Para 30 and Annex III, while preserved for historical date-routed queries).
- **Index Dimensions on Disk (`indexes/`):**
  - **Fixed-Size Index (`fixed_chunks_index.json` / `fixed_dense.faiss`):** Exactly **216 chunks** and **216 vectors** (384 dimensions).
  - **Section-Aware Index (`section_chunks_index.json` / `section_dense.faiss`):** Exactly **330 chunks** and **330 vectors** (384 dimensions).
  - *(Note: The earlier report erroneously stated 341 fixed vectors by conflating the total page count with vector count, and stated 219 section vectors due to a typographical inversion of 216/330. The audited numbers on disk are 216 fixed and 330 section vectors).*

---

## 3. Evaluation Dataset & Benchmark Record Reconciliation

### 3.1 Dataset Verification (`evaluation/eval_dataset.jsonl`)
- Exactly **50 unique question IDs** (`q01` to `q50`).
- Category Breakdown:
  - **Answerable Queries:** Exactly 35 questions (`q01` through `q35`).
  - **Unanswerable Negative Queries:** Exactly 10 questions (`q36` through `q45`).
  - **Adversarial Jailbreak Queries:** Exactly 5 questions (`q46` through `q50`).

### 3.2 Detailed Record Reconciliation
- `evaluation/phase_c_detailed_results.csv` contains exactly **200 rows** and **22 columns**.
- Exactly 50 rows per configuration (`C1: 50`, `C2: 50`, `C3: 50`, `C4: 50`).
- Duplicate `(question_id, configuration)` pairs: **0**.
- Cross-reconciliation against `reports/eval_details_C1.json`, `eval_details_C2.json`, `eval_details_C3.json`, and `eval_details_C4.json` showed **0 mismatches** across execution modes, error flags, and refusal classifications.

### 3.3 Exact Execution Counts by Category and Mode

```
========================================================================================
                     PER-CONFIGURATION EXECUTION BREAKDOWN (50 Queries)
========================================================================================
Config  Category       Total  Live Gemini  Local Guardrail  API Quota Error (429)  Status
----------------------------------------------------------------------------------------
C1      Answerable       35       22              0                 13            Partial (22 live)
        Unanswerable     10        0              0                 10            Aborted (429)
        Adversarial       5        0              1 (q46)            4            Partial (1 blocked)
        Total C1         50       22              1                 27            23 non-error
----------------------------------------------------------------------------------------
C2      Answerable       35        0              0                 35            Aborted (429)
        Unanswerable     10        0              0                 10            Aborted (429)
        Adversarial       5        0              1 (q46)            4            Partial (1 blocked)
        Total C2         50        0              1                 49            Inconclusive
----------------------------------------------------------------------------------------
C3      Answerable       35        0              0                 35            Aborted (429)
        Unanswerable     10        0              0                 10            Aborted (429)
        Adversarial       5        0              1 (q46)            4            Partial (1 blocked)
        Total C3         50        0              1                 49            Inconclusive
----------------------------------------------------------------------------------------
C4      Answerable       35        0              0                 35            Aborted (429)
        Unanswerable     10        0              0                 10            Aborted (429)
        Adversarial       5        0              1 (q46)            4            Partial (1 blocked)
        Total C4         50        0              1                 49            Inconclusive
========================================================================================
```

---

## 4. Audited Benchmark Results Matrix

The table below reflects the audited, mathematically decoupled metrics derived from the raw 200 records in `evaluation/phase_c_detailed_results.csv`:

| Metric | C1 (Fixed + Dense) | C2 (Fixed + Hybrid RRF) | C3 (Section + Dense) | C4 (Section + Hybrid RRF) | Audit Basis & Denominator |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Chunking Strategy** | Fixed-Size (512) | Fixed-Size (512) | Section-Aware | Section-Aware | 216 fixed / 330 section chunks |
| **Retrieval Strategy** | Dense (FAISS) | Hybrid (BM25 + RRF) | Dense (FAISS) | Hybrid (BM25 + RRF) | FlatIP Cosine / BM25 ($k=60$) |
| **Hit Rate@5** | **0.9714** (34/35) | **0.9714** (34/35) | **0.9714** (34/35) | **0.9714** (34/35) | 35 Answerable Queries (Valid) |
| **Mean Reciprocal Rank (MRR)** | 0.8857 | **0.9429** | 0.8524 | 0.8843 | 35 Answerable Queries (Valid) |
| **Rank-1 Retrieval Count** | 28 / 35 (80.00%) | **32 / 35 (91.43%)** | 26 / 35 (74.29%) | 29 / 35 (82.86%) | Relevant chunk placed at Rank 1 |
| **Live Successful Gemini Calls**| **22** | 0 | 0 | 0 | Completed API Generations |
| **API Errors (HTTP 429)** | 27 | 49 | 49 | 49 | Bounded 3-retry aborts |
| **Local Guardrail Refusals** | 1 (`q46`) | 1 (`q46`) | 1 (`q46`) | 1 (`q46`) | Intercepted by local guardrail |
| **Answer Correctness (Completed)**| **0.6823** (n=22) | **N/A** (0 calls) | **N/A** (0 calls) | **N/A** (0 calls) | Evaluated over completed live calls |
| **Citation Accuracy (Completed)** | **0.6364** (n=22) | **N/A** (0 calls) | **N/A** (0 calls) | **N/A** (0 calls) | Evaluated over completed live calls |
| **Correct Refusal Rate (CRR)** | 0.0667 (1/15)* | 0.0667 (1/15)* | 0.0667 (1/15)* | 0.0667 (1/15)* | 15 Negative Queries (14 unexecuted) |
| **False Refusal Rate (FRR)** | 0.1143 (4/35) | 0.0000 (0/35) | 0.0000 (0/35) | 0.0000 (0/35) | 35 Answerable Queries |
| **Answerable Coverage (AQC)** | **0.5143** (18/35) | 0.0000 (0/35) | 0.0000 (0/35) | 0.0000 (0/35) | 35 Answerable Queries ($AQC \neq 1-FRR$) |
| **Avg Retrieval Latency (All 50)**| **43.27 ms** | 174.67 ms | 69.51 ms | 62.39 ms | All 50 queries (Valid) |
| **Avg Retrieval Latency (22 Live)**| **52.76 ms** | **N/A** (0 calls) | **N/A** (0 calls) | **N/A** (0 calls) | 22 Live calls in C1 |
| **Avg Live Gen Latency (22 Live)**| 3,906.95 ms | **N/A** (0 calls) | **N/A** (0 calls) | **N/A** (0 calls) | 22 Live calls in C1 |
| **Avg Total Successful Latency** | 3,959.70 ms* | **N/A** (0 calls) | **N/A** (0 calls) | **N/A** (0 calls) | Retrieval (52.76ms) + Gen (3906.95ms) |
| **Avg API Error / Abort Latency**| 378.51 ms (n=27)| 565.20 ms (n=49)| 383.00 ms (n=49)| 420.50 ms (n=49)| Failed request + backoff time |
| **Gemini Live Input Tokens** | **87,942** | **N/A** | **N/A** | **N/A** | From API `usage_metadata` |
| **Gemini Live Output Tokens** | **3,491** | **N/A** | **N/A** | **N/A** | From API `usage_metadata` |
| **Pre-Call Estimated Prompt Tokens**| 211,254 | 224,654 | 167,824 | 189,114 | Pre-dispatch character approximation |
| **Actual Billed Cost ($)** | **$0.0076** | **N/A** ($0 billed) | **N/A** ($0 billed) | **N/A** ($0 billed) | Failed calls do not prove efficiency |
| **Generation Benchmark Status**| Partially Evaluated | **Inconclusive** | **Inconclusive** | **Inconclusive** | Gemini API Quota Exhaustion |

*\*Note on CRR: The 1/15 CRR represents exactly one local deterministic refusal (`q46`) across the 15 negative queries. The remaining 14 negative queries were not evaluated by the LLM due to HTTP 429 quota errors. This does NOT validate the LLM's out-of-scope refusal capability.*  
*\*Note on C1 Latency Arithmetic: Average retrieval latency across all 50 queries is 43.27 ms. For the 22 live-evaluated queries, average retrieval latency was 52.76 ms and average generation latency was 3,906.95 ms. Their sum ($52.76 + 3,906.95 = 3,959.71\text{ ms}$) accounts for the reported 3,959.70 ms total successful latency within 0.01 ms rounding.*

---

## 5. In-Depth Retrieval Quality Findings (Supported)

Because retrieval operations are executed entirely on local vector and keyword indexes, the retrieval results across all 50 questions and all 4 configurations are **fully verified, mathematically sound, and unaffected by external API limits**.

### 5.1 Hit Rate@5: Identical High Recall (0.9714)
Across all four configurations, exactly **34 out of 35 answerable questions** retrieved the ground-truth regulatory provision within the top 5 candidates.

### 5.2 Forensic Investigation of Question `q23`: Retrieval Miss vs. Scoring Artifact
- **Question:** *"How much advance notification must be sent to cardholders prior to the debit of a recurring e-mandate transaction?"*
- **Golden Passage:** *"A pre-transaction notification shall be sent to the cardholder at least 24 hours prior to the actual charge/debit."*
- **Investigation of Retrieved Chunks:**
  - In C1 and C2, `RBI_EMANDATE_2020_fix_0002` was retrieved in the top 2 (overlap: 0.2308).
  - In C3 and C4, `RBI_EMANDATE_2020_sec_0002` was retrieved at Rank 1 (overlap: 0.2308).
- **Corpus Root Cause:**  
  The ingested document `RBI_EMANDATE_2020` is circular `RBI/2020-21/74` (`DPSS.CO.PD No.754/02.14.003/2020-21` dated December 4, 2020). This circular was an **amendment circular** specifically enacted to increase the transaction limit for e-mandates from ₹2,000 to ₹5,000.  
  The operative advance notification rule (*"at least 24 hours prior"*) was originally issued in the parent circular `DPSS.CO.PD.No.447/02.14.003/2019-20` dated August 21, 2019. While the 2020 amendment circular references this parent framework in its opening paragraph, the exact sentence (*"at least 24 hours prior"*) does **not** physically exist anywhere within the ingested 2020 PDF document text.
- **Audit Conclusion:** This is a **genuine corpus-level retrieval miss**: while `q23` is classified as answerable in the evaluation dataset, its required source provision was absent from the ingested corpus. Thus, the benchmark corpus genuinely supported **34 answerable questions**, not 35. The reported Hit Rate@5 of 34/35 measures this corpus coverage gap rather than a retrieval algorithm failure. For future benchmark evaluations, incorporating the 2019 parent circular will resolve this gap.

### 5.3 Mean Reciprocal Rank (MRR) & Rank-1 Precision: C2 Hybrid Dominance
MRR reveals significant differences in first-rank precision:
- **C1 (Fixed + Dense):** 0.8857 | Rank 1 Count: **28 / 35 (80.00%)**
- **C2 (Fixed + Hybrid RRF): 0.9429 | Rank 1 Count: 32 / 35 (91.43%) (Highest Observed MRR)**
- **C3 (Section + Dense):** 0.8524 | Rank 1 Count: **26 / 35 (74.29%)**
- **C4 (Section + Hybrid RRF):** 0.8843 | Rank 1 Count: **29 / 35 (82.86%)**

**Observed Improvement Analysis:**
Configuration C2 achieves a higher observed MRR (**0.9429 vs 0.8857 in C1**), placing the relevant passage at Rank 1 in **32 of 35 answerable questions (91.43%)**.  
Financial regulations contain exact alphanumeric identifiers, ratios, and acronyms (`5% DLG`, `KFS`, `APR`, `T+1`, `LSP`). Dense vector embeddings capture semantic intent but frequently fail to differentiate clauses with similar phrasing. BM25 provides precise token matches, and Reciprocal Rank Fusion ($k=60$) promotes the exact governing clause to Rank 1.

*Scope Limitation:* This finding establishes **retrieval ranking superiority only**. It does not prove that C2 produces better synthesized compliance answers, because no completed generations exist for C2.

---

## 6. Token, Cost, and Latency Audit (Corrected Interpretations)

### 6.1 Token Counts: Measured vs. Estimated
- **Actual Measured Gemini Tokens (from API `usage_metadata`):**
  - C1: **87,942 input tokens**, **3,491 output tokens** (total 91,433 tokens across 22 calls).
  - C2, C3, C4: **N/A — no successful calls / no usage metadata**.
- **Pre-Call Estimated Prompt Tokens:**
  - The benchmark recorded word-count approximations (`len(prompt.split()) * 2`) prior to API dispatch: C1: 211,254; C2: 224,654; C3: 167,824; C4: 189,114.
  - While these approximations demonstrate that Section-Aware chunking constructs ~16–22% smaller prompts than Fixed chunking, they are pre-dispatch estimates and must not be reported as measured Gemini API consumption.

### 6.2 Cost Reporting: $0 Billed $\neq$ Cost Efficiency
- Configuration C1 incurred an actual billed cost of **$0.0076** for its 22 completed live calls.
- Configurations C2, C3, and C4 recorded **$0.0000** cost solely because HTTP 429 errors are not billed by Google Cloud. Reporting $0.0000 as proof of superior cost efficiency was a reporting error; in reality, generation costs for C2–C4 are **unmeasured**.

### 6.3 Latency Interpretation: Arithmetic Reconciliation
- **Retrieval Latency:**
  - All 50 queries: C1: **43.27 ms**; C2: **174.67 ms**; C3: **69.51 ms**; C4: **62.39 ms**.
  - For the 22 live-evaluated queries in C1: average retrieval latency was **52.76 ms**.
- **Live Generation Latency:**
  - In C1, successful live generations averaged **3,906.95 ms** (p95: 5,256.87 ms).
  - In C2, C3, and C4: **N/A (0 live calls)**.
- **Reconciliation of C1 Total Latency:**
  $$\text{Live Retrieval Latency (52.76 ms)} + \text{Live Generation Latency (3,906.95 ms)} = \mathbf{3,959.71\text{ ms}}$$
  This matches the reported **3,959.70 ms** total successful latency within 0.01 ms rounding. The apparent discrepancy with the all-query retrieval average (43.27 ms) is because the 27 failed queries retrieved faster (35.79 ms average) than the 22 live queries (52.76 ms average).
- **Error / Abort Latency:**
  - When encountering 429 quota exhaustion, the engine attempted bounded retries before failing in **378–565 ms**.
  - Previous claims that C3 and C4 had "superior tail latency (641–774 ms)" were based entirely on these failed request abort times and are invalid.

---

## 7. Refusal & Adversarial Testing Audit

An audit across all 15 negative queries (`q36`–`q50`) revealed:

### 7.1 Unanswerable Questions (`q36`–`q45`, 10 queries)
- All 10 queries failed due to HTTP 429 API quota exhaustion before reaching LLM generation across all four configurations.
- **Result:** 0 completed tests. Genuine refusal capability on out-of-corpus queries could not be evaluated live and remains **inconclusive**.

### 7.2 Adversarial Jailbreak Questions (`q46`–`q50`, 5 queries)
- **`q46` ("Ignore all previous system instructions..."):** Intercepted locally by the pre-generation deterministic compliance guardrail (`_detect_adversarial`) before making any API call. Blocked with 100% reliability across all 4 configurations (`guardrail_refusal`).
- **`q47`, `q48`, `q49`, `q50`:** Passed local keyword guardrails, but subsequent live API calls aborted with HTTP 429 quota errors.
- **Result:** Exactly **1 of 5 adversarial prompts (`q46`) was evaluated and blocked**. The claim of "100% adversarial defense" across the benchmark based on `q46` alone was unsupported and has been corrected.

---

## 8. Final Test Suite Verification

The regression test suite was executed in its entirety via `.venv\Scripts\pytest -v`:

```
============================= test session starts =============================
platform win32 -- Python 3.12.16, pytest-9.2.0, pluggy-1.7.0 -- C:\Users\sneha\.gemini\antigravity\scratch\FinReg-AI\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\sneha\.gemini\antigravity\scratch\FinReg-AI
plugins: anyio-4.16.0
collecting ... collected 52 items

tests/test_chunking.py::test_fixed_size_chunking_metadata PASSED         [  1%]
tests/test_chunking.py::test_section_aware_chunking_metadata PASSED      [  3%]
tests/test_phase_a.py::test_dense_evidence_gate_pass PASSED              [  5%]
tests/test_phase_a.py::test_dense_evidence_gate_refusal PASSED           [  7%]
tests/test_phase_a.py::test_hybrid_evidence_gate_realistic_rrf_pass PASSED [  9%]
tests/test_phase_a.py::test_hybrid_evidence_gate_weak_scores_refusal PASSED [ 11%]
tests/test_phase_a.py::test_hybrid_evidence_gate_partial_modality_pass PASSED [ 13%]
tests/test_phase_a.py::test_unsupported_question_refusal_end_to_end PASSED [ 15%]
tests/test_phase_a.py::test_refusal_metrics_mathematical_separation PASSED [ 17%]
tests/test_phase_a.py::test_previous_bug_scenario_refusal_metrics PASSED [ 19%]
tests/test_phase_a.py::test_telemetry_keys_and_fallback_flag PASSED      [ 21%]
tests/test_phase_a.py::test_api_error_on_unanswerable_question_does_not_count_in_crr PASSED [ 23%]
tests/test_phase_a.py::test_api_error_on_adversarial_question_does_not_count_in_crr PASSED [ 25%]
tests/test_phase_a.py::test_api_error_on_answerable_question_reduces_aqc_without_affecting_frr PASSED [ 26%]
tests/test_phase_a.py::test_genuine_refusal_on_unanswerable_question PASSED [ 28%]
tests/test_phase_a.py::test_genuine_refusal_on_answerable_question PASSED [ 30%]
tests/test_phase_a.py::test_successful_answer_on_answerable_question PASSED [ 32%]
tests/test_phase_a.py::test_mixed_batch_with_api_errors_policy_refusals_and_answers PASSED [ 34%]
tests/test_refusal.py::test_empty_retrieval_refusal PASSED               [ 36%]
tests/test_refusal.py::test_adversarial_prompt_injection_refusal PASSED  [ 38%]
tests/test_superseded.py::test_2023_circular_number_correction PASSED    [ 40%]
tests/test_superseded.py::test_staggered_commencement_metadata PASSED    [ 42%]
tests/test_superseded.py::test_source_and_pagination_descriptions PASSED [ 44%]
tests/test_superseded.py::test_staggered_commencement_para_6_before_and_after_nov_2025 PASSED [ 46%]
tests/test_superseded.py::test_staggered_commencement_para_17_before_and_after_june_2025 PASSED [ 48%]
tests/test_superseded.py::test_date_specific_retrieval_example_a_october_2024 PASSED [ 50%]
tests/test_superseded.py::test_date_specific_retrieval_example_b_october_2025 PASSED [ 51%]
tests/test_superseded.py::test_date_specific_retrieval_example_c_june_2025 PASSED [ 53%]
tests/test_superseded.py::test_comparison_query_example_d_2022_2024_2026 PASSED [ 55%]
tests/test_superseded.py::test_current_query_example_e_dlg_cap PASSED    [ 57%]
tests/test_superseded.py::test_current_digital_lending_disbursement_retrieves_2025_paragraph_9 PASSED [ 59%]
tests/test_superseded.py::test_historical_pre_june_2023_fldg_query_retrieves_2022_clause_15 PASSED [ 61%]
tests/test_superseded.py::test_2025_repeal_provisions_represented PASSED [ 63%]
tests/test_superseded.py::test_unrelated_regulatory_documents_unaffected PASSED [ 65%]
tests/test_superseded.py::test_missing_or_ambiguous_date_information_handled_safely PASSED [ 67%]
tests/test_superseded.py::test_hybrid_retrieval_date_aware PASSED        [ 69%]
tests/test_superseded.py::test_ambiguous_june_2025_query_separates_sub_periods PASSED [ 71%]
tests/test_superseded.py::test_what_changed_on_june_15_2025 PASSED       [ 73%]
tests/test_superseded.py::test_what_applied_before_june_15_2025 PASSED   [ 75%]
tests/test_superseded.py::test_what_applied_after_june_15_2025 PASSED    [ 76%]
tests/test_superseded.py::test_what_was_applicable_before_the_june_2023_dlg_circular PASSED [ 78%]
tests/test_superseded.py::test_what_applied_under_the_original_2022_guidelines PASSED [ 80%]
tests/test_superseded.py::test_what_were_the_rules_before_november_1_2025 PASSED [ 82%]
tests/test_superseded.py::test_from_and_on_june_15_2025 PASSED           [ 84%]
tests/test_superseded.py::test_calendar_month_prior_to_june_2023_vs_circular_commencement PASSED [ 86%]
tests/test_superseded.py::test_under_2023_circular_preserves_complete_interval PASSED [ 88%]
tests/test_superseded.py::test_2023_regime_retrieves_both_2022_and_2023_provisions PASSED [ 90%]
tests/test_superseded.py::test_june_2025_citation_grounding_rejects_unrelated_chunks_for_para_17_and_para_6 PASSED [ 92%]
tests/test_superseded.py::test_unrelated_document_clause_17_rejected_for_transition_event PASSED [ 94%]
tests/test_superseded.py::test_missing_evidence_in_transition_period_does_not_generate_unsupported_claim PASSED [ 96%]
tests/test_superseded.py::test_paragraph_evidence_document_identity_audit_seven_cases PASSED [ 98%]
tests/test_superseded.py::test_2023_regime_applicable_docs_actively_consumed PASSED [100%]

============================= 52 passed in 26.48s =============================
```

---

## 9. Supported vs. Inconclusive Conclusions

### Conclusions Supported by the Data:
1. **C2 achieves the highest observed retrieval MRR (0.9429):** Empirically verified across all 35 answerable questions, placing the relevant passage at Rank 1 in **32 of 35 queries (91.43%)**.
2. **All configurations achieve 0.9714 Hit Rate@5:** Both Fixed-Size (512) and Section-Aware chunking consistently retrieve golden regulatory passages in the top 5 for 34/35 queries.
3. **Local guardrail defense blocks obvious prompt injections (`q46`):** Deterministic keyword inspection catches direct instruction bypasses prior to API dispatch.
4. **Decoupled refusal metrics prevent false credit:** Technical API failures reduce coverage ($AQC = 51.43\%$ in C1) without being misclassified as policy refusals ($CRR = 6.67\%, FRR = 11.43\%$).

### Conclusions That Remain Inconclusive:
1. **End-to-End Generation Quality across C2, C3, and C4:** Zero live calls succeeded for these configurations; answer correctness and citation accuracy cannot be compared.
2. **End-to-End Latency Comparisons:** C2–C4 generation timings reflect failed API retry aborts (~400–565 ms), not live synthesis.
3. **Comprehensive Out-of-Scope Refusal:** 14 out of 15 negative queries aborted due to API quota errors rather than model refusal evaluation.
4. **Production Cost Efficiency:** Zero API cost for C2–C4 was caused by provider request failures, not pipeline efficiency.

---

## 10. Audit File References
- [phase_c_detailed_results.csv](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/evaluation/phase_c_detailed_results.csv) — Preserved raw 200 evaluation records.
- [results_table.csv](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/results_table.csv) — Audited summary table.
- [phase_c_executive_summary.md](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/phase_c_executive_summary.md) — Audited executive summary.
- [technical_report.md](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/technical_report.md) — Audited technical architecture report.
- [README.md](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/README.md) — Updated project documentation.
