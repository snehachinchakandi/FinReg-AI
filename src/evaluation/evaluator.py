"""
Comprehensive Evaluation Benchmark Harness for FinReg AI.
Runs the 50-question benchmark across all 4 configurations:
  C1: Fixed-Size Chunking + Dense Only
  C2: Fixed-Size Chunking + Hybrid (BM25 + Dense RRF)
  C3: Section-Aware Chunking + Dense Only
  C4: Section-Aware Chunking + Hybrid (BM25 + Dense RRF)
Exports results_table.csv and failure logs.
"""

import json
import time
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

from src.config import EVAL_DATASET_FILE, RESULTS_TABLE_FILE, REPORTS_DIR
from src.retrieval.dense import DenseRetriever
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.hybrid import HybridRetriever
from src.retrieval.reranker import CrossEncoderReranker
from src.generation.rag_engine import FinRegRAGEngine
from src.evaluation.metrics import (
    compute_hit_at_k,
    compute_reciprocal_rank,
    compute_citation_accuracy,
    compute_correct_refusal_rate,
    compute_false_refusal_rate,
    compute_answerable_coverage,
    compute_semantic_correctness
)

class BenchmarkEvaluator:
    """Evaluates RAG pipeline configurations against golden benchmark questions."""

    def __init__(self, eval_file: Path = EVAL_DATASET_FILE):
        self.eval_file = eval_file
        self.questions = self._load_questions()

    def _load_questions(self) -> List[Dict[str, Any]]:
        questions = []
        with open(self.eval_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    questions.append(json.loads(line))
        return questions

    def evaluate_configuration(
        self,
        config_id: str,
        config_name: str,
        chunk_strategy: str,
        retriever_type: str,
        dense_retriever: DenseRetriever,
        bm25_retriever: BM25Retriever,
        rag_engine: FinRegRAGEngine,
        top_k: int = 5,
        reranker: CrossEncoderReranker = None
    ) -> Dict[str, Any]:
        """Runs the entire 50-question benchmark on a single pipeline configuration."""
        print(f"\n==========================================")
        print(f"Evaluating {config_id}: {config_name}")
        print(f"==========================================")

        hybrid_retriever = HybridRetriever(dense_retriever, bm25_retriever)

        hit_scores = []
        mrr_scores = []
        citation_scores = []
        correctness_scores = []
        retrieval_latencies = []
        generation_latencies = []
        total_latencies = []
        input_tokens_list = []
        output_tokens_list = []
        costs = []
        execution_modes = []
        detailed_records = []

        for q in self.questions:
            q_id = q["id"]
            category = q["category"]
            question_text = q["question"]
            golden_passages = q.get("golden_passages", [])
            golden_answer = q.get("golden_answer", "")

            # 1. Retrieval Latency
            t0 = time.perf_counter()
            if retriever_type == "dense":
                retrieved = dense_retriever.search(question_text, top_k=top_k)
            elif retriever_type == "hybrid":
                retrieved = hybrid_retriever.search(question_text, top_k=top_k)
            else:
                retrieved = dense_retriever.search(question_text, top_k=top_k)

            # Optional reranking
            if reranker:
                retrieved, _ = reranker.rerank(question_text, retrieved, top_k=top_k)

            retrieval_latency = (time.perf_counter() - t0) * 1000.0

            # 2. Generation & Telemetry
            gen_result = rag_engine.generate_answer(
                question=question_text,
                retrieved_chunks=retrieved
            )

            gen_latency = gen_result.get("generation_latency_ms", 0.0)
            total_latency = retrieval_latency + gen_latency
            retrieval_latencies.append(retrieval_latency)
            generation_latencies.append(gen_latency)
            total_latencies.append(total_latency)

            costs.append(gen_result.get("estimated_cost_usd", 0.0))
            input_tokens_list.append(gen_result.get("input_tokens", 0))
            output_tokens_list.append(gen_result.get("output_tokens", 0))
            execution_modes.append(gen_result.get("execution_mode", "fallback_simulated"))

            retrieved_chunk_dicts = [c[0] for c in retrieved]

            # 3. Compute Metrics
            if category == "answerable":
                hit = compute_hit_at_k(retrieved_chunk_dicts, golden_passages, k=top_k)
                mrr = compute_reciprocal_rank(retrieved_chunk_dicts, golden_passages)
                hit_scores.append(hit)
                mrr_scores.append(mrr)
            else:
                hit = 0.0
                mrr = 0.0

            is_pol_refusal = gen_result.get("is_policy_refusal", gen_result.get("is_refusal", False))
            is_err = gen_result.get("is_error", False)
            exec_mode = gen_result.get("execution_mode", "fallback_simulated")

            cite_acc = compute_citation_accuracy(
                gen_result["answer"],
                retrieved_chunk_dicts,
                is_refusal=is_pol_refusal,
                execution_mode=exec_mode
            )
            correctness = compute_semantic_correctness(
                gen_result["answer"],
                golden_answer,
                is_refusal=is_pol_refusal,
                category=category,
                execution_mode=exec_mode
            )

            citation_scores.append(cite_acc)
            correctness_scores.append(correctness)

            detailed_records.append({
                "config_id": config_id,
                "question_id": q_id,
                "category": category,
                "question": question_text,
                "hit_at_5": hit,
                "mrr": mrr,
                "citation_accuracy": cite_acc,
                "correctness": correctness,
                "is_refusal": is_pol_refusal,
                "is_policy_refusal": is_pol_refusal,
                "is_error": is_err,
                "refusal_reason": gen_result.get("refusal_reason", "N/A"),
                "generated_answer": gen_result["answer"],
                "retrieval_latency_ms": retrieval_latency,
                "generation_latency_ms": gen_latency,
                "total_latency_ms": total_latency,
                "input_tokens": gen_result.get("input_tokens", 0),
                "output_tokens": gen_result.get("output_tokens", 0),
                "estimated_cost_usd": gen_result.get("estimated_cost_usd", 0.0),
                "execution_mode": exec_mode,
                "is_fallback": gen_result.get("is_fallback", True),
                "top_retrieved": [c["chunk_id"] for c in retrieved_chunk_dicts[:2]]
            })

        # Distinct refusal and coverage metrics (Task 2)
        crr = compute_correct_refusal_rate(detailed_records)
        frr = compute_false_refusal_rate(detailed_records)
        aqc = compute_answerable_coverage(detailed_records)

        # Aggregate retrieval & quality metrics
        avg_hit = sum(hit_scores) / max(1, len(hit_scores))
        avg_mrr = sum(mrr_scores) / max(1, len(mrr_scores))
        avg_cite = sum(citation_scores) / max(1, len(citation_scores))
        avg_corr = sum(correctness_scores) / max(1, len(correctness_scores))

        # Latency breakdown (Task 3)
        avg_ret_lat = sum(retrieval_latencies) / max(1, len(retrieval_latencies))
        avg_gen_lat = sum(generation_latencies) / max(1, len(generation_latencies))
        avg_tot_lat = sum(total_latencies) / max(1, len(total_latencies))
        avg_cost = sum(costs) / max(1, len(costs))

        # Determine overall execution mode
        live_calls = sum(1 for m in execution_modes if m == "live_gemini")
        if live_calls > 0:
            exec_mode_str = "live_gemini" if live_calls == len(execution_modes) else f"mixed ({live_calls} live)"
        else:
            exec_mode_str = "fallback_simulated"

        summary = {
            "Config ID": config_id,
            "Configuration": config_name,
            "Chunking Strategy": chunk_strategy,
            "Retrieval Strategy": retriever_type.title(),
            "Execution Mode": exec_mode_str,
            "Hit Rate@5": round(avg_hit, 4),
            "MRR": round(avg_mrr, 4),
            "Correctness": round(avg_corr, 4),
            "Citation Accuracy": round(avg_cite, 4),
            "Correct Refusal Rate (CRR)": round(crr, 4),
            "False Refusal Rate (FRR)": round(frr, 4),
            "Answerable Coverage (AQC)": round(aqc, 4),
            "Avg Retrieval Latency (ms)": round(avg_ret_lat, 2),
            "Avg Generation Latency (ms)": round(avg_gen_lat, 2),
            "Avg Total Latency (ms)": round(avg_tot_lat, 2),
            "Cost per Query ($)": f"${avg_cost:.6f}"
        }

        # Save granular dump
        dump_path = REPORTS_DIR / f"eval_details_{config_id}.json"
        with open(dump_path, "w", encoding="utf-8") as f:
            json.dump(detailed_records, f, indent=2, ensure_ascii=False)

        return summary, detailed_records

    def run_all_configurations(
        self,
        fixed_dense: DenseRetriever,
        fixed_bm25: BM25Retriever,
        section_dense: DenseRetriever,
        section_bm25: BM25Retriever,
        rag_engine: FinRegRAGEngine
    ) -> pd.DataFrame:
        """Executes all 4 configurations, prints summary, and writes results_table.csv."""
        configs = [
            ("C1", "Fixed Chunking + Dense Only", "Fixed-Size (512)", "dense", fixed_dense, fixed_bm25),
            ("C2", "Fixed Chunking + Hybrid (RRF)", "Fixed-Size (512)", "hybrid", fixed_dense, fixed_bm25),
            ("C3", "Section Chunking + Dense Only", "Section-Aware", "dense", section_dense, section_bm25),
            ("C4", "Section Chunking + Hybrid (RRF)", "Section-Aware", "hybrid", section_dense, section_bm25),
        ]

        summaries = []
        for cid, cname, cstrat, rtype, d_ret, b_ret in configs:
            summary, _ = self.evaluate_configuration(
                config_id=cid,
                config_name=cname,
                chunk_strategy=cstrat,
                retriever_type=rtype,
                dense_retriever=d_ret,
                bm25_retriever=b_ret,
                rag_engine=rag_engine
            )
            summaries.append(summary)

        df_results = pd.DataFrame(summaries)
        RESULTS_TABLE_FILE.parent.mkdir(parents=True, exist_ok=True)
        df_results.to_csv(RESULTS_TABLE_FILE, index=False)
        print(f"\nConsolidated results table written to {RESULTS_TABLE_FILE}")
        return df_results
