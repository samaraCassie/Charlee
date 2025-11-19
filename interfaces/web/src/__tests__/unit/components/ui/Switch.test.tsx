import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Switch } from '@/components/ui/switch';

describe('Switch', () => {
  it('should render unchecked by default', () => {
    const { container } = render(<Switch />);
    const input = container.querySelector('input[type="checkbox"]');
    expect(input).toBeInTheDocument();
    expect(input).not.toBeChecked();
  });

  it('should render checked when checked prop is true', () => {
    const { container } = render(<Switch checked={true} />);
    const input = container.querySelector('input[type="checkbox"]');
    expect(input).toBeChecked();
  });

  it('should call onCheckedChange when clicked', () => {
    const handleChange = vi.fn();
    const { container } = render(<Switch onCheckedChange={handleChange} />);

    const label = container.querySelector('label');
    expect(label).toBeInTheDocument();

    if (label) {
      fireEvent.click(label);
      expect(handleChange).toHaveBeenCalledWith(true);
    }
  });

  it('should toggle from checked to unchecked', () => {
    const handleChange = vi.fn();
    const { container } = render(<Switch checked={true} onCheckedChange={handleChange} />);

    const label = container.querySelector('label');
    if (label) {
      fireEvent.click(label);
      expect(handleChange).toHaveBeenCalledWith(false);
    }
  });

  it('should not call onCheckedChange when disabled', () => {
    const handleChange = vi.fn();
    const { container } = render(<Switch disabled onCheckedChange={handleChange} />);

    const input = container.querySelector('input[type="checkbox"]');
    if (input) {
      fireEvent.click(input);
      expect(handleChange).not.toHaveBeenCalled();
    }
  });

  it('should apply disabled styles when disabled', () => {
    const { container } = render(<Switch disabled />);
    const label = container.querySelector('label');
    expect(label).toHaveClass('opacity-50');
    expect(label).toHaveClass('cursor-not-allowed');
  });

  it('should apply custom className', () => {
    const { container } = render(<Switch className="custom-class" />);
    const label = container.querySelector('label');
    expect(label).toHaveClass('custom-class');
  });

  it('should apply checked styles when checked', () => {
    const { container } = render(<Switch checked={true} />);
    const label = container.querySelector('label');
    expect(label).toHaveClass('bg-primary');
  });

  it('should apply unchecked styles when not checked', () => {
    const { container } = render(<Switch checked={false} />);
    const label = container.querySelector('label');
    expect(label).toHaveClass('bg-input');
  });
});
