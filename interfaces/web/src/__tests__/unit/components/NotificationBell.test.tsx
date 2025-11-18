import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { NotificationBell } from '@/components/NotificationBell';
import { useNotificationStore } from '@/stores/notificationStore';
import * as useNotificationWebSocketModule from '@/hooks/useNotificationWebSocket';

// Mock the notification store
vi.mock('@/stores/notificationStore', () => ({
  useNotificationStore: vi.fn(),
}));

// Mock the WebSocket hook
vi.mock('@/hooks/useNotificationWebSocket', () => ({
  useNotificationWebSocket: vi.fn(),
}));

describe('NotificationBell', () => {
  const mockFetchNotifications = vi.fn();
  const mockMarkAllAsRead = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useNotificationWebSocketModule.useNotificationWebSocket).mockReturnValue({
      sendMessage: vi.fn(),
      reconnect: vi.fn(),
      disconnect: vi.fn(),
    });
  });

  it('should render bell icon', () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      notifications: [],
      unreadCount: 0,
      markAllAsRead: mockMarkAllAsRead,
      fetchNotifications: mockFetchNotifications,
    } as any);

    render(<NotificationBell />);

    const button = screen.getByRole('button', { name: /notifications/i });
    expect(button).toBeInTheDocument();
  });

  it('should fetch notifications on mount', () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      notifications: [],
      unreadCount: 0,
      markAllAsRead: mockMarkAllAsRead,
      fetchNotifications: mockFetchNotifications,
    } as any);

    render(<NotificationBell />);

    expect(mockFetchNotifications).toHaveBeenCalled();
  });

  it('should display unread count badge when there are unread notifications', () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      notifications: [
        {
          id: '1',
          type: 'task_due_soon',
          title: 'Test',
          message: 'Test message',
          read: false,
          extraData: {},
          createdAt: '2025-11-17T10:00:00Z',
        },
      ],
      unreadCount: 3,
      markAllAsRead: mockMarkAllAsRead,
      fetchNotifications: mockFetchNotifications,
    } as any);

    render(<NotificationBell />);

    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('should display "9+" when unread count exceeds 9', () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      notifications: [],
      unreadCount: 15,
      markAllAsRead: mockMarkAllAsRead,
      fetchNotifications: mockFetchNotifications,
    } as any);

    render(<NotificationBell />);

    expect(screen.getByText('9+')).toBeInTheDocument();
  });

  it('should not display badge when there are no unread notifications', () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      notifications: [],
      unreadCount: 0,
      markAllAsRead: mockMarkAllAsRead,
      fetchNotifications: mockFetchNotifications,
    } as any);

    render(<NotificationBell />);

    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });

  it('should show "No new notifications" when there are no unread notifications', async () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      notifications: [],
      unreadCount: 0,
      markAllAsRead: mockMarkAllAsRead,
      fetchNotifications: mockFetchNotifications,
    } as any);

    render(<NotificationBell />);

    const button = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('No new notifications')).toBeInTheDocument();
    });
  });

  it('should display unread notifications in popover', async () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      notifications: [
        {
          id: '1',
          type: 'task_due_soon',
          title: 'Task Due Soon',
          message: 'Your task is due',
          read: false,
          extraData: {},
          createdAt: '2025-11-17T10:00:00Z',
        },
        {
          id: '2',
          type: 'system',
          title: 'System Update',
          message: 'System updated',
          read: false,
          extraData: {},
          createdAt: '2025-11-17T09:00:00Z',
        },
      ],
      unreadCount: 2,
      markAllAsRead: mockMarkAllAsRead,
      fetchNotifications: mockFetchNotifications,
    } as any);

    render(<NotificationBell />);

    const button = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Task Due Soon')).toBeInTheDocument();
      expect(screen.getByText('System Update')).toBeInTheDocument();
    });
  });

  it('should show "Mark all as read" button when there are unread notifications', async () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      notifications: [
        {
          id: '1',
          type: 'task_due_soon',
          title: 'Test',
          message: 'Test',
          read: false,
          extraData: {},
          createdAt: '2025-11-17T10:00:00Z',
        },
      ],
      unreadCount: 1,
      markAllAsRead: mockMarkAllAsRead,
      fetchNotifications: mockFetchNotifications,
    } as any);

    render(<NotificationBell />);

    const button = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Mark all as read')).toBeInTheDocument();
    });
  });

  it('should call markAllAsRead when "Mark all as read" button is clicked', async () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      notifications: [
        {
          id: '1',
          type: 'task_due_soon',
          title: 'Test',
          message: 'Test',
          read: false,
          extraData: {},
          createdAt: '2025-11-17T10:00:00Z',
        },
      ],
      unreadCount: 1,
      markAllAsRead: mockMarkAllAsRead,
      fetchNotifications: mockFetchNotifications,
    } as any);

    render(<NotificationBell />);

    const bellButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(bellButton);

    await waitFor(() => {
      const markAllButton = screen.getByText('Mark all as read');
      fireEvent.click(markAllButton);
    });

    expect(mockMarkAllAsRead).toHaveBeenCalled();
  });

  it('should limit displayed notifications to 5 most recent unread', async () => {
    const notifications = Array.from({ length: 10 }, (_, i) => ({
      id: `${i + 1}`,
      type: 'system' as const,
      title: `Notification ${i + 1}`,
      message: 'Test',
      read: false,
      extraData: {},
      createdAt: '2025-11-17T10:00:00Z',
    }));

    vi.mocked(useNotificationStore).mockReturnValue({
      notifications,
      unreadCount: 10,
      markAllAsRead: mockMarkAllAsRead,
      fetchNotifications: mockFetchNotifications,
    } as any);

    render(<NotificationBell />);

    const button = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(button);

    await waitFor(() => {
      const items = screen.getAllByText(/Notification/);
      expect(items).toHaveLength(5);
    });
  });

  it('should show "View all notifications" link when there are notifications', async () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      notifications: [
        {
          id: '1',
          type: 'task_due_soon',
          title: 'Test',
          message: 'Test',
          read: false,
          extraData: {},
          createdAt: '2025-11-17T10:00:00Z',
        },
      ],
      unreadCount: 1,
      markAllAsRead: mockMarkAllAsRead,
      fetchNotifications: mockFetchNotifications,
    } as any);

    render(<NotificationBell />);

    const button = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('View all notifications')).toBeInTheDocument();
    });
  });

  it('should initialize WebSocket connection', () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      notifications: [],
      unreadCount: 0,
      markAllAsRead: mockMarkAllAsRead,
      fetchNotifications: mockFetchNotifications,
    } as any);

    render(<NotificationBell />);

    expect(useNotificationWebSocketModule.useNotificationWebSocket).toHaveBeenCalled();
  });
});
