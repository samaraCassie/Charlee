import { describe, it, expect, vi, beforeEach } from 'vitest'
import { bigRockService } from '@/services/bigRockService'
import api from '@/services/api'

vi.mock('@/services/api')

describe('bigRockService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getBigRocks', () => {
    it('should fetch and transform big rocks correctly', async () => {
      const mockApiResponse = {
        data: {
          big_rocks: [
            {
              id: 1,
              nome: 'Saúde',
              cor: 'bg-green-500',
              criado_em: '2024-01-01T00:00:00Z',
            },
            {
              id: 2,
              nome: 'Trabalho',
              cor: 'bg-blue-500',
              criado_em: '2024-01-02T00:00:00Z',
            },
          ],
        },
      }

      vi.mocked(api.get).mockResolvedValue(mockApiResponse)

      const result = await bigRockService.getBigRocks()

      expect(api.get).toHaveBeenCalledWith('/v1/big-rocks/')
      expect(result).toHaveLength(2)
      expect(result[0]).toEqual({
        id: '1',
        name: 'Saúde',
        description: 'Saúde',
        color: 'bg-green-500',
        hoursPerWeek: 20,
        priority: 1,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      })
    })

    it('should use default color when not provided', async () => {
      const mockApiResponse = {
        data: {
          big_rocks: [
            {
              id: 1,
              nome: 'Test',
              cor: null,
              criado_em: '2024-01-01T00:00:00Z',
            },
          ],
        },
      }

      vi.mocked(api.get).mockResolvedValue(mockApiResponse)

      const result = await bigRockService.getBigRocks()

      expect(result[0].color).toBe('bg-gray-500')
    })
  })

  describe('getBigRock', () => {
    it('should fetch and transform single big rock', async () => {
      const mockApiResponse = {
        data: {
          id: 1,
          nome: 'Saúde',
          cor: 'bg-green-500',
          criado_em: '2024-01-01T00:00:00Z',
        },
      }

      vi.mocked(api.get).mockResolvedValue(mockApiResponse)

      const result = await bigRockService.getBigRock('1')

      expect(api.get).toHaveBeenCalledWith('/v1/big-rocks/1')
      expect(result).toEqual({
        id: '1',
        name: 'Saúde',
        description: 'Saúde',
        color: 'bg-green-500',
        hoursPerWeek: 20,
        priority: 1,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      })
    })

    it('should use default color when null in getBigRock', async () => {
      const mockApiResponse = {
        data: {
          id: 1,
          nome: 'Test',
          cor: null,
          criado_em: '2024-01-01T00:00:00Z',
        },
      }

      vi.mocked(api.get).mockResolvedValue(mockApiResponse)

      const result = await bigRockService.getBigRock('1')

      expect(result.color).toBe('bg-gray-500')
    })
  })

  describe('createBigRock', () => {
    it('should create big rock and transform response', async () => {
      const newBigRock = {
        name: 'Nova Meta',
        description: 'Nova Meta',
        color: 'bg-purple-500',
        hoursPerWeek: 15,
        priority: 2,
      }

      const mockApiResponse = {
        data: {
          id: 3,
          nome: 'Nova Meta',
          cor: 'bg-purple-500',
          criado_em: '2024-01-03T00:00:00Z',
        },
      }

      vi.mocked(api.post).mockResolvedValue(mockApiResponse)

      const result = await bigRockService.createBigRock(newBigRock)

      expect(api.post).toHaveBeenCalledWith('/v1/big-rocks/', {
        nome: 'Nova Meta',
        cor: 'bg-purple-500',
      })
      expect(result).toEqual({
        id: '3',
        name: 'Nova Meta',
        description: 'Nova Meta',
        color: 'bg-purple-500',
        hoursPerWeek: 15,
        priority: 2,
        createdAt: '2024-01-03T00:00:00Z',
        updatedAt: '2024-01-03T00:00:00Z',
      })
    })

    it('should use default color when null in createBigRock', async () => {
      const newBigRock = {
        name: 'Test',
        description: 'Test',
        color: 'bg-blue-500',
        hoursPerWeek: 10,
        priority: 1,
      }

      const mockApiResponse = {
        data: {
          id: 1,
          nome: 'Test',
          cor: null,
          criado_em: '2024-01-01T00:00:00Z',
        },
      }

      vi.mocked(api.post).mockResolvedValue(mockApiResponse)

      const result = await bigRockService.createBigRock(newBigRock)

      expect(result.color).toBe('bg-gray-500')
    })
  })

  describe('updateBigRock', () => {
    it('should update big rock and transform response', async () => {
      const updates = {
        name: 'Saúde Atualizada',
        color: 'bg-red-500',
        hoursPerWeek: 25,
      }

      const mockApiResponse = {
        data: {
          id: 1,
          nome: 'Saúde Atualizada',
          cor: 'bg-red-500',
          criado_em: '2024-01-01T00:00:00Z',
        },
      }

      vi.mocked(api.patch).mockResolvedValue(mockApiResponse)

      const result = await bigRockService.updateBigRock('1', updates)

      expect(api.patch).toHaveBeenCalledWith('/v1/big-rocks/1', {
        nome: 'Saúde Atualizada',
        cor: 'bg-red-500',
      })
      expect(result.hoursPerWeek).toBe(25)
    })

    it('should use default color when null in updateBigRock', async () => {
      const updates = {
        name: 'Test',
        hoursPerWeek: 15,
      }

      const mockApiResponse = {
        data: {
          id: 1,
          nome: 'Test',
          cor: null,
          criado_em: '2024-01-01T00:00:00Z',
        },
      }

      vi.mocked(api.patch).mockResolvedValue(mockApiResponse)

      const result = await bigRockService.updateBigRock('1', updates)

      expect(result.color).toBe('bg-gray-500')
      expect(result.hoursPerWeek).toBe(15)
    })

    it('should use default values when optional fields not provided', async () => {
      const updates = {
        name: 'Teste',
      }

      const mockApiResponse = {
        data: {
          id: 1,
          nome: 'Teste',
          cor: 'bg-blue-500',
          criado_em: '2024-01-01T00:00:00Z',
        },
      }

      vi.mocked(api.patch).mockResolvedValue(mockApiResponse)

      const result = await bigRockService.updateBigRock('1', updates)

      expect(result.hoursPerWeek).toBe(20)
      expect(result.priority).toBe(1)
    })
  })

  describe('deleteBigRock', () => {
    it('should call delete endpoint', async () => {
      vi.mocked(api.delete).mockResolvedValue({})

      await bigRockService.deleteBigRock('1')

      expect(api.delete).toHaveBeenCalledWith('/v1/big-rocks/1')
    })
  })
})
