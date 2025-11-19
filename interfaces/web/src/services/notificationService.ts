import { api } from './api';

// API Types (snake_case from backend)
export interface NotificationAPI {
  id: number;
  user_id: number;
  type: string;
  title: string;
  message: string;
  read: boolean;
  extra_data?: Record<string, any>;
  created_at: string;
  read_at?: string;
}

export interface NotificationListResponse {
  total: number;
  unread_count: number;
  notifications: NotificationAPI[];
}

export interface NotificationPreferenceAPI {
  id: number;
  user_id: number;
  notification_type: string;
  enabled: boolean;
  in_app_enabled: boolean;
  email_enabled: boolean;
  push_enabled: boolean;
  settings?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface NotificationPreferenceListResponse {
  total: number;
  preferences: NotificationPreferenceAPI[];
}

export interface NotificationPreferenceUpdate {
  enabled?: boolean;
  in_app_enabled?: boolean;
  email_enabled?: boolean;
  push_enabled?: boolean;
  settings?: Record<string, any>;
}

export const notificationService = {
  /**
   * Get all notifications for the current user
   */
  async getNotifications(unreadOnly = false): Promise<NotificationListResponse> {
    const params = unreadOnly ? { unread_only: true } : {};
    const response = await api.get<NotificationListResponse>('/v2/notifications', { params });
    return response.data;
  },

  /**
   * Get a single notification by ID
   */
  async getNotification(notificationId: number): Promise<NotificationAPI> {
    const response = await api.get<NotificationAPI>(`/v2/notifications/${notificationId}`);
    return response.data;
  },

  /**
   * Mark notification as read
   */
  async markAsRead(notificationId: number): Promise<NotificationAPI> {
    const response = await api.patch<NotificationAPI>(
      `/v2/notifications/${notificationId}/read`
    );
    return response.data;
  },

  /**
   * Mark all notifications as read
   */
  async markAllAsRead(): Promise<{ message: string; updated_count: number }> {
    const response = await api.post<{ message: string; updated_count: number }>(
      '/v2/notifications/mark-all-read'
    );
    return response.data;
  },

  /**
   * Delete a notification
   */
  async deleteNotification(notificationId: number): Promise<void> {
    await api.delete(`/v2/notifications/${notificationId}`);
  },

  /**
   * Get all notification preferences
   */
  async getPreferences(): Promise<NotificationPreferenceListResponse> {
    const response = await api.get<NotificationPreferenceListResponse>(
      '/v2/notifications/preferences/'
    );
    return response.data;
  },

  /**
   * Get preference for a specific notification type
   */
  async getPreference(notificationType: string): Promise<NotificationPreferenceAPI> {
    const response = await api.get<NotificationPreferenceAPI>(
      `/v2/notifications/preferences/${notificationType}`
    );
    return response.data;
  },

  /**
   * Update notification preference
   */
  async updatePreference(
    notificationType: string,
    updates: NotificationPreferenceUpdate
  ): Promise<NotificationPreferenceAPI> {
    const response = await api.patch<NotificationPreferenceAPI>(
      `/v2/notifications/preferences/${notificationType}`,
      updates
    );
    return response.data;
  },

  /**
   * Delete notification preference
   */
  async deletePreference(notificationType: string): Promise<void> {
    await api.delete(`/v2/notifications/preferences/${notificationType}`);
  },
};
