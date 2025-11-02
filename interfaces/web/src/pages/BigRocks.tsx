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
import { Activity, Heart, Target, TrendingUp, Calendar, CheckCircle2, AlertCircle } from 'lucide-react';
import { useTaskStore } from '@/stores/taskStore';
import { useBigRockStore } from '@/stores/bigRockStore';
import { useCycleStore } from '@/stores/cycleStore';
import { useToast } from '@/hooks/use-toast';
import { inboxService } from '@/services/inboxService';

export default function Dashboard() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [newTaskDialogOpen, setNewTaskDialogOpen] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState<1 | 2 | 3>(2);
  const [inboxText, setInboxText] = useState<string>('');
  const [tarefasHoje, setTarefasHoje] = useState(0);
  const [tarefasAtrasadas, setTarefasAtrasadas] = useState(0);

  const { tasks, getPendingTasks, toggleTaskStatus, addTask, fetchTasks } = useTaskStore();
  const { bigRocks, fetchBigRocks } = useBigRockStore();
  const { currentPhase } = useCycleStore();

  // Fetch data on mount
  useEffect(() => {
    fetchTasks();
    fetchBigRocks();
    loadInboxData();
  }, [fetchTasks, fetchBigRocks]);

  // Load inbox data
  const loadInboxData = async () => {
    try {
      const [inbox, hoje, atrasadas] = await Promise.all([
        inboxService.getInboxRapido(3),
        inboxService.getTarefasHoje(),
        inboxService.getTarefasAtrasadas()
      ]);
      
      setInboxText(inbox.inbox_text);
      setTarefasHoje(hoje.length);
      setTarefasAtrasadas(atrasadas.length);
    } catch (error) {
      console.error('Failed to load inbox data:', error);
    }
  };

  const pendingTasks = getPendingTasks();
  const completedThisWeek = tasks.filter((t) => t.status === 'completed').length;
  console.log('inboxText',inboxText);
  console.log('tarefasHoje',tarefasHoje);
  
  const stats = [
    { 
      label: 'Tarefas Pendentes', 
      value: pendingTasks.length.toString(), 
      icon: Activity, 
      color: 'text-blue-500',
      onClick: () => navigate('/tasks')
    },
    { 
      label: 'Big Rocks Ativos', 
      value: bigRocks.length.toString(), 
      icon: Target, 
      color: 'text-teal-500',
      onClick: () => navigate('/big-rocks')
    },
    { 
      label: 'Concluídas (Semana)', 
      value: completedThisWeek.toString(), 
      icon: CheckCircle2, 
      color: 'text-green-500',
      onClick: () => navigate('/analytics')
    },
    { 
      label: 'Fase do Ciclo', 
      value: currentPhase.charAt(0).toUpperCase() + currentPhase.slice(1), 
      icon: Heart, 
      color: 'text-pink-500',
      onClick: () => navigate('/wellness')
    },
  ];

  // Show only top 3 pending tasks
  const topTasks = pendingTasks.slice(0, 3);

  // Show only top 3 big rocks
  const topBigRocks = bigRocks.slice(0, 3);

  const handleToggleTask = async (id: string) => {
    try {
      await toggleTaskStatus(id);
      toast({
        title: 'Tarefa atualizada',
        description: 'Status da tarefa alterado com sucesso.',
      });
      loadInboxData(); // Reload inbox
    } catch (error) {
      toast({
        title: 'Erro',
        description: `Não foi possível atualizar a tarefa.`,
        variant: 'destructive',
      });
      console.log(error);      
    }
  };

  const handleCreateTask = async () => {
    if (!newTaskTitle.trim()) {
      toast({
        title: 'Erro',
        description: 'Por favor, digite um título para a tarefa.',
        variant: 'destructive',
      });
      return;
    }

    try {
      await addTask({
        title: newTaskTitle,
        priority: newTaskPriority,
        status: 'pending',
      });

      toast({
        title: 'Tarefa criada',
        description: 'Nova tarefa adicionada com sucesso!',
      });

      setNewTaskTitle('');
      setNewTaskPriority(2);
      setNewTaskDialogOpen(false);
      loadInboxData(); // Reload inbox
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Não foi possível criar a tarefa.',
        variant: 'destructive',
      });
      console.log(error);
    }
  };

  const handleViewAllTasks = () => {
    navigate('/tasks');
  };

  const handleViewBigRock = (rockId: string) => {
    navigate(`/big-rocks/${rockId}`);
  };

  return (
    <div className="space-y-6 md:space-y-8">
      <div>
        <h1 className="text-2xl md:text-4xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1 md:mt-2 text-sm md:text-base">
          Bem-vinda de volta! Aqui está seu resumo de hoje.
        </p>
      </div>

      {/* Alerts */}
      {tarefasAtrasadas > 0 && (
        <div className="flex items-start gap-3 p-4 rounded-lg bg-orange-500/10 border border-orange-500/20">
          <AlertCircle className="h-5 w-5 text-orange-500 mt-0.5 shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium">
              Você tem {tarefasAtrasadas} tarefa{tarefasAtrasadas > 1 ? 's' : ''} atrasada{tarefasAtrasadas > 1 ? 's' : ''}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Considere priorizar ou reagendar estas tarefas
            </p>
          </div>
          <Button size="sm" variant="outline" onClick={() => navigate('/tasks?filter=overdue')}>
            Ver Atrasadas
          </Button>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-3 md:gap-4 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card 
              key={stat.label} 
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={stat.onClick}
            >
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-4 md:gap-6 lg:grid-cols-3">
        {/* Inbox Rápido */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-3">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <div>
                <CardTitle className="text-lg md:text-xl">Inbox Rápido</CardTitle>
                <p className="text-xs md:text-sm text-muted-foreground mt-1">
                  Top {topTasks.length} tarefas priorizadas para hoje
                </p>
              </div>
              <Button
                size="sm"
                variant="outline"
                className="w-full sm:w-auto"
                onClick={handleViewAllTasks}
              >
                Ver Todas ({pendingTasks.length})
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {topTasks.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <CheckCircle2 className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>Nenhuma tarefa pendente!</p>
                <p className="text-sm mt-1">Adicione uma nova tarefa para começar.</p>
              </div>
            ) : (
              <div className="space-y-2 md:space-y-3">
                {topTasks.map((task) => (
                  <div
                    key={task.id}
                    className="flex flex-col sm:flex-row sm:items-center gap-3 p-3 md:p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-start gap-3 flex-1">
                      <input
                        type="checkbox"
                        checked={task.status === 'completed'}
                        onChange={() => handleToggleTask(task.id)}
                        className="h-4 w-4 rounded border-gray-300 mt-0.5 cursor-pointer"
                      />
                      <div className="flex-1 min-w-0">
                        <div className={`font-medium text-sm md:text-base ${task.status === 'completed' ? 'line-through opacity-60' : ''}`}>
                          {task.title}
                        </div>
                        <div className="flex items-center flex-wrap gap-2 mt-1.5 text-xs md:text-sm text-muted-foreground">
                          <span
                            className={`px-2 py-0.5 rounded text-xs font-medium whitespace-nowrap ${
                              task.priority === 1
                                ? 'bg-red-500/10 text-red-500'
                                : task.priority === 2
                                ? 'bg-orange-500/10 text-orange-500'
                                : 'bg-blue-500/10 text-blue-500'
                            }`}
                          >
                            P{task.priority}
                          </span>
                          {task.bigRockId && (
                            <span className="truncate">
                              {bigRocks.find((r) => r.id === task.bigRockId)?.name}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    {task.deadline && (
                      <div className="flex items-center gap-1 text-xs md:text-sm text-muted-foreground pl-7 sm:pl-0">
                        <Calendar className="h-3.5 w-3.5 md:h-4 md:w-4" />
                        {new Date(task.deadline).toLocaleDateString('pt-BR')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Big Rocks */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg md:text-xl">Big Rocks</CardTitle>
            <p className="text-xs md:text-sm text-muted-foreground mt-1">Pilares de vida</p>
          </CardHeader>
          <CardContent>
            {topBigRocks.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Target className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Nenhum Big Rock configurado</p>
                <Button 
                  size="sm" 
                  className="mt-4"
                  onClick={() => navigate('/big-rocks')}
                >
                  Criar Big Rock
                </Button>
              </div>
            ) : (
              <div className="space-y-3 md:space-y-4">
                {topBigRocks.map((rock) => {
                  const rockTasks = tasks.filter((t) => t.bigRockId === rock.id);
                  const completed = rockTasks.filter((t) => t.status === 'completed').length;
                  const capacity = rockTasks.length > 0 ? (completed / rockTasks.length) * 100 : 0;

                  return (
                    <div 
                      key={rock.id} 
                      className="space-y-2 cursor-pointer hover:bg-accent/50 p-2 rounded-lg transition-colors"
                      onClick={() => handleViewBigRock(rock.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                          <div
                            className={`h-9 w-9 md:h-10 md:w-10 rounded-full ${rock.color} flex items-center justify-center text-white text-sm md:text-base font-bold shrink-0`}
                          >
                            {rock.name[0]}
                          </div>
                          <div className="min-w-0">
                            <div className="font-medium text-sm md:text-base truncate">{rock.name}</div>
                            <div className="text-xs text-muted-foreground">{rockTasks.length} tarefas</div>
                          </div>
                        </div>
                      </div>
                      <div className="relative h-2 bg-secondary/20 rounded-full overflow-hidden">
                        <div
                          className={`absolute top-0 left-0 h-full ${rock.color} transition-all`}
                          style={{ width: `${capacity}%` }}
                        />
                      </div>
                      <div className="text-xs text-muted-foreground text-right">{capacity.toFixed(0)}% concluído</div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg md:text-xl">Ações Rápidas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-2 md:gap-3">
            <Button className="flex-1" onClick={() => setNewTaskDialogOpen(true)}>
              <Activity className="mr-2 h-4 w-4" />
              Nova Tarefa
            </Button>
            <Button variant="outline" className="flex-1" onClick={() => navigate('/analytics')}>
              <TrendingUp className="mr-2 h-4 w-4" />
              Ver Analytics
            </Button>
            <Button variant="outline" className="flex-1" onClick={() => navigate('/chat')}>
              <Heart className="mr-2 h-4 w-4" />
              Chat com Charlee
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* New Task Dialog */}
      <Dialog open={newTaskDialogOpen} onOpenChange={setNewTaskDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nova Tarefa</DialogTitle>
            <DialogDescription>Adicione uma nova tarefa ao seu inbox.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Título</label>
              <input
                type="text"
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
                placeholder="Ex: Revisar código do projeto"
                className="w-full px-3 py-2 border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Prioridade</label>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant={newTaskPriority === 1 ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setNewTaskPriority(1)}
                  className="flex-1"
                >
                  Alta
                </Button>
                <Button
                  type="button"
                  variant={newTaskPriority === 2 ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setNewTaskPriority(2)}
                  className="flex-1"
                >
                  Média
                </Button>
                <Button
                  type="button"
                  variant={newTaskPriority === 3 ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setNewTaskPriority(3)}
                  className="flex-1"
                >
                  Baixa
                </Button>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setNewTaskDialogOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleCreateTask}>Criar Tarefa</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}