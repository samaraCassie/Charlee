import { describe, it, expect, vi, beforeEach } from 'vitest'
import { taskService, type TarefaAPI } from '@/services/taskService'
import api from '@/services/api'

vi.mock('@/services/api')

describe('taskService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const mockTask: TarefaAPI = {
    id: 1,
    descricao: 'Test Task',
    tipo: 'Tarefa',
    deadline: '2024-01-15',
    big_rock_id: 1,
    status: 'Pendente',
    prioridade_calculada: 5,
    pontuacao_prioridade: 75,
    criado_em: '2024-01-01T00:00:00Z',
    atualizado_em: '2024-01-01T00:00:00Z',
    concluido_em: null,
  }

  describe('getTasks', () => {
    it('should fetch all tasks', async () => {
      const mockResponse = {
        data: {
          tarefas: [mockTask],
        },
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await taskService.getTasks()

      expect(api.get).toHaveBeenCalledWith('/v1/tarefas/', { params: undefined })
      expect(result).toHaveLength(1)
      expect(result[0]).toEqual(mockTask)
    })

    it('should fetch tasks with filters', async () => {
      const mockResponse = {
        data: {
          tarefas: [],
        },
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await taskService.getTasks({
        status: 'Pendente',
        big_rock_id: 1,
        tipo: 'Tarefa',
        limit: 10,
      })

      expect(api.get).toHaveBeenCalledWith('/v1/tarefas/', {
        params: {
          status: 'Pendente',
          big_rock_id: 1,
          tipo: 'Tarefa',
          limit: 10,
        },
      })
    })
  })

  describe('getTask', () => {
    it('should fetch single task by id', async () => {
      const mockResponse = {
        data: mockTask,
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await taskService.getTask(1)

      expect(api.get).toHaveBeenCalledWith('/v1/tarefas/1')
      expect(result).toEqual(mockTask)
    })
  })

  describe('createTask', () => {
    it('should create new task', async () => {
      const newTask = {
        descricao: 'New Task',
        tipo: 'Tarefa' as const,
        deadline: '2024-01-20',
        big_rock_id: 1,
      }

      const mockResponse = {
        data: { ...mockTask, ...newTask },
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await taskService.createTask(newTask)

      expect(api.post).toHaveBeenCalledWith('/v1/tarefas/', newTask)
      expect(result.descricao).toBe('New Task')
    })

    it('should create task with minimal data', async () => {
      const newTask = {
        descricao: 'Simple Task',
      }

      const mockResponse = {
        data: { ...mockTask, descricao: 'Simple Task' },
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      await taskService.createTask(newTask)

      expect(api.post).toHaveBeenCalledWith('/v1/tarefas/', newTask)
    })
  })

  describe('updateTask', () => {
    it('should update task', async () => {
      const updates = {
        descricao: 'Updated Task',
        status: 'Em Progresso' as const,
      }

      const mockResponse = {
        data: { ...mockTask, ...updates },
      }

      vi.mocked(api.patch).mockResolvedValue(mockResponse)

      const result = await taskService.updateTask(1, updates)

      expect(api.patch).toHaveBeenCalledWith('/v1/tarefas/1', updates)
      expect(result.descricao).toBe('Updated Task')
      expect(result.status).toBe('Em Progresso')
    })
  })

  describe('deleteTask', () => {
    it('should delete task', async () => {
      vi.mocked(api.delete).mockResolvedValue({})

      await taskService.deleteTask(1)

      expect(api.delete).toHaveBeenCalledWith('/v1/tarefas/1')
    })
  })

  describe('toggleTaskStatus', () => {
    it('should complete pending task', async () => {
      const pendingTask = { ...mockTask, status: 'Pendente' }
      const completedTask = { ...mockTask, status: 'Concluída', concluido_em: '2024-01-10T00:00:00Z' }

      vi.mocked(api.get).mockResolvedValue({ data: pendingTask })
      vi.mocked(api.post).mockResolvedValue({ data: completedTask })

      const result = await taskService.toggleTaskStatus(1)

      expect(api.get).toHaveBeenCalledWith('/v1/tarefas/1')
      expect(api.post).toHaveBeenCalledWith('/v1/tarefas/1/concluir')
      expect(result.status).toBe('Concluída')
    })

    it('should reopen completed task', async () => {
      const completedTask = { ...mockTask, status: 'Concluída', concluido_em: '2024-01-10T00:00:00Z' }
      const reopenedTask = { ...mockTask, status: 'Pendente', concluido_em: null }

      vi.mocked(api.get).mockResolvedValue({ data: completedTask })
      vi.mocked(api.post).mockResolvedValue({ data: reopenedTask })

      const result = await taskService.toggleTaskStatus(1)

      expect(api.get).toHaveBeenCalledWith('/v1/tarefas/1')
      expect(api.post).toHaveBeenCalledWith('/v1/tarefas/1/reabrir')
      expect(result.status).toBe('Pendente')
    })
  })

  describe('getTasksByBigRock', () => {
    it('should fetch tasks filtered by big rock id', async () => {
      const mockResponse = {
        data: {
          tarefas: [mockTask],
        },
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await taskService.getTasksByBigRock(1)

      expect(api.get).toHaveBeenCalledWith('/v1/tarefas/', {
        params: { big_rock_id: 1 },
      })
    })
  })

  describe('getTasksByPriority', () => {
    it('should filter tasks by priority', async () => {
      const tasks = [
        { ...mockTask, id: 1, prioridade_calculada: 5 },
        { ...mockTask, id: 2, prioridade_calculada: 3 },
        { ...mockTask, id: 3, prioridade_calculada: 5 },
      ]

      vi.mocked(api.get).mockResolvedValue({
        data: { tarefas: tasks },
      })

      const result = await taskService.getTasksByPriority(5)

      expect(result).toHaveLength(2)
      expect(result[0].prioridade_calculada).toBe(5)
      expect(result[1].prioridade_calculada).toBe(5)
    })
  })

  describe('getTodayTasks', () => {
    it('should filter tasks for today', async () => {
      const today = new Date().toISOString().split('T')[0]
      const tasks = [
        { ...mockTask, id: 1, deadline: today },
        { ...mockTask, id: 2, deadline: '2024-12-31' },
        { ...mockTask, id: 3, deadline: today },
      ]

      vi.mocked(api.get).mockResolvedValue({
        data: { tarefas: tasks },
      })

      const result = await taskService.getTodayTasks()

      expect(result).toHaveLength(2)
      expect(result.every((t) => t.deadline === today)).toBe(true)
    })
  })

  describe('getInbox', () => {
    it('should fetch prioritized inbox', async () => {
      const mockResponse = {
        data: {
          inbox: 'Formatted inbox string',
        },
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await taskService.getInbox()

      expect(api.get).toHaveBeenCalledWith('/v2/priorizacao/inbox', {
        params: { limite: 10 },
      })
      expect(result.inbox).toBe('Formatted inbox string')
    })

    it('should fetch inbox with custom limit', async () => {
      const mockResponse = {
        data: {
          inbox: 'Formatted inbox string',
        },
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await taskService.getInbox(20)

      expect(api.get).toHaveBeenCalledWith('/v2/priorizacao/inbox', {
        params: { limite: 20 },
      })
    })
  })

  describe('recalculatePriorities', () => {
    it('should recalculate all priorities', async () => {
      vi.mocked(api.post).mockResolvedValue({})

      await taskService.recalculatePriorities()

      expect(api.post).toHaveBeenCalledWith('/v2/priorizacao/recalcular', null, {
        params: {},
      })
    })

    it('should recalculate priorities for specific big rock', async () => {
      vi.mocked(api.post).mockResolvedValue({})

      await taskService.recalculatePriorities(1)

      expect(api.post).toHaveBeenCalledWith('/v2/priorizacao/recalcular', null, {
        params: { big_rock_id: 1 },
      })
    })
  })
})
