import React, { useEffect, useState } from 'react';
import { 
  GitCommit, 
  Layers, 
  ArrowRight, 
  CheckCircle, 
  XCircle, 
  Calendar, 
  Search,
  Sparkles,
  Clock
} from 'lucide-react';
import { apiClient } from '../api/client';
import { TimelineEvent, ClauseDiff } from '../types';

export const TimelineDiffView: React.FC = () => {
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [diffs, setDiffs] = useState<ClauseDiff[]>([]);
  const [selectedRuleKey, setSelectedRuleKey] = useState<string>('FLDG_SYNTHETIC_SECURITISATION');
  const [asOfDate, setAsOfDate] = useState<string>('2023-05-15');
  const [simulationResult, setSimulationResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [timeRes, diffRes] = await Promise.all([
          apiClient.getTimeline(),
          apiClient.getClauseDiffs()
        ]);
        setTimeline(timeRes.events);
        setDiffs(diffRes);
        if (diffRes.length > 0) {
          setSelectedRuleKey(diffRes[0].rule_key);
        }
      } catch (err) {
        console.error('Failed to load timeline or diffs:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleSimulate = async () => {
    try {
      const res = await apiClient.getAsOfSimulation(asOfDate);
      setSimulationResult(res);
    } catch (err) {
      console.error('Simulation error:', err);
    }
  };

  const activeDiff = diffs.find((d) => d.rule_key === selectedRuleKey) || diffs[0];

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="border-b border-slate-200/80 pb-4">
        <h2 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
          <GitCommit className="w-5 h-5 text-blue-600" />
          <span>Tri-Temporal Regulatory Evolution & Clause Diffs</span>
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Trace how RBI digital lending, FLDG, and penal rules evolved across 2022, 2023, and the 2025 Master Directions.
        </p>
      </div>

      {/* Chronological Timeline Scrubber */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4">
        <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
          <Calendar className="w-4 h-4 text-blue-600" />
          <span>Chronological Regulatory Transition Milestones (2022 — 2025)</span>
        </h3>

        <div className="relative pl-6 space-y-5 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
          {timeline.map((event) => (
            <div key={event.id} className="relative group">
              <div className="absolute -left-[29px] top-1.5 w-3.5 h-3.5 rounded-full bg-white border-2 border-blue-600 group-hover:scale-125 transition-transform" />
              <div className="bg-slate-50/70 border border-slate-200/80 rounded-xl p-4 space-y-2 hover:bg-slate-50 transition shadow-2xs">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded border border-blue-200">
                      {event.date}
                    </span>
                    <span className="text-xs font-semibold text-slate-900">{event.title}</span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${
                    event.status === 'ACTIVE' 
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                      : 'bg-rose-50 text-rose-700 border border-rose-200'
                  }`}>
                    {event.status}
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">{event.summary}</p>
                <div className="text-[11px] font-mono text-slate-400 flex items-center space-x-3">
                  <span>Circular: {event.circular_no}</span>
                  <span>Doc ID: {event.doc_id}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Side-by-Side Clause Diff Viewer */}
      {activeDiff && (
        <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                <Layers className="w-4 h-4 text-indigo-600" />
                <span>Side-by-Side Clause-Level Supersession Comparison</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Inspect historical phrasing vs active legal obligations side by side.
              </p>
            </div>

            {/* Rule Selector Tabs */}
            <div className="flex flex-wrap gap-2">
              {diffs.map((d) => (
                <button
                  key={d.rule_key}
                  onClick={() => setSelectedRuleKey(d.rule_key)}
                  className={`text-xs px-3 py-1.5 rounded-xl font-medium transition cursor-pointer ${
                    selectedRuleKey === d.rule_key
                      ? 'bg-[#0c1322] text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:text-slate-900 border border-slate-200'
                  }`}
                >
                  {d.title}
                </button>
              ))}
            </div>
          </div>

          {/* Diff Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Outdated Column */}
            <div className="bg-rose-50/40 border border-rose-200 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between border-b border-rose-200 pb-2">
                <span className="text-xs font-bold text-rose-700 flex items-center space-x-1.5">
                  <XCircle className="w-4 h-4 text-rose-600" />
                  <span>Outdated / Superseded</span>
                </span>
                <span className="text-[10px] font-mono bg-rose-100 text-rose-800 px-2 py-0.5 rounded border border-rose-200">
                  Until {activeDiff.outdated.valid_until || '2025-05-07'}
                </span>
              </div>
              <div className="space-y-1">
                <div className="text-xs font-semibold text-slate-900">{activeDiff.outdated.doc_title}</div>
                <div className="text-[11px] font-mono text-slate-500">{activeDiff.outdated.clause}</div>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed bg-white p-3 rounded-lg border border-rose-100 shadow-2xs">
                {activeDiff.outdated.summary}
              </p>
            </div>

            {/* Intermediate Column (if exists) */}
            <div className="bg-amber-50/40 border border-amber-200 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between border-b border-amber-200 pb-2">
                <span className="text-xs font-bold text-amber-700 flex items-center space-x-1.5">
                  <Layers className="w-4 h-4 text-amber-600" />
                  <span>Intermediate Regime</span>
                </span>
                <span className="text-[10px] font-mono bg-amber-100 text-amber-800 px-2 py-0.5 rounded border border-amber-200">
                  {activeDiff.intermediate ? `Valid: ${activeDiff.intermediate.valid_until}` : 'N/A'}
                </span>
              </div>
              {activeDiff.intermediate ? (
                <>
                  <div className="space-y-1">
                    <div className="text-xs font-semibold text-slate-900">{activeDiff.intermediate.doc_title}</div>
                    <div className="text-[11px] font-mono text-slate-500">{activeDiff.intermediate.clause}</div>
                  </div>
                  <p className="text-xs text-slate-700 leading-relaxed bg-white p-3 rounded-lg border border-amber-100 shadow-2xs">
                    {activeDiff.intermediate.summary}
                  </p>
                </>
              ) : (
                <div className="text-xs text-slate-500 italic py-8 text-center">
                  Direct one-step regulatory transition (No intermediate circular)
                </div>
              )}
            </div>

            {/* Current / Active Column */}
            <div className="bg-emerald-50/40 border border-emerald-200 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between border-b border-emerald-200 pb-2">
                <span className="text-xs font-bold text-emerald-700 flex items-center space-x-1.5">
                  <CheckCircle className="w-4 h-4 text-emerald-600" />
                  <span>Active Governing Law</span>
                </span>
                <span className="text-[10px] font-mono bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded border border-emerald-200">
                  From {activeDiff.current.effective_date || '2025-05-08'}
                </span>
              </div>
              <div className="space-y-1">
                <div className="text-xs font-semibold text-slate-900">{activeDiff.current.doc_title}</div>
                <div className="text-[11px] font-mono text-slate-500">{activeDiff.current.clause}</div>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed bg-white p-3 rounded-lg border border-emerald-100 shadow-2xs">
                {activeDiff.current.summary}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* As-Of Date Simulation Sandbox */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
          <Search className="w-4 h-4 text-blue-600" />
          <span>Historical As-Of Date Regulatory Simulation Sandbox</span>
        </h3>
        <p className="text-xs text-slate-500">
          Simulate how FinReg AI routes queries and which rules are deemed active on any arbitrary date.
        </p>

        <div className="flex items-center space-x-3 pt-2">
          <input
            type="date"
            value={asOfDate}
            onChange={(e) => setAsOfDate(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-500 font-mono"
          />
          <button
            onClick={handleSimulate}
            className="bg-[#0c1322] hover:bg-blue-600 text-white px-4 py-2 rounded-xl text-xs font-semibold transition cursor-pointer"
          >
            Simulate Legal State
          </button>
        </div>

        {simulationResult && (
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 font-mono text-xs text-slate-800 space-y-2">
            <div className="text-blue-700 font-bold">
              Simulation Date: {simulationResult.query_date} (System Baseline: {simulationResult.current_system_date})
            </div>
            <pre className="text-[11px] text-slate-600 whitespace-pre-wrap">
              {JSON.stringify(simulationResult.interpretation, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
