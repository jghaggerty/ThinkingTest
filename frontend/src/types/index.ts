// API Types matching backend schema

export type EvaluationStatus = 'pending' | 'running' | 'completed' | 'failed';
export type ZoneStatus = 'green' | 'yellow' | 'red';
export type HeuristicType = 'anchoring' | 'loss_aversion' | 'sunk_cost' | 'confirmation_bias' | 'availability_heuristic';
export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type Impact = 'low' | 'medium' | 'high';
export type Difficulty = 'easy' | 'moderate' | 'complex';

export interface Evaluation {
  id: string;
  ai_system_name: string;
  heuristic_types: string[];
  iteration_count: number;
  status: EvaluationStatus;
  created_at: string;
  completed_at: string | null;
  overall_score: number | null;
  zone_status: ZoneStatus | null;
}

export interface EvaluationCreate {
  ai_system_name: string;
  heuristic_types: string[];
  iteration_count: number;
}

export interface EvaluationList {
  evaluations: Evaluation[];
  total: number;
  limit: number;
  offset: number;
}

export interface HeuristicFinding {
  id: string;
  evaluation_id: string;
  heuristic_type: HeuristicType;
  severity: Severity;
  severity_score: number;
  confidence_level: number;
  detection_count: number;
  example_instances: string[];
  pattern_description: string;
  created_at: string;
}

export interface HeuristicFindingsList {
  findings: HeuristicFinding[];
  total: number;
}

export interface Recommendation {
  id: string;
  evaluation_id: string;
  heuristic_type: string;
  priority: number;
  action_title: string;
  technical_description: string;
  simplified_description: string;
  estimated_impact: Impact;
  implementation_difficulty: Difficulty;
  created_at: string;
}

export interface RecommendationsList {
  recommendations: Recommendation[];
  total: number;
}

export interface Baseline {
  id: string;
  name: string;
  green_zone_max: number;
  yellow_zone_max: number;
  statistical_params: {
    mean: number;
    std_dev: number;
    sample_size: number;
  };
  created_at: string;
}

export interface TrendsResponse {
  evaluation_id: string;
  current_zone: string;
  time_series: Array<{
    timestamp: string;
    score: number;
    zone: string;
  }>;
  drift_alerts: Array<{
    message: string;
    z_score?: number;
    deviation?: number;
  }>;
}
