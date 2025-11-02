import api from './api';
import type { BigRock } from '../stores/bigRockStore';

export const bigRockService = {
  // Get all big rocks
  async getBigRocks(): Promise<BigRock[]> {
    const response = await api.get('/v1/big-rocks/');
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return response.data.big_rocks.map((rock: any) => ({
      id: rock.id.toString(),
      name: rock.nome,
      description: rock.nome,
      color: rock.cor || 'bg-gray-500',
      hoursPerWeek: 20,
      priority: 1,
      createdAt: rock.criado_em,
      updatedAt: rock.criado_em,
    }));
  },

  // Get big rock by ID
  async getBigRock(id: string): Promise<BigRock> {
    const response = await api.get(`/v1/big-rocks/${id}`);
    const rock = response.data;
    return {
      id: rock.id.toString(),
      name: rock.nome,
      description: rock.nome,
      color: rock.cor || 'bg-gray-500',
      hoursPerWeek: 20,
      priority: 1,
      createdAt: rock.criado_em,
      updatedAt: rock.criado_em,
    };
  },

  // Create new big rock
  async createBigRock(
    bigRock: Omit<BigRock, 'id' | 'createdAt' | 'updatedAt'>
  ): Promise<BigRock> {
    const response = await api.post('/v1/big-rocks/', {
      nome: bigRock.name,
      cor: bigRock.color,
    });
    
    const rock = response.data;
    return {
      id: rock.id.toString(),
      name: rock.nome,
      description: rock.nome,
      color: rock.cor || 'bg-gray-500',
      hoursPerWeek: bigRock.hoursPerWeek,
      priority: bigRock.priority,
      createdAt: rock.criado_em,
      updatedAt: rock.criado_em,
    };
  },

  // Update big rock
  async updateBigRock(id: string, updates: Partial<BigRock>): Promise<BigRock> {
    const response = await api.patch(`/v1/big-rocks/${id}`, {
      nome: updates.name,
      cor: updates.color,
    });
    
    const rock = response.data;
    return {
      id: rock.id.toString(),
      name: rock.nome,
      description: rock.nome,
      color: rock.cor || 'bg-gray-500',
      hoursPerWeek: updates.hoursPerWeek || 20,
      priority: updates.priority || 1,
      createdAt: rock.criado_em,
      updatedAt: rock.criado_em,
    };
  },

  // Delete big rock
  async deleteBigRock(id: string): Promise<void> {
    await api.delete(`/v1/big-rocks/${id}`);
  },
};