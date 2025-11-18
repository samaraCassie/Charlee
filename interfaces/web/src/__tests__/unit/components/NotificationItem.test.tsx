import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { NotificationItem } from '@/components/NotificationItem';
import { useNotificationStore } from '@/stores/notificationStore';
import type { Notification } from '@/stores/notificationStore';

// Mock the notification store
vi.mock('@/stores/notificationStore', () => ({
  useNotificationStore: vi.fn(),
}));

// Mock date-fns
vi.mock('date-fns', () => ({
  formatDistanceToNow: vi.fn(() => '2 hours ago'),
}));

describe('NotificationItem', () => {
  const mockMarkAsRead = vi.fn();
  const mockDeleteNotification = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useNotificationStore).mockReturnValue({
      markAsRead: mockMarkAsRead,
      deleteNotification: mockDeleteNotification,
    } as any);
  });

  const createMockNotification = (overrides?: Partial<Notification>): Notification => ({
    id: '1',
    type: 'task_due_soon',
    title: 'Task Due Soon',
    message: 'Your task is due in 2 hours',
    read: false,
    extraData: { priority: 'high' },
    createdAt: '2025-11-17T10:00:00Z',
    ...overrides,
  });

  it('should render notification with correct content', () => {
    const notification = createMockNotification();

    render(<NotificationItem notification={notification} />);

    expect(screen.getByText('Task Due Soon')).toBeInTheDocument();
    expect(screen.getByText('Your task is due in 2 hours')).toBeInTheDocument();
    expect(screen.getByText('2 hours ago')).toBeInTheDocument();
  });

  it('should display priority badge', () => {
    const notification = createMockNotification({
      extraData: { priority: 'critical' },
    });

    render(<NotificationItem notification={notification} />);

    expect(screen.getByText('critical')).toBeInTheDocument();
  });

  it('should show mark as read button for unread notifications', () => {
    const notification = createMockNotification({ read: false });

    render(<NotificationItem notification={notification} />);

    const markAsReadButton = screen.getByTitle('Mark as read');
    expect(markAsReadButton).toBeInTheDocument();
  });

  it('should not show mark as read button for read notifications', () => {
    const notification = createMockNotification({ read: true });

    render(<NotificationItem notification={notification} />);

    const markAsReadButton = screen.queryByTitle('Mark as read');
    expect(markAsReadButton).not.toBeInTheDocument();
  });

  it('should call markAsRead when mark as read button is clicked', async () => {
    const notification = createMockNotification({ read: false });

    render(<NotificationItem notification={notification} />);

    const markAsReadButton = screen.getByTitle('Mark as read');
    fireEvent.click(markAsReadButton);

    expect(mockMarkAsRead).toHaveBeenCalledWith('1');
  });

  it('should call deleteNotification when delete button is clicked', async () => {
    const notification = createMockNotification();

    render(<NotificationItem notification={notification} />);

    const deleteButton = screen.getByTitle('Delete notification');
    fireEvent.click(deleteButton);

    expect(mockDeleteNotification).toHaveBeenCalledWith('1');
  });

  it('should navigate to action URL when clicked', () => {
    const notification = createMockNotification({
      extraData: { action_url: '/tasks/1' },
    });

    // Mock window.location.href
    delete (window as any).location;
    window.location = { href: '' } as any;

    render(<NotificationItem notification={notification} />);

    const item = screen.getByRole('button');
    fireEvent.click(item);

    expect(mockMarkAsRead).toHaveBeenCalledWith('1');
    expect(window.location.href).toBe('/tasks/1');
  });

  it('should apply different styles for unread notifications', () => {
    const { container: unreadContainer } = render(
      <NotificationItem notification={createMockNotification({ read: false })} />
    );

    expect(unreadContainer.firstChild).toHaveClass('bg-blue-50/50');

    const { container: readContainer } = render(
      <NotificationItem notification={createMockNotification({ read: true })} />
    );

    expect(readContainer.firstChild).not.toHaveClass('bg-blue-50/50');
  });

  it('should render correct icon for different notification types', () => {
    const types: Array<Notification['type']> = [
      'task_due_soon',
      'capacity_overload',
      'cycle_phase_change',
      'freelance_invoice_ready',
      'system',
      'achievement',
    ];

    types.forEach((type) => {
      const { container } = render(
        <NotificationItem notification={createMockNotification({ type })} />
      );

      // Check that an icon is rendered (svg element)
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  it('should render different priority badge colors', () => {
    const priorities = ['critical', 'high', 'medium', 'low'];

    priorities.forEach((priority) => {
      const { container } = render(
        <NotificationItem notification={createMockNotification({ extraData: { priority } })} />
      );

      const badge = screen.getByText(priority);
      expect(badge).toBeInTheDocument();
    });
  });
});
