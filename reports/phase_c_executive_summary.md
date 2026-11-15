# FinReg AI: Phase C Executive Summary & Integrity Audit

**Submission:** Dvara Group AI/ML & Generative AI Internship Evaluation (Task 6 — RAG Pipeline)  
**Deliverable:** Phase C Comprehensive Evaluation Benchmark & Integrity Audit  
**Date:** November 14, 2026  
**Audited Benchmark Corpus:** Exactly 12 Documents, Exactly 341 Physical Pages (Historical Benchmark Scope)  
**Current Corpus State:** 13 Documents, 345 Physical Pages (Post-Ingestion Update)  
**Audited Historical Indexes:** 216 Fixed Chunks/Vectors (384-d), 330 Section Chunks/Vectors (384-d)  
**Current Re-Indexed Dimensions:** 220 Fixed Chunks/Vectors (384-d), 341 Section Chunks/Vectors (384-d)  
**Status:** Completed & Frozen (Audit Verified)  

---

## 🎯 Executive Overview

Phase C evaluated the **FinReg AI Regulatory Compliance RAG Pipeline** across its four core architectural configurations (**C1, C2, C3, and C4**) using the complete 50-question evaluation dataset (35 answerable compliance queries, 10 unanswerable queries, and 5 adversarial jailbreaks).

A total of **200 evaluations** (50 questions × 4 configurations) were executed against an authentic corpus of **12 RBI regulatory circulars (341 pages)**.

```
========================================================================================
                          HISTORICAL BENCHMARK SNAPSHOT (12-DOC SCOPE)
========================================================================================
 Total Ingested Corpus:       12 Authentic Source Documents (341 physical PDF pages)
 Chunk & Vector Index Sizes:  216 Fixed Chunks / 330 Section Chunks (BGE-small-en-v1.5)
 Total Evaluations Executed:  200 (50 questions x 4 configurations)
 Hit Rate@5 (All Configs):    0.9714 (34/35 Golden Regulatory Passages Retrieved)
 Top Retrieval Engine (MRR):  Configuration C2 (MRR = 0.9429; Rank 1 in 32/35 cases, 91.43%)
 Live Generation Scope:       22 completed live Gemini calls in C1 (0 in C2, C3, C4)
 End-to-End Generation State: Inconclusive across C2-C4 due to Gemini API 429 Quota Limits
 Regression Suite Status:     71 / 71 Passed (100% Pass Rate across all test modules)
========================================================================================
```

---

## 📊 Audited Historical Benchmark Results Matrix (12-Doc Corpus)

The table below reflects the audited empirical values measured during the original 200-run Phase C benchmark execution across the 12-document corpus:

