import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const getHealth = () => api.get('/api/health');

export const getLots = () => api.get('/api/lots');
export const getLot = (lotId) => api.get(`/api/lots/${lotId}`);
export const analyzeLot = (lotId) => api.post(`/api/lots/${lotId}/analyze`);

export const analyzeWafer = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/analyze/wafer', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const analyzeProcess = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/analyze/process', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const analyzeNewLot = (lotId, waferFile, processFile) => {
  const formData = new FormData();
  formData.append('lot_id', lotId);
  if (waferFile) formData.append('waferFile', waferFile);
  if (processFile) formData.append('processFile', processFile);
  return api.post('/api/analyze/new-lot', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const getUpcomingBatches = () => api.get('/api/batches/upcoming');
export const getUpcomingBatch = (batchId) => api.get(`/api/batches/${batchId}`);

export const getAnalyses = () => api.get('/api/analyses');
export const getModels = () => api.get('/api/models');
