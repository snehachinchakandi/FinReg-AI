# FinReg AI: Comprehensive Technical Audit Report
**Project:** FinReg AI – Intelligent RAG-Based Indian Financial Regulation Assistant  
**Evaluation Target:** Dvara Group AI/ML & Generative AI Internship Assessment (Task 6 — RAG Pipeline)  
**Audit Date:** November 14, 2026  
**Auditor:** Technical Assessment Protocol  
**Audit Scope:** Codebase, Data Artifacts, Indexing, LLM Generation, Evaluation Metrics, and Technical Documentation  

---

## 1. Executive Summary

This independent technical audit was conducted on the FinReg AI codebase and experimental artifacts located at `C:\Users\sneha\.gemini\antigravity\scratch\FinReg-AI`. 

The audit confirms that the core architectural foundations are solidly built:
1. An authentic corpus of **11 official RBI circulars** totaling **324 physical PDF pages** exists on disk (comfortably exceeding the 100-page threshold).
2. Two independent chunking strategies (Fixed-Size and Section-Aware) were implemented and produced **196** and **285** structured chunks respectively, retaining granular metadata envelopes.
3. Actual FAISS dense indexes (`BAAI/bge-small-en-v1.5`) and BM25Okapi keyword indexes were constructed and persisted to disk.
4. An evaluation set of **50 distinct questions** (35 answerable, 10 unanswerable, 5 adversarial) exists in `evaluation/eval_dataset.jsonl`.

However, the audit identified **four critical discrepancies and implementation bugs** that explain why the experimental results in `reports/results_table.csv` differed drastically from `reports/technical_report.md` and `README.md`:
- **Discrepancy 1:** The numerical values in `reports/technical_report.md` were written during the preliminary architectural drafting phase as target projections and were never reconciled with the actual experimental run.
- **Implementation Bug 1 (The RRF Scale Refusal Bug):** In `src/generation/rag_engine.py`, a hardcoded threshold `top_score < 0.1` was applied indiscriminately. In Hybrid RRF retrieval, ordinal rank fusion produces mathematical scores between $0.015$ and $0.033$. Consequently, **100% of queries in C2 and C4 were prematurely refused before generation**, resulting in `$0.00` cost, 0ms generation latency, and an artificial 0.30 correctness and refusal rate.
- **Implementation Bug 2 (LLM Execution Disconnect):** When the initial pipeline benchmark was executed, `.env` had not yet been created, forcing `rag_engine.py` into a local deterministic string fallback. The live Gemini API was not invoked during the recorded benchmark, explaining the unrealistically low latencies (31–41 ms).
- **Metric Calculation Flaw (Averaging Refusals Across All Categories):** `compute_refusal_accuracy` averaged refusal behavior across all 50 questions (including 35 answerables) rather than evaluating Correct Refusal Rate solely on the 15 unanswerable/adversarial queries.
- **Unexecuted Reranker Claims:** The cross-encoder reranker claims in `technical_report.md` (+0.015 MRR, +45ms latency) were based on hypothetical projections rather than logged experimental trials.

---

## 2. Audit Area 1: Results Consistency Audit

### 2.1 Side-by-Side Comparison of Data Sources

| Metric | CSV C1 | Report C1 | CSV C2 | Report C2 | CSV C3 | Report C3 | CSV C4 | Report C4 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Hit Rate@5** | 0.9714 | 0.8000 | 0.9714 | 0.8857 | 0.9714 | 0.8571 | 0.9714 | 0.9429 |
| **MRR** | 0.9000 | 0.6720 | 0.9286 | 0.7410 | 0.8667 | 0.7180 | 0.8914 | 0.8260 |
| **Correctness** | 0.2545 | 0.7850 | 0.3000 | 0.8420 | 0.2014 | 0.8300 | 0.3000 | 0.9150 |
| **Citation Acc.** | 0.9600 | 0.8200 | 1.0000 | 0.8800 | 0.9800 | 0.8900 | 1.0000 | 0.9600 |
| **Refusal Rate** | 0.7800 | 0.8667 | 0.3000 | 0.9333 | 0.7800 | 0.9333 | 0.3000 | 1.0000 |
| **Avg Latency** | 41.83 ms | 185 ms | 37.52 ms | 195 ms | 31.48 ms | 180 ms | 34.75 ms | 190 ms |
| **Cost / Query** | $0.000361 | N/A | $0.000000 | N/A | $0.000282 | N/A | $0.000000 | N/A |

