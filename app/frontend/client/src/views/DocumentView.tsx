import React, { useEffect, useState } from 'react';
import { 
  FileText, 
  Search, 
  ExternalLink, 
  CheckCircle2, 
  AlertTriangle, 
  Download, 
  Layers,
  ChevronRight
} from 'lucide-react';
import { apiClient } from '../api/client';
import { DocumentMetadata } from '../types';

interface DocumentViewProps {
  selectedDocId?: string | null;
}

export const DocumentView: React.FC<DocumentViewProps> = ({ selectedDocId }) => {
  const [docs, setDocs] = useState<DocumentMetadata[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<DocumentMetadata | null>(null);
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState<'ALL' | 'ACTIVE' | 'SUPERSEDED'>('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDocs() {
      try {
        const res = await apiClient.getDocuments();
        setDocs(res);
        if (selectedDocId) {
          const match = res.find((d) => d.doc_id === selectedDocId);
          if (match) setSelectedDoc(match);
        } else if (res.length > 0) {
          setSelectedDoc(res[0]);
        }
      } catch (err) {
        console.error('Failed to load documents:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDocs();
  }, [selectedDocId]);

  const filteredDocs = docs.filter((d) => {
    const q = (search || '').toLowerCase();
    const matchesSearch = 
      (d.title || '').toLowerCase().includes(q) ||
      (d.doc_id || '').toLowerCase().includes(q) ||
      (d.circular_no || '').toLowerCase().includes(q) ||
      (d.subject || '').toLowerCase().includes(q);
    if (!matchesSearch) return false;
    if (filterStatus === 'ACTIVE') return d.is_active;
    if (filterStatus === 'SUPERSEDED') return !d.is_active;
    return true;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-2">
      {/* View Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-200/80 pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <FileText className="w-5 h-5 text-blue-600" />
            <span>Authentic Regulatory Document Corpus & In-Situ PDF Viewer</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            12 official Reserve Bank of India (RBI) notifications and Master Directions totaling 341 PDF pages.
          </p>
        </div>
        <div className="text-xs font-mono text-slate-500 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
          Corpus: 10 Active &bull; 2 Superseded
        </div>
      </div>

      {/* Main Split-Screen Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[750px]">
        {/* Left Column: Document Catalog (5 cols) */}
        <div className="lg:col-span-5 bg-white border border-slate-200/90 rounded-2xl p-4 flex flex-col space-y-4 shadow-xs">
          {/* Search & Filter Bar */}
          <div className="space-y-2">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                placeholder="Search circulars by title, ID, or subject..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-500 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none transition"
              />
            </div>

            <div className="flex gap-1.5 bg-slate-100 p-1 rounded-xl border border-slate-200 text-[11px]">
              <button
                onClick={() => setFilterStatus('ALL')}
                className={`flex-1 py-1 rounded-lg font-medium transition cursor-pointer ${
                  filterStatus === 'ALL' ? 'bg-white text-slate-900 font-bold shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                All ({docs.length})
              </button>
              <button
                onClick={() => setFilterStatus('ACTIVE')}
                className={`flex-1 py-1 rounded-lg font-medium transition cursor-pointer ${
                  filterStatus === 'ACTIVE' ? 'bg-emerald-600 text-white font-bold shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Active ({docs.filter((d) => d.is_active).length})
              </button>
              <button
                onClick={() => setFilterStatus('SUPERSEDED')}
                className={`flex-1 py-1 rounded-lg font-medium transition cursor-pointer ${
                  filterStatus === 'SUPERSEDED' ? 'bg-rose-600 text-white font-bold shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Superseded ({docs.filter((d) => !d.is_active).length})
              </button>
            </div>
          </div>

          {/* Document List */}
          <div className="flex-1 overflow-y-auto space-y-2 pr-1 max-h-[640px]">
            {filteredDocs.map((doc) => {
              const isSelected = selectedDoc?.doc_id === doc.doc_id;
              return (
                <div
                  key={doc.doc_id}
                  onClick={() => setSelectedDoc(doc)}
                  className={`p-3.5 rounded-xl border text-xs cursor-pointer transition ${
                    isSelected
                      ? 'bg-blue-50/70 border-blue-400/90 shadow-xs'
                      : 'bg-white border-slate-200/80 hover:border-slate-300 hover:bg-slate-50/50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[10px] text-blue-700 font-semibold bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                      {doc.doc_id}
                    </span>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                      doc.is_active 
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                        : 'bg-rose-50 text-rose-700 border border-rose-200'
                    }`}>
                      {doc.is_active ? 'ACTIVE' : 'SUPERSEDED'}
                    </span>
                  </div>

                  <h3 className="font-semibold text-slate-900 mt-1.5 leading-snug line-clamp-2">
                    {doc.title}
                  </h3>

                  <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-100">
                    <span>{doc.publish_date}</span>
                    <span>{doc.pages} pages</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: PDF Viewer & Document Detail (7 cols) */}
        <div className="lg:col-span-7 bg-white border border-slate-200/90 rounded-2xl p-5 flex flex-col space-y-4 shadow-xs">
          {selectedDoc ? (
            <>
              {/* Document Header & Metadata */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-100 pb-4">
                <div>
                  <h3 className="text-base font-bold text-slate-900 leading-tight">
                    {selectedDoc.title}
                  </h3>
                  <p className="text-xs text-slate-500 font-mono mt-0.5">
                    {selectedDoc.circular_no}
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <a
                    href={apiClient.getDocumentPdfUrl(selectedDoc.doc_id)}
                    target="_blank"
                    rel="noreferrer"
                    className="bg-[#0c1322] hover:bg-blue-600 text-white px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition shadow-xs"
                  >
                    <span>Full Window</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>

              {/* Subject & Challenges */}
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-xs text-slate-700 space-y-1">
                <div><span className="font-semibold text-slate-900">Subject:</span> {selectedDoc.subject}</div>
                {selectedDoc.parsing_challenges && (
                  <div className="text-slate-500 text-[11px]">
                    <span className="font-semibold text-amber-700">Layout Challenges:</span> {selectedDoc.parsing_challenges}
                  </div>
                )}
              </div>

              {/* In-Situ PDF Viewer Frame */}
              <div className="flex-1 min-h-[520px] bg-slate-100 rounded-xl border border-slate-200 overflow-hidden relative">
                <iframe
                  src={`${apiClient.getDocumentPdfUrl(selectedDoc.doc_id)}#toolbar=1&navpanes=0`}
                  title={selectedDoc.title}
                  className="w-full h-full border-0 absolute inset-0"
                />
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-slate-400 text-xs">
              Select a regulatory circular from the list to view its PDF and metadata.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
