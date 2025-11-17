import { useEffect, useRef, useCallback } from 'react';
import { useNotificationStore } from '@/stores/notificationStore';

interface WebSocketMessage {
  type: 'connected' | 'notification' | 'unread_count' | 'heartbeat' | 'notification_read' | 'error';
  data: any;
}

/**
 * Custom hook for WebSocket connection to notification service
 * Handles real-time notification updates
 */
export function useNotificationWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000; // 3 seconds

  const {
    addNotification,
    updateUnreadCount,
    setWsConnected,
    fetchNotifications,
  } = useNotificationStore();

  const connect = useCallback(() => {
    // Get auth token from localStorage
    const token = localStorage.getItem('token');
    if (!token) {
      console.warn('No auth token found, skipping WebSocket connection');
      return;
    }

    // Get WebSocket URL from env or use default
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const url = `${wsUrl}/ws/notifications?token=${token}`;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        setWsConnected(true);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          switch (message.type) {
            case 'connected':
              console.log('WebSocket connection established:', message.data);
              break;

            case 'notification':
              // New notification received
              const notification = {
                id: message.data.id.toString(),
                type: message.data.type,
                title: message.data.title,
                message: message.data.message,
                read: message.data.read,
                metadata: message.data.metadata,
                createdAt: message.data.created_at,
                readAt: message.data.read_at,
              };
              addNotification(notification);

              // Show browser notification if permitted
              if (Notification.permission === 'granted') {
                new Notification(notification.title, {
                  body: notification.message,
                  icon: '/charlee-icon.png',
                });
              }
              break;

            case 'unread_count':
              updateUnreadCount(message.data.count);
              break;

            case 'heartbeat':
              // Respond to heartbeat
              ws.send(JSON.stringify({ type: 'pong' }));
              break;

            case 'notification_read':
              // Notification marked as read
              if (message.data.success) {
                console.log('Notification marked as read:', message.data.notification_id);
              }
              break;

            case 'error':
              console.error('WebSocket error message:', message.data);
              break;

            default:
              console.warn('Unknown WebSocket message type:', message.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setWsConnected(false);
        wsRef.current = null;

        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(
            `Reconnecting... (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          );
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectDelay);
        } else {
          console.error('Max reconnection attempts reached');
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      setWsConnected(false);
    }
  }, [addNotification, updateUnreadCount, setWsConnected]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setWsConnected(false);
  }, [setWsConnected]);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  // Request browser notification permission
  useEffect(() => {
    if (Notification.permission === 'default') {
      Notification.requestPermission().then((permission) => {
        console.log('Notification permission:', permission);
      });
    }
  }, []);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();
    fetchNotifications(); // Fetch initial notifications

    return () => {
      disconnect();
    };
  }, [connect, disconnect, fetchNotifications]);

  return {
    sendMessage,
    reconnect: connect,
    disconnect,
  };
}
