import { create } from 'zustand';
import axios from 'axios';
import { bigRockService } from '../services/bigRockService';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface BigRock {
  id: string;
  name: string;
  description?: string;
  color?: string;
  hoursPerWeek: number;
  priority: number;
  createdAt: string;
  updatedAt: string;
}

interface BigRockState {
  bigRocks: BigRock[];
  loading: boolean;
  error: string | null;

  // Actions
  fetchBigRocks: () => Promise<void>;
  setBigRocks: (bigRocks: BigRock[]) => void;
  addBigRock: (bigRock: Omit<BigRock, 'id' | 'createdAt' | 'updatedAt'>) => Promise<void>;
  updateBigRock: (id: string, updates: Partial<BigRock>) => Promise<void>;
  deleteBigRock: (id: string) => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Computed
  getTotalCapacity: () => number;
  getCapacityPercentage: () => number;
  getBigRockById: (id: string) => BigRock | undefined;
}

const WEEKLY_HOURS = 168;

export const useBigRockStore = create<BigRockState>((set, get) => ({
  bigRocks: [],
  loading: false,
  error: null,

  fetchBigRocks: async () => {
    set({ loading: true, error: null });
    try {
      const response = await axios.get(`${API_URL}/v1/big-rocks/`);
      const apiRocks = response.data.big_rocks;

      // Transform API data to match frontend interface
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const bigRocks: BigRock[] = apiRocks.map((rock: any) => ({
        id: rock.id.toString(),
        name: rock.nome,
        description: rock.nome, // API doesn't have description, use name
        color: rock.cor || 'bg-gray-500',
        hoursPerWeek: 20, // Default, will need to get from carga_trabalho
        priority: 1, // Default
        createdAt: rock.criado_em,
        updatedAt: rock.criado_em,
      }));

      set({ bigRocks, loading: false });
    } catch (error) {
      console.error('Error fetching big rocks:', error);
      set({ error: 'Failed to fetch big rocks', loading: false });
    }
  },

  setBigRocks: (bigRocks) => set({ bigRocks }),

  addBigRock: async (bigRockData) => {
    set({ loading: true, error: null });
    try {
      const newBigRock = await bigRockService.createBigRock(bigRockData);
      set((state) => ({
        bigRocks: [...state.bigRocks, newBigRock],
        loading: false
      }));
    } catch (error) {
      console.error('Error creating big rock:', error);
      set({ error: 'Failed to create big rock', loading: false });
      throw error;
    }
  },

  updateBigRock: async (id, updates) => {
    set({ loading: true, error: null });
    try {
      const updatedBigRock = await bigRockService.updateBigRock(id, updates);
      set((state) => ({
        bigRocks: state.bigRocks.map((rock) =>
          rock.id === id ? updatedBigRock : rock
        ),
        loading: false,
      }));
    } catch (error) {
      console.error('Error updating big rock:', error);
      set({ error: 'Failed to update big rock', loading: false });
      throw error;
    }
  },

  deleteBigRock: async (id) => {
    set({ loading: true, error: null });
    try {
      await bigRockService.deleteBigRock(id);
      set((state) => ({
        bigRocks: state.bigRocks.filter((rock) => rock.id !== id),
        loading: false,
      }));
    } catch (error) {
      console.error('Error deleting big rock:', error);
      set({ error: 'Failed to delete big rock', loading: false });
      throw error;
    }
  },

  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  getTotalCapacity: () => {
    return get().bigRocks.reduce((total, rock) => total + rock.hoursPerWeek, 0);
  },

  getCapacityPercentage: () => {
    const total = get().getTotalCapacity();
    return (total / WEEKLY_HOURS) * 100;
  },

  getBigRockById: (id) => {
    return get().bigRocks.find((rock) => rock.id === id);
  },
}));
