import api from './api';
import type { CycleData, CyclePhase } from '@/stores/cycleStore';

export const cycleService = {
  // Get all cycle data
  async getCycles(): Promise<CycleData[]> {
    const response = await api.get('/cycles');
    return response.data;
  },

  // Get cycle by ID
  async getCycle(id: string): Promise<CycleData> {
    const response = await api.get(`/cycles/${id}`);
    return response.data;
  },

  // Create new cycle entry
  async createCycle(
    cycle: Omit<CycleData, 'id' | 'createdAt' | 'updatedAt'>
  ): Promise<CycleData> {
    const response = await api.post('/cycles', cycle);
    return response.data;
  },

  // Update cycle
  async updateCycle(id: string, updates: Partial<CycleData>): Promise<CycleData> {
    const response = await api.patch(`/cycles/${id}`, updates);
    return response.data;
  },

  // Get current phase
  async getCurrentPhase(): Promise<CyclePhase> {
    const response = await api.get('/cycles/current-phase');
    return response.data.phase;
  },

  // Get cycle predictions
  async getPredictions() {
    const response = await api.get('/cycles/predictions');
    return response.data;
  },

  // Get productivity by phase
  async getProductivityByPhase() {
    const response = await api.get('/cycles/productivity');
    return response.data;
  },

  // Get phase recommendations
  async getPhaseRecommendations(phase: CyclePhase) {
    const response = await api.get(`/cycles/recommendations/${phase}`);
    return response.data;
  },
};