| Metric | C1 (Fixed + Dense) | C2 (Fixed + Hybrid RRF) | C3 (Section + Dense) | C4 (Section + Hybrid RRF) | Benchmark Evaluation Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Chunking Strategy** | Fixed-Size (400w/75o) | Fixed-Size (400w/75o) | Section-Aware | Section-Aware | 216 fixed / 330 section chunks |
| **Retrieval Strategy** | Dense (FAISS) | Hybrid (BM25 + RRF) | Dense (FAISS) | Hybrid (BM25 + RRF) | FlatIP Cosine / BM25 ($k=60$) |
| **Hit Rate@5 (n=35)** | **0.9714** (34/35) | **0.9714** (34/35) | **0.9714** (34/35) | **0.9714** (34/35) | **Fully Verified (Tie at 97.14%)**|
| **MRR (n=35)** | 0.8857 | **0.9429** | 0.8524 | 0.8843 | **Fully Verified (C2 Highest Observed)** |
| **Rank-1 Retrieval Count** | 28 / 35 (80.00%) | **32 / 35 (91.43%)** | 26 / 35 (74.29%) | 29 / 35 (82.86%) | Relevant chunk placed at Rank 1 |
| **Successful Live Gemini Calls** | **22** | 0 | 0 | 0 | API Quota Exhaustion in C2-C4 |
| **API Errors (HTTP 429)** | 27 | 49 | 49 | 49 | Bounded 3-retry aborts |
| **Local Guardrail Refusals** | 1 (`q46`) | 1 (`q46`) | 1 (`q46`) | 1 (`q46`) | Intercepted by local guardrail |
| **Answer Correctness (Completed)**| **0.6823** (n=22) | **N/A** (0 calls) | **N/A** (0 calls) | **N/A** (0 calls) | Inconclusive for C2, C3, C4 |
| **Citation Accuracy (Completed)** | **0.6364** (n=22) | **N/A** (0 calls) | **N/A** (0 calls) | **N/A** (0 calls) | Inconclusive for C2, C3, C4 |
| **CRR (15 Negative Queries)** | 0.0667 (1/15)* | 0.0667 (1/15)* | 0.0667 (1/15)* | 0.0667 (1/15)* | 1 blocked locally; 14 failed 429 |
| **FRR (35 Answerable Queries)** | 0.1143 (4/35) | 0.0000 (0/35) | 0.0000 (0/35) | 0.0000 (0/35) | Technical errors $\neq$ false refusals |
| **AQC (35 Answerable Queries)** | **0.5143** (18/35) | 0.0000 (0/35) | 0.0000 (0/35) | 0.0000 (0/35) | Coverage reduced by 429 errors |
| **Avg Retrieval Latency (All 50)**| **43.27 ms** | 174.67 ms | 69.51 ms | 62.39 ms | **Fully Verified** |
| **Avg Retrieval Latency (22 Live)**| **52.76 ms** | **N/A** (0 calls) | **N/A** (0 calls) | **N/A** (0 calls) | 22 Live calls in C1 |
| **Avg Live Gen Latency (22 Live)**| 3,906.95 ms | **N/A** (0 calls) | **N/A** (0 calls) | **N/A** (0 calls) | Inconclusive for C2, C3, C4 |
| **Avg Total Successful Latency**| 3,959.70 ms* | **N/A** (0 calls) | **N/A** (0 calls) | **N/A** (0 calls) | Retrieval (52.76ms) + Gen (3906.95ms) |
| **Avg API Error Abort Latency**| 378.51 ms (n=27)| 565.20 ms (n=49)| 383.00 ms (n=49)| 420.50 ms (n=49)| Failed request + backoff time |
| **Measured Gemini Input Tokens**| **87,942** | **N/A** | **N/A** | **N/A** | From API `usage_metadata` |
| **Measured Gemini Output Tokens**| **3,491** | **N/A** | **N/A** | **N/A** | From API `usage_metadata` |
| **Pre-Call Estimated Prompt Tokens**| 211,254 | 224,654 | 167,824 | 189,114 | Pre-dispatch character approximation |
| **Actual Billed Cost ($)** | **$0.0076** | **N/A** ($0 billed) | **N/A** ($0 billed) | **N/A** ($0 billed) | Failed calls do not prove efficiency |

*\*CRR Note: The 1/15 CRR represents solely the 1 adversarial query (`q46`) intercepted locally. The other 14 negative queries were not evaluated by the LLM due to 429 errors; this does not validate LLM refusal.*  
*\*Latency Reconciliation: In C1, average retrieval on the 22 live queries was 52.76 ms and average generation was 3,906.95 ms. Their sum ($52.76 + 3,906.95 = 3,959.71\text{ ms}$) accounts for the reported 3,959.70 ms total successful latency.*

---

## 💡 Supported Findings vs. Inconclusive Areas (Historical Benchmark)

### What the Historical Data Proves (Supported Conclusions):
1. **Hybrid Retrieval (Dense + BM25 RRF) Delivers Higher Observed Retrieval Precision:**
   - Configuration C2 achieved the highest observed Mean Reciprocal Rank (**MRR = 0.9429**), placing the relevant passage at Rank 1 in **32 of 35 answerable questions (91.43%)**.
   - Exact alphanumeric tokens (`5% DLG`, `KFS`, `APR`, `T+1`, `LSP`) are accurately captured by BM25, while dense vectors supply semantic recall.
2. **Local Compliance Guardrail Blocks Direct Instruction Bypasses:**
   - Adversarial prompt `q46` was intercepted deterministically by local guardrails before API dispatch.
3. **Question `q23` Corpus Coverage Limitation (34 Supported Answerable Questions):**
   - The evaluation dataset classified `q23` as answerable, but its required 24-hour notification rule comes from a 2019 parent circular absent from the ingested 2020 amendment circular text.
   - The 12-doc corpus genuinely supported 34 answerable questions. The reported Hit Rate@5 of 34/35 measured this corpus coverage gap rather than an algorithmic retrieval failure.
