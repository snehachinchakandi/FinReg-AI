import React, { useState } from 'react';
import { 
  AlertTriangle, 
  ShieldAlert, 
  CheckCircle2, 
  HelpCircle, 
  FileWarning, 
  Calculator,
  RefreshCw,
  Scale
} from 'lucide-react';
import { apiClient } from '../api/client';
import { RiskEvaluationResponse } from '../types';

export const RiskCalculatorView: React.FC = () => {
  const [fldg, setFldg] = useState<number>(5.0);
  const [compoundPenal, setCompoundPenal] = useState<boolean>(false);
  const [poolDisbursal, setPoolDisbursal] = useState<boolean>(false);
  const [harvestContacts, setHarvestContacts] = useState<boolean>(false);
  const [coolingOffDays, setCoolingOffDays] = useState<number>(3);
  const [loanTenor, setLoanTenor] = useState<number>(30);
  const [tatDelayDays, setTatDelayDays] = useState<number>(0);

  const [result, setResult] = useState<RiskEvaluationResponse | null>(null);
  const [evaluating, setEvaluating] = useState<boolean>(false);

  const runEvaluation = async () => {
    setEvaluating(true);
    try {
      const res = await apiClient.evaluateRisk({
        fldg_percentage: fldg,
        compounds_penal_interest: compoundPenal,
        disburses_via_pool_account: poolDisbursal,
        collects_borrower_contacts: harvestContacts,
        cooling_off_days_provided: coolingOffDays,
        loan_tenor_days: loanTenor,
        tat_reversal_delay_days: tatDelayDays
      });
      setResult(res);
    } catch (err) {
      console.error('Risk evaluation failed:', err);
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="border-b border-slate-200/80 pb-4">
        <h2 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
          <Calculator className="w-5 h-5 text-blue-600" />
          <span>Regulatory Risk & Statutory Breach Evaluator</span>
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Simulate operational practices against RBI digital lending caps, penal interest restrictions, and TAT customer compensation rules.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Scenario Input Controls (6 cols) */}
        <div className="lg:col-span-6 bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-5">
          <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3">
            <Scale className="w-4 h-4 text-blue-600" />
            <span>Configure Operational Parameters</span>
          </h3>

          {/* DLG Percentage */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-700">Default Loss Guarantee (DLG) Cover:</span>
              <span className="font-mono font-bold text-blue-600">{fldg.toFixed(1)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="15"
              step="0.5"
              value={fldg}
              onChange={(e) => setFldg(parseFloat(e.target.value))}
              className="w-full accent-blue-600 cursor-pointer"
            />
            <p className="text-[11px] text-slate-500">Statutory Limit: Maximum 5.0% of portfolio under Chapter VI, Para 23.</p>
          </div>

          {/* Checkbox Controls */}
          <div className="space-y-3 pt-2">
            <label className="flex items-start space-x-3 bg-slate-50 p-3 rounded-xl border border-slate-200/80 cursor-pointer">
              <input
                type="checkbox"
                checked={compoundPenal}
                onChange={(e) => setCompoundPenal(e.target.checked)}
                className="mt-0.5 rounded text-blue-600 accent-blue-600"
              />
              <div className="text-xs">
                <span className="font-semibold text-slate-900 block">Compound Penal Charges into Loan Interest</span>
                <span className="text-[11px] text-slate-500">Prohibited under RBI Fair Lending Practice Circular (Aug 2023).</span>
              </div>
            </label>

            <label className="flex items-start space-x-3 bg-slate-50 p-3 rounded-xl border border-slate-200/80 cursor-pointer">
              <input
                type="checkbox"
                checked={poolDisbursal}
                onChange={(e) => setPoolDisbursal(e.target.checked)}
                className="mt-0.5 rounded text-blue-600 accent-blue-600"
              />
              <div className="text-xs">
                <span className="font-semibold text-slate-900 block">Disburse Loan via LSP Intermediate Pool Account</span>
                <span className="text-[11px] text-slate-500">Prohibited under Paragraph 9: funds must flow direct RE-to-borrower.</span>
              </div>
            </label>

            <label className="flex items-start space-x-3 bg-slate-50 p-3 rounded-xl border border-slate-200/80 cursor-pointer">
              <input
                type="checkbox"
                checked={harvestContacts}
                onChange={(e) => setHarvestContacts(e.target.checked)}
                className="mt-0.5 rounded text-blue-600 accent-blue-600"
              />
              <div className="text-xs">
                <span className="font-semibold text-slate-900 block">App Requests Device Contact List / Media Access</span>
                <span className="text-[11px] text-slate-500">Prohibited under Paragraphs 12-14: privacy restriction on mobile phone resources.</span>
              </div>
            </label>
          </div>

          {/* Cooling Off & Tenor */}
          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/80 space-y-1">
              <span className="text-[11px] font-semibold text-slate-600">Cooling-Off Provided (Days):</span>
              <input
                type="number"
                min="0"
                max="10"
                value={coolingOffDays}
                onChange={(e) => setCoolingOffDays(parseInt(e.target.value) || 0)}
                className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1 text-xs text-slate-900 font-mono"
              />
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/80 space-y-1">
              <span className="text-[11px] font-semibold text-slate-600">Loan Tenor (Days):</span>
              <input
                type="number"
                min="1"
                max="365"
                value={loanTenor}
                onChange={(e) => setLoanTenor(parseInt(e.target.value) || 1)}
                className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1 text-xs text-slate-900 font-mono"
              />
            </div>
          </div>

          {/* TAT Delay */}
          <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/80 space-y-1">
            <span className="text-[11px] font-semibold text-slate-600">Failed Transaction Auto-Reversal Delay (Days past TAT):</span>
            <input
              type="number"
              min="0"
              max="30"
              value={tatDelayDays}
              onChange={(e) => setTatDelayDays(parseInt(e.target.value) || 0)}
              className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1 text-xs text-slate-900 font-mono"
            />
            <p className="text-[10px] text-slate-500">₹100/day statutory customer compensation applies after TAT expiry.</p>
          </div>

          <button
            onClick={runEvaluation}
            disabled={evaluating}
            className="w-full bg-[#0c1322] hover:bg-blue-600 text-white font-semibold py-3 rounded-xl text-xs flex items-center justify-center space-x-2 transition shadow-xs cursor-pointer"
          >
            {evaluating ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <Calculator className="w-4 h-4" />
                <span>Evaluate Regulatory Scenario</span>
              </>
            )}
          </button>
        </div>

        {/* Right Column: Risk Assessment Results (6 cols) */}
        <div className="lg:col-span-6 bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs flex flex-col space-y-5">
          <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-3">
            Regulatory Compliance Assessment Report
          </h3>

          {result ? (
            <div className="space-y-5 flex-1">
              {/* Score Banner */}
              <div className={`p-5 rounded-2xl border flex items-center justify-between ${
                result.severity_level === 'CRITICAL'
                  ? 'bg-rose-50 border-rose-200 text-rose-800'
                  : result.severity_level === 'HIGH'
                  ? 'bg-amber-50 border-amber-200 text-amber-800'
                  : result.severity_level === 'MEDIUM'
                  ? 'bg-yellow-50 border-yellow-200 text-yellow-800'
                  : 'bg-emerald-50 border-emerald-200 text-emerald-800'
              }`}>
                <div>
                  <div className="text-xs uppercase tracking-wider font-semibold">
                    Compliance Status: {result.status}
                  </div>
                  <div className="text-2xl font-black mt-1">
                    Risk Score: {result.overall_risk_score} / 100
                  </div>
                  <div className="text-xs mt-1 opacity-90">
                    Severity: {result.severity_level} ({result.total_breaches} statutory breaches detected)
                  </div>
                </div>

                {result.compensation_payable_inr > 0 && (
                  <div className="text-right">
                    <span className="text-[10px] uppercase font-mono block text-slate-500">Compensation Owed:</span>
                    <span className="text-xl font-bold font-mono text-rose-700">₹{result.compensation_payable_inr}</span>
                  </div>
                )}
              </div>

              {/* Itemized Breaches */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Itemized Regulatory Findings:
                </h4>

                {result.breaches.length === 0 ? (
                  <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-xl text-xs text-emerald-800 flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                    <span>All operational parameters fully conform to RBI Digital Lending Directions and Fair Practice Codes.</span>
                  </div>
                ) : (
                  result.breaches.map((b, idx) => (
                    <div
                      key={idx}
                      className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 space-y-1.5 text-xs"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-rose-700 flex items-center space-x-1.5">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          <span>{b.rule}</span>
                        </span>
                        <span className="text-[10px] font-mono bg-rose-100 text-rose-800 px-2 py-0.5 rounded border border-rose-200">
                          {b.severity}
                        </span>
                      </div>
                      <p className="text-slate-700 leading-relaxed">{b.finding}</p>
                      <div className="text-[11px] font-mono text-blue-700 pt-1">
                        Clause: {b.cited_clause}
                      </div>
                      <div className="text-[11px] text-slate-600 bg-white p-2 rounded border border-slate-200 shadow-2xs">
                        <span className="font-semibold text-slate-800">Remediation:</span> {b.remediation}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400 text-xs text-center py-12 space-y-2">
              <Calculator className="w-8 h-8 text-slate-300" />
              <span>Configure parameters on the left and click "Evaluate Regulatory Scenario" to generate an audit assessment.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
