# Priority 1: Missing 2019 RBI e-Mandate Circular Ingestion & q23 Retrieval Validation Report

**Status:** Completed & Fully Validated  
**Mode:** Controlled Scope Implementation (Corpus Ingestion & Retrieval Verification)  
**Date:** 2026-11-14  

---

## 1. Executive Summary & Resolution of Issue 1 (q23 Attribution)

During the technical audit and reconciliation, **Query 23 (`q23`)** was identified as suffering from an authentic corpus coverage gap:
- **Query 23:** *"How much advance notification must be sent to cardholders prior to the debit of a recurring e-mandate transaction?"*
- **Golden Answer:** *"The issuer must send a pre-transaction notification to the cardholder at least 24 hours before the recurring debit occurs."*
- **Root Cause:** The 24-hour advance notification mandate was originally enacted by the RBI on **August 21, 2019** under circular **`DPSS.CO.PD.No.447/02.14.003/2019-20`** (Annexure Paragraph 8). The repository previously only contained the subsequent amendment circular `RBI/2020-21/74 DPSS.CO.PD No.754/02.14.003/2020-21` (`RBI_EMANDATE_2020`), which primarily enhanced the transaction limit cap from ₹2,000 to ₹5,000 without repeating the 24-hour notification provision.

Rather than reclassifying `q23` as unanswerable and altering the 50-question evaluation design (35 answerable, 10 unanswerable, 5 adversarial), we executed **Priority 1**:
1. Ingested the authentic parent circular `DPSS.CO.PD.No.447/02.14.003/2019-20` (`RBI_EMANDATE_2019`).
2. Cataloged the document in `data/metadata/documents_metadata.json` and parsed it into `data/processed_documents/RBI_EMANDATE_2019.json`.
3. Updated `evaluation/eval_dataset.jsonl` Line 23 to attribute the ground truth to `RBI_EMANDATE_2019`, Clause `Para 8`, Page 3.
4. Regenerated chunks using both strategies (Fixed-Size: 400 words / 75-word overlap; Section-Aware: 100–600 words) and rebuilt both FAISS dense and BM25 indices.
5. Validated `q23` retrieval across all four RAG configurations (**C1, C2, C3, C4**).
6. Ran the complete 71-test regression suite with 100% pass rate.
7. Strictly protected the baseline benchmark files (`evaluation/phase_c_detailed_results.csv` and `reports/results_table.csv`).

---

## 2. Authentic Regulatory Document Ingestion Record

| Attribute | Specification |
| :--- | :--- |
| **Document Identifier** | `RBI_EMANDATE_2019` |
| **Title** | Processing of e-mandate on cards for recurring transactions |
| **Circular Reference Number** | `RBI/2019-20/47 DPSS.CO.PD.No.447/02.14.003/2019-20` |
| **Issuing Authority** | Reserve Bank of India (Department of Payment and Settlement Systems) |
| **Publish Date** | 2019-08-21 |
| **Effective Date** | 2019-09-01 |
| **Statutory Authority** | Section 10 (2) read with Section 18 of Payment and Settlement Systems Act, 2007 (Act 51 of 2007) |
| **Primary Source URL** | `https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11668&Mode=0` |
| **Direct RBI Doc ID** | `47EMANDATE39D1306C26AE4B44B2EA0050F23E7E3D.PDF` |
| **Physical PDF File** | [data/raw_documents/RBI_EMANDATE_2019.pdf](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/data/raw_documents/RBI_EMANDATE_2019.pdf) |
| **Physical Pages** | 4 pages |
| **Extracted Character Count** | 9,130 characters |
| **Statutory Anchor (q23)** | **Annexure, Paragraph 8 (Page 3)** |

### Exact Statutory Text (Annexure, Paragraph 8):
> *"8. As a risk mitigant and customer facilitation measure, the issuer shall send a pre-transaction notification to the cardholder, at least 24 hours prior to the actual charge / debit to the card. While registering e-mandate on the card, the cardholder shall be given facility to choose a mode among available options (SMS, email, etc.) for receiving the pre-transaction notification from the issuer in a clear, unambiguous manner and in an understandable language. The facility for changing this mode of receiving pre-transaction notification, shall also be provided to the cardholder."*

---

## 3. Corpus Transition Matrix

The addition of `RBI_EMANDATE_2019` expands the corpus while strictly complying with the assignment requirement of 10–15 regulatory documents totaling $\ge 100$ pages.

