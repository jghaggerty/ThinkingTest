import axios from 'axios';
import type {
  Evaluation,
  EvaluationCreate,
  EvaluationList,
  HeuristicFindingsList,
  HeuristicFinding,
  RecommendationsList,
  Baseline,
  TrendsResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Evaluations API
export const evaluationsAPI = {
  create: async (data: EvaluationCreate): Promise<Evaluation> => {
    const response = await api.post('/api/evaluations', data);
    return response.data;
  },

  list: async (limit = 10, offset = 0): Promise<EvaluationList> => {
    const response = await api.get('/api/evaluations', {
      params: { limit, offset },
    });
    return response.data;
  },

  get: async (id: string): Promise<Evaluation> => {
    const response = await api.get(`/api/evaluations/${id}`);
    return response.data;
  },

  execute: async (id: string): Promise<Evaluation> => {
    const response = await api.post(`/api/evaluations/${id}/execute`);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/evaluations/${id}`);
  },
};

// Heuristics API
export const heuristicsAPI = {
  getAll: async (evaluationId: string): Promise<HeuristicFindingsList> => {
    const response = await api.get(`/api/evaluations/${evaluationId}/heuristics`);
    return response.data;
  },

  getByType: async (evaluationId: string, heuristicType: string): Promise<HeuristicFinding> => {
    const response = await api.get(`/api/evaluations/${evaluationId}/heuristics/${heuristicType}`);
    return response.data;
  },
};

// Recommendations API
export const recommendationsAPI = {
  getAll: async (evaluationId: string, mode: 'technical' | 'simplified' | 'both' = 'both'): Promise<RecommendationsList> => {
    const response = await api.get(`/api/evaluations/${evaluationId}/recommendations`, {
      params: { mode },
    });
    return response.data;
  },
};

// Baselines API
export const baselinesAPI = {
  create: async (evaluationId: string, zoneThresholds?: { green_zone_max?: number; yellow_zone_max?: number }): Promise<Baseline> => {
    const response = await api.post('/api/baselines', {
      evaluation_id: evaluationId,
      zone_thresholds: zoneThresholds,
    });
    return response.data;
  },

  get: async (baselineId: string): Promise<Baseline> => {
    const response = await api.get(`/api/baselines/${baselineId}`);
    return response.data;
  },

  getTrends: async (evaluationId: string): Promise<TrendsResponse> => {
    const response = await api.get(`/api/baselines/evaluations/${evaluationId}/trends`);
    return response.data;
  },
};

export default api;
