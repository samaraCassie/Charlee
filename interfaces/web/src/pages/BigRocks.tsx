import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Target, Plus, Settings, List, BarChart3, AlertCircle } from 'lucide-react';
import { useTaskStore } from '@/stores/taskStore';
import { useBigRockStore } from '@/stores/bigRockStore';
import { useToast } from '@/hooks/use-toast';

export default function BigRocks() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [newBigRockDialogOpen, setNewBigRockDialogOpen] = useState(false);
  const [newBigRockName, setNewBigRockName] = useState('');
  const [newBigRockColor, setNewBigRockColor] = useState('bg-blue-500');
  const [newBigRockHoursPerWeek, setNewBigRockHoursPerWeek] = useState(20);

  const [editBigRockDialogOpen, setEditBigRockDialogOpen] = useState(false);
  const [selectedBigRock, setSelectedBigRock] = useState<string | null>(null);
  const [editBigRockName, setEditBigRockName] = useState('');
  const [editBigRockColor, setEditBigRockColor] = useState('bg-blue-500');
  const [editBigRockHoursPerWeek, setEditBigRockHoursPerWeek] = useState(20);

  const { tasks, fetchTasks } = useTaskStore();
  const { bigRocks, fetchBigRocks, getTotalCapacity, getCapacityPercentage, addBigRock, updateBigRock, deleteBigRock, getBigRockById } = useBigRockStore();

  // Fetch data on mount
  useEffect(() => {
    fetchTasks();
    fetchBigRocks();
  }, [fetchTasks, fetchBigRocks]);

  const totalCapacity = getTotalCapacity();
  const usedCapacity = getCapacityPercentage();

  const availableColors = [
    { name: 'Azul', value: 'bg-blue-500' },
    { name: 'Rosa', value: 'bg-pink-500' },
    { name: 'Roxo', value: 'bg-purple-500' },
    { name: 'Verde', value: 'bg-teal-500' },
    { name: 'Laranja', value: 'bg-orange-500' },
    { name: 'Vermelho', value: 'bg-red-500' },
    { name: 'Amarelo', value: 'bg-yellow-500' },
    { name: 'Índigo', value: 'bg-indigo-500' },
  ];

  const handleCreateBigRock = async () => {
    if (!newBigRockName.trim()) {
      toast({
        title: 'Erro',
        description: 'Por favor, digite um nome para o Big Rock.',
        variant: 'destructive',
      });
      return;
    }

    if (newBigRockHoursPerWeek <= 0 || newBigRockHoursPerWeek > 168) {
      toast({
        title: 'Erro',
        description: 'As horas por semana devem estar entre 1 e 168.',
        variant: 'destructive',
      });
      return;
    }

    try {
      await addBigRock({
        name: newBigRockName,
        description: newBigRockName,
        color: newBigRockColor,
        hoursPerWeek: newBigRockHoursPerWeek,
        priority: 1,
      });

      toast({
        title: 'Big Rock criado',
        description: 'Novo Big Rock adicionado com sucesso!',
      });

      setNewBigRockName('');
      setNewBigRockColor('bg-blue-500');
      setNewBigRockHoursPerWeek(20);
      setNewBigRockDialogOpen(false);
    } catch {
      toast({
        title: 'Erro',
        description: 'Não foi possível criar o Big Rock.',
        variant: 'destructive',
      });
    }
  };

  const handleViewTasks = (rockId: string) => {
    navigate(`/big-rocks/${rockId}`);
  };

  const handleViewAnalytics = (rockId: string) => {
    navigate(`/big-rocks/${rockId}/analytics`);
  };

  const handleOpenSettings = (rockId: string) => {
    const rock = getBigRockById(rockId);
    if (rock) {
      setSelectedBigRock(rockId);
      setEditBigRockName(rock.name);
      setEditBigRockColor(rock.color || 'bg-blue-500');
      setEditBigRockHoursPerWeek(rock.hoursPerWeek || 20);
      setEditBigRockDialogOpen(true);
    }
  };

  const handleUpdateBigRock = async () => {
    if (!selectedBigRock) return;

    if (!editBigRockName.trim()) {
      toast({
        title: 'Erro',
        description: 'Por favor, digite um nome para o Big Rock.',
        variant: 'destructive',
      });
      return;
    }

    if (editBigRockHoursPerWeek <= 0 || editBigRockHoursPerWeek > 168) {
      toast({
        title: 'Erro',
        description: 'As horas por semana devem estar entre 1 e 168.',
        variant: 'destructive',
      });
      return;
    }

    try {
      await updateBigRock(selectedBigRock, {
        name: editBigRockName,
        description: editBigRockName,
        color: editBigRockColor,
        hoursPerWeek: editBigRockHoursPerWeek,
      });

      toast({
        title: 'Big Rock atualizado',
        description: 'Alterações salvas com sucesso!',
      });

      setEditBigRockDialogOpen(false);
      setSelectedBigRock(null);
      setEditBigRockName('');
      setEditBigRockColor('bg-blue-500');
      setEditBigRockHoursPerWeek(20);
    } catch {
      toast({
        title: 'Erro',
        description: 'Não foi possível atualizar o Big Rock.',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteBigRock = async () => {
    if (!selectedBigRock) return;

    try {
      await deleteBigRock(selectedBigRock);

      toast({
        title: 'Big Rock arquivado',
        description: 'Big Rock foi arquivado e não aparecerá mais na lista.',
      });

      setEditBigRockDialogOpen(false);
      setSelectedBigRock(null);
      setEditBigRockName('');
      setEditBigRockColor('bg-blue-500');
    } catch {
      toast({
        title: 'Erro',
        description: 'Não foi possível arquivar o Big Rock.',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="space-y-6 md:space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-4xl font-bold tracking-tight">Big Rocks</h1>
          <p className="text-muted-foreground mt-1 md:mt-2 text-sm md:text-base">
            Gerencie os pilares mais importantes da sua vida.
          </p>
        </div>
        <Button onClick={() => setNewBigRockDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Novo Big Rock
        </Button>
      </div>

      {/* Capacity Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg md:text-xl">Visão Geral da Capacidade</CardTitle>
          <p className="text-xs md:text-sm text-muted-foreground">
            {totalCapacity.toFixed(1)} de 168 horas semanais alocadas
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="relative h-4 bg-secondary/20 rounded-full overflow-hidden">
              <div
                className={`absolute top-0 left-0 h-full transition-all ${
                  usedCapacity > 100 ? 'bg-red-500' : usedCapacity > 80 ? 'bg-orange-500' : 'bg-teal-500'
                }`}
                style={{ width: `${Math.min(usedCapacity, 100)}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">
                {usedCapacity.toFixed(1)}% da capacidade semanal
              </span>
              {usedCapacity > 100 && (
                <div className="flex items-center gap-1 text-red-500">
                  <AlertCircle className="h-4 w-4" />
                  <span className="font-medium">Sobrecarga!</span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Big Rocks Grid */}
      {bigRocks.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <Target className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
              <h3 className="text-lg font-medium mb-2">Nenhum Big Rock configurado</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Comece criando seu primeiro Big Rock para organizar suas prioridades de vida.
              </p>
              <Button onClick={() => setNewBigRockDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Criar Primeiro Big Rock
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:gap-6 lg:grid-cols-2">
          {bigRocks.map((rock) => {
            const rockTasks = tasks.filter((t) => t.bigRockId === rock.id);
            const completedTasks = rockTasks.filter((t) => t.status === 'completed');
            const pendingTasks = rockTasks.filter((t) => t.status !== 'completed');
            const completionRate = rockTasks.length > 0 ? (completedTasks.length / rockTasks.length) * 100 : 0;

            return (
              <Card key={rock.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className={`h-12 w-12 rounded-full ${rock.color} flex items-center justify-center text-white text-xl font-bold shrink-0`}
                      >
                        {rock.name[0]}
                      </div>
                      <div>
                        <CardTitle className="text-lg md:text-xl">{rock.name}</CardTitle>
                        {rock.description && (
                          <p className="text-sm text-muted-foreground mt-1">{rock.description}</p>
                        )}
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleOpenSettings(rock.id)}
                    >
                      <Settings className="h-4 w-4" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-2 md:gap-4">
                    <div className="text-center p-3 rounded-lg bg-secondary/20">
                      <div className="text-xl md:text-2xl font-bold">{rockTasks.length}</div>
                      <div className="text-xs text-muted-foreground">Tarefas</div>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-secondary/20">
                      <div className="text-xl md:text-2xl font-bold">{pendingTasks.length}</div>
                      <div className="text-xs text-muted-foreground">Pendentes</div>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-secondary/20">
                      <div className="text-xl md:text-2xl font-bold">{rock.hoursPerWeek}h</div>
                      <div className="text-xs text-muted-foreground">Por semana</div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Taxa de Conclusão</span>
                      <span className="font-medium">{completionRate.toFixed(0)}%</span>
                    </div>
                    <div className="relative h-2 bg-secondary/20 rounded-full overflow-hidden">
                      <div
                        className={`absolute top-0 left-0 h-full ${rock.color} transition-all`}
                        style={{ width: `${completionRate}%` }}
                      />
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col sm:flex-row gap-2 pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => handleViewTasks(rock.id)}
                    >
                      <List className="mr-2 h-4 w-4" />
                      Ver Tarefas
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => handleViewAnalytics(rock.id)}
                    >
                      <BarChart3 className="mr-2 h-4 w-4" />
                      Analytics
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* New Big Rock Dialog */}
      <Dialog open={newBigRockDialogOpen} onOpenChange={setNewBigRockDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Novo Big Rock</DialogTitle>
            <DialogDescription>
              Crie um novo pilar de vida para organizar suas prioridades.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Nome</label>
              <input
                type="text"
                value={newBigRockName}
                onChange={(e) => setNewBigRockName(e.target.value)}
                placeholder="Ex: Saúde & Bem-estar"
                className="w-full px-3 py-2 border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Cor</label>
              <div className="grid grid-cols-4 gap-2">
                {availableColors.map((color) => (
                  <button
                    key={color.value}
                    type="button"
                    onClick={() => setNewBigRockColor(color.value)}
                    className={`h-12 rounded-md ${color.value} transition-all ${
                      newBigRockColor === color.value
                        ? 'ring-2 ring-offset-2 ring-primary scale-105'
                        : 'opacity-70 hover:opacity-100'
                    }`}
                    title={color.name}
                  />
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Horas por semana</label>
              <input
                type="number"
                min="1"
                max="168"
                value={newBigRockHoursPerWeek}
                onChange={(e) => setNewBigRockHoursPerWeek(parseInt(e.target.value) || 1)}
                placeholder="Ex: 20"
                className="w-full px-3 py-2 border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
              <p className="text-xs text-muted-foreground">
                Quantas horas por semana você dedica a este Big Rock? (1-168)
              </p>
            </div>
          </div>
          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button variant="outline" onClick={() => setNewBigRockDialogOpen(false)} className="w-full sm:w-auto">
              Cancelar
            </Button>
            <Button onClick={handleCreateBigRock} className="w-full sm:w-auto">Criar Big Rock</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Big Rock Dialog */}
      <Dialog open={editBigRockDialogOpen} onOpenChange={setEditBigRockDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar Big Rock</DialogTitle>
            <DialogDescription>
              Atualize as informações do seu Big Rock.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Nome</label>
              <input
                type="text"
                value={editBigRockName}
                onChange={(e) => setEditBigRockName(e.target.value)}
                placeholder="Ex: Saúde & Bem-estar"
                className="w-full px-3 py-2 border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Cor</label>
              <div className="grid grid-cols-4 gap-2">
                {availableColors.map((color) => (
                  <button
                    key={color.value}
                    type="button"
                    onClick={() => setEditBigRockColor(color.value)}
                    className={`h-12 rounded-md ${color.value} transition-all ${
                      editBigRockColor === color.value
                        ? 'ring-2 ring-offset-2 ring-primary scale-105'
                        : 'opacity-70 hover:opacity-100'
                    }`}
                    title={color.name}
                  />
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Horas por semana</label>
              <input
                type="number"
                min="1"
                max="168"
                value={editBigRockHoursPerWeek}
                onChange={(e) => setEditBigRockHoursPerWeek(parseInt(e.target.value) || 1)}
                placeholder="Ex: 20"
                className="w-full px-3 py-2 border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
              <p className="text-xs text-muted-foreground">
                Quantas horas por semana você dedica a este Big Rock? (1-168)
              </p>
            </div>
          </div>
          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button
              variant="destructive"
              onClick={handleDeleteBigRock}
              className="w-full sm:w-auto sm:mr-auto"
            >
              Excluir Big Rock
            </Button>
            <Button variant="outline" onClick={() => setEditBigRockDialogOpen(false)} className="w-full sm:w-auto">
              Cancelar
            </Button>
            <Button onClick={handleUpdateBigRock} className="w-full sm:w-auto">Salvar Alterações</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
