import React, { useEffect, useState } from 'react';
import { 
  ShieldCheck, 
  Filter, 
  Building2, 
  Smartphone, 
  FileText, 
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';
import { apiClient } from '../api/client';
import { ComplianceObligation } from '../types';

export const ComplianceMatrixView: React.FC = () => {
  const [obligations, setObligations] = useState<ComplianceObligation[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMatrix() {
      try {
        const res = await apiClient.getComplianceMatrix();
        setObligations(res.obligations);
      } catch (err) {
        console.error('Failed to load compliance matrix:', err);
      } finally {
        setLoading(false);
      }
    }
    loadMatrix();
  }, []);

  const categories = ['ALL', ...Array.from(new Set(obligations.map((o) => o.category)))];

  const filtered = selectedCategory === 'ALL'
    ? obligations
    : obligations.filter((o) => o.category === selectedCategory);

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="border-b border-slate-200/80 pb-4">
        <h2 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-blue-600" />
          <span>Statutory Compliance Matrix: Regulated Entities (RE) vs LSPs</span>
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Comparative division of statutory duties between Banks/NBFCs and Lending Service Providers (LSPs) under RBI Digital Lending Directions.
        </p>
      </div>

      {/* Category Filter Chips */}
      <div className="flex flex-wrap items-center gap-2 bg-white border border-slate-200/90 p-3 rounded-2xl shadow-xs">
        <Filter className="w-4 h-4 text-slate-400 ml-1 mr-2 flex-shrink-0" />
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`text-xs px-3 py-1.5 rounded-xl font-medium transition cursor-pointer ${
              selectedCategory === cat
                ? 'bg-[#0c1322] text-white shadow-2xs'
                : 'bg-slate-100 text-slate-600 hover:text-slate-900 border border-slate-200'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Obligations Grid */}
      <div className="space-y-4">
        {filtered.map((item) => (
          <div
            key={item.id}
            className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs space-y-4 hover:border-slate-300 transition"
          >
            {/* Header / Meta */}
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2.5">
                <span className="font-mono text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                  {item.category}
                </span>
                <h3 className="text-sm font-bold text-slate-900">{item.topic}</h3>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                  item.severity === 'CRITICAL' 
                    ? 'bg-rose-50 text-rose-700 border border-rose-200' 
                    : item.severity === 'HIGH' 
                    ? 'bg-amber-50 text-amber-700 border border-amber-200' 
                    : 'bg-blue-50 text-blue-700 border border-blue-200'
                }`}>
                  {item.severity} SEVERITY
                </span>
              </div>
            </div>

            {/* Split RE vs LSP Duties */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* RE Obligation */}
              <div className="bg-blue-50/40 border border-blue-100 rounded-xl p-4 space-y-2">
                <div className="flex items-center space-x-2 text-blue-700 font-semibold text-xs">
                  <Building2 className="w-4 h-4 text-blue-600" />
                  <span>Regulated Entity (Bank / NBFC) Mandate</span>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed">
                  {item.re_obligation}
                </p>
              </div>

              {/* LSP Obligation */}
              <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4 space-y-2">
                <div className="flex items-center space-x-2 text-indigo-700 font-semibold text-xs">
                  <Smartphone className="w-4 h-4 text-indigo-600" />
                  <span>LSP / Digital Lending App (DLA) Mandate</span>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed">
                  {item.lsp_obligation}
                </p>
              </div>
            </div>

            {/* Legal Authority Citation */}
            <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-100 font-mono">
              <span className="flex items-center space-x-1.5">
                <FileText className="w-3.5 h-3.5 text-blue-600" />
                <span>Statutory Authority: {item.primary_clause}</span>
              </span>
              <span className="text-slate-400">Ref: {item.legal_reference}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
