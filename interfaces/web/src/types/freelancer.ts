// Freelancer System Types

export interface FreelanceOpportunity {
  id: number;
  user_id: number;
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
  status: 'pending' | 'accepted' | 'rejected' | 'negotiating' | 'completed';
  created_at: string;
  updated_at: string;

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
  user_id: number;
  version: number;
  base_hourly_rate: number;
  minimum_margin: number;
  currency: string;
  complexity_factors: Record<string, number>;
  specialization_factors: Record<string, number>;
  deadline_factors: Record<string, number>;
  client_factors: Record<string, number>;
  minimum_project_value: number;
  minimum_deadline_days: number;
  active: boolean;
  created_at: string;
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
