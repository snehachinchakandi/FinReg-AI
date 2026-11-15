# FinReg AI: Technical Evaluation & Architecture Report

**Submission for Dvara Group AI/ML & Generative AI Internship Assessment (Task 6 — RAG Pipeline)**  
**Historical Evaluation Benchmark:** Phase C Complete Evaluation & Integrity Audit (200 Runs across 50 Questions × 4 Configurations on 12 Documents)  
**Updated Retrieval Evaluation:** Post-Ingestion Evaluation across 35 Answerable Questions on 13 Documents  
**Current Corpus State:** Exactly 13 Documents, Exactly 345 Physical PDF Pages (11 Active, 2 Superseded)  
**Current Index Dimensions:** 220 Fixed Chunks/Vectors (384-d), 341 Section Chunks/Vectors (384-d)  
**Historical Benchmark Corpus:** Exactly 12 Documents, Exactly 341 Physical PDF Pages (216 Fixed / 330 Section Chunks)  
**Regression Test Suite:** 71 / 71 Tests Passed (100% Pass Rate)  

---

## 1. Measured Benchmark Results & Comparative Analysis

We evaluated four architectural configurations across our 50-question benchmark (35 answerable compliance queries, 10 unanswerable queries, and 5 adversarial jailbreaks). To maintain strict academic integrity, this report explicitly separates the **Historical Phase C 200-Run Benchmark (12 Documents)** from the **Updated Retrieval-Only Evaluation (13 Documents)**.

---

### 1.1 Historical Phase C Benchmark Performance Matrix (12-Document Corpus)
The table below reflects the exact empirical values measured during the original 200-run Phase C benchmark execution across the 12-document corpus:

| Config ID | Configuration | Chunking Strategy | Retrieval Strategy | Hit Rate@5 (n=35) | MRR (n=35) | Rank-1 Count (n=35) | Live Generations (n=50) | Answer Correctness (Completed) | Citation Accuracy (Completed) | CRR (n=15) | FRR (n=35) | AQC (n=35) | Avg Retrieval Latency (All 50) | Avg Live Gen Latency | Generation Benchmark Status |
|:---:|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:--- |
| **C1** | Fixed + Dense | Fixed (400w/75o) | Dense (FAISS FlatIP) | **0.9714** (34/35) | 0.8857 | 28 / 35 (80.00%) | **22** | **0.6823** (n=22) | **0.6364** (n=22) | 0.0667 (1/15)* | 0.1143 (4/35) | **0.5143** (18/35) | **43.27 ms** | 3,906.95 ms | Partially Evaluated (22 live calls) |
| **C2** | **Fixed + Hybrid** | **Fixed (400w/75o)** | **Hybrid (BM25 + RRF)** | **0.9714** (34/35) | **0.9429** | **32 / 35 (91.43%)** | 0 | **N/A** (0 calls) | **N/A** (0 calls) | 0.0667 (1/15)* | 0.0000 (0/35) | 0.0000 (0/35) | 174.67 ms | **N/A** (0 calls) | **Inconclusive (Quota Exhausted)** |
| **C3** | Section + Dense | Section-Aware (max 800) | Dense (FAISS FlatIP) | **0.9714** (34/35) | 0.8524 | 26 / 35 (74.29%) | 0 | **N/A** (0 calls) | **N/A** (0 calls) | 0.0667 (1/15)* | 0.0000 (0/35) | 0.0000 (0/35) | 69.51 ms | **N/A** (0 calls) | **Inconclusive (Quota Exhausted)** |
| **C4** | **Section + Hybrid** | **Section-Aware (max 800)** | **Hybrid (BM25 + RRF)** | **0.9714** (34/35) | **0.8843** | 29 / 35 (82.86%) | 0 | **N/A** (0 calls) | **N/A** (0 calls) | 0.0667 (1/15)* | 0.0000 (0/35) | 0.0000 (0/35) | 62.39 ms | **N/A** (0 calls) | **Inconclusive (Quota Exhausted)** |

*\*CRR Note: The 1/15 CRR represents solely the 1 adversarial query (`q46`) intercepted locally by compliance guardrails. The remaining 14 negative queries were unexecuted due to HTTP 429 quota exhaustion; this does not validate LLM out-of-scope refusal.*

---

### 1.2 Updated Retrieval-Only Benchmark Evaluation (13-Document Corpus)
Following Priority 1, the authentic parent circular `RBI_EMANDATE_2019` was ingested, resolving the coverage gap for `q23`. All 35 answerable questions were re-evaluated across the rebuilt FAISS dense and BM25 indexes:

| Config ID | Configuration | Chunking Strategy | Retrieval Strategy | Updated Hit Rate@5 (n=35) | Updated MRR (n=35) | Rank-1 Hits (n=35) | `q23` Retrieval Rank |
|:---:|---|---|---|:---:|:---:|:---:|:---:|
| **C1** | Fixed + Dense | Fixed-Size (400w/75o) | Dense (FAISS FlatIP) | **1.0000 (35/35)** | **0.9143** | 30 / 35 (85.71%) | **Rank 1** |
| **C2** | **Fixed + Hybrid** | **Fixed-Size (400w/75o)** | **Hybrid (BM25 + RRF)** | **1.0000 (35/35)** | **0.9714** | **33 / 35 (94.29%)** | **Rank 1** |
| **C3** | Section + Dense | Section-Aware | Dense (FAISS FlatIP) | **1.0000 (35/35)** | **0.8952** | 29 / 35 (82.86%) | **Rank 1** |
| **C4** | **Section + Hybrid** | **Section-Aware** | **Hybrid (BM25 + RRF)** | **1.0000 (35/35)** | **0.9129** | 30 / 35 (85.71%) | **Rank 1** |

---

### 1.3 Retrieval Findings (Empirically Supported)

1. **Higher Observed Retrieval Precision in C2 (Fixed-Size + Hybrid RRF):**
   - **Empirical Demonstration:** Across both the historical baseline (MRR = 0.9429) and the updated 13-document evaluation (**MRR = 0.9714**), Configuration C2 achieved the highest observed retrieval precision. In the updated evaluation, it placed the relevant regulatory provision at Rank 1 in **33 out of 35 answerable questions (94.29%)**.
   - **Why Hybrid RRF Achieved Higher MRR:** Dense embeddings (`bge-small-en-v1.5`) excel at semantic mapping but struggle to differentiate semantically identical provisions that differ by exact financial entities or numerical thresholds (`LSP` vs `RE`, `5% DLG` vs `synthetic securitisation`, `T+1` vs `T+5` auto-reversal). BM25 provides exact keyword matching, while Reciprocal Rank Fusion ($k=60$) seamlessly integrates both rankings without requiring brittle score normalization:
     $$RRF\_Score(d) = \sum_{m \in \{dense, bm25\}} \frac{1}{60 + \text{rank}_m(d)}$$
   - In fixed chunking, adding BM25 boosted MRR from **0.8857 (C1) to 0.9429 (C2)** in baseline, and from **0.9143 (C1) to 0.9714 (C2)** in the updated corpus.
2. **Perfect Retrieval Recall: Universal 1.0000 Hit Rate@5:**
   - In the updated 13-document corpus, all four configurations retrieved the golden regulatory passage within the top 5 chunks for **35 out of 35 answerable questions (100%)**.

---

### 1.4 Generation Findings & Inconclusive Comparisons

1. **Live Generation in C1:**
   - Configuration C1 completed 22 live generations before reaching external provider quota limits (HTTP 429).
   - On completed generations, C1 achieved an average Answer Correctness of **0.6823** and Citation Accuracy of **0.6364**, producing grounded answers citing exact circular clauses and pages.
   - Total prompt tokens measured via API metadata on live calls were **87,942 input tokens** and **3,491 output tokens**, incurring an actual cost of **$0.0076**.
   - Latency arithmetic: Live retrieval (52.76 ms) + Live generation (3,906.95 ms) = **3,959.71 ms**, accounting for the reported 3,959.70 ms total successful latency.
2. **Inconclusive Status of C2, C3, and C4 Generations:**
   - Because all calls in C2, C3, and C4 aborted due to HTTP 429 quota exhaustion, cross-configuration generation comparisons are **inconclusive**.
   - **C2 cannot be claimed to produce superior end-to-end answers in production.** It is the observed **retrieval MRR leader**, but end-to-end generation superiority is unproven.

---

## 2. Failure Case Studies Across the RAG Lifecycle

1. **Chunking Boundary Severance (`q10` — Penal Charges Proviso):**
   - *Problem:* Fixed-size chunking cleaved the primary rule on reasonable penal charges from its trailing proviso prohibiting penal charges from exceeding non-individual borrower rates.
   - *Resolution:* Hierarchical Section-Aware chunking groups operative clauses and provisos under the unified section heading, ensuring complete legal context is supplied to the LLM.