| Metric | Prior State (12 Docs) | Post-Ingestion State (13 Docs) | Net Delta |
| :--- | :---: | :---: | :---: |
| **Total Ingested Documents** | 12 documents | **13 documents** | +1 document |
| **Active Documents** | 10 documents | **11 documents** | +1 document |
| **Superseded Documents** | 2 documents (`RBI_DL_2022`, `RBI_DLG_2023`) | 2 documents | 0 |
| **Physical PDF Pages** | 341 pages | **345 pages** | +4 pages |
| **Fixed-Size Chunks (400w / 75o)** | 216 chunks | **220 chunks** | +4 chunks |
| **Section-Aware Chunks (100–600w)** | 330 chunks | **341 chunks** | +11 chunks |
| **Dense Vector Index Dimension** | 384 (`BAAI/bge-small-en-v1.5`) | 384 | Unchanged |
| **Dense Index Size (Fixed)** | 216 vectors | **220 vectors** | +4 vectors |
| **Dense Index Size (Section)** | 330 vectors | **341 vectors** | +11 vectors |
| **BM25 Inverted Index (Fixed)** | 216 documents | **220 documents** | +4 documents |
| **BM25 Inverted Index (Section)** | 330 documents | **341 documents** | +11 documents |

---

## 4. Evaluation Dataset Reconciliation

