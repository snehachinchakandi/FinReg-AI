# FinReg AI: Intelligent RAG-Based Indian Financial Regulation Assistant
*Submission for Dvara Group AI/ML & Generative AI Internship Evaluation (Task 6 — RAG Pipeline)*

---

## 🌟 Executive Overview
**FinReg AI** is a document-grounded Retrieval-Augmented Generation (RAG) system specialized in Indian digital payments and lending regulations issued by the **Reserve Bank of India (RBI)**.

The system addresses regulatory complexity, multi-page legal circulars, complex tables, strict clause-level citations, unanswerable queries, adversarial prompt injections, and the critical challenge of **superseded / outdated circulars** using clause-level bi-temporal metadata governance.

```
========================================================================================
                          FINREG AI AUDITED SYSTEM SPECIFICATION
========================================================================================
 Current Corpus Inventory:   13 Authentic RBI Circulars & Master Directions (345 PDF Pages)
 Regulatory Status:          11 Current Active Regulations / 2 Superseded Regimes Preserved
 Chunking Strategies:        Strategy A: Fixed-Size (400 words / 75-word overlap, 220 chunks)
                             Strategy B: Section-Aware Hierarchical Chunker (341 chunks)
 Embedding Model:            BAAI/bge-small-en-v1.5 (384-dimensional dense vectors)
 Index Infrastructure:       FAISS (IndexFlatIP Cosine Similarity) + BM25 Okapi Sparse Index
 Hybrid Retrieval:           Reciprocal Rank Fusion (RRF, k=60) combining Dense + BM25 Ranks
 Evidence Sufficiency Gate:  Dense Cosine >= 0.40 | BM25 Score >= 1.5 | Hybrid RRF >= 0.010
 Evaluation Dataset:         50 Questions (35 Answerable, 10 Unanswerable, 5 Adversarial)
 Web Cockpit Architecture:   FastAPI REST Backend + React 18 SPA (8 Dedicated Workspaces)
 Regression Suite:           71 / 71 Tests Passing (100% Pass Rate in 18.4s)
========================================================================================
```

---

## 📊 Evaluation Benchmarks & Findings

To maintain strict academic integrity, FinReg AI explicitly distinguishes between the **Historical Phase C 200-Run Benchmark (12 Documents)** and the **Updated Retrieval-Only Evaluation (13 Documents)**.

### Table 1: Updated Retrieval-Only Benchmark (Current 13-Document Corpus)
Executed after ingesting the 2019 parent circular (`RBI_EMANDATE_2019`), resolving question `q23`. All 35 answerable questions evaluated across all 4 configurations:

| Config ID | Configuration | Chunking Strategy | Retrieval Strategy | Hit Rate@5 (n=35) | MRR (n=35) | Rank-1 Hits (n=35) | `q23` Rank | Retrieval Precision Status |
|:---:|---|---|---|:---:|:---:|:---:|:---:|:--- |
| **C1** | Fixed + Dense | Fixed (400w/75o) | Dense (FAISS FlatIP) | **1.0000** (35/35) | 0.9143 | 30 / 35 (85.71%) | Rank 1 | Fully Verified |
| **C2** | **Fixed + Hybrid** | **Fixed (400w/75o)** | **Hybrid (BM25 + RRF)** | **1.0000** (35/35) | **0.9714** | **33 / 35 (94.29%)** | **Rank 1** | **Observed Retrieval MRR Leader** |
| **C3** | Section + Dense | Section-Aware | Dense (FAISS FlatIP) | **1.0000** (35/35) | 0.8952 | 29 / 35 (82.86%) | Rank 1 | Fully Verified |
| **C4** | Section + Hybrid | Section-Aware | Hybrid (BM25 + RRF) | **1.0000** (35/35) | 0.9129 | 30 / 35 (85.71%) | Rank 1 | Fully Verified |

---

### Table 2: Historical Phase C Benchmark Baseline (Original 12-Document Corpus)
The historical 200-run benchmark (50 questions × 4 configurations) recorded in `reports/results_table.csv` and `evaluation/phase_c_detailed_results.csv`:

