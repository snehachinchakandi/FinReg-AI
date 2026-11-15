import axios from 'axios';
import {
  DocumentMetadata,
  CorpusSummary,
  TimelineEvent,
  ClauseDiff,
  TransitionMilestone,
  QueryResponse,
  EvalSummaryRecord
} from '../types';

const api = axios.create({
  baseURL: '', // Uses Vite proxy
  timeout: 30000,
});

export const apiClient = {
  // Baseline Endpoints
  async health(): Promise<{ status: string; service: string; version: string }> {
    const res = await api.get('/health');
    return res.data;
  },

  async query(
    queryText: string,
    configId: string = 'C4',
    topK: number = 5,
    allowSuperseded: boolean = false
  ): Promise<QueryResponse> {
    const res = await api.post('/query', {
      query: queryText,
      config_id: configId,
      top_k: topK,
      allow_superseded: allowSuperseded
    });
    return res.data;
  },

  async getEvaluationSummary(): Promise<EvalSummaryRecord[]> {
    const res = await api.get('/eval_summary');
    return res.data;
  },

  // Document Intelligence Endpoints
  async getDocuments(): Promise<DocumentMetadata[]> {
    const res = await api.get('/api/documents');
    return res.data;
  },

  async getCorpusSummary(): Promise<CorpusSummary> {
    const res = await api.get('/api/documents/summary');
    return res.data;
  },

  async getDocumentDetails(docId: string): Promise<DocumentMetadata> {
    const res = await api.get(`/api/documents/${docId}`);
    return res.data;
  },

  getDocumentPdfUrl(docId: string): string {
    return `/api/documents/${docId}/pdf`;
  },

  // Evolution & Versioning Endpoints
  async getTimeline(): Promise<{ current_system_date: string; total_milestones: number; events: TimelineEvent[] }> {
    const res = await api.get('/api/evolution/timeline');
    return res.data;
  },

  async getClauseDiffs(): Promise<ClauseDiff[]> {
    const res = await api.get('/api/evolution/diffs');
    return res.data;
  },

  async getTransitions(): Promise<{ current_system_date: string; transitions: TransitionMilestone[] }> {
    const res = await api.get('/api/evolution/transitions');
    return res.data;
  },

  async getAsOfSimulation(dateStr: string): Promise<any> {
    const res = await api.get(`/api/evolution/as-of?date_str=${dateStr}`);
    return res.data;
  },

  // Compliance & Risk Intelligence Endpoints
  async getComplianceMatrix(category?: string): Promise<{ total: number; obligations: any[] }> {
    const url = category ? `/api/compliance/matrix?category=${encodeURIComponent(category)}` : '/api/compliance/matrix';
    const res = await api.get(url);
    return res.data;
  },

  async evaluateRisk(scenario: any): Promise<any> {
    const res = await api.post('/api/compliance/risk-eval', scenario);
    return res.data;
  },

  async getDependencyGraph(): Promise<any> {
    const res = await api.get('/api/compliance/graph');
    return res.data;
  },

  // Export & Audit Memo Endpoints
  async exportComplianceMemo(memoData: any): Promise<any> {
    const res = await api.post('/api/export/compliance-memo', memoData);
    return res.data;
  }
};