### 2.2 Root Cause Analysis
1. **Code Responsible:** `src/evaluation/evaluator.py` (`run_all_configurations()` lines 122–165) executed the test harness and wrote directly to `reports/results_table.csv`.
2. **Source of Divergence:** The markdown file `reports/technical_report.md` was authored during Phase 1 (Architecture & Planning) with target baseline figures. When `run_pipeline.py` ran in Phase 7, it output real runtime metrics to `results_table.csv`, but `technical_report.md` and `README.md` were never updated to reflect the actual experimental output.
3. **Verdict:** The CSV contains actual (flawed) experimental calculations; the technical report contained uncalibrated architectural estimates.

---

## 3. Audit Area 2: Evaluation Benchmark Integrity

### 3.1 Question Distribution & Verification
- **File Audited:** `evaluation/eval_dataset.jsonl`
- **Total Questions:** 50
  - **Answerable Questions:** 35 (`q01`–`q35`)
  - **Unanswerable Questions:** 10 (`q36`–`q45`) (e.g., SEBI IPO lock-in, crypto GST, IRDAI solvency, IBBI CIRP timelines)
  - **Adversarial Questions:** 5 (`q46`–`q50`) (e.g., prompt injection, jailbreak persona, false circular leak)
- **Golden Passages:** All 35 answerable questions map directly to authentic provisions in official RBI circulars.

### 3.2 Metric Calculation Formulas (`src/evaluation/metrics.py`)
1. **Hit Rate@5 (`compute_hit_at_k`):**
   - Evaluated using word unigram overlap between retrieved chunk text and golden passage with threshold $\tau = 0.4$.
   - For all 4 configurations, 34 out of 35 answerable queries placed the golden passage in top-5 chunks, giving $34 / 35 = 0.9714$.
2. **Mean Reciprocal Rank (`compute_reciprocal_rank`):**
   - Reciprocal rank $1 / \text{rank}$ for the first passage reaching $\ge 0.4$ overlap.
   - Fixed+Hybrid (C2) achieved 0.9286; Section+Hybrid (C4) achieved 0.8914.
3. **The Refusal Rate Flaw (`compute_refusal_accuracy`):**
   ```python
   def compute_refusal_accuracy(is_refusal: bool, category: str) -> float:
       if category in ("unanswerable", "adversarial"):
           return 1.0 if is_refusal else 0.0
       else:  # answerable
           return 1.0 if not is_refusal else 0.0
   ```
   - In `evaluator.py`, `sum(refusal_scores) / len(refusal_scores)` averaged this across all 50 items.
   - In C2 and C4, because every query was refused, the 15 unanswerables scored `1.0` and the 35 answerables scored `0.0`.
   - Result: $15 / 50 = 0.3000$.
   - **Correct Definition:** Correct Refusal Rate should be calculated solely over the negative class:
     $$CRR = \frac{\sum_{q \in Neg} \mathbb{I}(\text{refusal})}{\|Neg\|} = \frac{15}{15} = 1.00$$
     while false refusals on answerables should be reported as False Refusal Rate / Specificity.
4. **Consistency:** All four configurations evaluated the identical 50 questions in the same order.

---

## 4. Audit Area 3: LLM Execution, Token Tracking & Cost Calculation

### 4.1 Verification of Gemini API Calls During Benchmark
- **File Audited:** `src/generation/rag_engine.py` (lines 35–42, 105–125)
- **Finding:** During the initial pipeline run, `.env` did not exist on the filesystem (`Test-Path` returned `False`).
- Consequently, `self.client` was `None`, and the engine fell back to `_fallback_grounded_generator()`.
- **Verdict:** No live Gemini API calls were made during the benchmark that generated `results_table.csv`.

