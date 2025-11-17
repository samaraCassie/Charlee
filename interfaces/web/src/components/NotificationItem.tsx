import { Check, X, AlertCircle, Info, TrendingUp, Calendar, FileText } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useNotificationStore, type Notification } from '@/stores/notificationStore';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface NotificationItemProps {
  notification: Notification;
}

// Icon mapping for notification types
const typeIcons = {
  task_due_soon: Calendar,
  capacity_overload: AlertCircle,
  cycle_phase_change: Info,
  freelance_invoice_ready: FileText,
  system: Info,
  achievement: TrendingUp,
};

// Color mapping for notification types
const typeColors = {
  task_due_soon: 'text-blue-500',
  capacity_overload: 'text-red-500',
  cycle_phase_change: 'text-purple-500',
  freelance_invoice_ready: 'text-green-500',
  system: 'text-gray-500',
  achievement: 'text-yellow-500',
};

export function NotificationItem({ notification }: NotificationItemProps) {
  const { markAsRead, deleteNotification } = useNotificationStore();

  const Icon = typeIcons[notification.type] || Info;
  const iconColor = typeColors[notification.type] || 'text-gray-500';

  const handleClick = () => {
    if (!notification.read) {
      markAsRead(notification.id);
    }

    // Navigate to action URL if present
    if (notification.metadata?.action_url) {
      window.location.href = notification.metadata.action_url;
    }
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    deleteNotification(notification.id);
  };

  const handleMarkAsRead = (e: React.MouseEvent) => {
    e.stopPropagation();
    markAsRead(notification.id);
  };

  const timeAgo = formatDistanceToNow(new Date(notification.createdAt), {
    addSuffix: true,
  });

  return (
    <div
      className={cn(
        'flex items-start gap-3 px-4 py-3 transition-colors hover:bg-accent',
        !notification.read && 'bg-blue-50/50',
        notification.metadata?.action_url && 'cursor-pointer'
      )}
      onClick={handleClick}
      role={notification.metadata?.action_url ? 'button' : undefined}
      tabIndex={notification.metadata?.action_url ? 0 : undefined}
    >
      {/* Icon */}
      <div className={cn('mt-0.5', iconColor)}>
        <Icon className="h-5 w-5" />
      </div>

      {/* Content */}
      <div className="flex-1 space-y-1">
        <div className="flex items-start justify-between gap-2">
          <p className={cn('text-sm font-medium', !notification.read && 'font-semibold')}>
            {notification.title}
          </p>
          <span className="text-xs text-muted-foreground whitespace-nowrap">{timeAgo}</span>
        </div>

        <p className="text-sm text-muted-foreground">{notification.message}</p>

        {/* Priority badge */}
        {notification.metadata?.priority && (
          <span
            className={cn(
              'inline-block rounded-full px-2 py-0.5 text-xs font-medium',
              notification.metadata.priority === 'critical' && 'bg-red-100 text-red-800',
              notification.metadata.priority === 'high' && 'bg-orange-100 text-orange-800',
              notification.metadata.priority === 'medium' && 'bg-yellow-100 text-yellow-800',
              notification.metadata.priority === 'low' && 'bg-gray-100 text-gray-800'
            )}
          >
            {notification.metadata.priority}
          </span>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-1">
        {!notification.read && (
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={handleMarkAsRead}
            title="Mark as read"
          >
            <Check className="h-4 w-4" />
          </Button>
        )}
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7"
          onClick={handleDelete}
          title="Delete notification"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
