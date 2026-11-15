"""
Master Execution Pipeline for FinReg AI.
Orchestrates end-to-end ingestion, chunking, indexing, evaluation, and reporting.
"""

import sys
import json
import time
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from src.config import (
    RAW_DOCS_DIR,
    PROCESSED_DOCS_DIR,
    METADATA_FILE,
    FIXED_CHUNKS_FILE,
    SECTION_CHUNKS_FILE,
    INDEXES_DIR,
    RESULTS_TABLE_FILE,
    REPORTS_DIR
)
from src.ingestion.pdf_parser import RegulatoryPDFParser
from src.chunking.fixed_chunker import FixedSizeChunker
from src.chunking.section_chunker import SectionAwareChunker
from src.retrieval.dense import DenseRetriever
from src.retrieval.bm25 import BM25Retriever
from src.generation.rag_engine import FinRegRAGEngine
from src.evaluation.evaluator import BenchmarkEvaluator

def run_all():
    print("==================================================")
    print("   FinReg AI: Master RAG Pipeline Orchestrator    ")
    print("==================================================\n")

    # Step 1: Corpus Verification
    print(">>> STEP 1: Corpus Verification...")
    if METADATA_FILE.exists() and len(list(RAW_DOCS_DIR.glob("*.pdf"))) >= 10:
        print(f"Authentic corpus already compiled with {len(list(RAW_DOCS_DIR.glob('*.pdf')))} documents.")
    else:
        from src.ingestion.fetch_authentic_rbi_docs import fetch_and_build_corpus
        fetch_and_build_corpus()

    # Step 2: Parse PDFs into structured JSON
    print("\n>>> STEP 2: PDF Extraction (PyMuPDF)...")
    parser = RegulatoryPDFParser(remove_headers_footers=True)
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        doc_registry = json.load(f)

    parsed_docs = []
    total_pages = 0
    for doc_meta in doc_registry:
        pdf_path = Path(doc_meta["local_path"])
        if pdf_path.exists() and pdf_path.stat().st_size > 1000:
            print(f"Parsing: {doc_meta['title']} ({doc_meta['doc_id']})...")
            parsed = parser.parse_pdf(str(pdf_path), doc_meta)
            out_file = PROCESSED_DOCS_DIR / f"{doc_meta['doc_id']}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2, ensure_ascii=False)
            parsed_docs.append(parsed)
            total_pages += parsed["total_pages"]
        else:
            print(f"Skipping {doc_meta['doc_id']} (file missing or corrupt)")

    print(f"Successfully parsed {len(parsed_docs)} documents totaling {total_pages} pages.")

    # Step 3: Chunking documents with both strategies
    print("\n>>> STEP 3: Document Chunking (Fixed-Size vs. Section-Aware)...")
    fixed_chunker = FixedSizeChunker(chunk_size_words=400, overlap_words=75)
    section_chunker = SectionAwareChunker(min_words=100, max_words=600)

    all_fixed_chunks = []
    all_section_chunks = []

    for doc in parsed_docs:
        f_chunks = fixed_chunker.chunk_document(doc)
        s_chunks = section_chunker.chunk_document(doc)
        all_fixed_chunks.extend([c.to_dict() for c in f_chunks])
        all_section_chunks.extend([c.to_dict() for c in s_chunks])

    with open(FIXED_CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_fixed_chunks, f, indent=2, ensure_ascii=False)
    with open(SECTION_CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_section_chunks, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(all_fixed_chunks)} Fixed-Size chunks -> {FIXED_CHUNKS_FILE.name}")
    print(f"Generated {len(all_section_chunks)} Section-Aware chunks -> {SECTION_CHUNKS_FILE.name}")

    # Step 4: Indexing (Dense FAISS + BM25)
    print("\n>>> STEP 4: Vector & Keyword Index Construction...")
    # Fixed chunks indexes
    print("\nBuilding Fixed-Size Indexes...")
    fixed_dense = DenseRetriever()
    fixed_dense.build_index(all_fixed_chunks)
    fixed_dense.save(
        str(INDEXES_DIR / "fixed_dense.faiss"),
        str(INDEXES_DIR / "fixed_chunks_index.json")
    )

    fixed_bm25 = BM25Retriever()
    fixed_bm25.build_index(all_fixed_chunks)
    fixed_bm25.save(
        str(INDEXES_DIR / "fixed_bm25.pkl"),
        str(INDEXES_DIR / "fixed_bm25_chunks.json")
    )

    # Section chunks indexes
    print("\nBuilding Section-Aware Indexes...")
    section_dense = DenseRetriever()
    section_dense.build_index(all_section_chunks)
    section_dense.save(
        str(INDEXES_DIR / "section_dense.faiss"),
        str(INDEXES_DIR / "section_chunks_index.json")
    )

    section_bm25 = BM25Retriever()
    section_bm25.build_index(all_section_chunks)
    section_bm25.save(
        str(INDEXES_DIR / "section_bm25.pkl"),
        str(INDEXES_DIR / "section_bm25_chunks.json")
    )

    # Step 5: Evaluation
    print("\n>>> STEP 5: 50-Question Benchmark Evaluation across 4 Configurations...")
    rag_engine = FinRegRAGEngine()
    evaluator = BenchmarkEvaluator()
    results_df = evaluator.run_all_configurations(
        fixed_dense=fixed_dense,
        fixed_bm25=fixed_bm25,
        section_dense=section_dense,
        section_bm25=section_bm25,
        rag_engine=rag_engine
    )

    print("\n>>> FINAL RESULTS SUMMARY:")
    print(results_df.to_string(index=False))

    print("\n==================================================")
    print("   FinReg AI Pipeline Run Completed Successfully! ")
    print(f"   Results table: {RESULTS_TABLE_FILE}")
    print("==================================================")

if __name__ == "__main__":
    run_all()