### 4.2 The RRF Scale Refusal Bug (Why C2 and C4 Cost $0.00)
- **Code:** `src/generation/rag_engine.py`
  ```python
  top_score = retrieved_chunks[0][1]
  if force_refusal_threshold and top_score < SIMILARITY_REFUSAL_THRESHOLD and top_score < 0.1:
      return {"answer": "REFUSAL: ...", "estimated_cost_usd": 0.0, ...}
  ```
- **Root Cause:**
  - In Dense retrieval, `top_score` is cosine similarity ($\approx 0.50 - 0.95$).
  - In Hybrid retrieval, `top_score` is the Reciprocal Rank Fusion score:
    $$RRF = \frac{1}{60 + r_{\text{dense}}} + \frac{1}{60 + r_{\text{bm25}}} \le \frac{2}{61} \approx 0.0328$$
  - Because $0.0328 < 0.1$ is mathematically always true, **every single hybrid query was aborted at this gate before LLM generation**.
  - This explains why C2 and C4 recorded 0 tokens, $0.000000 cost, and 34–37 ms latency.

### 4.3 Latency Measurement Architecture
- In `evaluator.py`, total latency was computed as:
  `total_latency = retrieval_latency + gen_result["latency_ms"]`
- Retrieval latency and generation latency were collapsed into a single scalar, obscuring whether delays originated from vector search or LLM generation.

---

## 5. Audit Area 4: Retrieval & Indexing Mechanisms

### 5.1 Dense Retrieval Verification
- **File:** `src/retrieval/dense.py`
- **Embedding Model:** `BAAI/bge-small-en-v1.5` (384 dimensions, verified downloaded in HuggingFace cache).
- **Index:** `faiss.IndexFlatIP` (Inner product on normalized vectors = exact cosine similarity).
- **Artifacts on Disk:**
  - `indexes/fixed_dense.faiss` (196 vectors, 296 KB)
  - `indexes/section_dense.faiss` (285 vectors, 430 KB)
- **Verdict:** Fully implemented and operating on real neural embeddings.

### 5.2 BM25 Keyword Retrieval Verification
- **File:** `src/retrieval/bm25.py`
- **Algorithm:** `rank_bm25.BM25Okapi` ($k_1=1.5, b=0.75$).
- **Tokenizer:** Custom regex tokenizer preserving financial acronyms (`DLG`, `FLDG`, `KFS`, `APR`, `LSP`, `RE`).
- **Artifacts on Disk:**
  - `indexes/fixed_bm25.pkl` (78 KB)
  - `indexes/section_bm25.pkl` (112 KB)
- **Verdict:** Fully implemented, distinct from dense retrieval.

### 5.3 Reciprocal Rank Fusion (RRF) Verification
- **File:** `src/retrieval/hybrid.py`
- **Formula:** $RRF(d) = \sum_{m} \frac{1}{60 + \text{rank}_m(d)}$
- **Verdict:** Mathematically correct implementation of standard RRF.

### 5.4 Cross-Encoder Reranker Status
- **File:** `src/retrieval/reranker.py`
- **Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **Finding:** The reranker module was written and unit-tested, but in `run_pipeline.py`, `evaluator.run_all_configurations()` was called without passing the reranker instance.
- **Verdict:** The claims in `technical_report.md` describing a +0.015 MRR gain and +45ms latency were not derived from logged benchmark runs.

---

## 6. Audit Area 5: Document Corpus & Page Count Audit

### 6.1 Physical Document Inventory

Every PDF in `data/raw_documents/` was verified using PyMuPDF (`fitz`):

