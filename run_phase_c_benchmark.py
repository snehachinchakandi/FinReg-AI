"""
Master Phase C Benchmark Execution Script for FinReg AI.
Executes the complete 50-question evaluation dataset across all 4 configurations:
  C1: Fixed-Size Chunking (512) + Dense Only (BGE-small-en-v1.5)
  C2: Fixed-Size Chunking (512) + Hybrid Retrieval (BGE-small + BM25 RRF)
  C3: Section-Aware Chunking (max 800) + Dense Only (BGE-small-en-v1.5)
  C4: Section-Aware Chunking (max 800) + Hybrid Retrieval (BGE-small + BM25 RRF)

Total Evaluations: 200 (50 questions x 4 configurations).
Uses live Gemini API with bounded retry policy (max 3 retries).
Exports:
  - evaluation/phase_c_detailed_results.csv
  - reports/results_table.csv
  - reports/eval_details_{config_id}.json
"""

import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import sys
import json
import time
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from src.config import (
    INDEXES_DIR,
    EVAL_DATASET_FILE,
    RESULTS_TABLE_FILE,
    REPORTS_DIR,
    GEMINI_API_KEY,
    GEMINI_MODEL_NAME
)
from src.retrieval.dense import DenseRetriever
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.hybrid import HybridRetriever
from src.generation.rag_engine import FinRegRAGEngine
from src.evaluation.metrics import (
    compute_hit_at_k,
    compute_reciprocal_rank,
    compute_citation_accuracy,
    compute_correct_refusal_rate,
    compute_false_refusal_rate,
    compute_answerable_coverage,
    compute_semantic_correctness,
    TOTAL_NEGATIVE_QUESTIONS,
    TOTAL_ANSWERABLE_QUESTIONS
)


