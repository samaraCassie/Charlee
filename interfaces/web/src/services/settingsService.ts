import api from './api';

export interface UserSettings {
  user_id: string;
  display_name: string;
  email?: string;
  timezone: string;
  language: string;
  
  // Notificações
  notifications_enabled: boolean;
  email_notifications: boolean;
  push_notifications: boolean;
  
  // Exibição
  theme: 'auto' | 'light' | 'dark';
  density: 'compact' | 'comfortable' | 'spacious';
  
  // Planejamento
  work_hours_per_day: number;
  work_days_per_week: number;
  planning_horizon_days: number;
  
  // Ciclo
  cycle_tracking_enabled: boolean;
  cycle_length_days: number;
  
  // Integrações
  google_calendar_enabled: boolean;
  notion_enabled: boolean;
  trello_enabled: boolean;
}

export interface SystemStats {
  version: string;
  uptime_seconds: number;
  total_users: number;
  total_tasks: number;
  total_big_rocks: number;
  last_backup?: string;
}

export interface IntegrationStatus {
  enabled: boolean;
  connected: boolean;
  last_sync?: string;
}

export interface IntegrationsStatus {
  google_calendar: IntegrationStatus;
  notion: IntegrationStatus;
  trello: IntegrationStatus;
  github: IntegrationStatus;
}

export const settingsService = {
  /**
   * Get configurações do usuário
   */
  async getUserSettings(): Promise<UserSettings> {
    const response = await api.get('/v2/settings/user');
    return response.data;
  },

  /**
   * Update configurações do usuário
   */
  async updateUserSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
    const response = await api.patch('/v2/settings/user', settings);
    return response.data;
  },

  /**
   * Get estatísticas do sistema
   */
  async getSystemStats(): Promise<SystemStats> {
    const response = await api.get('/v2/settings/system');
    return response.data;
  },

  /**
   * Export todos os dados do usuário
   */
  async exportUserData(): Promise<Blob> {
    const response = await api.post('/v2/settings/export', null, {
      responseType: 'blob'
    });
    return response.data;
  },

  /**
   * Reset dados do usuário (CUIDADO!)
   */
  async resetUserData(confirm: boolean = false): Promise<{ message: string }> {
    const response = await api.post('/v2/settings/reset', null, {
      params: { confirm }
    });
    return response.data;
  },

  /**
   * Get status das integrações
   */
  async getIntegrationsStatus(): Promise<IntegrationsStatus> {
    const response = await api.get('/v2/settings/integrations');
    return response.data;
  },

  /**
   * Connect integração externa
   */
  async connectIntegration(service: string): Promise<{ message: string; status: string }> {
    const response = await api.post(`/v2/settings/integrations/${service}/connect`);
    return response.data;
  },

  /**
   * Download export de dados
   */
  downloadExport(data: Blob, filename: string = 'charlee-export.json') {
    const url = window.URL.createObjectURL(data);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};