| # | Document ID | Official Circular Reference | Date | Regulator | Physical Pages | File Size | Primary Compliance Subject |
|---|---|---|---|---|:---:|:---:|---|
| 1 | `RBI_DL_2022` | DOR.CRE.REC.66/21.07.001/2022-23 | 02-Sep-2022 | RBI | 26 | 170.6 KB | Digital Lending Framework, KFS, cooling-off, flow of funds |
| 2 | `RBI_DLG_2023` | DOR.STR.REC.20/21.04.048/2023-24 | 08-Jun-2023 | RBI | 22 | 136.8 KB | Default Loss Guarantee (DLG) 5% cap, eligible security forms |
| 3 | `RBI_PENAL_2023` | RBI/2023-24/53 DOR.MCS.REC.28/01.01.001/2023-24 | 18-Aug-2023 | RBI | 30 | 212.2 KB | Fair Lending Practice – Penal charges vs compounding interest |
| 4 | `RBI_PPI_MD_2021` | DPSS.CO.PD.No.1415/02.14.006/2021-22 | 27-Aug-2021 | RBI | 42 | 366.1 KB | Master Direction on Prepaid Payment Instruments (KYC, limits) |
| 5 | `RBI_PPI_CREDIT_2022` | DPSS.CO.PD.No.S-257/02.14.006/2022-23 | 20-Jun-2022 | RBI | 40 | 292.2 KB | Restriction on loading non-bank PPIs via credit lines |
| 6 | `RBI_COFT_2021` | RBI/2021-22/96 DPSS.CO.PD No.S516/02.14.003/2021-22 | 07-Sep-2021 | RBI | 23 | 136.5 KB | Card-on-File Tokenisation, merchant card storage ban |
| 7 | `RBI_P2P_MD_2017` | DNBR (PD) 054/03.10.119/2017-18 | 24-Aug-2017 | RBI | 41 | 363.9 KB | NBFC-P2P Master Directions, ₹50L aggregate lending cap |
| 8 | `RBI_PA_PG_2020` | DPSS.CO.PD.No.1810/02.14.008/2019-20 | 17-Mar-2020 | RBI | 29 | 212.0 KB | Payment Aggregators & Gateways, capital, escrow, T+1/T+2 |
| 9 | `RBI_EMANDATE_2020` | RBI/2020-21/74 DPSS.CO.PD No.754/02.14.003/2020-21 | 04-Dec-2020 | RBI | 21 | 120.2 KB | Recurring transaction e-mandate framework, AFA thresholds |
| 10 | `RBI_IT_GOV_2023` | RBI/2023-24/107 DoS.CO.CSITE.SEC.No.8/31.01.015/2023-24 | 07-Nov-2023 | RBI | 28 | 224.2 KB | IT Governance, cybersecurity incident reporting (6 hours) |
| 11 | `RBI_TAT_COMP_2019` | DPSS.CO.PD No.629/02.01.014/2019-20 | 20-Sep-2019 | RBI | 22 | 129.9 KB | Auto-reversal TATs, ₹100/day customer compensation matrix |
| **Total** | **11 Documents** | — | — | **RBI** | **324** | **2.38 MB** | **All 11 PDFs verified intact on disk** |

### 6.2 Reconciliation of Page Counts
- In `FinReg_AI_Architecture_and_Plan.md`, the anticipated page count was estimated at **~197 pages**.
- In the final rendered PDFs (`data/raw_documents/`), the actual physical page count across all 11 documents is **324 pages**.
- **Verdict:** The corpus satisfies Dvara's requirement of "at least 100 pages in total" by a wide margin (324 vs 100). The report must be updated to state the verified count of 324 pages.

---

## 7. Audit Area 6: Regulatory Versioning & Superseded Circular Mechanics

### 7.1 Existing Implementation
- **Registry:** `src/versioning/temporal_filter.py` defines two explicit superseded pairs:
  1. `FLDG_SYNTHETIC_SECURITISATION`: `RBI_DL_2022` Para 6 $\rightarrow$ `RBI_DLG_2023` Clause 6.
  2. `PENAL_INTEREST_TO_CHARGES`: Legacy compounding penal interest $\rightarrow$ `RBI_PENAL_2023` Clause 3.
- **Routing:**
  - `is_historical_query(query)` checks regex triggers for comparison/evolution intent.
  - In default compliance mode, `filter_chunks()` checks `chunk.get("is_active", True)`.

### 7.2 Identified Vulnerability: Whole-Document vs. Clause-Level Validity
- **Finding:** In `data/metadata/documents_metadata.json`, the document `RBI_DL_2022` is marked `is_active: True`.
- Because `is_active` was set at the document level, the specific superseded clause (Para 6 restricting FLDG under securitisation) inherited `is_active: True` on its chunk (`RBI_DL_2022_sec_0006`).
- **Risk:** In financial regulation, new circulars frequently amend **a single clause** while leaving the rest of the parent circular intact. A document-level boolean cannot handle partial amendments.
- **Requirement for Robustness:** Chunks corresponding specifically to superseded clauses must carry explicit clause-level flags:
  ```json
  "is_active": false,
  "superseded_by": "RBI_DLG_2023"
  ```
  while the rest of `RBI_DL_2022` remains `is_active: true`.

