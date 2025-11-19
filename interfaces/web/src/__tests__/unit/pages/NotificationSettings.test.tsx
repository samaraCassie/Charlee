import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import NotificationSettings from '@/pages/NotificationSettings';
import { useNotificationStore } from '@/stores/notificationStore';
import * as useToastModule from '@/hooks/use-toast';

// Mock the notification store
vi.mock('@/stores/notificationStore', () => ({
  useNotificationStore: vi.fn(),
}));

// Mock the toast hook
vi.mock('@/hooks/use-toast', () => ({
  useToast: vi.fn(),
}));

describe('NotificationSettings', () => {
  const mockFetchPreferences = vi.fn();
  const mockUpdatePreference = vi.fn();
  const mockToast = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useToastModule.useToast).mockReturnValue({
      toast: mockToast,
      dismiss: vi.fn(),
      toasts: [],
    });
  });

  it('should show loading state initially', () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      preferences: [],
      fetchPreferences: mockFetchPreferences,
      updatePreference: mockUpdatePreference,
      loading: true,
    } as any);

    render(<NotificationSettings />);

    expect(screen.getByText('Carregando preferências...')).toBeInTheDocument();
  });

  it('should fetch preferences on mount', () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      preferences: [],
      fetchPreferences: mockFetchPreferences,
      updatePreference: mockUpdatePreference,
      loading: false,
    } as any);

    render(<NotificationSettings />);

    expect(mockFetchPreferences).toHaveBeenCalled();
  });

  it('should display empty state when no preferences', () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      preferences: [],
      fetchPreferences: mockFetchPreferences,
      updatePreference: mockUpdatePreference,
      loading: false,
    } as any);

    render(<NotificationSettings />);

    expect(screen.getByText('Nenhuma preferência de notificação configurada')).toBeInTheDocument();
  });

  it('should display preferences when available', () => {
    const preferences = [
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
        enabled: true,
        inAppEnabled: true,
        emailEnabled: true,
        pushEnabled: false,
      },
    ];

    vi.mocked(useNotificationStore).mockReturnValue({
      preferences,
      fetchPreferences: mockFetchPreferences,
      updatePreference: mockUpdatePreference,
      loading: false,
    } as any);

    render(<NotificationSettings />);

    expect(screen.getByText('Tarefa com Prazo Próximo')).toBeInTheDocument();
    expect(screen.getByText('Sobrecarga de Capacidade')).toBeInTheDocument();
  });

  it('should show channel toggles when preference is enabled', () => {
    const preferences = [
      {
        id: '1',
        notificationType: 'task_due_soon',
        enabled: true,
        inAppEnabled: true,
        emailEnabled: false,
        pushEnabled: false,
      },
    ];

    vi.mocked(useNotificationStore).mockReturnValue({
      preferences,
      fetchPreferences: mockFetchPreferences,
      updatePreference: mockUpdatePreference,
      loading: false,
    } as any);

    render(<NotificationSettings />);

    expect(screen.getByText('No aplicativo')).toBeInTheDocument();
    expect(screen.getByText('Por e-mail')).toBeInTheDocument();
    expect(screen.getByText('Push (celular)')).toBeInTheDocument();
  });

  it('should not show channel toggles when preference is disabled', () => {
    const preferences = [
      {
        id: '1',
        notificationType: 'task_due_soon',
        enabled: false,
        inAppEnabled: true,
        emailEnabled: false,
        pushEnabled: false,
      },
    ];

    vi.mocked(useNotificationStore).mockReturnValue({
      preferences,
      fetchPreferences: mockFetchPreferences,
      updatePreference: mockUpdatePreference,
      loading: false,
    } as any);

    render(<NotificationSettings />);

    expect(screen.queryByText('No aplicativo')).not.toBeInTheDocument();
  });

  it('should call updatePreference when toggling enabled', async () => {
    mockUpdatePreference.mockResolvedValue({});

    const preferences = [
      {
        id: '1',
        notificationType: 'task_due_soon',
        enabled: true,
        inAppEnabled: true,
        emailEnabled: false,
        pushEnabled: false,
      },
    ];

    vi.mocked(useNotificationStore).mockReturnValue({
      preferences,
      fetchPreferences: mockFetchPreferences,
      updatePreference: mockUpdatePreference,
      loading: false,
    } as any);

    render(<NotificationSettings />);

    const switches = screen.getAllByRole('checkbox');
    const mainSwitch = switches[0]; // First switch is the main enabled toggle

    fireEvent.click(mainSwitch);

    await waitFor(() => {
      expect(mockUpdatePreference).toHaveBeenCalledWith('task_due_soon', { enabled: false });
    });
  });

  it('should show success toast when preference is updated', async () => {
    mockUpdatePreference.mockResolvedValue({});

    const preferences = [
      {
        id: '1',
        notificationType: 'task_due_soon',
        enabled: true,
        inAppEnabled: true,
        emailEnabled: false,
        pushEnabled: false,
      },
    ];

    vi.mocked(useNotificationStore).mockReturnValue({
      preferences,
      fetchPreferences: mockFetchPreferences,
      updatePreference: mockUpdatePreference,
      loading: false,
    } as any);

    render(<NotificationSettings />);

    const switches = screen.getAllByRole('checkbox');
    fireEvent.click(switches[0]);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Preferência atualizada',
        })
      );
    });
  });

  it('should show error toast when update fails', async () => {
    mockUpdatePreference.mockRejectedValue(new Error('Update failed'));

    const preferences = [
      {
        id: '1',
        notificationType: 'task_due_soon',
        enabled: true,
        inAppEnabled: true,
        emailEnabled: false,
        pushEnabled: false,
      },
    ];

    vi.mocked(useNotificationStore).mockReturnValue({
      preferences,
      fetchPreferences: mockFetchPreferences,
      updatePreference: mockUpdatePreference,
      loading: false,
    } as any);

    render(<NotificationSettings />);

    const switches = screen.getAllByRole('checkbox');
    fireEvent.click(switches[0]);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Erro ao atualizar',
          variant: 'destructive',
        })
      );
    });
  });

  it('should call updatePreference when toggling channel', async () => {
    mockUpdatePreference.mockResolvedValue({});

    const preferences = [
      {
        id: '1',
        notificationType: 'task_due_soon',
        enabled: true,
        inAppEnabled: true,
        emailEnabled: false,
        pushEnabled: false,
      },
    ];

    vi.mocked(useNotificationStore).mockReturnValue({
      preferences,
      fetchPreferences: mockFetchPreferences,
      updatePreference: mockUpdatePreference,
      loading: false,
    } as any);

    render(<NotificationSettings />);

    // Find the email channel toggle
    const emailSwitch = screen.getAllByRole('checkbox')[2]; // 0=main, 1=in_app, 2=email

    fireEvent.click(emailSwitch);

    await waitFor(() => {
      expect(mockUpdatePreference).toHaveBeenCalledWith('task_due_soon', {
        email_enabled: true,
      });
    });
  });

  it('should display all notification types with correct icons and descriptions', () => {
    const preferences = [
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
        enabled: true,
        inAppEnabled: true,
        emailEnabled: false,
        pushEnabled: false,
      },
      {
        id: '3',
        notificationType: 'cycle_phase_change',
        enabled: true,
        inAppEnabled: true,
        emailEnabled: false,
        pushEnabled: false,
      },
      {
        id: '4',
        notificationType: 'freelance_invoice_ready',
        enabled: true,
        inAppEnabled: true,
        emailEnabled: false,
        pushEnabled: false,
      },
      {
        id: '5',
        notificationType: 'system',
        enabled: true,
        inAppEnabled: true,
        emailEnabled: false,
        pushEnabled: false,
      },
      {
        id: '6',
        notificationType: 'achievement',
        enabled: true,
        inAppEnabled: true,
        emailEnabled: false,
        pushEnabled: false,
      },
    ];

    vi.mocked(useNotificationStore).mockReturnValue({
      preferences,
      fetchPreferences: mockFetchPreferences,
      updatePreference: mockUpdatePreference,
      loading: false,
    } as any);

    render(<NotificationSettings />);

    expect(screen.getByText('Tarefa com Prazo Próximo')).toBeInTheDocument();
    expect(screen.getByText('Sobrecarga de Capacidade')).toBeInTheDocument();
    expect(screen.getByText('Mudança de Fase do Ciclo')).toBeInTheDocument();
    expect(screen.getByText('Fatura Freelance Pronta')).toBeInTheDocument();
    expect(screen.getByText('Notificações do Sistema')).toBeInTheDocument();
    expect(screen.getByText('Conquistas')).toBeInTheDocument();
  });

  it('should display information about notification channels', () => {
    vi.mocked(useNotificationStore).mockReturnValue({
      preferences: [],
      fetchPreferences: mockFetchPreferences,
      updatePreference: mockUpdatePreference,
      loading: false,
    } as any);

    render(<NotificationSettings />);

    expect(screen.getByText('Sobre as Notificações')).toBeInTheDocument();
    expect(screen.getByText(/No aplicativo:/)).toBeInTheDocument();
    expect(screen.getByText(/Por e-mail:/)).toBeInTheDocument();
    expect(screen.getByText(/Push:/)).toBeInTheDocument();
  });
});