def run_benchmark():
    print("=" * 70)
    print("      FinReg AI: Phase C Full 50-Question Benchmark (200 Runs)     ")
    print("=" * 70)

    # 1. Mandatory Pre-run verification of evaluation dataset
    print("\n>>> STEP 1: Pre-Run Dataset Verification...")
    if not EVAL_DATASET_FILE.exists():
        raise FileNotFoundError(f"Evaluation dataset missing: {EVAL_DATASET_FILE}")

    questions = []
    with open(EVAL_DATASET_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    assert len(questions) == 50, f"Expected 50 questions, found {len(questions)}"
    categories = {}
    q_ids = set()
    for q in questions:
        cat = q.get("category")
        categories[cat] = categories.get(cat, 0) + 1
        q_ids.add(q.get("id"))

    print(f"Total Questions: {len(questions)}")
    print(f"Categories: {categories}")
    print(f"Unique Question IDs: {len(q_ids)}")
    assert categories.get("answerable") == 35, f"Expected 35 answerable, got {categories.get('answerable')}"
    assert categories.get("unanswerable") == 10, f"Expected 10 unanswerable, got {categories.get('unanswerable')}"
    assert categories.get("adversarial") == 5, f"Expected 5 adversarial, got {categories.get('adversarial')}"
    assert len(q_ids) == 50, "Duplicate question IDs detected!"
    print("Pre-Run Dataset Verification: PASSED (35 answerable, 10 unanswerable, 5 adversarial).")

    # 2. Loading Phase B Pre-built Indexes
    print("\n>>> STEP 2: Loading Phase B Pre-Built Indexes...")
    print("Loading Fixed Dense index...")
    fixed_dense = DenseRetriever()
    fixed_dense.load(str(INDEXES_DIR / "fixed_dense.faiss"), str(INDEXES_DIR / "fixed_chunks_index.json"))

    print("Loading Fixed BM25 index...")
    fixed_bm25 = BM25Retriever()
    fixed_bm25.load(str(INDEXES_DIR / "fixed_bm25.pkl"), str(INDEXES_DIR / "fixed_bm25_chunks.json"))

    print("Loading Section Dense index...")
    section_dense = DenseRetriever()
    section_dense.load(str(INDEXES_DIR / "section_dense.faiss"), str(INDEXES_DIR / "section_chunks_index.json"))

    print("Loading Section BM25 index...")
    section_bm25 = BM25Retriever()
    section_bm25.load(str(INDEXES_DIR / "section_bm25.pkl"), str(INDEXES_DIR / "section_bm25_chunks.json"))

    print(f"Fixed Chunks: {len(fixed_dense.chunks)} | Section Chunks: {len(section_dense.chunks)}")

    # 3. Initializing Live Gemini Generation Engine
    print("\n>>> STEP 3: Initializing Live Gemini Generation Engine...")
    print(f"Configured Model: {GEMINI_MODEL_NAME}")
    assert GEMINI_API_KEY, "GEMINI_API_KEY is not set in environment or .env!"
    rag_engine = FinRegRAGEngine(api_key=GEMINI_API_KEY, model_name=GEMINI_MODEL_NAME)
    assert rag_engine.client is not None, "Failed to initialize live Gemini Client!"
    print("Live Gemini Client: INITIALIZED & READY.")

    # 4. Define C1-C4 Configurations
    configs = [
        {
            "id": "C1",
            "name": "Fixed Chunking + Dense Only",
            "chunk_strategy": "Fixed-Size (512)",
            "retriever_type": "dense",
            "dense": fixed_dense,
            "bm25": fixed_bm25
        },
        {
            "id": "C2",
            "name": "Fixed Chunking + Hybrid (RRF)",
            "chunk_strategy": "Fixed-Size (512)",
            "retriever_type": "hybrid",
            "dense": fixed_dense,
            "bm25": fixed_bm25
        },
        {
            "id": "C3",
            "name": "Section Chunking + Dense Only",
            "chunk_strategy": "Section-Aware",
            "retriever_type": "dense",
            "dense": section_dense,
            "bm25": section_bm25
        },
        {
            "id": "C4",
            "name": "Section Chunking + Hybrid (RRF)",
            "chunk_strategy": "Section-Aware",
            "retriever_type": "hybrid",
            "dense": section_dense,
            "bm25": section_bm25
        }
    ]

    all_detailed_results = []
    summary_rows = []

    print("\n>>> STEP 4: Executing Benchmark (200 evaluations)...")
    t_benchmark_start = time.perf_counter()

    for cfg in configs:
        cid = cfg["id"]
        cname = cfg["name"]
        cstrat = cfg["chunk_strategy"]
        rtype = cfg["retriever_type"]
        d_ret = cfg["dense"]
        b_ret = cfg["bm25"]
        h_ret = HybridRetriever(d_ret, b_ret)

        print(f"\n--- Running Configuration {cid}: {cname} ---")
        cfg_records = []
        hit_scores = []
        mrr_scores = []
        cite_scores = []
        corr_scores = []
        ret_lats = []
        gen_lats = []
        tot_lats = []
        token_counts = []
        costs = []

        for idx, q in enumerate(questions, 1):
            qid = q["id"]
            cat = q["category"]
            q_text = q["question"]
            gold_passages = q.get("golden_passages", [])
            gold_ans = q.get("golden_answer", "")

            # A. Actual Retrieval
            t_ret_start = time.perf_counter()
            if rtype == "dense":
                retrieved = d_ret.search(q_text, top_k=5)
            elif rtype == "hybrid":
                retrieved = h_ret.search(q_text, top_k=5)
            else:
                retrieved = d_ret.search(q_text, top_k=5)
            ret_latency_ms = (time.perf_counter() - t_ret_start) * 1000.0
            ret_lats.append(ret_latency_ms)

            retrieved_chunk_dicts = [c[0] for c in retrieved]
            retrieved_doc_ids = list(dict.fromkeys([c.get("doc_id", "Unknown") for c in retrieved_chunk_dicts]))
            retrieved_chunk_ids = [c.get("chunk_id", "") for c in retrieved_chunk_dicts]

            # B. Retrieval Quality Metrics (Answerable Questions Only)
            if cat == "answerable":
                hit = compute_hit_at_k(retrieved_chunk_dicts, gold_passages, k=5)
                mrr = compute_reciprocal_rank(retrieved_chunk_dicts, gold_passages)
                hit_scores.append(hit)
                mrr_scores.append(mrr)
            else:
                hit = 0.0
                mrr = 0.0

            # C. Generation with Bounded Retries (Max 3 attempts on live Gemini)
            max_retries = 3
            gen_result = None
            err_msg = ""

            for attempt in range(1, max_retries + 1):
                try:
                    gen_result = rag_engine.generate_answer(
                        question=q_text,
                        retrieved_chunks=retrieved
                    )
                    # If an internal error occurred, retry if attempts remain
                    if gen_result.get("is_error"):
                        err_msg = gen_result.get("refusal_reason", "API error")
                        if attempt < max_retries:
                            time.sleep(2.0 * attempt)
                            continue
                    break
                except Exception as exc:
                    err_msg = str(exc)
                    if attempt < max_retries:
                        time.sleep(2.0 * attempt)
                        continue
                    gen_result = {
                        "answer": f"ERROR: Execution failure ({str(exc)})",
                        "is_refusal": False,
                        "is_policy_refusal": False,
                        "is_error": True,
                        "refusal_reason": f"Execution failure: {str(exc)}",
                        "citations": [],
                        "retrieved_chunks": retrieved_chunk_ids,
                        "generation_latency_ms": 0.0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "estimated_cost_usd": 0.0,
                        "execution_mode": "api_error",
                        "is_fallback": True
                    }

            # Slight delay between live API calls to preserve rate limits
            if gen_result.get("execution_mode") == "live_gemini":
                time.sleep(1.2)

            gen_latency_ms = gen_result.get("generation_latency_ms", 0.0)
            total_latency_ms = ret_latency_ms + gen_latency_ms
            gen_lats.append(gen_latency_ms)
            tot_lats.append(total_latency_ms)

            in_tok = gen_result.get("input_tokens", 0)
            out_tok = gen_result.get("output_tokens", 0)
            tot_tok = in_tok + out_tok
            token_counts.append(tot_tok)

            cost = gen_result.get("estimated_cost_usd", 0.0)
            costs.append(cost)

            is_pol_refusal = gen_result.get("is_policy_refusal", False)
            is_err = gen_result.get("is_error", False)
            exec_mode = gen_result.get("execution_mode", "unknown")
            gen_ans = gen_result.get("answer", "")
            citations = gen_result.get("citations", [])

            # D. Answer Quality & Refusal Metrics
            cite_acc = compute_citation_accuracy(
                gen_ans,
                retrieved_chunk_dicts,
                is_refusal=is_pol_refusal,
                execution_mode=exec_mode
            )
            corr = compute_semantic_correctness(
                gen_ans,
                gold_ans,
                is_refusal=is_pol_refusal,
                category=cat,
                execution_mode=exec_mode
            )
            cite_scores.append(cite_acc)
            corr_scores.append(corr)

            row = {
                "question_id": qid,
                "question_type": cat,
                "configuration": cid,
                "retrieved_document_ids": ", ".join(retrieved_doc_ids),
                "retrieved_chunk_ids": ", ".join(retrieved_chunk_ids),
                "retrieval_hit_at_5": round(hit, 4),
                "reciprocal_rank": round(mrr, 4),
                "generated_answer": gen_ans.replace("\n", " ").strip(),
                "citations": json.dumps(citations, ensure_ascii=False),
                "answer_correctness": round(corr, 4),
                "citation_accuracy": round(cite_acc, 4),
                "is_policy_refusal": is_pol_refusal,
                "is_error": is_err,
                "execution_mode": exec_mode,
                "retrieval_latency_ms": round(ret_latency_ms, 2),
                "generation_latency_ms": round(gen_latency_ms, 2),
                "total_latency_ms": round(total_latency_ms, 2),
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "total_tokens": tot_tok,
                "estimated_cost": round(cost, 6),
                "error_message": err_msg if is_err else ""
            }

            all_detailed_results.append(row)
            cfg_records.append(row)

            if idx % 10 == 0 or idx == 50:
                print(f"[{cid}] Processed {idx}/50 questions (Mode: {exec_mode}, Hit@5: {hit}, Corr: {round(corr, 2)})")

        # Configuration Level Aggregation
        crr = compute_correct_refusal_rate(cfg_records, total_negative=TOTAL_NEGATIVE_QUESTIONS)
        frr = compute_false_refusal_rate(cfg_records, total_answerable=TOTAL_ANSWERABLE_QUESTIONS)
        aqc = compute_answerable_coverage(cfg_records, total_answerable=TOTAL_ANSWERABLE_QUESTIONS)

        avg_hit = float(np.mean(hit_scores)) if hit_scores else 0.0
        avg_mrr = float(np.mean(mrr_scores)) if mrr_scores else 0.0
        avg_cite = float(np.mean(cite_scores)) if cite_scores else 0.0
        avg_corr = float(np.mean(corr_scores)) if corr_scores else 0.0

        avg_ret_lat = float(np.mean(ret_lats))
        avg_gen_lat = float(np.mean(gen_lats))
        avg_tot_lat = float(np.mean(tot_lats))
        med_tot_lat = float(np.median(tot_lats))
        p95_tot_lat = float(np.percentile(tot_lats, 95))

        total_tok = int(np.sum(token_counts))
        total_cost = float(np.sum(costs))

        live_count = sum(1 for r in cfg_records if r["execution_mode"] == "live_gemini")
        api_err_count = sum(1 for r in cfg_records if r["is_error"] is True or r["execution_mode"] == "api_error")
        fallback_count = sum(1 for r in cfg_records if r["execution_mode"] == "fallback_simulated")
        gate_refusal_count = sum(1 for r in cfg_records if r["execution_mode"] == "gate_refusal")

        summary_rows.append({
            "Configuration": cid,
            "Chunking Strategy": cstrat,
            "Retrieval Strategy": rtype.title(),
            "Hit Rate@5": round(avg_hit, 4),
            "MRR": round(avg_mrr, 4),
            "Answer Correctness": round(avg_corr, 4),
            "Citation Accuracy": round(avg_cite, 4),
            "CRR": round(crr, 4),
            "FRR": round(frr, 4),
            "AQC": round(aqc, 4),
            "Average Retrieval Latency (ms)": round(avg_ret_lat, 2),
            "Average Generation Latency (ms)": round(avg_gen_lat, 2),
            "Average Total Latency (ms)": round(avg_tot_lat, 2),
            "Median Total Latency (ms)": round(med_tot_lat, 2),
            "p95 Total Latency (ms)": round(p95_tot_lat, 2),
            "Total Tokens": total_tok,
            "Total Estimated Cost ($)": round(total_cost, 4),
            "Successful Live Gemini Evaluations": live_count,
            "Gate Refusal Count": gate_refusal_count,
            "API Error Count": api_err_count,
            "Simulated/Fallback Count": fallback_count
        })

        # Save granular JSON dump for each configuration
        dump_path = REPORTS_DIR / f"eval_details_{cid}.json"
        with open(dump_path, "w", encoding="utf-8") as f:
            json.dump(cfg_records, f, indent=2, ensure_ascii=False)
        print(f"Dumped granular records to {dump_path.name}")

    total_benchmark_time = time.perf_counter() - t_benchmark_start
    print(f"\nAll 200 evaluations executed in {total_benchmark_time:.2f} seconds ({total_benchmark_time/60.0:.2f} minutes).")

    # 5. Export Detailed CSV & Summary CSV
    detailed_df = pd.DataFrame(all_detailed_results)
    detailed_csv_path = BASE_DIR / "evaluation" / "phase_c_detailed_results.csv"
    detailed_df.to_csv(detailed_csv_path, index=False, encoding="utf-8")
    print(f"\nDetailed CSV exported: {detailed_csv_path} ({len(detailed_df)} rows)")

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(RESULTS_TABLE_FILE, index=False, encoding="utf-8")
    print(f"Results summary table exported: {RESULTS_TABLE_FILE}")

    print("\n================== CONSOLIDATED RESULTS TABLE ==================")
    print(summary_df.to_string(index=False))
    print("================================================================\n")

    return detailed_df, summary_df


if __name__ == "__main__":
    run_benchmark()
