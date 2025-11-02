import { create } from 'zustand';
import axios from 'axios';

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
  addBigRock: (bigRock: Omit<BigRock, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateBigRock: (id: string, updates: Partial<BigRock>) => void;
  deleteBigRock: (id: string) => void;
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

  addBigRock: (bigRockData) => {
    const newBigRock: BigRock = {
      ...bigRockData,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    set((state) => ({ bigRocks: [...state.bigRocks, newBigRock] }));
  },

  updateBigRock: (id, updates) => {
    set((state) => ({
      bigRocks: state.bigRocks.map((rock) =>
        rock.id === id
          ? { ...rock, ...updates, updatedAt: new Date().toISOString() }
          : rock
      ),
    }));
  },

  deleteBigRock: (id) => {
    set((state) => ({
      bigRocks: state.bigRocks.filter((rock) => rock.id !== id),
    }));
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
