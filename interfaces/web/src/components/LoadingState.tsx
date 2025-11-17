import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoadingStateProps {
  message?: string;
  submessage?: string;
  variant?: 'default' | 'card' | 'inline';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Carregando...',
  submessage,
  variant = 'default',
  size = 'md',
  className,
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
  };

  const renderContent = () => (
    <div className="flex flex-col items-center justify-center gap-3">
      {/* Animated spinner */}
      <div className="relative">
        <Loader2 className={cn(sizeClasses[size], 'animate-spin text-primary')} />
        {/* Pulse effect */}
        <div
          className={cn(
            sizeClasses[size],
            'absolute top-0 left-0 animate-ping opacity-20 bg-primary rounded-full'
          )}
        />
      </div>

      {/* Messages */}
      <div className="space-y-1 text-center">
        <p className={cn(textSizeClasses[size], 'font-medium text-foreground')}>{message}</p>
        {submessage && (
          <p className="text-sm text-muted-foreground animate-pulse">{submessage}</p>
        )}
      </div>

      {/* Progress dots */}
      <div className="flex gap-1.5">
        <div className="h-2 w-2 rounded-full bg-primary animate-bounce [animation-delay:-0.3s]" />
        <div className="h-2 w-2 rounded-full bg-primary animate-bounce [animation-delay:-0.15s]" />
        <div className="h-2 w-2 rounded-full bg-primary animate-bounce" />
      </div>
    </div>
  );

  if (variant === 'inline') {
    return (
      <div className={cn('flex items-center gap-2', className)}>
        <Loader2 className={cn(sizeClasses[size], 'animate-spin text-primary')} />
        <span className={cn(textSizeClasses[size], 'text-muted-foreground')}>{message}</span>
      </div>
    );
  }

  if (variant === 'card') {
    return (
      <div className={cn('rounded-lg border border-border bg-card p-8', className)}>
        {renderContent()}
      </div>
    );
  }

  return <div className={cn('py-12', className)}>{renderContent()}</div>;
};

// Skeleton components for content loading
export const SkeletonText: React.FC<{ className?: string; lines?: number }> = ({
  className,
  lines = 1,
}) => (
  <div className={cn('space-y-2', className)}>
    {Array.from({ length: lines }).map((_, i) => (
      <div
        key={i}
        className={cn(
          'h-4 bg-muted rounded animate-pulse',
          i === lines - 1 && 'w-3/4' // Last line shorter
        )}
      />
    ))}
  </div>
);

export const SkeletonCard: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('rounded-lg border border-border bg-card p-4 space-y-3', className)}>
    <div className="h-5 w-1/3 bg-muted rounded animate-pulse" />
    <SkeletonText lines={2} />
    <div className="flex gap-2">
      <div className="h-8 w-20 bg-muted rounded animate-pulse" />
      <div className="h-8 w-20 bg-muted rounded animate-pulse" />
    </div>
  </div>
);