| Config ID | Configuration | Chunking | Retrieval | Hit Rate@5 (n=35) | MRR (n=35) | Rank-1 Hits | Live Gen (n=50) | Correctness (Completed) | Citation Acc. (Completed) | CRR (15 Neg) | FRR (35 Ans) | AQC (35 Ans) | Generation Status |
|:---:|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:--- |
| **C1** | Fixed + Dense | Fixed (400w/75o) | Dense | **0.9714** (34/35) | 0.8857 | 28 / 35 (80.00%) | **22** | **0.6823** (n=22) | **0.6364** (n=22) | 0.0667 (1/15)* | 0.1143 (4/35) | **0.5143** (18/35) | Partially Evaluated (22 live calls) |
| **C2** | **Fixed + Hybrid** | **Fixed (400w/75o)** | **Hybrid RRF** | **0.9714** (34/35) | **0.9429** | **32 / 35 (91.43%)** | 0 | **N/A** (0 calls) | **N/A** (0 calls) | 0.0667 (1/15)* | 0.0000 (0/35) | 0.0000 (0/35) | **Inconclusive (Quota Exhausted)** |
| **C3** | Section + Dense | Section-Aware | Dense | **0.9714** (34/35) | 0.8524 | 26 / 35 (74.29%) | 0 | **N/A** (0 calls) | **N/A** (0 calls) | 0.0667 (1/15)* | 0.0000 (0/35) | 0.0000 (0/35) | **Inconclusive (Quota Exhausted)** |
| **C4** | Section + Hybrid | Section-Aware | Hybrid RRF | **0.9714** (34/35) | 0.8843 | 29 / 35 (82.86%) | 0 | **N/A** (0 calls) | **N/A** (0 calls) | 0.0667 (1/15)* | 0.0000 (0/35) | 0.0000 (0/35) | **Inconclusive (Quota Exhausted)** |

*\*CRR Note: The 1/15 CRR represents solely the 1 adversarial query (`q46`) intercepted locally by compliance guardrails. The other 14 negative queries were unexecuted due to HTTP 429 quota exhaustion.*

### Critical Evaluation Takeaways & Scope Boundaries:
1. **Retrieval MRR Leader (Empirically Supported):** Configuration **C2 (Fixed + Hybrid RRF)** achieved the highest observed Mean Reciprocal Rank across both the historical baseline (**0.9429**) and the updated corpus (**0.9714**), placing the relevant statutory provision at Rank 1 in **33 of 35 answerable questions (94.29%)**.
2. **Generation Benchmark Limitation:** Due to external Gemini API rate-limiting (HTTP 429), only C1 completed live generations (22 calls). Cross-configuration generation quality across C2–C4 is **inconclusive**. **C2 cannot be claimed to produce superior end-to-end answers in production.**
3. **Question `q23` Resolution:** In the historical baseline, `q23` was missing because the 2020 circular was an amendment that omitted the parent 24-hour notification rule. Ingesting the authentic 2019 circular resolved this gap, bringing retrieval Hit Rate@5 to **100% (35/35)** across all 4 configurations.

---

## 🏛️ Authentic Regulatory Corpus (13 Documents, 345 Pages)

The corpus consists of **13 authentic RBI regulatory circulars and Master Directions** totaling **345 physical PDF pages**:

| # | Document ID | Circular Reference | Title & Subject | Date | Pages | Regulatory Status |
|:-:|---|---|---|:---:|:---:|:---:|
| 1 | `RBI_DL_2025` | `DOR.CRE.REC.14/21.07.001/2025-26` | Reserve Bank of India (Digital Lending) Directions, 2025 | 08-May-2025 | 17 | **Active Baseline** *(Staggered)* |
| 2 | `RBI_DL_2022` | `DOR.CRE.REC.66/21.07.001/2022-23` | Guidelines on Digital Lending | 02-Sep-2022 | 26 | **Superseded** *(Historical queries)* |
| 3 | `RBI_DLG_2023` | `DOR.STR.REC.20/21.04.048/2023-24` | Default Loss Guarantee (DLG) in Digital Lending | 08-Jun-2023 | 22 | **Superseded** *(2023–2025 regime)* |
| 4 | `RBI_PENAL_2023` | `RBI/2023-24/53` | Fair Lending Practice – Penal Charges in Loan Accounts | 18-Aug-2023 | 30 | **Active Baseline** |
| 5 | `RBI_PPI_MD_2021` | `DPSS.CO.PD.No.1415/02.14.006/2021-22` | Master Directions on Prepaid Payment Instruments (PPIs) | 27-Aug-2021 | 42 | **Active Baseline** |
| 6 | `RBI_PPI_CREDIT_2022` | `DPSS.CO.PD.No.S-257/02.14.006/2022-23` | Restriction on Loading Non-Bank PPIs via Credit Lines | 20-Jun-2022 | 40 | **Active Baseline** |
| 7 | `RBI_COFT_2021` | `RBI/2021-22/96` | Card-on-File Tokenisation (CoFT) – Scope Extension | 07-Sep-2021 | 23 | **Active Baseline** |
| 8 | `RBI_P2P_MD_2017` | `DNBR (PD) 054/03.10.119/2017-18` | Master Directions – NBFC – Peer to Peer (P2P) Platforms | 24-Aug-2017 | 41 | **Active Baseline** |
| 9 | `RBI_PA_PG_2020` | `DPSS.CO.PD.No.1810/02.14.008/2019-20` | Regulation of Payment Aggregators & Payment Gateways | 17-Mar-2020 | 29 | **Active Baseline** |
| 10 | `RBI_EMANDATE_2020` | `RBI/2020-21/74` | Framework for Processing of e-mandates (Limit Enhancement) | 04-Dec-2020 | 21 | **Active Baseline** |
| 11 | `RBI_IT_GOV_2023` | `RBI/2023-24/107` | Master Direction on IT Governance, Risk & Controls | 07-Nov-2023 | 28 | **Active Baseline** |
| 12 | `RBI_TAT_COMP_2019` | `DPSS.CO.PD No.629/02.01.014/2019-20` | Harmonisation of TAT & Customer Compensation | 20-Sep-2019 | 22 | **Active Baseline** |
| 13 | `RBI_EMANDATE_2019` | `RBI/2019-20/47` | Processing of e-mandate on cards for recurring transactions | 21-Aug-2019 | 4 | **Active Baseline** *(Annexure Para 8)* |

