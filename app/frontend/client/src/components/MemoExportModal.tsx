import React, { useState } from 'react';
import { 
  X, 
  Download, 
  Printer, 
  FileText, 
  Check, 
  Copy,
  Sparkles
} from 'lucide-react';
import { apiClient } from '../api/client';
import { Citation } from '../types';

interface MemoExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  query: string;
  answer: string;
  citations: Citation[];
  configId: string;
}

export const MemoExportModal: React.FC<MemoExportModalProps> = ({
  isOpen,
  onClose,
  query,
  answer,
  citations,
  configId
}) => {
  const [title, setTitle] = useState('Regulatory Compliance Advisory Memorandum');
  const [author, setAuthor] = useState('Compliance & Legal Advisory Officer');
  const [organization, setOrganization] = useState('FinReg AI Intelligence Practice');
  const [memoData, setMemoData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'PREVIEW' | 'MARKDOWN'>('PREVIEW');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await apiClient.exportComplianceMemo({
        title,
        query,
        answer,
        citations,
        config_id: configId,
        author,
        organization,
        as_of_date: '2026-11-14'
      });
      setMemoData(res);
    } catch (err) {
      console.error('Failed to generate compliance memo:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    if (!memoData?.html) return;
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(memoData.html);
      printWindow.document.close();
      printWindow.focus();
      printWindow.print();
    }
  };

  const handleDownloadMd = () => {
    if (!memoData?.markdown) return;
    const blob = new Blob([memoData.markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Compliance_Memo_${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleCopyMd = () => {
    if (!memoData?.markdown) return;
    navigator.clipboard.writeText(memoData.markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-blue-400" />
            <h3 className="text-base font-bold text-white">Generate Formal Compliance Advisory Memo</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-4 flex-1">
          {/* Controls */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div>
              <label className="text-[11px] font-semibold text-slate-400 block mb-1">Memo Title:</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white"
              />
            </div>
            <div>
              <label className="text-[11px] font-semibold text-slate-400 block mb-1">Author Title:</label>
              <input
                type="text"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white"
              />
            </div>
            <div>
              <label className="text-[11px] font-semibold text-slate-400 block mb-1">Division / Org:</label>
              <input
                type="text"
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-4 py-2 rounded-xl text-xs flex items-center space-x-1.5 shadow"
            >
              <Sparkles className="w-4 h-4" />
              <span>{memoData ? 'Update Memo' : 'Generate Compliance Memo'}</span>
            </button>
          </div>

          {/* Memo Preview Area */}
          {memoData && (
            <div className="space-y-3 pt-2 border-t border-slate-800">
              <div className="flex items-center justify-between">
                <div className="flex space-x-2 text-xs">
                  <button
                    onClick={() => setActiveTab('PREVIEW')}
                    className={`px-3 py-1 rounded-lg font-medium transition ${
                      activeTab === 'PREVIEW' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Printable Document
                  </button>
                  <button
                    onClick={() => setActiveTab('MARKDOWN')}
                    className={`px-3 py-1 rounded-lg font-medium transition ${
                      activeTab === 'MARKDOWN' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Raw Markdown
                  </button>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleCopyMd}
                    className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg text-xs font-medium flex items-center space-x-1 border border-slate-700"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                  </button>
                  <button
                    onClick={handleDownloadMd}
                    className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg text-xs font-medium flex items-center space-x-1 border border-slate-700"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download .md</span>
                  </button>
                  <button
                    onClick={handlePrint}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1 shadow"
                  >
                    <Printer className="w-3.5 h-3.5" />
                    <span>Print / PDF</span>
                  </button>
                </div>
              </div>

              {activeTab === 'PREVIEW' ? (
                <div className="bg-white text-slate-900 p-6 rounded-xl border border-slate-300 font-sans text-xs space-y-4 max-h-[400px] overflow-y-auto shadow-inner">
                  <div className="border-b border-slate-900 pb-3">
                    <h2 className="text-base font-bold text-slate-900">{memoData.title}</h2>
                    <div className="text-[10px] text-slate-500 font-mono mt-1">
                      DATE: {memoData.timestamp} | LEGAL AS-OF DATE: {memoData.as_of_date} | AUTHOR: {author}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-bold text-slate-800 uppercase tracking-wider text-[10px] mb-1">
                      1. Compliance Inquiry
                    </h4>
                    <p className="bg-slate-100 p-2.5 rounded border-l-2 border-blue-600 italic">
                      {query}
                    </p>
                  </div>

                  <div>
                    <h4 className="font-bold text-slate-800 uppercase tracking-wider text-[10px] mb-1">
                      2. Regulatory Determination & Analysis
                    </h4>
                    <p className="whitespace-pre-wrap leading-relaxed">{answer}</p>
                  </div>

                  <div>
                    <h4 className="font-bold text-slate-800 uppercase tracking-wider text-[10px] mb-1">
                      3. Statutory Authorities & Verified Citations
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-[11px] text-slate-700">
                      {citations.map((c, i) => (
                        <li key={i}>
                          <strong>{c.doc_title || 'RBI Circular'}</strong> (Clause: {c.clause || 'N/A'}, Date: {c.publish_date || 'N/A'}, Page: {c.page || 'N/A'})
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <textarea
                  readOnly
                  value={memoData.markdown}
                  className="w-full h-[400px] bg-slate-950 font-mono text-xs text-slate-300 p-4 rounded-xl border border-slate-800 focus:outline-none"
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