---

## 8. Consolidated Bug & Risk Register

| Priority | Issue ID | Component | Exact Location | Description & Impact |
|:---:|---|---|---|---|
| **CRITICAL** | BUG-01 | Generation / Refusal Gate | `src/generation/rag_engine.py` (L63–75) | Applied `top_score < 0.1` indiscriminately. Caused 100% of hybrid queries to falsely refuse before LLM generation. |
| **CRITICAL** | BUG-02 | Evaluation Experimentation | `run_pipeline.py` / `reports/results_table.csv` | Pipeline was evaluated when `.env` was missing, falling back to local simulation and yielding artificial 31ms latencies and inaccurate correctness scores. |
| **HIGH** | BUG-03 | Metric Aggregation | `src/evaluation/metrics.py` (L85–96) | Averaged refusal accuracy across both answerable and unanswerable queries, producing the confusing 0.3000 refusal rate in the CSV. |
| **HIGH** | BUG-04 | Report Inconsistency | `reports/technical_report.md` & `README.md` | Reported preliminary placeholder metrics (Hit@5 0.9429, MRR 0.8260, latency 190ms) that did not match the generated CSV. |
| **MEDIUM** | BUG-05 | Latency Breakdown | `src/evaluation/evaluator.py` (L75–85) | Collapsed retrieval latency and generation latency into a single number rather than reporting them in separate columns. |
| **MEDIUM** | BUG-06 | Unverified Claims | `reports/technical_report.md` (L19) | Stated cross-encoder reranker gained +0.015 MRR and +45ms latency without logged benchmark backing. |
| **MEDIUM** | BUG-07 | Clause-Level Validity | `data/metadata/documents_metadata.json` | Used document-level `is_active` rather than clause-level flags for partial amendments (e.g., Para 6 of DL 2022). |
| **LOW** | BUG-08 | Page Count Statement | `reports/technical_report.md` (L7) | Stated "~197 pages" based on pre-download estimate instead of actual 324 physical PDF pages. |

---

## 9. Recommended Corrections (Prioritized Execution Plan)

### Phase A: Metric Calculation & Evaluation Architecture Fixes
1. **Fix `src/evaluation/metrics.py`:**
   - Define **Correct Refusal Rate (CRR)** strictly over the 15 unanswerable + adversarial queries:
     $$\text{CRR} = \frac{\text{Correct Refusals}}{15}$$
   - Add a separate **False Refusal Rate (FRR)** over the 35 answerable queries:
     $$\text{FRR} = \frac{\text{False Refusals}}{35}$$
2. **Expand Latency & Token Telemetry in `evaluator.py`:**
   - Report `Retrieval Latency (ms)`, `Generation Latency (ms)`, and `Total Latency (ms)` as distinct CSV columns.

### Phase B: Granular Clause-Level Supersession
1. Statically tag chunk `RBI_DL_2022_sec_0006` (Para 6 synthetic securitisation) with `is_active: false` and `superseded_by: "RBI_DLG_2023"`.
2. Confirm that queries concerning current FLDG retrieve exclusively from `RBI_DLG_2023`.

### Phase C: Re-run Live Experimental Benchmark
1. Execute the 50-question benchmark with the live Gemini API key (now verified working with `gemini-2.5-flash`).
2. Log actual live token usage, true end-to-end API latency, and authentic semantic correctness scores.
3. Test the cross-encoder reranker on the benchmark to obtain real empirical comparative numbers or remove the claim.

### Phase D: Reconcile Technical Report, CSV & Submission Archive
1. Regenerate `reports/results_table.csv` with live, verified metrics.
2. Update `reports/technical_report.md` and `README.md` so that every single table cell and analytical statement agrees with the CSV.
3. Update the physical page count to the verified 324 pages.
4. Repackage the clean submission archive `01FE23BCS276_Task6.zip`.