> **Document Provenance Disclosure (`RBI_EMANDATE_2019`):**  
> The statutory text of `RBI_EMANDATE_2019` was captured from the official RBI HTML notification (`https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11668&Mode=0`). Because RBI's raw PDF endpoint was gated by an automated anti-bot CAPTCHA block, the local PDF (`data/raw_documents/RBI_EMANDATE_2019.pdf`) is an **authentic archival PDF rendered from official RBI HTML notification text**. It is not the original RBI-downloaded PDF file.

---

## 📐 Ingestion & Dual Chunking Strategies

Every chunk strictly preserves metadata: `doc_title`, `circular_no`, `publish_date`, `section_heading`, `clause_no`, `page_no`, and temporal validity tags (`is_active`, `valid_from`, `valid_to`, `superseded_by`).
- **Strategy A: Fixed-Size with Overlap** (400 words with 75-word overlap). Produces **220 chunks** and **220 vectors** (384 dimensions) in `fixed_dense.faiss`.
- **Strategy B: Section-Heading & Clause-Aware Hierarchical Chunker** (respecting Chapters, Sections, Sub-clauses, Annexures). Produces **341 chunks** and **341 vectors** (384 dimensions) in `section_dense.faiss`.
- **Table Extraction:** PyMuPDF structured table extraction (`page.find_tables()`) converts tables into Markdown pipe-delimited tables, preserving capital adequacy schedules and TAT compensation columns.

---

## 🔍 Retrieval & Hybrid Ranking

- **Dense:** FAISS index using `BAAI/bge-small-en-v1.5` embeddings (384 dimensions, Inner Product / Cosine Similarity).
- **Keyword:** BM25 Okapi with domain-specific tokenization preserving banking acronyms (`LSP`, `RE`, `FLDG`, `DLG`, `KFS`, `APR`).
- **Hybrid Fusion:** Reciprocal Rank Fusion (RRF, $k=60$) combining dense and lexical ranks without scale calibration issues:
  $$RRF\_Score(d) = \sum_{m \in \{dense, bm25\}} \frac{1}{60 + \text{rank}_m(d)}$$

---

## 🛡️ Retrieval-Mode Aware Evidence Gate & Guardrails

The evidence gate in `src/generation/rag_engine.py` validates evidence before triggering generation:
1. **Thresholds (`src/config.py`):**
   - `DENSE_REFUSAL_THRESHOLD = 0.40`
   - `BM25_REFUSAL_THRESHOLD = 1.5`
   - `HYBRID_RRF_MIN_SCORE = 0.010`
2. **Mode-Aware Logic:**
   - In Dense-only mode, chunks with cosine score $< 0.40$ are refused immediately.
   - In Hybrid mode, the gate checks underlying component scores via `_fusion_meta`. It refuses only if **both** dense ($< 0.40$) and BM25 ($< 1.5$) are weak, or if the fused score is $< 0.010$. This prevents false refusals on valid low-score RRF ranks.
3. **Adversarial Guardrails:**
   - Pre-generation deterministic compliance guardrails intercept prompt injection attempts locally:
     `REFUSAL: This request attempts to bypass regulatory compliance guardrails...`
4. **Decoupled Metric Formulations:**
   - $CRR$ denominator is strictly 15 negative questions.
   - $FRR$ denominator is strictly 35 answerable questions.
   - $AQC$ independently measures answered coverage ($AQC \neq 1 - FRR$).

