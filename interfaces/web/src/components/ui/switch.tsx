import * as React from 'react';
import { cn } from '@/lib/utils';

export interface SwitchProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
}

const Switch = React.forwardRef<HTMLInputElement, SwitchProps>(
  ({ className, checked, onCheckedChange, disabled, ...props }, ref) => {
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      if (!disabled) {
        onCheckedChange?.(event.target.checked);
      }
    };

    return (
      <label
        className={cn(
          'relative inline-flex h-6 w-11 cursor-pointer items-center rounded-full transition-colors',
          checked ? 'bg-primary' : 'bg-input',
          disabled && 'cursor-not-allowed opacity-50',
          className
        )}
      >
        <input
          type="checkbox"
          className="sr-only"
          ref={ref}
          checked={checked}
          onChange={handleChange}
          disabled={disabled}
          {...props}
        />
        <span
          className={cn(
            'inline-block h-5 w-5 transform rounded-full bg-white shadow-lg transition-transform',
            checked ? 'translate-x-5' : 'translate-x-0.5'
          )}
        />
      </label>
    );
  }
);

Switch.displayName = 'Switch';

export { Switch };
