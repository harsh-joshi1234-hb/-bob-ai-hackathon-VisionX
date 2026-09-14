import { apiClient } from './apiClient';

export interface UpcomingBatch {
  batch_id: string;
  scheduled_at: string;
  status: string;
  predicted_risk?: number;
  risk_level?: string;
  flag_reason?: string;
}

export interface BatchAnalysisResponse {
  batch_id: string;
  risk: number;
  risk_level: string;
  top_signals: {
    feature: string;
    contribution: number;
    direction: string;
    rank: number;
  }[];
  reason: string;
  recommended_action: string;
}

export const batchesApi = {
  getUpcomingBatches: async (): Promise<UpcomingBatch[]> => {
    const response = await apiClient.get('/api/batches/upcoming');
    return response.data;
  },

  getBatch: async (batchId: string): Promise<UpcomingBatch> => {
    const response = await apiClient.get(`/api/batches/${batchId}`);
    return response.data;
  },
  
  analyzeBatch: async (batchId: string): Promise<BatchAnalysisResponse> => {
    const response = await apiClient.post(`/api/batches/${batchId}/analyze`);
    return response.data;
  }
};
