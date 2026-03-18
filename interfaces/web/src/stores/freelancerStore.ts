import { create } from 'zustand';
import type {
  FreelanceOpportunity,
  FreelancePlatform,
  PricingParameter,
  EvaluationCriteria,
  OpportunityFilters,
  OpportunityStats,
  CareerInsight,
  LearningComponentPerformance,
  CreateOpportunityRequest,
} from '../types/freelancer';
import * as freelancerService from '../services/freelancerService';

interface FreelancerState {
  // Data
  opportunities: FreelanceOpportunity[];
  selectedOpportunity: FreelanceOpportunity | null;
  platforms: FreelancePlatform[];
  pricingParameters: PricingParameter | null;
  evaluationCriteria: EvaluationCriteria | null;
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
  createOpportunity: (data: CreateOpportunityRequest) => Promise<FreelanceOpportunity | null>;
  updateOpportunityStatus: (id: number, status: FreelanceOpportunity['status']) => Promise<void>;
  acceptOpportunity: (id: number, reason?: string) => Promise<freelancerService.AcceptanceResponse | null>;
  updateOpportunity: (id: number, data: Partial<FreelanceOpportunity>) => Promise<FreelanceOpportunity | null>;
  deleteOpportunity: (id: number) => Promise<void>;
  processOpportunity: (id: number) => Promise<Awaited<ReturnType<typeof freelancerService.analyzeOpportunity>> | null>;
  analyzeAllNewOpportunities: () => Promise<freelancerService.BatchAnalysisResult | null>;

  fetchPlatforms: () => Promise<void>;
  fetchPricingParameters: () => Promise<void>;
  updatePricingParameters: (data: Partial<PricingParameter>) => Promise<void>;
  fetchEvaluationCriteria: () => Promise<void>;
  updateEvaluationCriteria: (data: Partial<EvaluationCriteria>) => Promise<void>;
  optimizeEvaluationCriteria: (basedOnLastN?: number) => Promise<string | null>;

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
  evaluationCriteria: null,
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
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to fetch opportunities', loading: false });
    }
  },

  fetchOpportunityById: async (id) => {
    set({ loading: true, error: null });
    try {
      const opportunity = await freelancerService.getOpportunityById(id);
      set({ selectedOpportunity: opportunity, loading: false });
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to fetch opportunity', loading: false });
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
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to create opportunity', loading: false });
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
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to update opportunity', loading: false });
    }
  },

  acceptOpportunity: async (id, reason?) => {
    set({ loading: true, error: null });
    try {
      const result = await freelancerService.acceptOpportunity(id, reason);
      set((state) => ({
        opportunities: state.opportunities.map((opp) =>
          opp.id === id ? result.opportunity : opp
        ),
        selectedOpportunity:
          state.selectedOpportunity?.id === id ? result.opportunity : state.selectedOpportunity,
        loading: false,
      }));
      return result;
    } catch (error: unknown) {
      set({
        error: error instanceof Error ? error.message : 'Falha ao aceitar oportunidade',
        loading: false,
      });
      return null;
    }
  },

  updateOpportunity: async (id, data) => {
    set({ loading: true, error: null });
    try {
      const updated = await freelancerService.updateOpportunity(id, data);
      set((state) => ({
        opportunities: state.opportunities.map((opp) => (opp.id === id ? updated : opp)),
        selectedOpportunity: state.selectedOpportunity?.id === id ? updated : state.selectedOpportunity,
        loading: false,
      }));
      return updated;
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to update opportunity', loading: false });
      return null;
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
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to delete opportunity', loading: false });
    }
  },

  processOpportunity: async (id) => {
    set({ loading: true, error: null });
    try {
      const result = await freelancerService.analyzeOpportunity(id);

      // Update the opportunity with the analysis results
      set((state) => ({
        opportunities: state.opportunities.map((opp) =>
          opp.id === id
            ? {
                ...result.opportunity,
              }
            : opp
        ),
        selectedOpportunity:
          state.selectedOpportunity?.id === id
            ? {
                ...result.opportunity,
              }
            : state.selectedOpportunity,
        loading: false,
      }));

      return result;
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to process opportunity', loading: false });
      return null;
    }
  },

  analyzeAllNewOpportunities: async () => {
    set({ loading: true, error: null });
    try {
      const result = await freelancerService.analyzeAllNewOpportunities();

      // Refresh opportunities list after batch analysis
      const opportunities = await freelancerService.getOpportunities({});
      set({ opportunities, loading: false });

      return result;
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to analyze opportunities', loading: false });
      return null;
    }
  },

  fetchPlatforms: async () => {
    set({ loading: true, error: null });
    try {
      const platforms = await freelancerService.getPlatforms();
      set({ platforms, loading: false });
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to fetch platforms', loading: false });
    }
  },

  fetchPricingParameters: async () => {
    set({ loading: true, error: null });
    try {
      const params = await freelancerService.getPricingParameters();
      set({ pricingParameters: params, loading: false });
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to fetch pricing parameters', loading: false });
    }
  },

  updatePricingParameters: async (data) => {
    set({ loading: true, error: null });
    try {
      const params = await freelancerService.updatePricingParameters(data);
      set({ pricingParameters: params, loading: false });
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to update pricing parameters', loading: false });
    }
  },

  fetchEvaluationCriteria: async () => {
    set({ loading: true, error: null });
    try {
      const criteria = await freelancerService.getEvaluationCriteria();
      set({ evaluationCriteria: criteria, loading: false });
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to fetch evaluation criteria', loading: false });
    }
  },

  updateEvaluationCriteria: async (data) => {
    set({ loading: true, error: null });
    try {
      const criteria = await freelancerService.updateEvaluationCriteria(data);
      set({ evaluationCriteria: criteria, loading: false });
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to update evaluation criteria', loading: false });
    }
  },

  optimizeEvaluationCriteria: async (basedOnLastN = 30) => {
    set({ loading: true, error: null });
    try {
      const result = await freelancerService.optimizeEvaluationCriteria(basedOnLastN);
      // Refresh criteria after optimization
      const criteria = await freelancerService.getEvaluationCriteria();
      set({ evaluationCriteria: criteria, loading: false });
      return result.report;
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to optimize criteria', loading: false });
      return null;
    }
  },

  fetchStats: async () => {
    set({ loading: true, error: null });
    try {
      const stats = await freelancerService.getOpportunityStats();
      set({ stats, loading: false });
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to fetch stats', loading: false });
    }
  },

  fetchCareerInsights: async () => {
    set({ loading: true, error: null });
    try {
      const insights = await freelancerService.getCareerInsights();
      set({ careerInsights: insights, loading: false });
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to fetch career insights', loading: false });
    }
  },

  fetchLearningPerformance: async () => {
    set({ loading: true, error: null });
    try {
      const performance = await freelancerService.getLearningPerformance();
      set({ learningPerformance: performance, loading: false });
    } catch (error: unknown) {
      set({ error: error instanceof Error ? error.message : 'Failed to fetch learning performance', loading: false });
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