---

## 🔄 Bi-Temporal Metadata & Supersession Governance

- Chunks carry validity attributes: `is_active`, `valid_from`, `valid_to`, `superseded_by`, and `supersedes`.
- **May 8, 2025 Baseline:** The Master Directions on Digital Lending (`RBI_DL_2025`) repealed the 2022 guidelines and 2023 DLG circular.
- **Staggered Commencement Handling:**
  - General provisions: Active May 8, 2025.
  - Paragraph 17 (RE-LSP agreement requirements): Active June 15, 2025.
  - Paragraph 6 (Credit assessment & limits): Active November 1, 2025.
- **Date Simulation:** Queries targeting past regimes (e.g., pre-June 2023 FLDG prohibition under 2022 rules, June 2023–May 2025 5% DLG cap) accurately retrieve historical provisions.

---

## 🖥️ Full-Stack Web Platform (8 Workspaces)

FinReg AI includes an enterprise regulatory cockpit built with **FastAPI** (backend) and **React 18** (frontend):

1. **Overview Dashboard:** Regulatory corpus statistics (13 circulars, 345 pages), active vs. superseded ratio, and transition milestones.
2. **Regulatory Database:** Split-screen document explorer streaming official RBI PDFs directly in-browser.
3. **Timeline & Monitors:** Tri-temporal milestone scrubber and 3-column side-by-side clause diffs.
4. **Compliance Copilot:** Context-grounded Q&A with configuration switcher (C1–C4), Top-K slider, verified citations, in-situ PDF anchors, and refusal banners.
5. **Compliance Matrix:** Interactive statutory checklist comparing Regulated Entity (RE) vs. LSP obligations.
6. **Risk Evaluator:** Scenario calculator analyzing DLG 5% caps, penal charges vs compounding interest, and failed transaction TAT penalties.
7. **Dependency Graph:** Visual node-link network illustrating how circulars repeal, amend, and cross-reference earlier directions.
8. **Empirical Benchmark:** Interactive viewer displaying Phase C benchmark metrics, latency splits, and token accounting.

> **Authentication & RBAC Scope Disclosure:**  
> The web interface features an executive sign-in screen with 3 authorized role profiles:  
> • **Andrew:** Lead Compliance Officer (Full Administrator — 8/8 Workspaces)  
> • **Priya Sharma:** Senior Regulatory Risk Auditor (Audit & Risk — 5/8 Workspaces)  
> • **Vikram Mehta:** Head of Legal & Banking Governance (Legal & Policy — 5/8 Workspaces)  
> *Note:* Authentication and RBAC are implemented as an **interactive compliance-cockpit evaluation and demonstration prototype** designed for assessment walkthroughs. They are not backed by server-side OAuth2 or enterprise SSO infrastructure.

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- Python 3.12 (managed via `uv` or system Python)
- Node.js 18+ (for frontend client)
- Windows / macOS / Linux

### 2. Environment Activation & Dependencies
```bash
# Windows
.venv\Scripts\activate
# Unix/macOS: source .venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt
```

### 3. Configure API Key
Create `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Launch the Enterprise Web Cockpit (FastAPI + React SPA)
```bash
python run_platform.py
```
Open your browser to:
- **Cockpit UI:** `http://127.0.0.1:8000`
- **Interactive REST Swagger Docs:** `http://127.0.0.1:8000/docs`

### 5. Run Unit & Regression Tests (71 Passing Tests)
```bash
pytest tests/ -v
```

### 6. Create Submission Archive
```bash
python package_submission.py --usn <YOUR_USN>
```
Produces a clean `<USN>_Task6.zip` archive excluding virtual environments and cache directories.

---

## 📁 Key Project Files & Reports

- **Master Technical Architecture Report:** [reports/technical_report.md](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/technical_report.md)
- **Executive Summary:** [reports/phase_c_executive_summary.md](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/phase_c_executive_summary.md)
- **Priority 1 q23 Validation Report:** [reports/q23_corpus_correction_validation.md](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/q23_corpus_correction_validation.md)
- **Historical Benchmark Report (12 Docs):** [reports/phase_c_benchmark_report.md](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/phase_c_benchmark_report.md)
- **Historical Results Table (CSV):** [reports/results_table.csv](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/reports/results_table.csv)
- **Detailed 200 Evaluation Records:** [evaluation/phase_c_detailed_results.csv](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/evaluation/phase_c_detailed_results.csv)
- **Evaluation Dataset (50 Questions):** [evaluation/eval_dataset.jsonl](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/evaluation/eval_dataset.jsonl)
- **Platform Server:** [run_platform.py](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/run_platform.py)
