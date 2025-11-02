import api from './api';

export interface WeeklyStats {
  day: string;
  completed: number;
  pending: number;
}

export interface MonthlyStats {
  month: string;
  tasks: number;
}

export interface BigRockDistribution {
  name: string;
  value: number;
  color: string;
}

export interface ProductivityStats {
  completion_rate: number;
  avg_time_per_task: number;
  productivity_trend: number;
  overdue_tasks: number;
}

export interface CycleProductivity {
  menstrual: number;
  follicular: number;
  ovulation: number;
  luteal: number;
}

export const analyticsService = {
  /**
   * Get estatísticas semanais (últimos 7 dias)
   */
  async getWeeklyStats(): Promise<WeeklyStats[]> {
    const response = await api.get('/v2/analytics/weekly');
    return response.data;
  },

  /**
   * Get estatísticas mensais (últimos 6 meses)
   */
  async getMonthlyStats(): Promise<MonthlyStats[]> {
    const response = await api.get('/v2/analytics/monthly');
    return response.data;
  },

  /**
   * Get distribuição de tarefas por Big Rock
   */
  async getBigRocksDistribution(): Promise<BigRockDistribution[]> {
    const response = await api.get('/v2/analytics/big-rocks-distribution');
    return response.data;
  },

  /**
   * Get estatísticas gerais de produtividade
   */
  async getProductivityStats(): Promise<ProductivityStats> {
    const response = await api.get('/v2/analytics/productivity');
    return response.data;
  },

  /**
   * Get produtividade por fase do ciclo
   */
  async getCycleProductivity(): Promise<CycleProductivity> {
    const response = await api.get('/v2/analytics/cycle-productivity');
    return response.data;
  },
};