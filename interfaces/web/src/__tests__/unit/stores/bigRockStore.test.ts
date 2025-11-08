import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useBigRockStore } from '@/stores/bigRockStore'
import { bigRockService } from '@/services/bigRockService'
import axios from 'axios'

vi.mock('@/services/bigRockService')
vi.mock('axios')

describe('bigRockStore', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset store state
    useBigRockStore.setState({
      bigRocks: [],
      loading: false,
      error: null,
    })
  })

  describe('Initial State', () => {
    it('should have empty bigRocks array initially', () => {
      const { bigRocks } = useBigRockStore.getState()
      expect(bigRocks).toEqual([])
    })

    it('should not be loading initially', () => {
      const { loading } = useBigRockStore.getState()
      expect(loading).toBe(false)
    })

    it('should have no error initially', () => {
      const { error } = useBigRockStore.getState()
      expect(error).toBeNull()
    })
  })

  describe('fetchBigRocks', () => {
    it('should fetch and set big rocks successfully', async () => {
      const mockData = {
        data: {
          big_rocks: [
            {
              id: 1,
              nome: 'Saúde',
              cor: 'bg-green-500',
              criado_em: '2024-01-01T00:00:00Z',
            },
          ],
        },
      }

      vi.mocked(axios.get).mockResolvedValue(mockData)

      const { fetchBigRocks } = useBigRockStore.getState()
      await fetchBigRocks()

      const { bigRocks, loading, error } = useBigRockStore.getState()

      expect(bigRocks).toHaveLength(1)
      expect(bigRocks[0].name).toBe('Saúde')
      expect(loading).toBe(false)
      expect(error).toBeNull()
    })

    it('should set loading state during fetch', async () => {
      const mockData = { data: { big_rocks: [] } }

      vi.mocked(axios.get).mockImplementation(() => {
        const { loading } = useBigRockStore.getState()
        expect(loading).toBe(true)
        return Promise.resolve(mockData)
      })

      const { fetchBigRocks } = useBigRockStore.getState()
      await fetchBigRocks()
    })

    it('should handle fetch error', async () => {
      vi.mocked(axios.get).mockRejectedValue(new Error('Network error'))

      const { fetchBigRocks } = useBigRockStore.getState()
      await fetchBigRocks()

      const { error, loading } = useBigRockStore.getState()

      expect(error).toBe('Failed to fetch big rocks')
      expect(loading).toBe(false)
    })

    it('should use default color when cor is null in fetchBigRocks', async () => {
      const mockData = {
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

      vi.mocked(axios.get).mockResolvedValue(mockData)

      const { fetchBigRocks } = useBigRockStore.getState()
      await fetchBigRocks()

      const { bigRocks } = useBigRockStore.getState()
      expect(bigRocks[0].color).toBe('bg-gray-500')
    })

    it('should use default color when cor is undefined in fetchBigRocks', async () => {
      const mockData = {
        data: {
          big_rocks: [
            {
              id: 1,
              nome: 'Test',
              criado_em: '2024-01-01T00:00:00Z',
            },
          ],
        },
      }

      vi.mocked(axios.get).mockResolvedValue(mockData)

      const { fetchBigRocks } = useBigRockStore.getState()
      await fetchBigRocks()

      const { bigRocks } = useBigRockStore.getState()
      expect(bigRocks[0].color).toBe('bg-gray-500')
    })
  })

  describe('addBigRock', () => {
    it('should add big rock successfully', async () => {
      const newBigRock = {
        id: '1',
        name: 'Nova Meta',
        description: 'Nova Meta',
        color: 'bg-blue-500',
        hoursPerWeek: 10,
        priority: 1,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      }

      vi.mocked(bigRockService.createBigRock).mockResolvedValue(newBigRock)

      const { addBigRock } = useBigRockStore.getState()
      await addBigRock({
        name: 'Nova Meta',
        description: 'Nova Meta',
        color: 'bg-blue-500',
        hoursPerWeek: 10,
        priority: 1,
      })

      const { bigRocks } = useBigRockStore.getState()

      expect(bigRocks).toHaveLength(1)
      expect(bigRocks[0]).toEqual(newBigRock)
    })

    it('should handle add error', async () => {
      vi.mocked(bigRockService.createBigRock).mockRejectedValue(
        new Error('Failed to create')
      )

      const { addBigRock } = useBigRockStore.getState()

      await expect(
        addBigRock({
          name: 'Test',
          description: 'Test',
          color: 'bg-blue-500',
          hoursPerWeek: 10,
          priority: 1,
        })
      ).rejects.toThrow()

      const { error } = useBigRockStore.getState()
      expect(error).toBe('Failed to create big rock')
    })
  })

  describe('updateBigRock', () => {
    it('should update big rock successfully', async () => {
      // Set initial state with multiple rocks to test both branches
      useBigRockStore.setState({
        bigRocks: [
          {
            id: '1',
            name: 'Old Name',
            description: 'Old',
            color: 'bg-blue-500',
            hoursPerWeek: 10,
            priority: 1,
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-01T00:00:00Z',
          },
          {
            id: '2',
            name: 'Other Rock',
            description: 'Other',
            color: 'bg-green-500',
            hoursPerWeek: 20,
            priority: 2,
            createdAt: '2024-01-02T00:00:00Z',
            updatedAt: '2024-01-02T00:00:00Z',
          },
        ],
      })

      const updatedBigRock = {
        id: '1',
        name: 'New Name',
        description: 'New',
        color: 'bg-red-500',
        hoursPerWeek: 15,
        priority: 2,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-02T00:00:00Z',
      }

      vi.mocked(bigRockService.updateBigRock).mockResolvedValue(updatedBigRock)

      const { updateBigRock } = useBigRockStore.getState()
      await updateBigRock('1', { name: 'New Name', hoursPerWeek: 15 })

      const { bigRocks } = useBigRockStore.getState()

      expect(bigRocks[0].name).toBe('New Name')
      expect(bigRocks[0].hoursPerWeek).toBe(15)
      // Verify the other rock was not modified
      expect(bigRocks[1].name).toBe('Other Rock')
      expect(bigRocks[1].hoursPerWeek).toBe(20)
    })

    it('should handle update error', async () => {
      useBigRockStore.setState({
        bigRocks: [
          {
            id: '1',
            name: 'Test',
            description: 'Test',
            color: 'bg-blue-500',
            hoursPerWeek: 10,
            priority: 1,
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-01T00:00:00Z',
          },
        ],
      })

      vi.mocked(bigRockService.updateBigRock).mockRejectedValue(
        new Error('Update failed')
      )

      const { updateBigRock } = useBigRockStore.getState()

      await expect(updateBigRock('1', { name: 'New' })).rejects.toThrow()

      const { error } = useBigRockStore.getState()
      expect(error).toBe('Failed to update big rock')
    })
  })

  describe('deleteBigRock', () => {
    it('should delete big rock successfully', async () => {
      useBigRockStore.setState({
        bigRocks: [
          {
            id: '1',
            name: 'To Delete',
            description: 'To Delete',
            color: 'bg-blue-500',
            hoursPerWeek: 10,
            priority: 1,
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-01T00:00:00Z',
          },
          {
            id: '2',
            name: 'Keep',
            description: 'Keep',
            color: 'bg-green-500',
            hoursPerWeek: 20,
            priority: 1,
            createdAt: '2024-01-02T00:00:00Z',
            updatedAt: '2024-01-02T00:00:00Z',
          },
        ],
      })

      vi.mocked(bigRockService.deleteBigRock).mockResolvedValue()

      const { deleteBigRock } = useBigRockStore.getState()
      await deleteBigRock('1')

      const { bigRocks } = useBigRockStore.getState()

      expect(bigRocks).toHaveLength(1)
      expect(bigRocks[0].id).toBe('2')
    })

    it('should handle delete error', async () => {
      useBigRockStore.setState({
        bigRocks: [
          {
            id: '1',
            name: 'Test',
            description: 'Test',
            color: 'bg-blue-500',
            hoursPerWeek: 10,
            priority: 1,
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-01T00:00:00Z',
          },
        ],
      })

      vi.mocked(bigRockService.deleteBigRock).mockRejectedValue(
        new Error('Delete failed')
      )

      const { deleteBigRock } = useBigRockStore.getState()

      await expect(deleteBigRock('1')).rejects.toThrow()

      const { error, bigRocks } = useBigRockStore.getState()
      expect(error).toBe('Failed to delete big rock')
      expect(bigRocks).toHaveLength(1) // Should not be deleted
    })
  })

  describe('Computed Functions', () => {
    beforeEach(() => {
      useBigRockStore.setState({
        bigRocks: [
          {
            id: '1',
            name: 'First',
            description: 'First',
            color: 'bg-blue-500',
            hoursPerWeek: 20,
            priority: 1,
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-01T00:00:00Z',
          },
          {
            id: '2',
            name: 'Second',
            description: 'Second',
            color: 'bg-green-500',
            hoursPerWeek: 30,
            priority: 1,
            createdAt: '2024-01-02T00:00:00Z',
            updatedAt: '2024-01-02T00:00:00Z',
          },
        ],
      })
    })

    it('should calculate total capacity correctly', () => {
      const { getTotalCapacity } = useBigRockStore.getState()
      expect(getTotalCapacity()).toBe(50)
    })

    it('should calculate capacity percentage correctly', () => {
      const { getCapacityPercentage } = useBigRockStore.getState()
      const percentage = getCapacityPercentage()
      expect(percentage).toBeCloseTo(29.76, 2) // 50/168 * 100
    })

    it('should find big rock by id', () => {
      const { getBigRockById } = useBigRockStore.getState()
      const rock = getBigRockById('1')
      expect(rock?.name).toBe('First')
    })

    it('should return undefined for non-existent id', () => {
      const { getBigRockById } = useBigRockStore.getState()
      const rock = getBigRockById('999')
      expect(rock).toBeUndefined()
    })
  })

  describe('setLoading', () => {
    it('should set loading state', () => {
      const { setLoading } = useBigRockStore.getState()
      setLoading(true)

      const { loading } = useBigRockStore.getState()
      expect(loading).toBe(true)
    })
  })

  describe('setError', () => {
    it('should set error state', () => {
      const { setError } = useBigRockStore.getState()
      setError('Test error')

      const { error } = useBigRockStore.getState()
      expect(error).toBe('Test error')
    })

    it('should clear error state', () => {
      useBigRockStore.setState({ error: 'Some error' })

      const { setError } = useBigRockStore.getState()
      setError(null)

      const { error } = useBigRockStore.getState()
      expect(error).toBeNull()
    })
  })

  describe('setBigRocks', () => {
    it('should set big rocks directly', () => {
      const mockBigRocks = [
        {
          id: '1',
          name: 'Test',
          description: 'Test',
          color: 'bg-blue-500',
          hoursPerWeek: 10,
          priority: 1,
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z',
        },
      ]

      const { setBigRocks } = useBigRockStore.getState()
      setBigRocks(mockBigRocks)

      const { bigRocks } = useBigRockStore.getState()
      expect(bigRocks).toEqual(mockBigRocks)
    })
  })
})
