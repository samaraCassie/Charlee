// Freelancer System Types

export interface FreelanceOpportunity {
  id: number;
  user_id: number;
  platform_id: number;
  external_id: string;
  title: string;
  description: string;
  client_budget?: number;
  client_budget_min?: number; // For budget ranges (Smart Paste/Bookmarklet)
  client_name?: string;
  client_rating?: number;
  client_projects_count?: number;
  client_payment_verified?: boolean;
  client_total_spent?: number;
  client_country?: string;
  estimated_hours?: number;
  skills_required?: string[];
  status: 'new' | 'analyzed' | 'pending' | 'accepted' | 'rejected' | 'negotiating' | 'completed';
  created_at: string;
  updated_at: string;

  // Smart Paste / Bookmarklet fields (RF01)
  source_url?: string; // URL of origin
  raw_input_text?: string; // Original pasted text

  // Analysis results
  recommendation?: string; // accept, negotiate, reject
  recommendation_reason?: string;
  red_flags?: (string | Record<string, unknown>)[]; // Can be string[] or object[]
  opportunities?: (string | Record<string, unknown>)[]; // Can be string[] or object[]
  final_score?: number;
  extracted_context?: {
    risk_score?: number;
    risk_level?: string;
    [key: string]: unknown;
  };

  // Relationships
  platform?: FreelancePlatform;
  risk_assessment?: RiskAssessment;
  financial_calculation?: FinancialCalculation;
  pricing_suggestion?: PricingSuggestion;
}

export interface FreelancePlatform {
  id: number;
  user_id: number;
  name: string;
  api_key?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RiskAssessment {
  id: number;
  opportunity_id: number;
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high';
  recommendation: 'accept' | 'negotiate' | 'reject';
  red_flags: string[];
  green_flags: string[];
  risk_factors: {
    client_rating_risk?: number;
    client_experience_risk?: number;
    payment_verification_risk?: number;
  };
  created_at: string;
}

export interface FinancialCalculation {
  id: number;
  opportunity_id: number;
  gross_usd: number;
  exchange_rate: number;
  gross_brl: number;
  platform_fee_brl?: number;
  tax_brl: number;
  net_brl: number;
  effective_tax_rate: number;
  tax_regime: 'simples_nacional' | 'mei' | 'lucro_presumido';
  platform_name?: string;
  created_at: string;
}

export interface PricingSuggestion {
  id: number;
  opportunity_id: number;
  suggested_hourly_rate: number;
  suggested_value: number;
  breakdown: {
    base_rate: number;
    complexity_multiplier: number;
    specialization_multiplier: number;
    deadline_multiplier: number;
    client_multiplier: number;
  };
  created_at: string;
}

export interface PricingParameter {
  id: number;
  user_id?: number;
  version: number;
  base_hourly_rate: number;
  minimum_margin: number;
  minimum_project_value: number;
  complexity_factors: Record<string, number>;
  specialization_factors: Record<string, number>;
  deadline_factors: Record<string, number>;
  client_factors: Record<string, number>;
  active: boolean;
  auto_adjusted: boolean;
  based_on_executions_count: number;
  adjustment_reason?: string;
  created_at: string;
}

export interface RedFlag {
  name: string;
  keywords?: string[];
  threshold?: number;
  weight: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  details?: string;
}

export interface GreenFlag {
  name: string;
  min_words?: number;
  min_projects?: number;
  min_rating?: number;
  min_ratio?: number;
  buffer_ratio?: number;
  keywords?: string[];
  weight: number;
}

export interface EvaluationCriteria {
  id: number;
  user_id: number;
  version: number;
  red_flags: Record<string, RedFlag>;
  green_flags: Record<string, GreenFlag>;
  score_weights: {
    viability: number;
    alignment: number;
    strategic: number;
  };
  minimum_risk_score: number;
  minimum_final_score: number;
  risk_tolerance: 'conservative' | 'moderate' | 'aggressive';
  auto_adjust_enabled: boolean;
  adjustment_threshold: number;
  based_on_evaluations_count: number;
  last_adjustment_reason?: string;
  active: boolean;
  created_at: string;
  updated_at: string;
  activated_at?: string;
}

export interface NegotiationResponse {
  id: number;
  opportunity_id: number;
  original_budget: number;
  counter_offer: number;
  reasoning: string;
  message_template: string;
  negotiation_strategy: string;
  created_at: string;
}

export interface CareerInsight {
  total_opportunities: number;
  total_accepted: number;
  total_rejected: number;
  acceptance_rate: number;
  avg_project_value: number;
  total_revenue: number;
  avg_hourly_rate: number;
  top_skills: Array<{ skill: string; count: number; avg_value: number }>;
  top_platforms: Array<{ platform: string; count: number; revenue: number }>;
  revenue_by_month: Array<{ month: string; revenue: number; projects: number }>;
}

export interface LearningComponentPerformance {
  pricing_accuracy?: {
    avg_accuracy_score: number;
    avg_error_margin: number;
    needs_adjustment: boolean;
  };
  rejection_patterns?: {
    total_opportunities: number;
    rejected_count: number;
    rejection_rate: number;
    high_risk_flags: Array<{
      flag: string;
      rejection_probability: number;
      occurrences: number;
    }>;
  };
  hourly_rate_optimization?: {
    current_rate: number;
    suggested_rate: number;
    optimal_range: string;
    current_acceptance_rate: number;
  };
}

// Request types
export interface CreateOpportunityRequest {
  platform_id: number;
  external_id: string;
  title: string;
  description: string;
  client_budget?: number;
  client_rating?: number;
  client_projects_count?: number;
  client_payment_verified?: boolean;
  client_country?: string;
  estimated_hours?: number;
  skills_required?: string[];
}

export interface ProcessOpportunityRequest {
  opportunity_id: number;
}

export interface CalculateFinancialRequest {
  opportunity_id: number;
  tax_regime?: 'simples_nacional' | 'mei' | 'lucro_presumido';
}

export interface GenerateNegotiationRequest {
  opportunity_id: number;
  counter_offer?: number;
}

// Filter types
export interface OpportunityFilters {
  status?: string[];
  platform_id?: number;
  risk_level?: string[];
  min_budget?: number;
  max_budget?: number;
  skills?: string[];
  date_from?: string;
  date_to?: string;
}

export interface OpportunityStats {
  total: number;
  pending: number;
  accepted: number;
  rejected: number;
  negotiating: number;
  completed: number;
  avg_budget: number;
  total_revenue: number;
}
