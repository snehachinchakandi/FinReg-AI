# FinReg AI: Deep-Dive Failure Analysis
*Prepared for Dvara Group Task 6 RAG Pipeline Evaluation*

This report investigates three concrete failure cases observed during pipeline experimentation, tracing each error to its precise failure stage across the RAG lifecycle: **Parsing**, **Chunking**, **Retrieval**, and **Generation**.

---

### Failure Case 1: Chunk Boundary Truncation (Chunking Stage)
- **Question (q10):** *"Can higher penal charges be levied on individual borrowers compared to non-individual borrowers?"*
- **Golden Regulatory Provision:** RBI Circular RBI/2023-24/53 (Aug 18, 2023), Clause 3(b):
  > *"The quantum of penal charges shall be reasonable and commensurate with the non-compliance... The penal charges on loans to individual borrowers, for purposes other than business, shall not be higher than the penal charges applicable to non-individual borrowers for similar non-compliance."*
- **Observed Failure in Configuration C1 (Fixed-Size + Dense):**
  - The pipeline retrieved a chunk that contained the opening sentence of Clause 3(b) concerning "reasonable quantum", but the 512-token fixed sliding window severed the second sentence containing the explicit comparison between individual and non-individual borrowers.
  - As a result, the LLM answered: *"Penal charges must be reasonable and proportional to non-compliance,"* failing to state the core restriction that individual charges cannot exceed non-individual charges.
- **Root Cause & Stage:** **Chunking Boundary Severance**. Legal regulations often place the operative exception or comparative constraint immediately following a general principle. Arbitrary word/token slicing detaches the condition from the rule.
- **Resolution in C3/C4 (Section-Aware Chunking):** The Section-Aware chunker treats Clause 3(b) as a single semantic entity, preserving the qualification intact. Hit rate and answer correctness for q10 reached 1.0 in C4.

---

### Failure Case 2: Lexical Density & Acronym Confusion (Retrieval Stage)
- **Question (q26):** *"What is the Turn Around Time (TAT) for reversal of a failed merchant transaction where account was debited but merchant did not confirm confirmation (e-commerce)?"*
- **Golden Regulatory Provision:** RBI Circular DPSS.CO.PD No.629 (Sept 20, 2019), Harmonisation of TAT Table, Item IV:
  > *"Card Not Present (CNP) - e-commerce: Account debited but confirmation not received at merchant's end. Auto-reversal within T + 1 day; ₹100/day compensation beyond T+1."*
- **Observed Failure in Configurations C1 and C3 (Dense-Only):**
  - The dense retriever (`bge-small-en-v1.5`) mapped all rows of the failed transaction table to almost identical semantic vector representations because every row contains nearly identical phraseology: *"failed transaction", "account debited", "auto-reversal", "compensation of ₹100 per day"*.
  - Consequently, the dense retriever returned Item I (ATM cash withdrawal, $T+5$ days) as Rank 1 instead of Item IV (CNP/e-commerce, $T+1$ day). The generated answer erroneously cited a 5-day TAT.
- **Root Cause & Stage:** **Dense Retrieval Granularity Failure**. Dense bi-encoders struggle with semantic saturation when multiple distinct tabular rules differ by only one or two exact keywords (e.g. "ATM" vs. "PoS" vs. "e-commerce").
- **Resolution in C2/C4 (Hybrid RRF):** The BM25 keyword component specifically scored the exact terms `"e-commerce"` and `"merchant confirmation"`, ranking Item IV at Rank 1 in sparse search. Reciprocal Rank Fusion promoted the correct passage to Rank 1 overall, correctly generating $T+1$ day.

---

### Failure Case 3: Table Layout Collapse (Parsing Stage)
- **Question (q20):** *"What is the minimum net worth required for non-bank Payment Aggregators (PAs) at the time of application?"*
- **Golden Regulatory Provision:** RBI Guidelines on Payment Aggregators (March 17, 2020), Section 4.1:
  > *"Existing non-bank PAs shall achieve a net-worth of ₹15 crore by March 31, 2021 and ₹25 crore by March 31, 2023. New PAs shall have a minimum net-worth of ₹15 crore at the time of application."*
- **Observed Failure in Early Ingestion:**
  - Standard linear PDF text stream extraction intermingled the table cells of existing entities with new applicant columns: *"Existing PAs ₹15 crore new PAs ₹25 crore March 31 2023"*.
  - The generator incorrectly answered that new PAs require ₹25 crore at the time of application.
- **Root Cause & Stage:** **PDF Table Layout Flattening**. RBI documents heavily utilize tabular matrices for capital adequacy and implementation timelines. Naive line-by-line reading collapses column alignments into meaningless sequences.
- **Resolution:** Upgraded `pdf_parser.py` using PyMuPDF's table extraction API (`page.find_tables()`) which converts tables into clean Markdown tables with explicit column headers before chunking.
