import api from './api';
import type { TarefaAPI } from './taskService';

export interface InboxResponse {
  inbox_text: string;
  tarefas: TarefaAPI[];
  total: number;
}

export const inboxService = {
  /**
   * Get inbox rápido - top tarefas priorizadas
   */
  async getInboxRapido(limite: number = 10): Promise<InboxResponse> {
    const response = await api.get('/v2/inbox/rapido', {
      params: { limite }
    });
    return response.data;
  },

  /**
   * Get tarefas com deadline hoje
   */
  async getTarefasHoje(): Promise<TarefaAPI[]> {
    const response = await api.get('/v2/inbox/hoje');
    return response.data.tarefas;
  },

  /**
   * Get tarefas atrasadas
   */
  async getTarefasAtrasadas(): Promise<TarefaAPI[]> {
    const response = await api.get('/v2/inbox/atrasadas');
    return response.data.tarefas;
  },

  /**
   * Get tarefas da próxima semana
   */
  async getTarefasProximaSemana(): Promise<TarefaAPI[]> {
    const response = await api.get('/v2/inbox/proxima-semana');
    return response.data.tarefas;
  },
};