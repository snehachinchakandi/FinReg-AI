import React, { useEffect, useState } from 'react';
import { 
  BarChart3, 
  CheckCircle2, 
  Layers, 
  Clock, 
  ShieldCheck, 
  Award,
  Info
} from 'lucide-react';
import { apiClient } from '../api/client';
import { EvalSummaryRecord } from '../types';

export const BenchmarkView: React.FC = () => {
  const [records, setRecords] = useState<EvalSummaryRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSummary() {
      try {
        const res = await apiClient.getEvaluationSummary();
        setRecords(res);
      } catch (err) {
        console.error('Failed to load evaluation summary:', err);
      } finally {
        setLoading(false);
      }
    }
    loadSummary();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-2">
      {/* View Header */}
      <div className="border-b border-slate-200/80 pb-4">
        <h2 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-blue-600" />
          <span>Empirical Evaluation Benchmark (Phase C — 200 Evaluations)</span>
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Rigorous 4-configuration benchmark over 50 questions (35 answerable, 10 unanswerable, 5 adversarial)
          comparing fixed vs section-aware chunking and dense vs hybrid RRF retrieval.
        </p>
      </div>

      {/* Benchmark Matrix Table */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4">
        <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
          <Award className="w-4 h-4 text-amber-600" />
          <span>Results Table: C1 vs C2 vs C3 vs C4 Comparative Performance</span>
        </h3>

        <div className="overflow-x-auto border border-slate-200 rounded-xl">
          <table className="w-full text-xs text-left text-slate-700">
            <thead className="text-[11px] uppercase tracking-wider bg-slate-50 text-slate-600 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-bold">Config</th>
                <th className="py-3 px-4 font-bold">Chunking Strategy</th>
                <th className="py-3 px-4 font-bold">Retrieval Mode</th>
                <th className="py-3 px-4 text-emerald-700 font-bold">Hit Rate@5</th>
                <th className="py-3 px-4 text-blue-700 font-bold">MRR</th>
                <th className="py-3 px-4 font-bold">Rank-1 Count</th>
                <th className="py-3 px-4 font-bold">CRR (Refusals)</th>
                <th className="py-3 px-4 font-bold">FRR</th>
                <th className="py-3 px-4 font-bold">Avg Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {records.map((r, i) => {
                const isC4 = r.Configuration === 'C4';
                return (
                  <tr
                    key={i}
                    className={`hover:bg-slate-50/70 transition ${
                      isC4 ? 'bg-blue-50/30 font-semibold' : ''
                    }`}
                  >
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded font-bold ${
                        isC4 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-slate-100 text-slate-700 border border-slate-200'
                      }`}>
                        {r.Configuration} {isC4 ? '★' : ''}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-sans text-slate-800">{r['Chunking Strategy']}</td>
                    <td className="py-3 px-4 font-sans text-slate-800">{r['Retrieval Strategy']}</td>
                    <td className="py-3 px-4 text-emerald-700 font-bold text-sm">
                      {r['Hit Rate@5 (n=35)']}
                    </td>
                    <td className="py-3 px-4 text-blue-700 font-bold text-sm">
                      {r['MRR (n=35)']}
                    </td>
                    <td className="py-3 px-4 text-slate-700">{r['Rank-1 Retrieval Count (n=35)']}</td>
                    <td className="py-3 px-4 text-emerald-700">{r['CRR (n=15)']}</td>
                    <td className="py-3 px-4 text-slate-500">{r['FRR (n=35)']}</td>
                    <td className="py-3 px-4 text-slate-600">{r['Avg Retrieval Latency (All 50, ms)']} ms</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Key Architectural Takeaways */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-3">
          <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Why Configuration C4 is Recommended</span>
          </h3>
          <ul className="space-y-2 text-xs text-slate-600 leading-relaxed list-disc list-inside">
            <li>
              <span className="font-semibold text-slate-900">Section-Aware Chunking (Strategy B):</span> Preserves complete statutory paragraphs and chapter headers, preventing fragmented clauses and preserving disclosure schedules.
            </li>
            <li>
              <span className="font-semibold text-slate-900">Hybrid Retrieval (RRF $k=60$):</span> Combines dense semantic vector retrieval (BAAI/bge-small-en-v1.5) with sparse keyword matching (BM25 Okapi), eliminating failure on acronyms like DLG, KFS, CoFT, and PPI.
            </li>
            <li>
              <span className="font-semibold text-slate-900">Top Performance:</span> Achieves top-tier Hit Rate@5 with low retrieval latency (~40-50 ms).
            </li>
          </ul>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-3">
          <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            <span>Audited Safeguards & Refusal Decoupling</span>
          </h3>
          <ul className="space-y-2 text-xs text-slate-600 leading-relaxed list-disc list-inside">
            <li>
              <span className="font-semibold text-slate-900">Decoupled CRR vs FRR:</span> Strict mathematical separation ensuring external API quota limits do not contaminate genuine compliance guardrail measurements.
            </li>
            <li>
              <span className="font-semibold text-slate-900">Local Guardrails:</span> Catch adversarial prompt injection attempts before LLM dispatch (e.g., query 46).
            </li>
            <li>
              <span className="font-semibold text-slate-900">71 Passing Tests:</span> Full regression suite protects temporal filtering, staggered dates, and citation accuracy.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};
