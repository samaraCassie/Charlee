import api from './api';

// Types matching backend
export interface TarefaAPI {
  id: number;
  descricao: string;
  tipo: 'Compromisso Fixo' | 'Tarefa' | 'Contínuo';
  deadline: string | null;
  big_rock_id: number | null;
  status: 'Pendente' | 'Em Progresso' | 'Concluída' | 'Cancelada';
  prioridade_calculada: number;
  pontuacao_prioridade: number;
  criado_em: string;
  atualizado_em: string;
  concluido_em: string | null;
  big_rock?: {
    id: number;
    nome: string;
    cor: string | null;
    ativo: boolean;
  };
}

export interface TarefaCreate {
  descricao: string;
  tipo?: 'Compromisso Fixo' | 'Tarefa' | 'Contínuo';
  deadline?: string; // YYYY-MM-DD
  big_rock_id?: number;
}

export interface TarefaUpdate {
  descricao?: string;
  tipo?: 'Compromisso Fixo' | 'Tarefa' | 'Contínuo';
  deadline?: string;
  big_rock_id?: number;
  status?: 'Pendente' | 'Em Progresso' | 'Concluída' | 'Cancelada';
}

export const taskService = {
  // Get all tasks
  async getTasks(params?: {
    status?: string;
    big_rock_id?: number;
    tipo?: string;
    limit?: number;
  }): Promise<TarefaAPI[]> {
    const response = await api.get('/v1/tarefas/', { params });
    return response.data.tarefas;
  },

  // Get task by ID
  async getTask(id: number): Promise<TarefaAPI> {
    const response = await api.get(`/v1/tarefas/${id}`);
    return response.data;
  },

  // Create new task
  async createTask(tarefa: TarefaCreate): Promise<TarefaAPI> {
    const response = await api.post('/v1/tarefas/', tarefa);
    return response.data;
  },

  // Update task
  async updateTask(id: number, updates: TarefaUpdate): Promise<TarefaAPI> {
    const response = await api.patch(`/v1/tarefas/${id}`, updates);
    return response.data;
  },

  // Delete task
  async deleteTask(id: number): Promise<void> {
    await api.delete(`/v1/tarefas/${id}`);
  },

  // Mark as completed
  async toggleTaskStatus(id: number): Promise<TarefaAPI> {
    const task = await this.getTask(id);
    
    if (task.status === 'Concluída') {
      // Reopen task
      const response = await api.post(`/v1/tarefas/${id}/reabrir`);
      return response.data;
    } else {
      // Complete task
      const response = await api.post(`/v1/tarefas/${id}/concluir`);
      return response.data;
    }
  },

  // Get tasks by big rock
  async getTasksByBigRock(bigRockId: number): Promise<TarefaAPI[]> {
    return this.getTasks({ big_rock_id: bigRockId });
  },

  // Get tasks by priority (using prioridade_calculada)
  async getTasksByPriority(priority: number): Promise<TarefaAPI[]> {
    const allTasks = await this.getTasks({ status: 'Pendente' });
    return allTasks.filter(t => t.prioridade_calculada === priority);
  },

  // Get today's tasks
  async getTodayTasks(): Promise<TarefaAPI[]> {
    const today = new Date().toISOString().split('T')[0];
    const allTasks = await this.getTasks({ status: 'Pendente' });
    return allTasks.filter(t => t.deadline === today);
  },

  // Get prioritized inbox (V2)
  async getInbox(limite: number = 10): Promise<{ inbox: string }> {
    const response = await api.get('/v2/priorizacao/inbox', {
      params: { limite }
    });
    return response.data;
  },

  // Recalculate priorities (V2)
  async recalculatePriorities(bigRockId?: number): Promise<void> {
    await api.post('/v2/priorizacao/recalcular', null, {
      params: bigRockId ? { big_rock_id: bigRockId } : {}
    });
  },
};