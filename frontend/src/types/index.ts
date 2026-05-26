// --- Document Types ---
export interface Document {
  id: string;
  filename: string;
  source_type: 'interview' | 'report' | 'linkedin' | 'analysis';
  author?: string;
  doc_date?: string;
  metadata: Record<string, any>;
  created_at: string;
}

export interface IngestionResponse {
  document_id: string;
  chunk_count: number;
  entities_extracted: number;
  edges_created: number;
}

// --- Graph Types ---
export interface GraphNode {
  id: string;
  label: string;
  type: 'person' | 'company' | 'theme' | 'concept' | 'insight';
  description?: string;
  source_ids: string[];
  properties: Record<string, any>;
  created_at: string;
}

export interface GraphEdge {
  id: string;
  source_node: string;
  target_node: string;
  relation: string;
  weight: number;
  source_ids: string[];
  properties: Record<string, any>;
  created_at: string;
}

export interface SubgraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphStats {
  total_nodes: number;
  total_edges: number;
  type_breakdown: Record<string, number>;
}

// --- Chat Types ---
export interface Citation {
  chunk_id?: string;
  document_id: string;
  filename: string;
  source_type: 'interview' | 'report' | 'linkedin' | 'analysis';
  excerpt: string;
}

export interface StatementLabel {
  text: string;
  label: 'fact' | 'opinion' | 'inference';
}

export interface ChatMessageRequest {
  session_id: string;
  message: string;
  output_format?: 'text' | 'swot' | 'pestel';
}

export interface ChatMessageResponse {
  answer: string;
  citations: Citation[];
  output_type: string;
  confidence: number;
  fact_vs_opinion_labels: StatementLabel[];
}

export interface MessageHistoryItem {
  role: 'user' | 'assistant';
  content: string;
  citations: Citation[];
  timestamp: string;
}

export interface ChatHistoryResponse {
  session_id: string;
  user_id: string;
  messages: MessageHistoryItem[];
  created_at: string;
  updated_at: string;
}

// --- Simulation Types ---
export interface StepOption {
  label: string;
  next_step_id?: string;
  score_delta: number;
  score_threshold_min?: number;
  score_threshold_max?: number;
}

export interface ScenarioStep {
  id: string;
  scenario_id: string;
  content: string;
  step_type: 'prompt' | 'decision' | 'evaluation' | 'end';
  options: StepOption[];
  evaluation_criteria: Record<string, any>;
  knowledge_refs: string[];
  referenced_nodes?: Array<{
    id: string;
    label: string;
    type: string;
    description: string;
  }>;
  created_at: string;
}

export interface Scenario {
  id: string;
  title: string;
  description?: string;
  domain: 'interview' | 'negotiation' | 'leadership';
  root_step_id?: string;
  metadata: Record<string, any>;
  created_at: string;
}

export interface SimulationStartResponse {
  session_id: string;
  first_step?: ScenarioStep;
}

export interface SimulationResponseResponse {
  next_step?: ScenarioStep;
  score_delta: number;
  feedback: string;
  is_complete: boolean;
}

export interface SimulationSession {
  id: string;
  scenario_id: string;
  user_id: string;
  current_step?: string;
  path_taken: Array<{
    step_id: string;
    step_type: string;
    response: string | number;
    score_delta: number;
    feedback: string;
    timestamp: string;
  }>;
  scores: {
    content: number;
    reasoning: number;
    total: number;
  };
  status: 'active' | 'completed' | 'abandoned';
  started_at: string;
  completed_at?: string;
}

export interface SimulationReportResponse {
  session: SimulationSession;
  scenario_title: string;
  step_breakdown: Array<{
    step_id: string;
    step_content: string;
    step_type: string;
    user_response: string | number;
    score_delta: number;
    feedback: string;
  }>;
  recommended_nodes: Array<{
    id: string;
    label: string;
    type: string;
    description: string;
  }>;
}
