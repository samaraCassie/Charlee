import api from './api';

// Types matching backend TaskResponse schema
export interface TaskAPI {
  id: number;
  description: string;
  type: 'fixed_appointment' | 'task' | 'continuous';
  deadline: string | null;
  big_rock_id: number | null;
  status: string;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  big_rock?: {
    id: number;
    name: string;
    color: string | null;
    active: boolean;
  };
}

export interface TaskCreate {
  description: string;
  type?: 'fixed_appointment' | 'task' | 'continuous';
  deadline?: string; // YYYY-MM-DD
  big_rock_id?: number;
}

export interface TaskUpdate {
  description?: string;
  type?: 'fixed_appointment' | 'task' | 'continuous';
  deadline?: string;
  big_rock_id?: number;
  status?: string;
}

export const taskService = {
  // Get all tasks
  async getTasks(params?: {
    status?: string;
    big_rock_id?: number;
    task_type?: string;
    limit?: number;
  }): Promise<TaskAPI[]> {
    const response = await api.get('/v1/tasks/', { params });
    return response.data.tasks;
  },

  // Get task by ID
  async getTask(id: number): Promise<TaskAPI> {
    const response = await api.get(`/v1/tasks/${id}`);
    return response.data;
  },

  // Create new task
  async createTask(task: TaskCreate): Promise<TaskAPI> {
    const response = await api.post('/v1/tasks/', task);
    return response.data;
  },

  // Update task
  async updateTask(id: number, updates: TaskUpdate): Promise<TaskAPI> {
    const response = await api.patch(`/v1/tasks/${id}`, updates);
    return response.data;
  },

  // Delete task
  async deleteTask(id: number): Promise<void> {
    await api.delete(`/v1/tasks/${id}`);
  },

  // Mark as completed / reopen
  async toggleTaskStatus(id: number): Promise<TaskAPI> {
    const task = await this.getTask(id);

    if (task.status === 'completed') {
      const response = await api.post(`/v1/tasks/${id}/reopen`);
      return response.data;
    } else {
      const response = await api.post(`/v1/tasks/${id}/complete`);
      return response.data;
    }
  },

  // Get tasks by big rock
  async getTasksByBigRock(bigRockId: number): Promise<TaskAPI[]> {
    return this.getTasks({ big_rock_id: bigRockId });
  },

  // Get tasks by status
  async getTasksByStatus(status: string): Promise<TaskAPI[]> {
    return this.getTasks({ status });
  },

  // Get today's tasks
  async getTodayTasks(): Promise<TaskAPI[]> {
    const today = new Date().toISOString().split('T')[0];
    const allTasks = await this.getTasks({ status: 'pending' });
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
