import api from './api';
import type {
  FreelanceOpportunity,
  FreelancePlatform,
  PricingParameter,
  RiskAssessment,
  FinancialCalculation,
  PricingSuggestion,
  NegotiationResponse,
  CareerInsight,
  LearningComponentPerformance,
  CreateOpportunityRequest,
  ProcessOpportunityRequest,
  CalculateFinancialRequest,
  GenerateNegotiationRequest,
  OpportunityFilters,
  OpportunityStats,
} from '../types/freelancer';

const BASE_URL = '/v1';

// Opportunities
export const getOpportunities = async (filters?: OpportunityFilters): Promise<FreelanceOpportunity[]> => {
  const params = new URLSearchParams();
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach((v) => params.append(key, v.toString()));
        } else {
          params.append(key, value.toString());
        }
      }
    });
  }
  const response = await api.get(`${BASE_URL}/opportunities?${params.toString()}`);
  return response.data;
};

export const getOpportunityById = async (id: number): Promise<FreelanceOpportunity> => {
  const response = await api.get(`${BASE_URL}/opportunities/${id}`);
  return response.data;
};

export const createOpportunity = async (data: CreateOpportunityRequest): Promise<FreelanceOpportunity> => {
  const response = await api.post(`${BASE_URL}/opportunities`, data);
  return response.data;
};

export const updateOpportunityStatus = async (
  id: number,
  status: FreelanceOpportunity['status']
): Promise<FreelanceOpportunity> => {
  const response = await api.patch(`${BASE_URL}/opportunities/${id}/status`, { status });
  return response.data;
};

export const deleteOpportunity = async (id: number): Promise<void> => {
  await api.delete(`${BASE_URL}/opportunities/${id}`);
};

// Platforms
export const getPlatforms = async (): Promise<FreelancePlatform[]> => {
  const response = await api.get(`${BASE_URL}/platforms`);
  return response.data;
};

export const createPlatform = async (data: Partial<FreelancePlatform>): Promise<FreelancePlatform> => {
  const response = await api.post(`${BASE_URL}/platforms`, data);
  return response.data;
};

// Duplication Check (RN09)
export const checkDuplicate = async (
  title: string,
  description: string,
  platform_id: number,
  external_id: string
): Promise<{
  is_duplicate: boolean;
  similarity_score: number;
  similar_opportunities: Array<{ id: number; title: string; similarity: number }>;
}> => {
  const response = await api.post(`${BASE_URL}/duplication/check`, {
    title,
    description,
    platform_id,
    external_id,
  });
  return response.data;
};

// Risk Assessment (RN12)
export const assessRisk = async (opportunity_id: number): Promise<RiskAssessment> => {
  const response = await api.post(`${BASE_URL}/risk/assess`, { opportunity_id });
  return response.data;
};

// Financial Calculation (RN11)
export const calculateFinancial = async (data: CalculateFinancialRequest): Promise<FinancialCalculation> => {
  const response = await api.post(`${BASE_URL}/financial/calculate`, data);
  return response.data;
};

// Pricing
export const getPricingParameters = async (): Promise<PricingParameter> => {
  const response = await api.get(`${BASE_URL}/pricing/parameters`);
  return response.data;
};

export const updatePricingParameters = async (data: Partial<PricingParameter>): Promise<PricingParameter> => {
  const response = await api.put(`${BASE_URL}/pricing/parameters`, data);
  return response.data;
};

export const calculatePricing = async (opportunity_id: number): Promise<PricingSuggestion> => {
  const response = await api.post(`${BASE_URL}/pricing/calculate`, { opportunity_id });
  return response.data;
};

// Negotiation
export const generateNegotiation = async (data: GenerateNegotiationRequest): Promise<NegotiationResponse> => {
  const response = await api.post(`${BASE_URL}/negotiation/generate`, data);
  return response.data;
};