2. **Dense Semantic Conflation (`q26` — Failed E-Commerce TAT Compensation):**
   - *Problem:* Dense retrieval conflated ATM cash withdrawal auto-reversals ($T+5$) with e-commerce card-not-present transaction failures ($T+1$) due to shared vocabulary (*"failed transaction"*, *"auto-reversal"*, *"compensation"*).
   - *Resolution:* Lexical BM25 specifically matched the unique token `"e-commerce"`, allowing RRF fusion to promote the correct $T+1$ passage from `DPSS.CO.PD No.629` to Rank 1.
3. **Complex Tabular Parsing (`q20` — Payment Aggregator Net Worth Milestones):**
   - *Problem:* Tabular net-worth schedules (₹15 crore at time of application rising to ₹25 crore by end of third financial year) collapsed into linear text runs during basic PDF extraction, obscuring timeline milestones.
   - *Resolution:* Integrated PyMuPDF structured table extraction into Markdown pipe-delimited tables, preserving column relationships and net-worth milestones.
4. **Adversarial Jailbreak Detection (`q46`):**
   - *Problem:* Prompt injection attempt (`q46`) seeking to force the pipeline to confirm 100% FLDG guarantees and ignore system rules.
   - *Resolution:* Pre-generation deterministic compliance guardrail intercepted the query locally, emitting `REFUSAL: This request attempts to bypass regulatory compliance guardrails...` without requiring cloud LLM dispatch.

---

## 3. Handling Outdated & Superseded Circulars: Bi-Temporal Governance

In financial regulation, citing superseded circulars creates critical compliance liabilities. FinReg AI implements **clause-level bi-temporal metadata governance**:

### The 2025 Regulatory Baseline
On **May 8, 2025**, the RBI issued the **Reserve Bank of India (Digital Lending) Directions, 2025** (`RBI_DL_2025`, Notification `DOR.CRE.REC.14/21.07.001/2025-26`). These Directions consolidated and superseded earlier guidelines, with staggered commencement dates:
- **General Provisions:** Effective immediately on May 8, 2025.
- **Paragraph 17 (RE-LSP / DLF Agreement Requirements):** Effective **June 15, 2025** (existing DLFs permitted until June 14, 2025).
- **Paragraph 6 (Comprehensive Credit Assessment & Limits):** Effective **November 1, 2025** (existing arrangements permitted until October 31, 2025).

### Staggered Commencement & Clause-Level Supersession
Earlier guidelines are handled with precise temporal routing:
- **2022 Guidelines (`DOR.CRE.REC.66/21.07.001/2022-23`):** Clause 15 (First Loss Default Guarantee) was superseded on **June 8, 2023** by the DLG Circular (`DOR.STR.REC.20/21.04.048/2023-24`), which introduced the 5% DLG cap. However, surviving clauses of the 2022 guidelines remained active until repealed on May 8, 2025.
- **Bi-Temporal Routing:** Every chunk carries `valid_from`, `valid_to`, `superseded_by`, and `supersedes`.
- **Date-Aware Filtering:**
  - Queries specifying a date prior to June 1, 2023 retrieve the 2022 guidelines (where FLDG was prohibited under synthetic securitisation rules).
  - Queries referencing the 2023–2024 regime retrieve the 2023 circular (5% DLG cap) alongside surviving 2022 operational clauses.
  - Queries targeting "current" regulations retrieve the 2025 Directions, citing Paragraph 8 for KFS disclosures, Paragraph 9 for direct borrower bank account disbursals, and Paragraph 10 for cooling-off rights.
  - Ambiguous transition queries (e.g., "June 2025") trigger explicit transition period analysis separating pre-June 15 rules from post-June 15 requirements.

---

## 4. Evidence Gate Architecture & Refusal Formulations

The evidence gate in `src/generation/rag_engine.py` operates in a **retrieval-mode aware** manner:

1. **Threshold Configurations (`src/config.py`):**
   - `DENSE_REFUSAL_THRESHOLD = 0.40`: Cosine similarity threshold for BGE-small embeddings. Below 0.40 indicates out-of-scope content.
   - `BM25_REFUSAL_THRESHOLD = 1.5`: Lexical relevance threshold for keyword search.
   - `HYBRID_RRF_MIN_SCORE = 0.010`: Minimum combined RRF score.
2. **Mode-Aware Gating Logic:**
   - In **Dense-Only mode**, chunks with score $< 0.40$ are refused immediately.
   - In **Hybrid mode**, the gate checks the underlying modalities via `_fusion_meta`. It refuses only if **both** dense ($< 0.40$) and BM25 ($< 1.5$) are weak, or if the top fused RRF score is $< 0.010$. This prevents false refusals on valid hybrid matches.