4. **Mathematical Separation of Coverage and Refusals ($AQC \neq 1 - FRR$):**
   - API quota failures reduced answerable coverage ($AQC = 51.43\%$ in C1) without corrupting policy refusal metrics ($CRR = 6.67\%, FRR = 11.43\%$).

### What Remains Inconclusive:
1. **Cross-Configuration Answer Quality:** Because C2, C3, and C4 completed zero live generations due to external API quota limits, their generation correctness, citation fidelity, and end-to-end answer quality cannot be compared to C1.
2. **Tail Latency Comparisons:** The 380–565 ms latencies recorded for C2–C4 represent rapid HTTP 429 retry aborts, not live generation performance.
3. **Comprehensive Refusal on Unanswerable Queries:** All 10 unanswerable queries failed due to HTTP 429 quota exhaustion rather than model evaluation.

---

## 🔄 Subsequent Priority 1 Corpus Expansion & Updated Retrieval Evaluation (13 Documents)

Following the benchmark audit, **Priority 1** resolved the `q23` corpus coverage limitation by ingesting the authentic parent circular:

1. **Document Ingestion & Provenance:**
   - **Document Added:** `RBI_EMANDATE_2019` (`DPSS.CO.PD.No.447/02.14.003/2019-20`, August 21, 2019, 4 pages).
   - **Source Provenance:** The statutory text was captured directly from the official RBI HTML notification (`https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11668&Mode=0`). The local PDF was rendered from this official HTML because RBI's raw PDF endpoint was gated by an automated anti-bot CAPTCHA block. It is an authentic archival PDF derivative, not the original RBI-downloaded PDF file.
   - **Ground-Truth Attribution:** `q23` was updated to cite Annexure Paragraph 8, Page 3.
2. **Expanded Corpus Dimensions:**
   - Total Documents: **13 documents** (11 active, 2 superseded).
   - Total Physical Pages: **345 pages**.
   - Fixed Chunks: **220 chunks** (+4).
   - Section-Aware Chunks: **341 chunks** (+11).
3. **Updated Retrieval-Only Evaluation Results (13 Documents, n=35 Answerables):**

| Configuration | Chunking | Retrieval Strategy | Updated Hit Rate@5 | Updated MRR | Rank-1 Hits (n=35) | `q23` Retrieval Rank |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **C1** | Fixed-Size | Dense (FAISS) | **1.0000 (35/35)** | **0.9143** | 30 / 35 (85.71%) | **Rank 1** |
| **C2** | Fixed-Size | Hybrid (BM25 + RRF) | **1.0000 (35/35)** | **0.9714** | **33 / 35 (94.29%)** | **Rank 1** |
| **C3** | Section-Aware | Dense (FAISS) | **1.0000 (35/35)** | **0.8952** | 29 / 35 (82.86%) | **Rank 1** |
| **C4** | Section-Aware | Hybrid (BM25 + RRF) | **1.0000 (35/35)** | **0.9129** | 30 / 35 (85.71%) | **Rank 1** |

> **Key Takeaway:** Configuration **C2 (Fixed + Hybrid RRF)** is the **observed retrieval MRR leader** across both the 12-document baseline (0.9429) and the updated 13-document corpus (0.9714). However, C2 is **not proven as the best overall RAG configuration** because end-to-end generation quality across C2–C4 remains inconclusive due to Gemini API rate limits.

---

## 📁 Audit & Deliverable Links
- Audited Historical Results Table (12 Docs): [results_table.csv](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/results_table.csv)
- Comprehensive Historical Audit Report: [phase_c_benchmark_report.md](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/phase_c_benchmark_report.md)
- Priority 1 q23 Validation Report: [q23_corpus_correction_validation.md](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/q23_corpus_correction_validation.md)
- Technical Architecture Report: [technical_report.md](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/technical_report.md)
- Raw 200 Evaluation Records: [phase_c_detailed_results.csv](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/evaluation/phase_c_detailed_results.csv)
- Regression Test Suite (71/71 Passing): [tests/](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/tests/)