// Integration Service - Full Pipeline
export const processOpportunity = async (
  data: ProcessOpportunityRequest
): Promise<{
  opportunity_id: number;
  is_duplicate: boolean;
  risk_assessment: RiskAssessment;
  financial_calculation: FinancialCalculation;
  pricing_suggestion: PricingSuggestion;
  recommendation: string;
}> => {
  const response = await api.post(`${BASE_URL}/integration/process`, data);
  return response.data;
};

// Learning Components
export const getPricingPerformance = async (): Promise<{
  total_records: number;
  avg_accuracy_score: number;
  avg_error_margin: number;
  needs_adjustment: boolean;
  complexity_performance: Record<string, any>;
}> => {
  const response = await api.get(`${BASE_URL}/learning/pricing/performance`);
  return response.data;
};

export const getRejectionPatterns = async (): Promise<{
  total_opportunities: number;
  rejected_count: number;
  rejection_rate: number;
  red_flag_stats: Record<string, any>;
  high_risk_flags: Array<{
    flag: string;
    rejection_probability: number;
    occurrences: number;
  }>;
}> => {
  const response = await api.get(`${BASE_URL}/learning/rejection/patterns`);
  return response.data;
};

export const getHourlyRateAnalysis = async (): Promise<{
  total_opportunities: number;
  rate_range_stats: Record<string, any>;
  optimal_range: {
    range_name: string;
    range_min: number;
    range_max: number;
    expected_value: number;
  };
}> => {
  const response = await api.get(`${BASE_URL}/learning/hourly-rate/analysis`);
  return response.data;
};

export const applyPricingAdjustment = async (): Promise<{ success: boolean; message: string }> => {
  const response = await api.post(`${BASE_URL}/learning/pricing/adjust`);
  return response.data;
};

export const applyRateAdjustment = async (): Promise<{ success: boolean; message: string }> => {
  const response = await api.post(`${BASE_URL}/learning/hourly-rate/adjust`);
  return response.data;
};

// Career Insights
export const getCareerInsights = async (): Promise<CareerInsight> => {
  const response = await api.get(`${BASE_URL}/insights/career`);
  return response.data;
};

export const getTopPerformingProjects = async (): Promise<
  Array<{
    opportunity: FreelanceOpportunity;
    revenue: number;
    profitability: number;
  }>
> => {
  const response = await api.get(`${BASE_URL}/insights/top-projects`);
  return response.data;
};

export const getIncomeTrends = async (
  period: 'week' | 'month' | 'year' = 'month'
): Promise<{
  period: string;
  data: Array<{ date: string; revenue: number; projects: number }>;
}> => {
  const response = await api.get(`${BASE_URL}/insights/income-trends?period=${period}`);
  return response.data;
};

// Statistics
export const getOpportunityStats = async (): Promise<OpportunityStats> => {
  const response = await api.get(`${BASE_URL}/opportunities/stats`);
  return response.data;
};

// Learning Performance Dashboard
export const getLearningPerformance = async (): Promise<LearningComponentPerformance> => {
  const [pricing, rejection, hourlyRate] = await Promise.all([
    getPricingPerformance().catch(() => null),
    getRejectionPatterns().catch(() => null),
    getHourlyRateAnalysis().catch(() => null),
  ]);

  return {
    pricing_accuracy: pricing
      ? {
          avg_accuracy_score: pricing.avg_accuracy_score,
          avg_error_margin: pricing.avg_error_margin,
          needs_adjustment: pricing.needs_adjustment,
        }
      : undefined,
    rejection_patterns: rejection
      ? {
          total_opportunities: rejection.total_opportunities,
          rejected_count: rejection.rejected_count,
          rejection_rate: rejection.rejection_rate,
          high_risk_flags: rejection.high_risk_flags,
        }
      : undefined,
    hourly_rate_optimization: hourlyRate?.optimal_range
      ? {
          current_rate: 0, // Will be filled from pricing parameters
          suggested_rate: (hourlyRate.optimal_range.range_min + hourlyRate.optimal_range.range_max) / 2,
          optimal_range: `$${hourlyRate.optimal_range.range_min}-$${hourlyRate.optimal_range.range_max}/hr`,
          current_acceptance_rate: 0, // Calculate from stats
        }
      : undefined,
  };
};
