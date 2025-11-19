import { api } from './api';

// API Types (snake_case from backend)
export interface NotificationSourceAPI {
  id: number;
  user_id: number;
  source_type: string;
  name: string;
  enabled: boolean;
  credentials: Record<string, any>;
  settings?: Record<string, any>;
  last_sync?: string;
  last_error?: string;
  created_at: string;
  updated_at: string;
}

export interface NotificationSourceListResponse {
  total: number;
  sources: NotificationSourceAPI[];
}

export interface NotificationSourceCreate {
  source_type: string;
  name: string;
  credentials: Record<string, any>;
  settings?: Record<string, any>;
  enabled?: boolean;
}

export interface NotificationSourceUpdate {
  name?: string;
  enabled?: boolean;
  credentials?: Record<string, any>;
  settings?: Record<string, any>;
}

export interface CollectionStatsResponse {
  collected: number;
  spam_filtered: number;
  errors: string[];
}

export const notificationSourcesService = {
  /**
   * Get all notification sources for the current user
   */
  async getSources(): Promise<NotificationSourceListResponse> {
    const response = await api.get<NotificationSourceListResponse>(
      '/v2/notifications/sources/'
    );
    return response.data;
  },

  /**
   * Get a single notification source by ID
   */
  async getSource(sourceId: number): Promise<NotificationSourceAPI> {
    const response = await api.get<NotificationSourceAPI>(
      `/v2/notifications/sources/${sourceId}`
    );
    return response.data;
  },

  /**
   * Create a new notification source
   */
  async createSource(source: NotificationSourceCreate): Promise<NotificationSourceAPI> {
    const response = await api.post<NotificationSourceAPI>(
      '/v2/notifications/sources/',
      source
    );
    return response.data;
  },

  /**
   * Update a notification source
   */
  async updateSource(
    sourceId: number,
    updates: NotificationSourceUpdate
  ): Promise<NotificationSourceAPI> {
    const response = await api.put<NotificationSourceAPI>(
      `/v2/notifications/sources/${sourceId}`,
      updates
    );
    return response.data;
  },

  /**
   * Delete a notification source
   */
  async deleteSource(sourceId: number): Promise<void> {
    await api.delete(`/v2/notifications/sources/${sourceId}`);
  },

  /**
   * Test authentication for a notification source
   */
  async testAuthentication(sourceId: number): Promise<{ success: boolean; message: string }> {
    const response = await api.post<{ success: boolean; message: string }>(
      `/v2/notifications/sources/${sourceId}/test-auth`
    );
    return response.data;
  },

  /**
   * Trigger manual collection from a notification source
   */
  async collectNow(sourceId: number): Promise<CollectionStatsResponse> {
    const response = await api.post<CollectionStatsResponse>(
      `/v2/notifications/sources/${sourceId}/collect`
    );
    return response.data;
  },
};
