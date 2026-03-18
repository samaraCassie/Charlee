import api from './api';
import type { TaskAPI } from './taskService';

export interface InboxResponse {
  inbox_text: string;
  tasks: TaskAPI[];
  total: number;
}

export const inboxService = {
  /**
   * Quick inbox - top prioritized tasks
   */
  async getInboxRapido(limite: number = 10): Promise<InboxResponse> {
    const response = await api.get('/v2/inbox/rapido', {
      params: { limite }
    });
    return response.data;
  },

  /**
   * Tasks with today's deadline
   */
  async getTarefasHoje(): Promise<TaskAPI[]> {
    const response = await api.get('/v2/inbox/hoje');
    return response.data.tasks;
  },

  /**
   * Overdue tasks
   */
  async getTarefasAtrasadas(): Promise<TaskAPI[]> {
    const response = await api.get('/v2/inbox/atrasadas');
    return response.data.tasks;
  },

  /**
   * Tasks for next week
   */
  async getTarefasProximaSemana(): Promise<TaskAPI[]> {
    const response = await api.get('/v2/inbox/proxima-semana');
    return response.data.tasks;
  },
};