3. **Decoupled Evaluation Metrics:**
   $$CRR = \frac{\text{Genuine Policy Refusals on Negative Questions}}{15}$$
   $$FRR = \frac{\text{Genuine Policy Refusals on Answerable Questions}}{35}$$
   $$AQC = \frac{\text{Successful Answers on Answerable Questions}}{35}$$
   $$AQC \neq 1 - FRR$$
   Execution failures (HTTP 429) reduce $AQC$ without corrupting policy refusal metrics ($CRR$, $FRR$).

---

## 5. Document Provenance & Question 23 Resolution

1. **Root Cause of `q23` Gap in Baseline:**
   Query `q23` asked for the 24-hour advance pre-debit notification requirement for recurring e-mandates. The original 12-doc corpus contained only `RBI_EMANDATE_2020` (`RBI/2020-21/74`), which amended transaction limits from ₹2,000 to ₹5,000 without repeating the 24-hour notification rule. The provision was enacted in the 2019 parent circular.
2. **Document Acquisition & Provenance:**
   - Circular: `RBI/2019-20/47 DPSS.CO.PD.No.447/02.14.003/2019-20` (August 21, 2019, 4 pages).
   - Source: The official RBI HTML notification page (`https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11668&Mode=0`).
   - Derivative Note: RBI's direct PDF endpoint (`rbidocs.rbi.org.in`) presented an automated anti-bot CAPTCHA block. The local PDF `data/raw_documents/RBI_EMANDATE_2019.pdf` is an **authentic archival PDF rendered from official RBI HTML notification text**. It is not the original RBI-downloaded PDF file.
   - Operative Provision: Annexure, Paragraph 8 (Page 3).
3. **Validation Result:**
   Following ingestion, `q23` retrieved at **Rank 1 across all four configurations (C1, C2, C3, C4)**.

---

## 6. Full-Stack Web Platform Architecture

FinReg AI is deployed as a unified enterprise compliance platform:
- **Backend:** FastAPI REST API providing endpoints for retrieval, generation, document metadata, timeline diffs, compliance checklists, and audit memos.
- **Frontend:** React 18 Single Page Application built with Vite and Tailwind CSS.
- **8 Dedicated Workspaces:**
  1. **Overview Dashboard:** Regulatory corpus statistics, active vs. superseded ratio, transition milestones.
  2. **Regulatory Database:** Split-screen document explorer streaming RBI PDFs in-browser.
  3. **Timeline & Monitors:** Tri-temporal milestone scrubber, side-by-side clause diffs.
  4. **Compliance Copilot:** Context-grounded Q&A with configuration switcher (C1–C4), Top-K slider, verified citations.
  5. **Compliance Matrix:** Regulated Entity (RE) vs. LSP statutory obligation checklist.
  6. **Risk Evaluator:** Scenario calculator analyzing DLG caps, penal interest, and TAT penalties.
  7. **Dependency Graph:** Visual node-link network illustrating circular repeals and amendments.
  8. **Empirical Benchmark:** Interactive viewer for Phase C benchmark metrics and latency splits.
- **Authentication & RBAC Disclosure:**
  The platform includes an executive role-based sign-in interface with 3 profiles:
  - *Andrew:* Lead Compliance Officer (Full Administrator, 8/8 workspaces)
  - *Priya Sharma:* Senior Regulatory Risk Auditor (5/8 workspaces)
  - *Vikram Mehta:* Head of Legal & Banking Governance (5/8 workspaces)
  *Disclaimer:* Authentication and RBAC are implemented as a **client-side compliance-cockpit evaluation and demonstration prototype**, designed to demonstrate role-segregated statutory workflows for assessment evaluation. It is not backed by server-side OAuth2 or enterprise SSO infrastructure.

---

## 7. Audit & File References
- Master Benchmark Report (12 Docs): [phase_c_benchmark_report.md](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/phase_c_benchmark_report.md)
- Executive Summary: [phase_c_executive_summary.md](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/phase_c_executive_summary.md)
- Priority 1 Validation Report: [q23_corpus_correction_validation.md](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/q23_corpus_correction_validation.md)
- Audited Results Table: [results_table.csv](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/results_table.csv)
- Raw 200 Evaluation Records: [phase_c_detailed_results.csv](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/evaluation/phase_c_detailed_results.csv)
- Regression Test Suite (71 Tests): [tests/](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/tests/)
