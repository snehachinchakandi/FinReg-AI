import React, { useEffect, useState } from 'react';
import {
  FileText,
  Layers,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  History,
  FileCheck,
  RotateCw,
  ExternalLink,
  MessageSquare,
  Globe,
  Folder,
  Briefcase,
  Mail,
  Scale,
  Shield,
  Clock,
  Building2,
  ChevronRight,
  ShieldAlert,
  Award,
  Share2
} from 'lucide-react';
import { apiClient } from '../api/client';
import { CorpusSummary, TransitionMilestone } from '../types';
import { UserProfile } from './SignInView';

interface DashboardViewProps {
  onNavigate: (tab: string) => void;
  user?: UserProfile | null;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ onNavigate, user }) => {
  const [summary, setSummary] = useState<CorpusSummary | null>(null);
  const [transitions, setTransitions] = useState<TransitionMilestone[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [sumRes, transRes] = await Promise.all([
          apiClient.getCorpusSummary(),
          apiClient.getTransitions()
        ]);
        setSummary(sumRes);
        setTransitions(transRes.transitions);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const latestDevelopments = [
    {
      id: 'RBI_DL_2025',
      flag: '🇮🇳',
      regulator: 'Reserve Bank of India (RBI)',
      title: 'Reserve Bank of India issues Master Directions on Digital Lending 2025',
      circularNo: 'DOR.CRE.REC.14/21.07.001/2025-26',
      date: 'May 8, 2025',
      relativeTime: 'In Force',
      summary:
        'Comprehensive Master Directions repealing the 2022 Guidelines and 2023 DLG circular. Mandates Chapter VI 5% DLG portfolio cap, direct bank account disbursals, and staggered commencement dates on 15 June 2025 (Para 17) and 01 November 2025 (Para 6).',
      tags: ['Digital Lending', 'Master Direction', 'In Force', 'Chapter VI DLG']
    },
    {
      id: 'RBI_PENAL_2023',
      flag: '🇮🇳',
      regulator: 'Reserve Bank of India (RBI)',
      title: 'Fair Lending Practice – Penal Charges in Loan Accounts',
      circularNo: 'RBI/2023-24/53',
      date: 'Aug 18, 2023',
      relativeTime: 'In Force',
      summary:
        'Supersedes legacy penal interest compounding. Mandates that penal charges must be distinct, operational, non-capitalised, and strictly never added to principal or loan interest.',
      tags: ['Penal Charges', 'Fair Lending', 'Operational', 'Non-Capitalised']
    },
    {
      id: 'RBI_PPI_CREDIT_2022',
      flag: '🇮🇳',
      regulator: 'Reserve Bank of India (RBI)',
      title: 'Restriction on Loading of Non-Bank Prepaid Payment Instruments (PPIs) via Credit Lines',
      circularNo: 'DPSS.CO.PD.No.S-257',
      date: 'Jun 20, 2022',
      relativeTime: 'Active',
      summary:
        'RBI clarifies that Master Directions on PPIs do not permit loading of non-bank prepaid wallets from credit lines; any such practice must be discontinued immediately.',
      tags: ['PPI', 'Credit Lines', 'Enforcement', 'Payment Wallets']
    },
    {
      id: 'RBI_TAT_2019',
      flag: '🇮🇳',
      regulator: 'Reserve Bank of India (RBI)',
      title: 'Harmonisation of Turn Around Time (TAT) and Customer Compensation for Failed Transactions',
      circularNo: 'DPSS.CO.PD No.629',
      date: 'Sep 20, 2019',
      relativeTime: 'Mandatory',
      summary:
        'Establishes strict TAT windows for failed digital transactions across UPI, IMPS, and Wallets. Mandates ₹100 per day statutory customer compensation for delayed auto-reversals.',
      tags: ['TAT', 'Customer Compensation', 'Statutory Penalty', '₹100/day']
    }
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-2">
      {/* Hero Welcome Banner - Identical to Reference Pimlico / XIIS UI */}
      <div className="bg-[#0c1322] border border-slate-800/90 rounded-2xl p-7 text-white shadow-md relative overflow-hidden">
        {/* Subtle decorative glow */}
        <div className="absolute -right-20 -top-20 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          {/* Left Greeting & Subtitle */}
          <div className="space-y-3 max-w-2xl">
            <div className="flex items-center space-x-2 text-xs font-semibold text-blue-400">
              <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              <span className="font-mono uppercase tracking-wider">FinReg AI &bull; RBI Intelligence</span>
              <span className="text-[10px] bg-blue-900/80 text-blue-300 px-2 py-0.5 rounded-full border border-blue-700 font-mono">
                {user?.clearanceLevel || 'Full Administrator'}
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
              Welcome back, {user?.name || 'Andrew'}
            </h1>
            <p className="text-slate-300 text-xs md:text-sm leading-relaxed">
              {user?.avatarText === 'PS'
                ? 'Risk & Governance Audit Portal: Monitor statutory breach penalties, ₹100/day TAT compensations, and FLDG compliance exposure.'
                : user?.avatarText === 'VM'
                ? 'Legal & Regulatory Governance Portal: Track statutory circular diffs, legislative repeals, and Master Direction compliance.'
                : 'Executive Compliance Portal: Full unconstrained authority across digital lending, PPIs, penal interest, and statutory enforcement.'}
            </p>

            {/* 4 Quick Action Buttons inside Hero - Dynamically tailored to User Role */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-3">
              {user?.avatarText === 'PS' ? (
                <>
                  <button
                    onClick={() => onNavigate('risk')}
                    className="bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 rounded-xl p-3 text-left transition flex flex-col justify-between group shadow-xs cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-rose-600/20 text-rose-400 flex items-center justify-center mb-2 group-hover:bg-rose-600 group-hover:text-white transition">
                      <ShieldAlert className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Risk Evaluator</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">Penalties & FLDG Breaches</div>
                    </div>
                  </button>

                  <button
                    onClick={() => onNavigate('matrix')}
                    className="bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 rounded-xl p-3 text-left transition flex flex-col justify-between group shadow-xs cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-amber-600/20 text-amber-400 flex items-center justify-center mb-2 group-hover:bg-amber-600 group-hover:text-white transition">
                      <Scale className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Compliance Matrix</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">RE vs LSP Statutory Duties</div>
                    </div>
                  </button>

                  <button
                    onClick={() => onNavigate('documents')}
                    className="bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 rounded-xl p-3 text-left transition flex flex-col justify-between group shadow-xs cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-indigo-600/20 text-indigo-400 flex items-center justify-center mb-2 group-hover:bg-indigo-600 group-hover:text-white transition">
                      <FileText className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Database</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">12 Circulars & PDFs</div>
                    </div>
                  </button>

                  <button
                    onClick={() => onNavigate('benchmark')}
                    className="bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 rounded-xl p-3 text-left transition flex flex-col justify-between group shadow-xs cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-emerald-600/20 text-emerald-400 flex items-center justify-center mb-2 group-hover:bg-emerald-600 group-hover:text-white transition">
                      <Award className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Audit Benchmark</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">RAG Accuracy & Precision</div>
                    </div>
                  </button>
                </>
              ) : user?.avatarText === 'VM' ? (
                <>
                  <button
                    onClick={() => onNavigate('copilot')}
                    className="bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 rounded-xl p-3 text-left transition flex flex-col justify-between group shadow-xs cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center mb-2 group-hover:bg-blue-600 group-hover:text-white transition">
                      <Sparkles className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Legal Copilot</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">Clause Grounding & Citations</div>
                    </div>
                  </button>

                  <button
                    onClick={() => onNavigate('timeline')}
                    className="bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 rounded-xl p-3 text-left transition flex flex-col justify-between group shadow-xs cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-emerald-600/20 text-emerald-400 flex items-center justify-center mb-2 group-hover:bg-emerald-600 group-hover:text-white transition">
                      <Clock className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Timeline Monitors</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">2022 vs 2023 vs 2025 Diffs</div>
                    </div>
                  </button>

                  <button
                    onClick={() => onNavigate('documents')}
                    className="bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 rounded-xl p-3 text-left transition flex flex-col justify-between group shadow-xs cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-indigo-600/20 text-indigo-400 flex items-center justify-center mb-2 group-hover:bg-indigo-600 group-hover:text-white transition">
                      <FileText className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Regulatory Corpus</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">Master Directions & Gazettes</div>
                    </div>
                  </button>

                  <button
                    onClick={() => onNavigate('graph')}
                    className="bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 rounded-xl p-3 text-left transition flex flex-col justify-between group shadow-xs cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-purple-600/20 text-purple-400 flex items-center justify-center mb-2 group-hover:bg-purple-600 group-hover:text-white transition">
                      <Share2 className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Precedence Graph</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">Citation & Repeal Links</div>
                    </div>
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => onNavigate('copilot')}
                    className="bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 rounded-xl p-3 text-left transition flex flex-col justify-between group shadow-xs cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center mb-2 group-hover:bg-blue-600 group-hover:text-white transition">
                      <Sparkles className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Workspace</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">Copilot Q&A & Memos</div>
                    </div>
                  </button>

                  <button
                    onClick={() => onNavigate('documents')}
                    className="bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 rounded-xl p-3 text-left transition flex flex-col justify-between group shadow-xs cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-indigo-600/20 text-indigo-400 flex items-center justify-center mb-2 group-hover:bg-indigo-600 group-hover:text-white transition">
                      <FileText className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Database</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">12 Circulars & PDFs</div>
                    </div>
                  </button>

                  <button
                    onClick={() => onNavigate('timeline')}
                    className="bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 rounded-xl p-3 text-left transition flex flex-col justify-between group shadow-xs cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-emerald-600/20 text-emerald-400 flex items-center justify-center mb-2 group-hover:bg-emerald-600 group-hover:text-white transition">
                      <Clock className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Monitors</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">Staggered Timelines</div>
                    </div>
                  </button>

                  <button
                    onClick={() => onNavigate('matrix')}
                    className="bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 rounded-xl p-3 text-left transition flex flex-col justify-between group shadow-xs cursor-pointer"
                  >
                    <div className="w-7 h-7 rounded-lg bg-amber-600/20 text-amber-400 flex items-center justify-center mb-2 group-hover:bg-amber-600 group-hover:text-white transition">
                      <Scale className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Organisation</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">RE vs LSP Duties</div>
                    </div>
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Right Quadrant: 4 KPI Tiles matching Reference UI */}
          <div className="grid grid-cols-2 gap-3 shrink-0 lg:w-72">
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <Globe className="w-4 h-4 text-blue-400" />
                <span className="text-[10px] uppercase font-mono text-slate-400">Regulator</span>
              </div>
              <div>
                <div className="text-sm font-bold text-white">RBI (India)</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Central Bank Jurisdiction</div>
              </div>
            </div>

            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <Folder className="w-4 h-4 text-indigo-400" />
                <span className="text-[10px] uppercase font-mono text-emerald-400">10 Active</span>
              </div>
              <div>
                <div className="text-sm font-bold text-white">Watchlists</div>
                <div className="text-[10px] text-slate-400 mt-0.5">2 Superseded / Filtered</div>
              </div>
            </div>

            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <Briefcase className="w-4 h-4 text-emerald-400" />
                <span className="text-[10px] uppercase font-mono text-blue-400">2025</span>
              </div>
              <div>
                <div className="text-sm font-bold text-white">Projects</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Digital Lending Baseline</div>
              </div>
            </div>

            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <Mail className="w-4 h-4 text-amber-400" />
                <span className="text-[10px] uppercase font-mono text-emerald-400">Ready</span>
              </div>
              <div>
                <div className="text-sm font-bold text-white">Briefings</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Audit Memos & PDF Export</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Two-Column Grid matching Reference UI Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (Wide 2/3): Regulatory Updates Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  REGULATORY UPDATES
                </span>
                <div className="flex items-center space-x-2 mt-0.5">
                  <h2 className="text-lg font-bold text-slate-900">Latest developments</h2>
                  <span className="bg-blue-50 text-blue-700 text-[11px] font-semibold px-2 py-0.5 rounded-full border border-blue-100">
                    4 active
                  </span>
                  <button
                    onClick={() => {}}
                    title="Refresh Feed"
                    className="text-slate-400 hover:text-slate-600 transition"
                  >
                    <RotateCw className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
              <button
                onClick={() => onNavigate('documents')}
                className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center space-x-1"
              >
                <span>All circulars</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Circular Feed Cards */}
            <div className="space-y-3.5">
              {latestDevelopments.map((dev) => (
                <div
                  key={dev.id}
                  className="p-4 rounded-xl border border-slate-100 bg-slate-50/50 hover:bg-slate-50 hover:border-slate-200 transition space-y-2.5"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start space-x-2.5">
                      <span className="text-base select-none mt-0.5">{dev.flag}</span>
                      <div>
                        <h3 className="text-xs md:text-sm font-bold text-slate-900 hover:text-blue-600 transition cursor-pointer" onClick={() => onNavigate('copilot')}>
                          {dev.title}
                        </h3>
                        <p className="text-[11px] font-mono text-slate-400 mt-0.5">
                          {dev.circularNo} &bull; {dev.date}
                        </p>
                      </div>
                    </div>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">
                      {dev.relativeTime}
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed pl-7">
                    {dev.summary}
                  </p>

                  <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-200/60 pl-7">
                    <div className="flex flex-wrap gap-1.5">
                      {dev.tags.map((tag) => (
                        <span
                          key={tag}
                          className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-white border border-slate-200 text-slate-600"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => onNavigate('copilot')}
                        className="text-[11px] font-semibold text-blue-600 hover:text-blue-700 flex items-center space-x-1 bg-blue-50 hover:bg-blue-100/80 px-2.5 py-1 rounded-lg transition"
                      >
                        <MessageSquare className="w-3 h-3" />
                        <span>Ask Copilot</span>
                      </button>
                      <button
                        onClick={() => onNavigate('documents')}
                        className="text-[11px] font-medium text-slate-600 hover:text-slate-900 flex items-center space-x-1 bg-white border border-slate-200 px-2.5 py-1 rounded-lg transition"
                      >
                        <FileText className="w-3 h-3 text-slate-400" />
                        <span>PDF</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column (Narrow 1/3): Monitoring Watchlists & Insights */}
        <div className="space-y-6">
          {/* Monitoring Watchlists Card */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  MONITORING
                </span>
                <h3 className="text-sm font-bold text-slate-900">Your watchlists</h3>
              </div>
              <button
                onClick={() => onNavigate('timeline')}
                className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center space-x-0.5"
              >
                <span>Manage</span>
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>

            <div className="space-y-2.5">
              <div className="p-3 rounded-xl border border-slate-100 bg-slate-50/60 flex items-center justify-between">
                <div className="space-y-0.5">
                  <div className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
                    <span>12 Regulatory Circulars</span>
                  </div>
                  <div className="text-[11px] text-slate-500">341 PDF pages &bull; Dual-Chunk Indexed</div>
                </div>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-100">
                  Surveillance
                </span>
              </div>

              <div className="p-3 rounded-xl border border-slate-100 bg-slate-50/60 flex items-center justify-between">
                <div className="space-y-0.5">
                  <div className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <span>Enacted: DL Directions 2025</span>
                  </div>
                  <div className="text-[11px] text-slate-500">Effective from 08 May 2025</div>
                </div>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-100">
                  Active
                </span>
              </div>

              <div className="p-3 rounded-xl border border-slate-100 bg-slate-50/60 flex items-center justify-between">
                <div className="space-y-0.5">
                  <div className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                    <span>Para 17 System Audit Directives</span>
                  </div>
                  <div className="text-[11px] text-slate-500">Commenced 15 June 2025</div>
                </div>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-100">
                  In Effect
                </span>
              </div>

              <div className="p-3 rounded-xl border border-slate-100 bg-slate-50/60 flex items-center justify-between">
                <div className="space-y-0.5">
                  <div className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                    <span>Para 6 CIMS & Bureau Feeds</span>
                  </div>
                  <div className="text-[11px] text-slate-500">Commencement: 01 Nov 2025</div>
                </div>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-100">
                  Scheduled
                </span>
              </div>
            </div>
          </div>

          {/* Analysis & Insights Card */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  ANALYSIS
                </span>
                <h3 className="text-sm font-bold text-slate-900">Latest insights</h3>
              </div>
              <button
                onClick={() => onNavigate('matrix')}
                className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center space-x-0.5"
              >
                <span>All</span>
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>

            <div className="space-y-3">
              <div
                onClick={() => onNavigate('timeline')}
                className="flex items-start space-x-3 p-2.5 rounded-xl hover:bg-slate-50 transition cursor-pointer"
              >
                <div className="w-9 h-9 rounded-lg bg-blue-50 border border-blue-100 text-blue-600 flex items-center justify-center shrink-0 mt-0.5">
                  <Building2 className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900 hover:text-blue-600 transition">
                    FLDG Evolution: 2022 Prohibition to 2025 5% Cap
                  </h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    How synthetic securitisation rules evolved into Chapter VI DLG arrangements.
                  </p>
                  <span className="text-[10px] font-mono text-blue-600 mt-1 inline-block">
                    Fintech Lending &bull; 08 May 2025
                  </span>
                </div>
              </div>

              <div
                onClick={() => onNavigate('copilot')}
                className="flex items-start space-x-3 p-2.5 rounded-xl hover:bg-slate-50 transition cursor-pointer"
              >
                <div className="w-9 h-9 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center shrink-0 mt-0.5">
                  <Scale className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900 hover:text-blue-600 transition">
                    Penal Charges Must Never Be Capitalised
                  </h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Compounding penal interest is prohibited; penal charges must be distinct.
                  </p>
                  <span className="text-[10px] font-mono text-indigo-600 mt-1 inline-block">
                    Credit Governance &bull; 18 Aug 2023
                  </span>
                </div>
              </div>

              <div
                onClick={() => onNavigate('risk')}
                className="flex items-start space-x-3 p-2.5 rounded-xl hover:bg-slate-50 transition cursor-pointer"
              >
                <div className="w-9 h-9 rounded-lg bg-emerald-50 border border-emerald-100 text-emerald-600 flex items-center justify-center shrink-0 mt-0.5">
                  <Shield className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900 hover:text-blue-600 transition">
                    Direct Escrow Disbursals: No LSP Pool Accounts
                  </h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Strict pass-through directly to borrower account without intermediary pooling.
                  </p>
                  <span className="text-[10px] font-mono text-emerald-600 mt-1 inline-block">
                    Disbursal Rules &bull; In Force
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
