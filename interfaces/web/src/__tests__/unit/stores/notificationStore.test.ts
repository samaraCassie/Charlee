import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useNotificationStore } from '@/stores/notificationStore';
import * as notificationService from '@/services/notificationService';

// Mock the notification service
vi.mock('@/services/notificationService');

describe('NotificationStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useNotificationStore.setState({
      notifications: [],
      unreadCount: 0,
      preferences: [],
      loading: false,
      error: null,
      wsConnected: false,
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('fetchNotifications', () => {
    it('should fetch and store notifications', async () => {
      const mockResponse = {
        total: 2,
        unread_count: 1,
        notifications: [
          {
            id: 1,
            type: 'task_due_soon',
            title: 'Task Due Soon',
            message: 'Your task is due in 2 hours',
            read: false,
            extra_data: { priority: 'high' },
            created_at: '2025-11-17T10:00:00Z',
          },
          {
            id: 2,
            type: 'system',
            title: 'System Update',
            message: 'System maintenance scheduled',
            read: true,
            extra_data: {},
            created_at: '2025-11-17T09:00:00Z',
          },
        ],
      };

      vi.mocked(notificationService.notificationService.getNotifications).mockResolvedValue(
        mockResponse
      );

      const { fetchNotifications, notifications, unreadCount } = useNotificationStore.getState();

      await fetchNotifications();

      expect(notificationService.notificationService.getNotifications).toHaveBeenCalledWith(false);
      expect(useNotificationStore.getState().notifications).toHaveLength(2);
      expect(useNotificationStore.getState().unreadCount).toBe(1);
      expect(useNotificationStore.getState().loading).toBe(false);
    });

    it('should fetch only unread notifications when unreadOnly is true', async () => {
      const mockResponse = {
        total: 1,
        unread_count: 1,
        notifications: [
          {
            id: 1,
            type: 'task_due_soon',
            title: 'Task Due Soon',
            message: 'Your task is due in 2 hours',
            read: false,
            extra_data: {},
            created_at: '2025-11-17T10:00:00Z',
          },
        ],
      };

      vi.mocked(notificationService.notificationService.getNotifications).mockResolvedValue(
        mockResponse
      );

      const { fetchNotifications } = useNotificationStore.getState();

      await fetchNotifications(true);

      expect(notificationService.notificationService.getNotifications).toHaveBeenCalledWith(true);
      expect(useNotificationStore.getState().notifications).toHaveLength(1);
    });

    it('should handle fetch errors', async () => {
      vi.mocked(notificationService.notificationService.getNotifications).mockRejectedValue(
        new Error('Network error')
      );

      const { fetchNotifications } = useNotificationStore.getState();

      await fetchNotifications();

      expect(useNotificationStore.getState().error).toBe('Failed to fetch notifications');
      expect(useNotificationStore.getState().loading).toBe(false);
    });
  });

  describe('markAsRead', () => {
    it('should mark notification as read', async () => {
      const mockNotification = {
        id: 1,
        type: 'task_due_soon',
        title: 'Task Due Soon',
        message: 'Test',
        read: true,
        metadata: {},
        created_at: '2025-11-17T10:00:00Z',
        read_at: '2025-11-17T10:30:00Z',
      };

      vi.mocked(notificationService.notificationService.markAsRead).mockResolvedValue(
        mockNotification
      );

      // Set initial state with unread notification
      useNotificationStore.setState({
        notifications: [
          {
            id: '1',
            type: 'task_due_soon',
            title: 'Task Due Soon',
            message: 'Test',
            read: false,
            extra_data: {},
            createdAt: '2025-11-17T10:00:00Z',
          },
        ],
        unreadCount: 1,
      });

      const { markAsRead } = useNotificationStore.getState();

      await markAsRead('1');

      expect(notificationService.notificationService.markAsRead).toHaveBeenCalledWith(1);
      expect(useNotificationStore.getState().notifications[0].read).toBe(true);
      expect(useNotificationStore.getState().unreadCount).toBe(0);
    });

    it('should handle mark as read errors', async () => {
      vi.mocked(notificationService.notificationService.markAsRead).mockRejectedValue(
        new Error('Failed')
      );

      useNotificationStore.setState({
        notifications: [
          {
            id: '1',
            type: 'system',
            title: 'Test',
            message: 'Test',
            read: false,
            extra_data: {},
            createdAt: '2025-11-17T10:00:00Z',
          },
        ],
      });

      const { markAsRead } = useNotificationStore.getState();

      await markAsRead('1');

      expect(useNotificationStore.getState().error).toBe('Failed to mark notification as read');
    });
  });

  describe('markAllAsRead', () => {
    it('should mark all notifications as read', async () => {
      vi.mocked(notificationService.notificationService.markAllAsRead).mockResolvedValue({
        message: 'Marked 3 notifications as read',
        updated_count: 3,
      });

      useNotificationStore.setState({
        notifications: [
          {
            id: '1',
            type: 'system',
            title: 'Test 1',
            message: 'Test',
            read: false,
            extra_data: {},
            createdAt: '2025-11-17T10:00:00Z',
          },
          {
            id: '2',
            type: 'system',
            title: 'Test 2',
            message: 'Test',
            read: false,
            extra_data: {},
            createdAt: '2025-11-17T09:00:00Z',
          },
        ],
        unreadCount: 2,
      });

      const { markAllAsRead } = useNotificationStore.getState();

      await markAllAsRead();

      expect(notificationService.notificationService.markAllAsRead).toHaveBeenCalled();
      expect(useNotificationStore.getState().notifications.every((n) => n.read)).toBe(true);
      expect(useNotificationStore.getState().unreadCount).toBe(0);
    });
  });

  describe('deleteNotification', () => {
    it('should delete notification', async () => {
      vi.mocked(notificationService.notificationService.deleteNotification).mockResolvedValue();

      useNotificationStore.setState({
        notifications: [
          {
            id: '1',
            type: 'system',
            title: 'Test',
            message: 'Test',
            read: false,
            extra_data: {},
            createdAt: '2025-11-17T10:00:00Z',
          },
          {
            id: '2',
            type: 'system',
            title: 'Test 2',
            message: 'Test',
            read: true,
            extra_data: {},
            createdAt: '2025-11-17T09:00:00Z',
          },
        ],
        unreadCount: 1,
      });

      const { deleteNotification } = useNotificationStore.getState();

      await deleteNotification('1');

      expect(notificationService.notificationService.deleteNotification).toHaveBeenCalledWith(1);
      expect(useNotificationStore.getState().notifications).toHaveLength(1);
      expect(useNotificationStore.getState().unreadCount).toBe(0); // Unread was deleted
    });
  });

  describe('addNotification', () => {
    it('should add notification to store', () => {
      const newNotification = {
        id: '1',
        type: 'task_due_soon' as const,
        title: 'New Notification',
        message: 'Test message',
        read: false,
        metadata: {},
        createdAt: '2025-11-17T10:00:00Z',
      };

      const { addNotification } = useNotificationStore.getState();

      addNotification(newNotification);

      expect(useNotificationStore.getState().notifications).toHaveLength(1);
      expect(useNotificationStore.getState().notifications[0]).toEqual(newNotification);
      expect(useNotificationStore.getState().unreadCount).toBe(1);
    });

    it('should not increase unread count for read notifications', () => {
      const readNotification = {
        id: '1',
        type: 'system' as const,
        title: 'Already Read',
        message: 'Test',
        read: true,
        metadata: {},
        createdAt: '2025-11-17T10:00:00Z',
      };

      const { addNotification } = useNotificationStore.getState();

      addNotification(readNotification);

      expect(useNotificationStore.getState().notifications).toHaveLength(1);
      expect(useNotificationStore.getState().unreadCount).toBe(0);
    });
  });

  describe('computed getters', () => {
    beforeEach(() => {
      useNotificationStore.setState({
        notifications: [
          {
            id: '1',
            type: 'task_due_soon',
            title: 'Task Due',
            message: 'Test',
            read: false,
            extra_data: {},
            createdAt: '2025-11-17T10:00:00Z',
          },
          {
            id: '2',
            type: 'capacity_overload',
            title: 'Overload',
            message: 'Test',
            read: true,
            extra_data: {},
            createdAt: '2025-11-17T09:00:00Z',
          },
          {
            id: '3',
            type: 'task_due_soon',
            title: 'Another Task',
            message: 'Test',
            read: false,
            extra_data: {},
            createdAt: '2025-11-17T08:00:00Z',
          },
        ],
        preferences: [
          {
            id: '1',
            notificationType: 'task_due_soon',
            enabled: true,
            inAppEnabled: true,
            emailEnabled: false,
            pushEnabled: false,
          },
          {
            id: '2',
            notificationType: 'capacity_overload',
            enabled: false,
            inAppEnabled: false,
            emailEnabled: false,
            pushEnabled: false,
          },
        ],
      });
    });

    it('getUnreadNotifications should filter unread', () => {
      const { getUnreadNotifications } = useNotificationStore.getState();
      const unread = getUnreadNotifications();

      expect(unread).toHaveLength(2);
      expect(unread.every((n) => !n.read)).toBe(true);
    });

    it('getNotificationsByType should filter by type', () => {
      const { getNotificationsByType } = useNotificationStore.getState();
      const taskNotifications = getNotificationsByType('task_due_soon');

      expect(taskNotifications).toHaveLength(2);
      expect(taskNotifications.every((n) => n.type === 'task_due_soon')).toBe(true);
    });

    it('isPreferenceEnabled should check if preference is enabled', () => {
      const { isPreferenceEnabled } = useNotificationStore.getState();

      expect(isPreferenceEnabled('task_due_soon')).toBe(true);
      expect(isPreferenceEnabled('capacity_overload')).toBe(false);
      expect(isPreferenceEnabled('system')).toBe(true); // Default if not found
    });
  });
});
