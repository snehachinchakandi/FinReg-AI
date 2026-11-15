export interface DocumentMetadata {
  doc_id: string;
  title: string;
  circular_no: string;
  regulator: string;
  publish_date: string;
  effective_date: string;
  is_active: boolean;
  superseded_by?: string;
  supersedes?: string;
  url?: string;
  primary_source_url?: string;
  filename: string;
  subject: string;
  parsing_challenges?: string;
  pages: number;
  file_size_bytes?: number;
  valid_until?: string;
}

export interface CorpusSummary {
  total_documents: number;
  total_pages: number;
  active_documents: number;
  superseded_documents: number;
  regulator: string;
}

export interface TimelineEvent {
  id: string;
  date: string;
  title: string;
  circular_no: string;
  doc_id: string;
  category: string;
  summary: string;
  status: string;
  clause_no?: string;
}

export interface ClauseDiff {
  rule_key: string;
  title: string;
  outdated: {
    doc_id: string;
    doc_title: string;
    circular_no: string;
    clause: string;
    valid_until?: string;
    summary: string;
  };
  intermediate?: {
    doc_id: string;
    doc_title: string;
    circular_no: string;
    clause: string;
    valid_until?: string;
    summary: string;
  } | null;
  current: {
    doc_id: string;
    doc_title: string;
    circular_no: string;
    clause: string;
    effective_date?: string;
    summary: string;
  };
  key_phrases: string[];
}

export interface TransitionMilestone {
  effective_date: string;
  event_name: string;
  circular_no: string;
  doc_id: string;
  clause_no: string;
  pre_regime: string;
  post_regime: string;
  is_in_effect: boolean;
  days_elapsed: number;
  days_remaining: number;
}

export interface Citation {
  doc_title?: string;
  doc_id?: string;
  clause?: string;
  publish_date?: string;
  page?: string | number;
  source?: string;
}

export interface QueryResponse {
  query: string;
  config_id: string;
  answer: string;
  is_refusal: boolean;
  citations: Citation[];
  retrieved_chunks: string[];
  latency_ms: number;
  estimated_cost_usd: number;
}

export interface EvalSummaryRecord {
  Configuration: string;
  "Chunking Strategy": string;
  "Retrieval Strategy": string;
  "Hit Rate@5 (n=35)": string | number;
  "MRR (n=35)": string | number;
  "Rank-1 Retrieval Count (n=35)": string | number;
  "Successful Gemini Generations": number;
  "API Quota Errors (429)": number;
  "Local Guardrail Refusals": number;
  "Answer Correctness (Completed)": string;
  "Citation Accuracy (Completed)": string;
  "CRR (n=15)": string;
  "FRR (n=35)": string;
  "Avg Retrieval Latency (All 50, ms)": number;
  "Generation Status": string;
}

export interface ComplianceObligation {
  id: string;
  category: string;
  topic: string;
  re_obligation: string;
  lsp_obligation: string;
  primary_clause: string;
  legal_reference: string;
  governing_circular: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface RiskBreach {
  severity: string;
  rule: string;
  finding: string;
  cited_clause: string;
  remediation: string;
}

export interface RiskEvaluationResponse {
  overall_risk_score: number;
  severity_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'COMPLIANT';
  total_breaches: number;
  breaches: RiskBreach[];
  compensation_payable_inr: number;
  status: 'NON_COMPLIANT' | 'COMPLIANT';
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  year: number;
  status: string;
  pages: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: string;
  detail: string;
}

export interface RegulatoryGraph {
  total_nodes: number;
  total_edges: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface MemoResponse {
  title: string;
  timestamp: string;
  as_of_date: string;
  markdown: string;
  html: string;
}
