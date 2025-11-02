import { create } from 'zustand';
import { taskService } from '@/services/taskService';
import type { TarefaAPI } from '@/services/taskService';

export interface Task {
  id: string;
  title: string;
  description?: string;
  priority: 1 | 2 | 3;
  status: 'pending' | 'in_progress' | 'completed';
  deadline?: string;
  bigRockId?: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

interface TaskState {
  tasks: Task[];
  loading: boolean;
  error: string | null;

  // Actions
  fetchTasks: () => Promise<void>;
  setTasks: (tasks: Task[]) => void;
  addTask: (task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) => Promise<void>;
  updateTask: (id: string, updates: Partial<Task>) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  toggleTaskStatus: (id: string) => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Computed
  getPendingTasks: () => Task[];
  getTasksByBigRock: (bigRockId: string) => Task[];
  getTasksByPriority: (priority: number) => Task[];
  getTodayTasks: () => Task[];
}

// Helper: Convert API task to frontend task
function apiToTask(apiTask: TarefaAPI): Task {
  let status: 'pending' | 'in_progress' | 'completed' = 'pending';
  if (apiTask.status === 'Concluída') status = 'completed';
  else if (apiTask.status === 'Em Progresso') status = 'in_progress';

  // Map prioridade_calculada (1-10) to priority (1-3)
  let priority: 1 | 2 | 3 = 2;
  if (apiTask.prioridade_calculada && apiTask.prioridade_calculada <= 3) priority = 1;
  else if (apiTask.prioridade_calculada && apiTask.prioridade_calculada <= 7) priority = 2;
  else priority = 3;

  return {
    id: apiTask.id.toString(),
    title: apiTask.descricao,
    description: apiTask.descricao,
    priority,
    status,
    deadline: apiTask.deadline || undefined,
    bigRockId: apiTask.big_rock_id ? apiTask.big_rock_id.toString() : undefined,
    createdAt: apiTask.criado_em,
    updatedAt: apiTask.atualizado_em,
    completedAt: apiTask.concluido_em || undefined,
  };
}

export const useTaskStore = create<TaskState>((set, get) => ({
  tasks: [],
  loading: false,
  error: null,

  fetchTasks: async () => {
    set({ loading: true, error: null });
    try {
      const apiTasks = await taskService.getTasks();
      const tasks = apiTasks.map(apiToTask);
      set({ tasks, loading: false });
    } catch (error) {
      console.error('Error fetching tasks:', error);
      set({ error: 'Failed to fetch tasks', loading: false });
    }
  },

  setTasks: (tasks) => set({ tasks }),

  addTask: async (taskData) => {
    set({ loading: true, error: null });
    try {
      const apiTask = await taskService.createTask({
        descricao: taskData.title,
        tipo: 'Tarefa',
        deadline: taskData.deadline,
        big_rock_id: taskData.bigRockId ? parseInt(taskData.bigRockId) : undefined,
      });

      const newTask = apiToTask(apiTask);
      set((state) => ({ 
        tasks: [...state.tasks, newTask],
        loading: false 
      }));
    } catch (error) {
      console.error('Error creating task:', error);
      set({ error: 'Failed to create task', loading: false });
      throw error;
    }
  },

  updateTask: async (id, updates) => {
    set({ loading: true, error: null });
    try {
      const apiTask = await taskService.updateTask(parseInt(id), {
        descricao: updates.title,
        deadline: updates.deadline,
        big_rock_id: updates.bigRockId ? parseInt(updates.bigRockId) : undefined,
      });

      const updatedTask = apiToTask(apiTask);
      set((state) => ({
        tasks: state.tasks.map((task) =>
          task.id === id ? updatedTask : task
        ),
        loading: false,
      }));
    } catch (error) {
      console.error('Error updating task:', error);
      set({ error: 'Failed to update task', loading: false });
      throw error;
    }
  },

  deleteTask: async (id) => {
    set({ loading: true, error: null });
    try {
      await taskService.deleteTask(parseInt(id));
      set((state) => ({
        tasks: state.tasks.filter((task) => task.id !== id),
        loading: false,
      }));
    } catch (error) {
      console.error('Error deleting task:', error);
      set({ error: 'Failed to delete task', loading: false });
      throw error;
    }
  },

  toggleTaskStatus: async (id) => {
    set({ loading: true, error: null });
    try {
      const apiTask = await taskService.toggleTaskStatus(parseInt(id));
      const updatedTask = apiToTask(apiTask);

      set((state) => ({
        tasks: state.tasks.map((task) =>
          task.id === id ? updatedTask : task
        ),
        loading: false,
      }));
    } catch (error) {
      console.error('Error toggling task:', error);
      set({ error: 'Failed to toggle task', loading: false });
      throw error;
    }
  },

  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  getPendingTasks: () => {
    return get().tasks.filter((task) => task.status !== 'completed');
  },

  getTasksByBigRock: (bigRockId) => {
    return get().tasks.filter((task) => task.bigRockId === bigRockId);
  },

  getTasksByPriority: (priority) => {
    return get().tasks.filter((task) => task.priority === priority);
  },

  getTodayTasks: () => {
    const today = new Date().toISOString().split('T')[0];
    return get().tasks.filter((task) => {
      if (!task.deadline) return false;
      const taskDate = task.deadline.split('T')[0];
      return taskDate === today;
    });
  },
}));