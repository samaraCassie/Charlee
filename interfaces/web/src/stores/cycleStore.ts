import { create } from 'zustand';
import { addDays, differenceInDays } from 'date-fns';

export type CyclePhase = 'menstrual' | 'follicular' | 'ovulation' | 'luteal';

export interface CycleData {
  id: string;
  startDate: string;
  endDate?: string;
  cycleLength: number;
  phase: CyclePhase;
  symptoms: string[];
  mood: 'great' | 'good' | 'okay' | 'bad' | 'terrible';
  energy: 'high' | 'medium' | 'low';
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CycleStats {
  averageCycleLength: number;
  productivity: {
    menstrual: number;
    follicular: number;
    ovulation: number;
    luteal: number;
  };
}

interface CycleState {
  cycles: CycleData[];
  currentPhase: CyclePhase;
  lastPeriodStart: string | null;
  averageCycleLength: number;
  loading: boolean;
  error: string | null;

  // Actions
  setCycles: (cycles: CycleData[]) => void;
  addCycle: (cycle: Omit<CycleData, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateCycle: (id: string, updates: Partial<CycleData>) => void;
  setCurrentPhase: (phase: CyclePhase) => void;
  setLastPeriodStart: (date: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Computed
  getCurrentPhase: () => CyclePhase;
  getDaysUntilNextPeriod: () => number;
  getDaysInCurrentPhase: () => number;
  getPhaseProductivity: (phase: CyclePhase) => number;
  getCycleStats: () => CycleStats;
  getPhaseRecommendations: (phase: CyclePhase) => string[];
}

export const useCycleStore = create<CycleState>((set, get) => ({
  cycles: [],
  currentPhase: 'follicular',
  lastPeriodStart: null,
  averageCycleLength: 28,
  loading: false,
  error: null,

  setCycles: (cycles) => set({ cycles }),

  addCycle: (cycleData) => {
    const newCycle: CycleData = {
      ...cycleData,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    set((state) => ({ cycles: [...state.cycles, newCycle] }));
  },

  updateCycle: (id, updates) => {
    set((state) => ({
      cycles: state.cycles.map((cycle) =>
        cycle.id === id
          ? { ...cycle, ...updates, updatedAt: new Date().toISOString() }
          : cycle
      ),
    }));
  },

  setCurrentPhase: (phase) => set({ currentPhase: phase }),
  setLastPeriodStart: (date) => set({ lastPeriodStart: date }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  getCurrentPhase: () => {
    const { lastPeriodStart, averageCycleLength } = get();
    if (!lastPeriodStart) return 'follicular';

    const daysSinceStart = differenceInDays(new Date(), new Date(lastPeriodStart));
    const dayInCycle = daysSinceStart % averageCycleLength;

    if (dayInCycle <= 5) return 'menstrual';
    if (dayInCycle <= 13) return 'follicular';
    if (dayInCycle <= 16) return 'ovulation';
    return 'luteal';
  },

  getDaysUntilNextPeriod: () => {
    const { lastPeriodStart, averageCycleLength } = get();
    if (!lastPeriodStart) return 0;

    const nextPeriod = addDays(new Date(lastPeriodStart), averageCycleLength);
    return differenceInDays(nextPeriod, new Date());
  },

  getDaysInCurrentPhase: () => {
    const { lastPeriodStart, averageCycleLength, getCurrentPhase } = get();
    if (!lastPeriodStart) return 0;

    const daysSinceStart = differenceInDays(new Date(), new Date(lastPeriodStart));
    const dayInCycle = daysSinceStart % averageCycleLength;
    const phase = getCurrentPhase();

    switch (phase) {
      case 'menstrual':
        return dayInCycle;
      case 'follicular':
        return dayInCycle - 5;
      case 'ovulation':
        return dayInCycle - 13;
      case 'luteal':
        return dayInCycle - 16;
      default:
        return 0;
    }
  },

  getPhaseProductivity: (phase) => {
    const productivity = {
      menstrual: 65,
      follicular: 92,
      ovulation: 95,
      luteal: 78,
    };
    return productivity[phase];
  },

  getCycleStats: () => {
    const { cycles } = get();
    const totalCycles = cycles.length;

    if (totalCycles === 0) {
      return {
        averageCycleLength: 28,
        productivity: {
          menstrual: 65,
          follicular: 92,
          ovulation: 95,
          luteal: 78,
        },
      };
    }

    const avgLength = cycles.reduce((sum, c) => sum + c.cycleLength, 0) / totalCycles;

    return {
      averageCycleLength: Math.round(avgLength),
      productivity: {
        menstrual: 65,
        follicular: 92,
        ovulation: 95,
        luteal: 78,
      },
    };
  },

  getPhaseRecommendations: (phase) => {
    const recommendations = {
      menstrual: [
        'Priorize descanso e autocuidado',
        'Evite tarefas muito exigentes',
        'Faça exercícios leves como yoga',
        'Aumente a ingestão de ferro',
      ],
      follicular: [
        'Ótimo momento para iniciar novos projetos',
        'Alta energia para tarefas complexas',
        'Aproveite para networking',
        'Exercícios mais intensos são bem-vindos',
      ],
      ovulation: [
        'Pico de energia e criatividade',
        'Ideal para apresentações e reuniões importantes',
        'Comunicação está em alta',
        'Aproveite para resolver problemas complexos',
      ],
      luteal: [
        'Foco em finalizar projetos existentes',
        'Organize e planeje próximas etapas',
        'Evite iniciar grandes mudanças',
        'Priorize tarefas detalhistas',
      ],
    };
    return recommendations[phase];
  },
}));
