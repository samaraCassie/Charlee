import { create } from 'zustand';
import { notificationService } from '@/services/notificationService';
import type { NotificationAPI, NotificationPreferenceAPI } from '@/services/notificationService';

export type NotificationType =
  | 'task_due_soon'
  | 'capacity_overload'
  | 'cycle_phase_change'
  | 'freelance_invoice_ready'
  | 'system'
  | 'achievement';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  read: boolean;
  metadata?: Record<string, any>;
  createdAt: string;
  readAt?: string;
}

export interface NotificationPreference {
  id: string;
  notificationType: NotificationType | 'all';
  enabled: boolean;
  inAppEnabled: boolean;
  emailEnabled: boolean;
  pushEnabled: boolean;
  settings?: Record<string, any>;
}

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  preferences: NotificationPreference[];
  loading: boolean;
  error: string | null;
  wsConnected: boolean;

  // Actions - Notifications
  fetchNotifications: (unreadOnly?: boolean) => Promise<void>;
  markAsRead: (notificationId: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (notificationId: string) => Promise<void>;
  addNotification: (notification: Notification) => void;
  updateUnreadCount: (count: number) => void;

  // Actions - Preferences
  fetchPreferences: () => Promise<void>;
  updatePreference: (
    notificationType: string,
    updates: Partial<NotificationPreference>
  ) => Promise<void>;

  // WebSocket
  setWsConnected: (connected: boolean) => void;

  // Utility
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Computed
  getUnreadNotifications: () => Notification[];
  getNotificationsByType: (type: NotificationType) => Notification[];
  isPreferenceEnabled: (type: NotificationType) => boolean;
}

// Helper: Convert API notification to frontend notification
function apiToNotification(apiNotification: NotificationAPI): Notification {
  return {
    id: apiNotification.id.toString(),
    type: apiNotification.type as NotificationType,
    title: apiNotification.title,
    message: apiNotification.message,
    read: apiNotification.read,
    metadata: apiNotification.metadata,
    createdAt: apiNotification.created_at,
    readAt: apiNotification.read_at,
  };
}

// Helper: Convert API preference to frontend preference
function apiToPreference(apiPreference: NotificationPreferenceAPI): NotificationPreference {
  return {
    id: apiPreference.id.toString(),
    notificationType: apiPreference.notification_type as NotificationType | 'all',
    enabled: apiPreference.enabled,
    inAppEnabled: apiPreference.in_app_enabled,
    emailEnabled: apiPreference.email_enabled,
    pushEnabled: apiPreference.push_enabled,
    settings: apiPreference.settings,
  };
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  preferences: [],
  loading: false,
  error: null,
  wsConnected: false,

  fetchNotifications: async (unreadOnly = false) => {
    set({ loading: true, error: null });
    try {
      const response = await notificationService.getNotifications(unreadOnly);
      const notifications = response.notifications.map(apiToNotification);
      set({
        notifications,
        unreadCount: response.unread_count,
        loading: false,
      });
    } catch (error) {
      console.error('Error fetching notifications:', error);
      set({ error: 'Failed to fetch notifications', loading: false });
    }
  },

  markAsRead: async (notificationId: string) => {
    try {
      const apiNotification = await notificationService.markAsRead(parseInt(notificationId));
      const notification = apiToNotification(apiNotification);

      // Update notification in state
      set((state) => ({
        notifications: state.notifications.map((n) =>
          n.id === notificationId ? notification : n
        ),
        unreadCount: Math.max(0, state.unreadCount - 1),
      }));
    } catch (error) {
      console.error('Error marking notification as read:', error);
      set({ error: 'Failed to mark notification as read' });
    }
  },

  markAllAsRead: async () => {
    try {
      await notificationService.markAllAsRead();

      // Mark all as read in state
      set((state) => ({
        notifications: state.notifications.map((n) => ({ ...n, read: true })),
        unreadCount: 0,
      }));
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      set({ error: 'Failed to mark all notifications as read' });
    }
  },

  deleteNotification: async (notificationId: string) => {
    try {
      await notificationService.deleteNotification(parseInt(notificationId));

      // Remove notification from state
      set((state) => ({
        notifications: state.notifications.filter((n) => n.id !== notificationId),
        unreadCount: state.notifications.find((n) => n.id === notificationId && !n.read)
          ? state.unreadCount - 1
          : state.unreadCount,
      }));
    } catch (error) {
      console.error('Error deleting notification:', error);
      set({ error: 'Failed to delete notification' });
    }
  },

  addNotification: (notification: Notification) => {
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: notification.read ? state.unreadCount : state.unreadCount + 1,
    }));
  },

  updateUnreadCount: (count: number) => {
    set({ unreadCount: count });
  },

  fetchPreferences: async () => {
    try {
      const response = await notificationService.getPreferences();
      const preferences = response.preferences.map(apiToPreference);
      set({ preferences });
    } catch (error) {
      console.error('Error fetching preferences:', error);
      set({ error: 'Failed to fetch preferences' });
    }
  },

  updatePreference: async (notificationType: string, updates: Partial<NotificationPreference>) => {
    try {
      const apiUpdates = {
        enabled: updates.enabled,
        in_app_enabled: updates.inAppEnabled,
        email_enabled: updates.emailEnabled,
        push_enabled: updates.pushEnabled,
        settings: updates.settings,
      };

      const apiPreference = await notificationService.updatePreference(
        notificationType,
        apiUpdates
      );
      const preference = apiToPreference(apiPreference);

      // Update preference in state
      set((state) => ({
        preferences: state.preferences.map((p) =>
          p.notificationType === notificationType ? preference : p
        ),
      }));
    } catch (error) {
      console.error('Error updating preference:', error);
      set({ error: 'Failed to update preference' });
    }
  },

  setWsConnected: (connected: boolean) => {
    set({ wsConnected: connected });
  },

  setLoading: (loading: boolean) => {
    set({ loading });
  },

  setError: (error: string | null) => {
    set({ error });
  },

  // Computed getters
  getUnreadNotifications: () => {
    return get().notifications.filter((n) => !n.read);
  },

  getNotificationsByType: (type: NotificationType) => {
    return get().notifications.filter((n) => n.type === type);
  },

  isPreferenceEnabled: (type: NotificationType) => {
    const preference = get().preferences.find((p) => p.notificationType === type);
    return preference ? preference.enabled && preference.inAppEnabled : true;
  },
}));
