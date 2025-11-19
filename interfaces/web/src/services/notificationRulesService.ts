import { api } from './api';

// API Types (snake_case from backend)
export interface NotificationRuleAPI {
  id: number;
  user_id: number;
  name: string;
  enabled: boolean;
  priority: number;
  conditions: Record<string, any>;
  actions: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface NotificationRuleListResponse {
  total: number;
  rules: NotificationRuleAPI[];
}

export interface NotificationRuleCreate {
  name: string;
  conditions: Record<string, any>;
  actions: Record<string, any>;
  enabled?: boolean;
  priority?: number;
}

export interface NotificationRuleUpdate {
  name?: string;
  enabled?: boolean;
  priority?: number;
  conditions?: Record<string, any>;
  actions?: Record<string, any>;
}

export const notificationRulesService = {
  /**
   * Get all notification rules for the current user
   */
  async getRules(): Promise<NotificationRuleListResponse> {
    const response = await api.get<NotificationRuleListResponse>('/v2/notifications/rules/');
    return response.data;
  },

  /**
   * Get a single notification rule by ID
   */
  async getRule(ruleId: number): Promise<NotificationRuleAPI> {
    const response = await api.get<NotificationRuleAPI>(`/v2/notifications/rules/${ruleId}`);
    return response.data;
  },

  /**
   * Create a new notification rule
   */
  async createRule(rule: NotificationRuleCreate): Promise<NotificationRuleAPI> {
    const response = await api.post<NotificationRuleAPI>('/v2/notifications/rules/', rule);
    return response.data;
  },

  /**
   * Update a notification rule
   */
  async updateRule(
    ruleId: number,
    updates: NotificationRuleUpdate
  ): Promise<NotificationRuleAPI> {
    const response = await api.put<NotificationRuleAPI>(
      `/v2/notifications/rules/${ruleId}`,
      updates
    );
    return response.data;
  },

  /**
   * Delete a notification rule
   */
  async deleteRule(ruleId: number): Promise<void> {
    await api.delete(`/v2/notifications/rules/${ruleId}`);
  },

  /**
   * Test a rule against a notification
   */
  async testRule(
    ruleId: number,
    notificationId: number
  ): Promise<{ matched: boolean; actions_taken: string[] }> {
    const response = await api.post<{ matched: boolean; actions_taken: string[] }>(
      `/v2/notifications/rules/${ruleId}/test`,
      { notification_id: notificationId }
    );
    return response.data;
  },
};
