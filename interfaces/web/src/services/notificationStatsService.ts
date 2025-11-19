import { api } from './api';

export interface PatternInsightsResponse {
  total_patterns: number;
  average_confidence: number;
  most_confident_patterns: Array<{
    pattern_key: string;
    pattern_type: string;
    confidence: number;
    frequency: number;
  }>;
  most_frequent_patterns: Array<{
    pattern_key: string;
    pattern_type: string;
    confidence: number;
    frequency: number;
  }>;
}

export interface DigestAPI {
  id: number;
  user_id: number;
  digest_type: string;
  start_date: string;
  end_date: string;
  summary: string;
  notification_count: number;
  created_at: string;
}

export const notificationStatsService = {
  /**
   * Get pattern insights summary
   */
  async getPatternInsights(): Promise<PatternInsightsResponse> {
    const response = await api.get<PatternInsightsResponse>(
      '/v2/notifications/patterns/insights/summary'
    );
    return response.data;
  },

  /**
   * Get latest digest by type
   */
  async getLatestDigest(digestType: 'daily' | 'weekly' | 'monthly'): Promise<DigestAPI | null> {
    try {
      const response = await api.get<DigestAPI>(
        `/v2/notifications/digests/latest/${digestType}`
      );
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  },

  /**
   * Generate a new digest
   */
  async generateDigest(digestType: 'daily' | 'weekly' | 'monthly'): Promise<DigestAPI> {
    const response = await api.post<DigestAPI>(
      `/v2/notifications/digests/generate?digest_type=${digestType}`
    );
    return response.data;
  },
};
