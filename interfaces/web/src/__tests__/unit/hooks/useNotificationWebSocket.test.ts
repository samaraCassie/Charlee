import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useNotificationWebSocket } from '@/hooks/useNotificationWebSocket';
import { useNotificationStore } from '@/stores/notificationStore';

// Mock the notification store
vi.mock('@/stores/notificationStore', () => ({
  useNotificationStore: vi.fn(),
}));

// Mock WebSocket
class MockWebSocket {
  public onopen: ((event: Event) => void) | null = null;
  public onmessage: ((event: MessageEvent) => void) | null = null;
  public onerror: ((event: Event) => void) | null = null;
  public onclose: ((event: CloseEvent) => void) | null = null;
  public readyState: number = WebSocket.CONNECTING;

  constructor(public url: string) {
    // Trigger onopen synchronously
    queueMicrotask(() => {
      this.readyState = WebSocket.OPEN;
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    });
  }

  send(data: string) {
    // Mock send
  }

  close() {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) {
      this.onclose(new CloseEvent('close'));
    }
  }

  // Helper to simulate receiving a message
  simulateMessage(data: any) {
    if (this.onmessage) {
      this.onmessage(new MessageEvent('message', { data: JSON.stringify(data) }));
    }
  }
}

describe('useNotificationWebSocket', () => {
  let mockAddNotification: ReturnType<typeof vi.fn>;
  let mockUpdateUnreadCount: ReturnType<typeof vi.fn>;
  let mockSetWsConnected: ReturnType<typeof vi.fn>;
  let mockFetchNotifications: ReturnType<typeof vi.fn>;
  let originalWebSocket: typeof WebSocket;
  let mockWebSocketInstance: MockWebSocket;

  beforeEach(() => {
    // Create stable mock functions
    mockAddNotification = vi.fn();
    mockUpdateUnreadCount = vi.fn();
    mockSetWsConnected = vi.fn();
    mockFetchNotifications = vi.fn().mockResolvedValue(undefined);

    // Mock the store with stable references
    const mockStore = {
      addNotification: mockAddNotification,
      updateUnreadCount: mockUpdateUnreadCount,
      setWsConnected: mockSetWsConnected,
      fetchNotifications: mockFetchNotifications,
      notifications: [],
      unreadCount: 0,
      wsConnected: false,
      markAsRead: vi.fn(),
      markAllAsRead: vi.fn(),
      deleteNotification: vi.fn(),
    };

    vi.mocked(useNotificationStore).mockReturnValue(mockStore as any);

    // Mock localStorage
    Storage.prototype.getItem = vi.fn((key) => {
      if (key === 'token') return 'mock-token';
      return null;
    });

    // Mock WebSocket
    originalWebSocket = global.WebSocket;
    // Store the instance when MockWebSocket is constructed
    const OriginalMockWebSocket = MockWebSocket;
    const WebSocketMockClass = class extends OriginalMockWebSocket {
      constructor(url: string) {
        super(url);
        mockWebSocketInstance = this as any;
      }
    };
    global.WebSocket = vi.fn((url: string) => new WebSocketMockClass(url)) as any;

    // Mock Notification API
    global.Notification = {
      permission: 'default',
      requestPermission: vi.fn().mockResolvedValue('granted'),
    } as any;
  });

  afterEach(() => {
    global.WebSocket = originalWebSocket;
    vi.clearAllMocks();
  });

  it('should connect to WebSocket on mount', async () => {
    renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(global.WebSocket).toHaveBeenCalledWith(
        expect.stringContaining('/ws/notifications?token=mock-token')
      );
    });
  });

  it('should not connect if no token is available', () => {
    Storage.prototype.getItem = vi.fn(() => null);

    renderHook(() => useNotificationWebSocket());

    expect(global.WebSocket).not.toHaveBeenCalled();
  });

  it('should set wsConnected to true when connection opens', async () => {
    renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(mockSetWsConnected).toHaveBeenCalledWith(true);
    });
  });

  it('should fetch notifications on mount', async () => {
    renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(mockFetchNotifications).toHaveBeenCalled();
    });
  });

  it('should handle "connected" message', async () => {
    renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(mockWebSocketInstance).toBeDefined();
    });

    mockWebSocketInstance.simulateMessage({
      type: 'connected',
      data: { message: 'Connected to notification service' },
    });

    // Should not throw any errors
    expect(true).toBe(true);
  });

  it('should handle "notification" message and add to store', async () => {
    renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(mockWebSocketInstance).toBeDefined();
    });

    const notificationData = {
      type: 'notification',
      data: {
        id: 1,
        type: 'task_due_soon',
        title: 'Task Due Soon',
        message: 'Your task is due',
        read: false,
        extra_data: { priority: 'high' },
        created_at: '2025-11-17T10:00:00Z',
      },
    };

    mockWebSocketInstance.simulateMessage(notificationData);

    await waitFor(() => {
      expect(mockAddNotification).toHaveBeenCalledWith(
        expect.objectContaining({
          id: '1',
          type: 'task_due_soon',
          title: 'Task Due Soon',
          message: 'Your task is due',
          read: false,
        })
      );
    });
  });

  it('should handle "unread_count" message', async () => {
    renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(mockWebSocketInstance).toBeDefined();
    });

    mockWebSocketInstance.simulateMessage({
      type: 'unread_count',
      data: { count: 5 },
    });

    await waitFor(() => {
      expect(mockUpdateUnreadCount).toHaveBeenCalledWith(5);
    });
  });

  it('should respond to heartbeat with pong', async () => {
    const sendSpy = vi.spyOn(MockWebSocket.prototype, 'send');

    renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(mockWebSocketInstance).toBeDefined();
    });

    mockWebSocketInstance.simulateMessage({
      type: 'heartbeat',
      data: {},
    });

    await waitFor(() => {
      expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({ type: 'pong' }));
    });
  });

  it('should set wsConnected to false on error', async () => {
    renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(mockWebSocketInstance).toBeDefined();
    });

    if (mockWebSocketInstance.onerror) {
      mockWebSocketInstance.onerror(new Event('error'));
    }

    await waitFor(() => {
      expect(mockSetWsConnected).toHaveBeenCalledWith(false);
    });
  });

  it('should set wsConnected to false on close', async () => {
    renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(mockWebSocketInstance).toBeDefined();
    });

    if (mockWebSocketInstance.onclose) {
      mockWebSocketInstance.onclose(new CloseEvent('close'));
    }

    await waitFor(() => {
      expect(mockSetWsConnected).toHaveBeenCalledWith(false);
    });
  });

  it('should disconnect on unmount', async () => {
    const { unmount } = renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(mockWebSocketInstance).toBeDefined();
    });

    const closeSpy = vi.spyOn(mockWebSocketInstance, 'close');

    unmount();

    expect(closeSpy).toHaveBeenCalled();
  });

  it('should request notification permission if default', async () => {
    global.Notification = {
      permission: 'default',
      requestPermission: vi.fn().mockResolvedValue('granted'),
    } as any;

    renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(global.Notification.requestPermission).toHaveBeenCalled();
    });
  });

  it('should not request notification permission if already granted', async () => {
    global.Notification = {
      permission: 'granted',
      requestPermission: vi.fn(),
    } as any;

    renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(global.Notification.requestPermission).not.toHaveBeenCalled();
    });
  });

  it('should send message when sendMessage is called', async () => {
    const { result } = renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(mockWebSocketInstance).toBeDefined();
    });

    const sendSpy = vi.spyOn(mockWebSocketInstance, 'send');

    result.current.sendMessage({ type: 'test', data: 'test data' });

    expect(sendSpy).toHaveBeenCalledWith(
      JSON.stringify({ type: 'test', data: 'test data' })
    );
  });

  it('should warn when trying to send message on closed connection', async () => {
    const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

    const { result } = renderHook(() => useNotificationWebSocket());

    await waitFor(() => {
      expect(mockWebSocketInstance).toBeDefined();
    });

    mockWebSocketInstance.readyState = WebSocket.CLOSED;

    result.current.sendMessage({ type: 'test' });

    expect(consoleWarnSpy).toHaveBeenCalledWith('WebSocket is not connected');

    consoleWarnSpy.mockRestore();
  });
});