In [evaluation/eval_dataset.jsonl](file:///C:/Users/sneha/.gemini/antigravity/scratch/FinReg-AI/evaluation/eval_dataset.jsonl), only **Line 23 (`id: "q23"`)** was updated. All other 49 benchmark questions remained completely untouched:

```json
{
  "id": "q23",
  "category": "answerable",
  "doc_id": "RBI_EMANDATE_2019",
  "clause": "Para 8",
  "page": 3,
  "question": "How much advance notification must be sent to cardholders prior to the debit of a recurring e-mandate transaction?",
  "golden_passages": [
    "A pre-transaction notification shall be sent to the cardholder at least 24 hours prior to the actual charge/debit."
  ],
  "golden_answer": "The issuer must send a pre-transaction notification to the cardholder at least 24 hours before the recurring debit occurs."
}
```

---

## 5. Query 23 Retrieval Validation across All 4 Configurations

With the re-indexed vector and keyword indices, `q23` was evaluated independently across configurations C1, C2, C3, and C4 at Top-$K=5$:

| Config ID | Configuration Name | Chunking Strategy | Retrieval Engine | Rank of Golden Chunk | Reciprocal Rank (RR) | Hit@1 | Hit@5 | Golden Passage Overlap | Top Retrieved Document |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **C1** | Fixed + Dense | Fixed (400w / 75o) | BGE Dense (FAISS) | **1** | **1.0000** | 1.0 | 1.0 | **1.0000** | `RBI_EMANDATE_2019` |
| **C2** | Fixed + Hybrid RRF | Fixed (400w / 75o) | Dense + BM25 (RRF $k=60$) | **1** | **1.0000** | 1.0 | 1.0 | **1.0000** | `RBI_EMANDATE_2019` |
| **C3** | Section + Dense | Section-Aware | BGE Dense (FAISS) | **1** | **1.0000** | 1.0 | 1.0 | **0.9231** | `RBI_EMANDATE_2019` |
| **C4** | Section + Hybrid RRF | Section-Aware | Dense + BM25 (RRF $k=60$) | **1** | **1.0000** | 1.0 | 1.0 | **0.9231** | `RBI_EMANDATE_2019` |

### Detailed Top-5 Evidence Traces for q23:

#### C1: Fixed-Size Chunks + Dense Retrieval
- **Rank 1 (Score: 0.8318):** `RBI_EMANDATE_2019`, Overlap: **1.0000** (Full unigram match: includes *"issuer shall send a pre-transaction notification to the cardholder, at least 24 hours prior to the actual charge / debit"*)
- **Rank 2 (Score: 0.7997):** `RBI_EMANDATE_2019`, Overlap: 0.6154 (Pre-transaction notification parameters)
- **Rank 3 (Score: 0.7799):** `RBI_EMANDATE_2019`, Overlap: 0.4615 (Recurring transactions scope)
- **Rank 4 (Score: 0.7552):** `RBI_EMANDATE_2019`, Overlap: 0.3846 (Introductory authority)
- **Rank 5 (Score: 0.7458):** `RBI_EMANDATE_2020`, Overlap: 0.2308 (2020 amendment circular)

#### C2: Fixed-Size Chunks + Hybrid RRF Retrieval
- **Rank 1 (Score: 0.0328):** `RBI_EMANDATE_2019`, Overlap: **1.0000** (Full statutory provision)
- **Rank 2 (Score: 0.0323):** `RBI_EMANDATE_2019`, Overlap: 0.6154
- **Rank 3 (Score: 0.0315):** `RBI_EMANDATE_2019`, Overlap: 0.4615
- **Rank 4 (Score: 0.0315):** `RBI_EMANDATE_2019`, Overlap: 0.3846
- **Rank 5 (Score: 0.0305):** `RBI_PPI_MD_2021`, Overlap: 0.3846

#### C3: Section-Aware Chunks + Dense Retrieval
- **Rank 1 (Score: 0.8605):** `RBI_EMANDATE_2019`, Clause: `Para 7-8` (Section: Pre-transaction notification), Overlap: **0.9231**
- **Rank 2 (Score: 0.8434):** `RBI_EMANDATE_2019`, Clause: `Para 11` (Post-transaction alert), Overlap: 0.4615
- **Rank 3 (Score: 0.8160):** `RBI_EMANDATE_2019`, Clause: `Para 9` (Notification contents), Overlap: 0.6154
- **Rank 4 (Score: 0.8092):** `RBI_EMANDATE_2019`, Clause: `Para 15` (Withdrawal provisions), Overlap: 0.6154
- **Rank 5 (Score: 0.7992):** `RBI_EMANDATE_2019`, Clause: `Para 5` (AFA modification), Overlap: 0.2308

#### C4: Section-Aware Chunks + Hybrid RRF Retrieval
- **Rank 1 (Score: 0.0323):** `RBI_EMANDATE_2019`, Clause: `Para 7-8`, Overlap: **0.9231**
- **Rank 2 (Score: 0.0323):** `RBI_EMANDATE_2019`, Clause: `Para 9`, Overlap: 0.6154
- **Rank 3 (Score: 0.0318):** `RBI_EMANDATE_2019`, Clause: `Para 11`, Overlap: 0.4615
- **Rank 4 (Score: 0.0318):** `RBI_EMANDATE_2019`, Clause: `Para 15`, Overlap: 0.6154
- **Rank 5 (Score: 0.0303):** `RBI_EMANDATE_2019`, Clause: `Preamble`, Overlap: 0.3077

---

## 6. Updated 35-Answerable Retrieval Benchmark Summary

Evaluating the 35 answerable benchmark questions against the updated 13-document corpus reveals that **C2 (Fixed-Size + Hybrid RRF)** achieves the highest observed retrieval MRR and Rank-1 hit rate:

| Configuration ID | Configuration Name | Hit Rate@1 | Hit Rate@3 | Hit Rate@5 | Mean Reciprocal Rank (MRR) | Rank-1 Hits / Total |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **C1** | Fixed-Size + Dense | 82.86% | 100.00% | 100.00% | **0.9143** | 29 / 35 |
| **C2** | **Fixed-Size + Hybrid RRF** | **94.29%** | **100.00%** | **100.00%** | **0.9714** | **33 / 35** |
| **C3** | Section-Aware + Dense | 80.00% | 100.00% | 100.00% | **0.8952** | 28 / 35 |
| **C4** | Section-Aware + Hybrid RRF | 85.71% | 94.29% | 100.00% | **0.9129** | 30 / 35 |

### Key Benchmark Observations:
1. **Resolution of q23 Rank-1 Hit:** With `RBI_EMANDATE_2019` in place, `q23` immediately succeeds at Rank 1 across all 4 configurations, lifting C2's Rank-1 hits from 32/35 to **33/35** ($94.29\%$).
2. **C2 MRR Leadership Reconfirmed:** C2 exhibits the highest retrieval MRR (**0.9714**), outperforming C4 (**0.9129**), C1 (**0.9143**), and C3 (**0.8952**).
3. **100% Hit Rate@5:** In both C1 and C2, every single one of the 35 answerable questions retrieved its ground-truth passage within the top 5 candidates.

---

## 7. Baseline Benchmark Protection Verification

In strict adherence to the evaluation protocol:
- **`evaluation/phase_c_detailed_results.csv` (200 records):** **Untouched.** Preserves the authentic Phase C benchmark run.
- **`reports/results_table.csv`:** **Untouched.** Preserves the historical benchmark table.
- **LLM API Quota:** **0 API calls consumed.** No 200-query Gemini generation benchmark was executed.

---

## 8. Regression Suite Verification

The full pytest test suite was executed across all testing modules:
```
tests/test_api_extensions.py       19 passed
tests/test_chunking.py              2 passed
tests/test_phase_a.py              16 passed
tests/test_refusal.py               2 passed
tests/test_superseded.py           32 passed
------------------------------------------------
TOTAL                              71 passed in 18.37s (100% PASS RATE)
```
All temporal versioning, staggered commencement, date simulation, evidence gating, and router extension tests continue to pass without errors or regressions.
