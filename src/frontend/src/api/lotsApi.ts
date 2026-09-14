import { apiClient } from './apiClient';

export interface LotSummary {
  id: string;
  lot_id: string;
  status: string;
  wafer_image_path: string;
}

export interface RootCause {
  feature: string;
  contribution: number;
  direction: 'increases_risk' | 'decreases_risk' | 'neutral';
  rank: number;
}

export interface Recommendation {
  action: string;
  reason: string;
}

export interface AIExplanation {
  summary: string;
  root_cause_explanation: string;
  evidence: string[];
  corrective_actions: string[];
  next_checks: string[];
  limitations: string[];
  status: string;
  message?: string;
}

export interface AnalysisResponse {
  lot_id: string;
  wafer_analysis: {
    prediction: string;
    confidence: number;
  };
  process_analysis: {
    prediction: string;
    probability: number;
  };
  root_causes: {
    feature_name: string;
    importance: number;
    direction: string;
  }[];
  overall_risk: {
    level: string;
    score: number;
  };
  recommendations: Recommendation[];
  ai_explanation?: AIExplanation;
  analysis_timestamp: string;
}

export const lotsApi = {
  getLots: async (): Promise<LotSummary[]> => {
    const response = await apiClient.get('/api/lots');
    return response.data;
  },

  getLot: async (lotId: string): Promise<any> => {
    const response = await apiClient.get(`/api/lots/${lotId}`);
    return response.data;
  },
  
  analyzeLot: async (lotId: string): Promise<AnalysisResponse> => {
    const response = await apiClient.post(`/api/lots/${lotId}/analyze`);
    return response.data;
  },

  getRootCauses: async (lotId: string): Promise<{ root_causes: RootCause[] }> => {
    const response = await apiClient.get(`/api/lots/${lotId}/root-causes`);
    return response.data;
  }
};
