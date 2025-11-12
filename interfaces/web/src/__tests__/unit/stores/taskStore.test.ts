import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useTaskStore } from '@/stores/taskStore'
import { taskService } from '@/services/taskService'

vi.mock('@/services/taskService')

describe('taskStore', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset store state
    useTaskStore.setState({
      tasks: [],
      loading: false,
      error: null,
    })
  })

  const mockApiTask = {
    id: 1,
    descricao: 'Test Task',
    tipo: 'Tarefa' as const,
    deadline: '2024-01-15',
    big_rock_id: 1,
    status: 'Pendente' as const,
    prioridade_calculada: 5,
    pontuacao_prioridade: 75,
    criado_em: '2024-01-01T00:00:00Z',
    atualizado_em: '2024-01-01T00:00:00Z',
    concluido_em: null,
  }

  describe('Initial State', () => {
    it('should have empty tasks array initially', () => {
      const { tasks } = useTaskStore.getState()
      expect(tasks).toEqual([])
    })

    it('should not be loading initially', () => {
      const { loading } = useTaskStore.getState()
      expect(loading).toBe(false)
    })

    it('should have no error initially', () => {
      const { error } = useTaskStore.getState()
      expect(error).toBeNull()
    })
  })

  describe('fetchTasks', () => {
    it('should fetch and transform tasks successfully', async () => {
      vi.mocked(taskService.getTasks).mockResolvedValue([mockApiTask])

      const { fetchTasks } = useTaskStore.getState()
      await fetchTasks()

      const { tasks, loading, error } = useTaskStore.getState()

      expect(tasks).toHaveLength(1)
      expect(tasks[0].title).toBe('Test Task')
      expect(tasks[0].status).toBe('pending')
      expect(loading).toBe(false)
      expect(error).toBeNull()
    })

    it('should transform status correctly', async () => {
      const completedTask = { ...mockApiTask, status: 'Concluída' as const }
      const inProgressTask = { ...mockApiTask, id: 2, status: 'Em Progresso' as const }

      vi.mocked(taskService.getTasks).mockResolvedValue([
        completedTask,
        inProgressTask,
      ])

      const { fetchTasks } = useTaskStore.getState()
      await fetchTasks()

      const { tasks } = useTaskStore.getState()

      expect(tasks[0].status).toBe('completed')
      expect(tasks[1].status).toBe('in_progress')
    })

    it('should transform priority correctly', async () => {
      const highPriority = { ...mockApiTask, id: 1, prioridade_calculada: 2 }
      const mediumPriority = { ...mockApiTask, id: 2, prioridade_calculada: 5 }
      const lowPriority = { ...mockApiTask, id: 3, prioridade_calculada: 9 }

      vi.mocked(taskService.getTasks).mockResolvedValue([
        highPriority,
        mediumPriority,
        lowPriority,
      ])

      const { fetchTasks } = useTaskStore.getState()
      await fetchTasks()

      const { tasks } = useTaskStore.getState()

      expect(tasks[0].priority).toBe(1) // <= 3
      expect(tasks[1].priority).toBe(2) // 4-7
      expect(tasks[2].priority).toBe(3) // >= 8
    })

    it('should handle fetch error', async () => {
      vi.mocked(taskService.getTasks).mockRejectedValue(new Error('Network error'))

      const { fetchTasks } = useTaskStore.getState()
      await fetchTasks()

      const { error, loading } = useTaskStore.getState()

      expect(error).toBe('Failed to fetch tasks')
      expect(loading).toBe(false)
    })
  })

  describe('addTask', () => {
    it('should add task successfully', async () => {
      vi.mocked(taskService.createTask).mockResolvedValue(mockApiTask)

      const { addTask } = useTaskStore.getState()
      await addTask({
        title: 'New Task',
        priority: 2,
        status: 'pending',
        deadline: '2024-01-15',
        bigRockId: '1',
      })

      const { tasks } = useTaskStore.getState()

      expect(tasks).toHaveLength(1)
      expect(tasks[0].title).toBe('Test Task')
    })

    it('should handle add error', async () => {
      vi.mocked(taskService.createTask).mockRejectedValue(
        new Error('Failed to create')
      )

      const { addTask } = useTaskStore.getState()

      await expect(
        addTask({
          title: 'Test',
          priority: 2,
          status: 'pending',
        })
      ).rejects.toThrow()

      const { error } = useTaskStore.getState()
      expect(error).toBe('Failed to create task')
    })
  })

  describe('updateTask', () => {
    it('should update task successfully', async () => {
      useTaskStore.setState({
        tasks: [
          {
            id: '1',
            title: 'Old Title',
            description: 'Old Title',
            priority: 2,
            status: 'pending',
            deadline: '2024-01-15',
            bigRockId: '1',
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-01T00:00:00Z',
          },
        ],
      })

      const updatedTask = {
        ...mockApiTask,
        descricao: 'Updated Title',
      }

      vi.mocked(taskService.updateTask).mockResolvedValue(updatedTask)

      const { updateTask } = useTaskStore.getState()
      await updateTask('1', { title: 'Updated Title' })

      const { tasks } = useTaskStore.getState()

      expect(tasks[0].title).toBe('Updated Title')
    })

    it('should handle update error', async () => {
      useTaskStore.setState({
        tasks: [
          {
            id: '1',
            title: 'Test',
            description: 'Test',
            priority: 2,
            status: 'pending',
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-01T00:00:00Z',
          },
        ],
      })

      vi.mocked(taskService.updateTask).mockRejectedValue(
        new Error('Update failed')
      )

      const { updateTask } = useTaskStore.getState()

      await expect(updateTask('1', { title: 'New' })).rejects.toThrow()

      const { error } = useTaskStore.getState()
      expect(error).toBe('Failed to update task')
    })
  })

  describe('deleteTask', () => {
    it('should delete task successfully', async () => {
      useTaskStore.setState({
        tasks: [
          {
            id: '1',
            title: 'To Delete',
            description: 'To Delete',
            priority: 2,
            status: 'pending',
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-01T00:00:00Z',
          },
          {
            id: '2',
            title: 'Keep',
            description: 'Keep',
            priority: 2,
            status: 'pending',
            createdAt: '2024-01-02T00:00:00Z',
            updatedAt: '2024-01-02T00:00:00Z',
          },
        ],
      })

      vi.mocked(taskService.deleteTask).mockResolvedValue()

      const { deleteTask } = useTaskStore.getState()
      await deleteTask('1')

      const { tasks } = useTaskStore.getState()

      expect(tasks).toHaveLength(1)
      expect(tasks[0].id).toBe('2')
    })

    it('should handle delete error', async () => {
      useTaskStore.setState({
        tasks: [
          {
            id: '1',
            title: 'Test',
            description: 'Test',
            priority: 2,
            status: 'pending',
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-01T00:00:00Z',
          },
        ],
      })

      vi.mocked(taskService.deleteTask).mockRejectedValue(
        new Error('Delete failed')
      )

      const { deleteTask } = useTaskStore.getState()

      await expect(deleteTask('1')).rejects.toThrow()

      const { error, tasks } = useTaskStore.getState()
      expect(error).toBe('Failed to delete task')
      expect(tasks).toHaveLength(1)
    })
  })

  describe('toggleTaskStatus', () => {
    it('should toggle task status successfully', async () => {
      useTaskStore.setState({
        tasks: [
          {
            id: '1',
            title: 'Test',
            description: 'Test',
            priority: 2,
            status: 'pending',
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-01T00:00:00Z',
          },
        ],
      })

      const completedTask = {
        ...mockApiTask,
        status: 'Concluída' as const,
        concluido_em: '2024-01-10T00:00:00Z',
      }

      vi.mocked(taskService.toggleTaskStatus).mockResolvedValue(completedTask)

      const { toggleTaskStatus } = useTaskStore.getState()
      await toggleTaskStatus('1')

      const { tasks } = useTaskStore.getState()

      expect(tasks[0].status).toBe('completed')
      expect(tasks[0].completedAt).toBe('2024-01-10T00:00:00Z')
    })

    it('should handle toggle error', async () => {
      useTaskStore.setState({
        tasks: [
          {
            id: '1',
            title: 'Test',
            description: 'Test',
            priority: 2,
            status: 'pending',
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-01T00:00:00Z',
          },
        ],
      })

      vi.mocked(taskService.toggleTaskStatus).mockRejectedValue(
        new Error('Toggle failed')
      )

      const { toggleTaskStatus } = useTaskStore.getState()

      await expect(toggleTaskStatus('1')).rejects.toThrow()

      const { error } = useTaskStore.getState()
      expect(error).toBe('Failed to toggle task')
    })
  })

  describe('Computed Functions', () => {
    beforeEach(() => {
      useTaskStore.setState({
        tasks: [
          {
            id: '1',
            title: 'Pending Task 1',
            description: 'Pending Task 1',
            priority: 1,
            status: 'pending',
            bigRockId: '1',
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-01T00:00:00Z',
          },
          {
            id: '2',
            title: 'Completed Task',
            description: 'Completed Task',
            priority: 2,
            status: 'completed',
            bigRockId: '1',
            createdAt: '2024-01-02T00:00:00Z',
            updatedAt: '2024-01-02T00:00:00Z',
          },
          {
            id: '3',
            title: 'Pending Task 2',
            description: 'Pending Task 2',
            priority: 1,
            status: 'pending',
            bigRockId: '2',
            deadline: new Date().toISOString().split('T')[0],
            createdAt: '2024-01-03T00:00:00Z',
            updatedAt: '2024-01-03T00:00:00Z',
          },
        ],
      })
    })

    it('should get pending tasks', () => {
      const { getPendingTasks } = useTaskStore.getState()
      const pending = getPendingTasks()

      expect(pending).toHaveLength(2)
      expect(pending.every((t) => t.status !== 'completed')).toBe(true)
    })

    it('should get tasks by big rock', () => {
      const { getTasksByBigRock } = useTaskStore.getState()
      const tasks = getTasksByBigRock('1')

      expect(tasks).toHaveLength(2)
      expect(tasks.every((t) => t.bigRockId === '1')).toBe(true)
    })

    it('should get tasks by priority', () => {
      const { getTasksByPriority } = useTaskStore.getState()
      const tasks = getTasksByPriority(1)

      expect(tasks).toHaveLength(2)
      expect(tasks.every((t) => t.priority === 1)).toBe(true)
    })

    it('should get today tasks', () => {
      const { getTodayTasks } = useTaskStore.getState()
      const tasks = getTodayTasks()

      expect(tasks).toHaveLength(1)
      expect(tasks[0].id).toBe('3')
    })
  })

  describe('setLoading', () => {
    it('should set loading state', () => {
      const { setLoading } = useTaskStore.getState()
      setLoading(true)

      const { loading } = useTaskStore.getState()
      expect(loading).toBe(true)
    })
  })

  describe('setError', () => {
    it('should set error state', () => {
      const { setError } = useTaskStore.getState()
      setError('Test error')

      const { error } = useTaskStore.getState()
      expect(error).toBe('Test error')
    })

    it('should clear error state', () => {
      useTaskStore.setState({ error: 'Some error' })

      const { setError } = useTaskStore.getState()
      setError(null)

      const { error } = useTaskStore.getState()
      expect(error).toBeNull()
    })
  })

  describe('setTasks', () => {
    it('should set tasks directly', () => {
      const mockTasks = [
        {
          id: '1',
          title: 'Test',
          description: 'Test',
          priority: 2 as const,
          status: 'pending' as const,
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z',
        },
      ]

      const { setTasks } = useTaskStore.getState()
      setTasks(mockTasks)

      const { tasks } = useTaskStore.getState()
      expect(tasks).toEqual(mockTasks)
    })
  })
})
