import api from './api';
import type {
  FreelanceOpportunity,
  FreelancePlatform,
  PricingParameter,
  EvaluationCriteria,
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

const BASE_URL = '/v2/freelancer';

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
  return response.data.opportunities;
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

export interface AcceptanceResponse {
  opportunity: FreelanceOpportunity;
  project_id: number | null;
  execution_id: number | null;
  task_ids: number[];
  message: string;
}

export const acceptOpportunity = async (
  id: number,
  reason?: string
): Promise<AcceptanceResponse> => {
  const response = await api.post(`${BASE_URL}/opportunities/${id}/accept`, { reason });
  return response.data;
};

export const updateOpportunity = async (
  id: number,
  data: Partial<FreelanceOpportunity>
): Promise<FreelanceOpportunity> => {
  const response = await api.patch(`${BASE_URL}/opportunities/${id}`, data);
  return response.data;
};

export interface BatchAnalysisResult {
  message: string;
  total: number;
  success: number;
  failed: number;
  results: Array<{
    opportunity_id: number;
    title: string;
    status: 'success' | 'failed';
    recommendation?: string;
    error?: string;
  }>;
}

export const analyzeAllNewOpportunities = async (): Promise<BatchAnalysisResult> => {
  const response = await api.post(`${BASE_URL}/opportunities/analyze-all`);
  return response.data;
};

// Platforms
export const getPlatforms = async (): Promise<FreelancePlatform[]> => {
  const response = await api.get(`${BASE_URL}/platforms`);
  return response.data.platforms;
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
  const response = await api.get(`${BASE_URL}/pricing`);
  return response.data;
};

export const updatePricingParameters = async (data: Partial<PricingParameter>): Promise<PricingParameter> => {
  const response = await api.put(`${BASE_URL}/pricing`, data);
  return response.data;
};

export const calculatePricing = async (opportunity_id: number): Promise<PricingSuggestion> => {
  const response = await api.post(`${BASE_URL}/pricing/calculate`, { opportunity_id });
  return response.data;
};

// Evaluation Criteria
export const getEvaluationCriteria = async (): Promise<EvaluationCriteria> => {
  const response = await api.get(`${BASE_URL}/evaluation-criteria`);
  return response.data;
};

export const updateEvaluationCriteria = async (data: Partial<EvaluationCriteria>): Promise<EvaluationCriteria> => {
  const response = await api.put(`${BASE_URL}/evaluation-criteria`, data);
  return response.data;
};

export const optimizeEvaluationCriteria = async (
  basedOnLastN: number = 30
): Promise<{ report: string; success: boolean }> => {
  const response = await api.post(`${BASE_URL}/evaluation-criteria/optimize`, {
    based_on_last_n_evaluations: basedOnLastN,
  });
  return response.data;
};

// Negotiation
export const generateNegotiation = async (data: GenerateNegotiationRequest): Promise<NegotiationResponse> => {
  const response = await api.post(`${BASE_URL}/negotiation/generate`, data);
  return response.data;
};

// Analyze existing opportunity (RN09-RN13)
export const analyzeOpportunity = async (
  opportunity_id: number
): Promise<{
  opportunity: FreelanceOpportunity;
  analysis: {
    duplication_check?: Record<string, unknown>;
    risk_assessment?: RiskAssessment;
    financial_analysis?: FinancialCalculation;
    pricing_suggestion?: PricingSuggestion;
    final_recommendation?: Record<string, unknown>;
  };
}> => {
  const response = await api.post(`${BASE_URL}/opportunities/${opportunity_id}/analyze`);
  return response.data;
};

// Integration Service - Full Pipeline (Create + Analyze)
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
  complexity_performance: Record<string, unknown>;
}> => {
  const response = await api.get(`${BASE_URL}/learning/pricing/performance`);
  return response.data;
};

export const getRejectionPatterns = async (): Promise<{
  total_opportunities: number;
  rejected_count: number;
  rejection_rate: number;
  red_flag_stats: Record<string, unknown>;
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
  rate_range_stats: Record<string, unknown>;
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

// ==================== Smart Paste & Bookmarklet (RF01) ====================

export interface SmartPasteRequest {
  raw_text: string;
  source_url?: string;
}

export interface SmartPasteExtractedData {
  title: string;
  description: string;
  client_name?: string;
  budget_min?: number;
  budget_max?: number;
  currency: string;
  deadline_days?: number;
  required_skills?: string[];
  contract_type?: 'fixed_price' | 'hourly' | 'milestone';
  complexity_estimate?: number;
  category?: string;
  red_flags?: string[];
  opportunities?: string[];
}

export interface SmartPasteResponse {
  id: number;
  extracted: SmartPasteExtractedData;
  message: string;
  requires_confirmation: boolean;
}

export interface BookmarkletRequest {
  source: 'upwork' | 'freelancer' | 'linkedin' | 'unknown';
  url: string;
  title?: string;
  description?: string;
  budget?: string;
  skills?: string;
  client_name?: string;
  client_rating?: string;
  client_country?: string;
}

export interface BookmarkletResponse {
  id: number;
  source: string;
  title: string;
  message: string;
}

/**
 * Smart Paste - Extract opportunity from raw text using LLM
 *
 * Allows users to paste text from any source (Upwork, email, WhatsApp, etc.)
 * and have the system automatically extract structured data.
 */
export const smartPasteOpportunity = async (data: SmartPasteRequest): Promise<SmartPasteResponse> => {
  const response = await api.post(`${BASE_URL}/opportunities/smart-paste`, data);
  return response.data;
};

/**
 * Bookmarklet - Import opportunity from browser DOM extraction
 *
 * Receives data extracted by the bookmarklet JavaScript from platform pages.
 */
export const bookmarkletOpportunity = async (data: BookmarkletRequest): Promise<BookmarkletResponse> => {
  const response = await api.post(`${BASE_URL}/opportunities/bookmarklet`, data);
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
