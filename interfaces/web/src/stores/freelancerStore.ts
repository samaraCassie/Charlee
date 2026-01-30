import { create } from 'zustand';
import {
  FreelanceOpportunity,
  FreelancePlatform,
  PricingParameter,
  OpportunityFilters,
  OpportunityStats,
  CareerInsight,
  LearningComponentPerformance,
} from '../types/freelancer';
import * as freelancerService from '../services/freelancerService';

interface FreelancerState {
  // Data
  opportunities: FreelanceOpportunity[];
  selectedOpportunity: FreelanceOpportunity | null;
  platforms: FreelancePlatform[];
  pricingParameters: PricingParameter | null;
  stats: OpportunityStats | null;
  careerInsights: CareerInsight | null;
  learningPerformance: LearningComponentPerformance | null;

  // UI State
  loading: boolean;
  error: string | null;
  filters: OpportunityFilters;

  // Actions
  fetchOpportunities: (filters?: OpportunityFilters) => Promise<void>;
  fetchOpportunityById: (id: number) => Promise<void>;
  createOpportunity: (data: any) => Promise<FreelanceOpportunity | null>;
  updateOpportunityStatus: (id: number, status: FreelanceOpportunity['status']) => Promise<void>;
  deleteOpportunity: (id: number) => Promise<void>;
  processOpportunity: (id: number) => Promise<any>;

  fetchPlatforms: () => Promise<void>;
  fetchPricingParameters: () => Promise<void>;
  updatePricingParameters: (data: Partial<PricingParameter>) => Promise<void>;

  fetchStats: () => Promise<void>;
  fetchCareerInsights: () => Promise<void>;
  fetchLearningPerformance: () => Promise<void>;

  setFilters: (filters: OpportunityFilters) => void;
  clearFilters: () => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

export const useFreelancerStore = create<FreelancerState>((set, get) => ({
  // Initial state
  opportunities: [],
  selectedOpportunity: null,
  platforms: [],
  pricingParameters: null,
  stats: null,
  careerInsights: null,
  learningPerformance: null,
  loading: false,
  error: null,
  filters: {},

  // Actions
  fetchOpportunities: async (filters) => {
    set({ loading: true, error: null });
    try {
      const opportunities = await freelancerService.getOpportunities(filters || get().filters);
      set({ opportunities, loading: false });
    } catch (error: any) {
      set({ error: error.message || 'Failed to fetch opportunities', loading: false });
    }
  },

  fetchOpportunityById: async (id) => {
    set({ loading: true, error: null });
    try {
      const opportunity = await freelancerService.getOpportunityById(id);
      set({ selectedOpportunity: opportunity, loading: false });
    } catch (error: any) {
      set({ error: error.message || 'Failed to fetch opportunity', loading: false });
    }
  },

  createOpportunity: async (data) => {
    set({ loading: true, error: null });
    try {
      const opportunity = await freelancerService.createOpportunity(data);
      set((state) => ({
        opportunities: [opportunity, ...state.opportunities],
        loading: false,
      }));
      return opportunity;
    } catch (error: any) {
      set({ error: error.message || 'Failed to create opportunity', loading: false });
      return null;
    }
  },

  updateOpportunityStatus: async (id, status) => {
    set({ loading: true, error: null });
    try {
      const updated = await freelancerService.updateOpportunityStatus(id, status);
      set((state) => ({
        opportunities: state.opportunities.map((opp) => (opp.id === id ? updated : opp)),
        selectedOpportunity: state.selectedOpportunity?.id === id ? updated : state.selectedOpportunity,
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message || 'Failed to update opportunity', loading: false });
    }
  },

  deleteOpportunity: async (id) => {
    set({ loading: true, error: null });
    try {
      await freelancerService.deleteOpportunity(id);
      set((state) => ({
        opportunities: state.opportunities.filter((opp) => opp.id !== id),
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message || 'Failed to delete opportunity', loading: false });
    }
  },

  processOpportunity: async (id) => {
    set({ loading: true, error: null });
    try {
      const result = await freelancerService.processOpportunity({ opportunity_id: id });

      // Update the opportunity with the processing results
      set((state) => ({
        opportunities: state.opportunities.map((opp) =>
          opp.id === id
            ? {
                ...opp,
                risk_assessment: result.risk_assessment,
                financial_calculation: result.financial_calculation,
                pricing_suggestion: result.pricing_suggestion,
              }
            : opp
        ),
        selectedOpportunity:
          state.selectedOpportunity?.id === id
            ? {
                ...state.selectedOpportunity,
                risk_assessment: result.risk_assessment,
                financial_calculation: result.financial_calculation,
                pricing_suggestion: result.pricing_suggestion,
              }
            : state.selectedOpportunity,
        loading: false,
      }));

      return result;
    } catch (error: any) {
      set({ error: error.message || 'Failed to process opportunity', loading: false });
      return null;
    }
  },

  fetchPlatforms: async () => {
    set({ loading: true, error: null });
    try {
      const platforms = await freelancerService.getPlatforms();
      set({ platforms, loading: false });
    } catch (error: any) {
      set({ error: error.message || 'Failed to fetch platforms', loading: false });
    }
  },

  fetchPricingParameters: async () => {
    set({ loading: true, error: null });
    try {
      const params = await freelancerService.getPricingParameters();
      set({ pricingParameters: params, loading: false });
    } catch (error: any) {
      set({ error: error.message || 'Failed to fetch pricing parameters', loading: false });
    }
  },

  updatePricingParameters: async (data) => {
    set({ loading: true, error: null });
    try {
      const params = await freelancerService.updatePricingParameters(data);
      set({ pricingParameters: params, loading: false });
    } catch (error: any) {
      set({ error: error.message || 'Failed to update pricing parameters', loading: false });
    }
  },

  fetchStats: async () => {
    set({ loading: true, error: null });
    try {
      const stats = await freelancerService.getOpportunityStats();
      set({ stats, loading: false });
    } catch (error: any) {
      set({ error: error.message || 'Failed to fetch stats', loading: false });
    }
  },

  fetchCareerInsights: async () => {
    set({ loading: true, error: null });
    try {
      const insights = await freelancerService.getCareerInsights();
      set({ careerInsights: insights, loading: false });
    } catch (error: any) {
      set({ error: error.message || 'Failed to fetch career insights', loading: false });
    }
  },

  fetchLearningPerformance: async () => {
    set({ loading: true, error: null });
    try {
      const performance = await freelancerService.getLearningPerformance();
      set({ learningPerformance: performance, loading: false });
    } catch (error: any) {
      set({ error: error.message || 'Failed to fetch learning performance', loading: false });
    }
  },

  setFilters: (filters) => {
    set({ filters });
  },

  clearFilters: () => {
    set({ filters: {} });
  },

  setError: (error) => {
    set({ error });
  },

  clearError: () => {
    set({ error: null });
  },
}));
