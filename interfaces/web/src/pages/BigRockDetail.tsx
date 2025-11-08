import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
import { DatePicker } from '@/components/ui/date-picker';
import {
  ArrowLeft,
  Plus,
  CheckCircle2,
  Circle,
  Calendar,
  TrendingUp,
  Settings,
} from 'lucide-react';
import { useTaskStore } from '@/stores/taskStore';
import { useBigRockStore } from '@/stores/bigRockStore';
import { useToast } from '@/hooks/use-toast';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export default function BigRockDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [newTaskDialogOpen, setNewTaskDialogOpen] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState<1 | 2 | 3>(2);
  const [newTaskDeadline, setNewTaskDeadline] = useState('');

  const { tasks, fetchTasks, toggleTaskStatus, addTask } = useTaskStore();
  const { fetchBigRocks, getBigRockById } = useBigRockStore();

  useEffect(() => {
    fetchTasks();
    fetchBigRocks();
  }, [fetchTasks, fetchBigRocks]);

  const bigRock = getBigRockById(id || '');
  const rockTasks = tasks.filter((t) => t.bigRockId === id);
  const completedTasks = rockTasks.filter((t) => t.status === 'completed');
  const pendingTasks = rockTasks.filter((t) => t.status !== 'completed');
  const completionRate = rockTasks.length > 0 ? (completedTasks.length / rockTasks.length) * 100 : 0;

  if (!bigRock) {
    return (
      <div className="space-y-6 md:space-y-8">
        <div className="text-center py-12">
          <h1 className="text-2xl font-bold mb-4">Big Rock não encontrado</h1>
          <Button onClick={() => navigate('/big-rocks')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Voltar para Big Rocks
          </Button>
        </div>
      </div>
    );
  }

  const handleToggleTask = async (taskId: string) => {
    try {
      await toggleTaskStatus(taskId);
      toast({
        title: 'Tarefa atualizada',
        description: 'Status alterado com sucesso.',
      });
    } catch {
      toast({
        title: 'Erro',
        description: 'Não foi possível atualizar a tarefa.',
        variant: 'destructive',
      });
    }
  };

  const handleCreateTask = async () => {
    if (!newTaskTitle.trim()) {
      toast({
        title: 'Erro',
        description: 'Digite um título para a tarefa.',
        variant: 'destructive',
      });
      return;
    }

    try {
      await addTask({
        title: newTaskTitle,
        priority: newTaskPriority,
        status: 'pending',
        deadline: newTaskDeadline || undefined,
        bigRockId: id, // Pré-seleciona o Big Rock atual
      });

      toast({
        title: 'Tarefa criada',
        description: 'Nova tarefa adicionada com sucesso!',
      });

      setNewTaskTitle('');
      setNewTaskPriority(2);
      setNewTaskDeadline('');
      setNewTaskDialogOpen(false);
    } catch {
      toast({
        title: 'Erro',
        description: 'Não foi possível criar a tarefa.',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="space-y-6 md:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate('/big-rocks')}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="flex items-center gap-3">
            <div
              className={`h-12 w-12 rounded-full ${bigRock.color} flex items-center justify-center text-white text-xl font-bold shrink-0`}
            >
              {bigRock.name[0]}
            </div>
            <div>
              <h1 className="text-2xl md:text-4xl font-bold tracking-tight">
                {bigRock.name}
              </h1>
              {bigRock.description && (
                <p className="text-muted-foreground mt-1">
                  {bigRock.description}
                </p>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Settings className="mr-2 h-4 w-4" />
            Configurações
          </Button>
          <Button onClick={() => setNewTaskDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Nova Tarefa
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total de Tarefas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{rockTasks.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Pendentes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-500">
              {pendingTasks.length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Concluídas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-500">
              {completedTasks.length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Taxa de Conclusão
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{completionRate.toFixed(0)}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Progresso
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Conclusão geral</span>
              <span className="font-medium">{completionRate.toFixed(1)}%</span>
            </div>
            <div className="relative h-4 bg-secondary/20 rounded-full overflow-hidden">
              <div
                className={`absolute top-0 left-0 h-full ${bigRock.color} transition-all`}
                style={{ width: `${completionRate}%` }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tasks List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Tarefas ({rockTasks.length})</CardTitle>
            <Button size="sm" onClick={() => setNewTaskDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Nova Tarefa
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {rockTasks.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>Nenhuma tarefa vinculada a este Big Rock.</p>
              <Button
                className="mt-4"
                variant="outline"
                onClick={() => setNewTaskDialogOpen(true)}
              >
                Criar Primeira Tarefa
              </Button>
            </div>
          ) : (
            <div className="space-y-2">
              {rockTasks.map((task) => (
                <div
                  key={task.id}
                  className="p-4 rounded-lg border bg-card hover:shadow-md transition-all"
                >
                  <div className="flex items-start gap-3">
                    <button
                      onClick={() => handleToggleTask(task.id)}
                      className="mt-0.5"
                    >
                      {task.status === 'completed' ? (
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                      ) : (
                        <Circle className="h-5 w-5 text-muted-foreground hover:text-primary" />
                      )}
                    </button>

                    <div className="flex-1 min-w-0">
                      <h3
                        className={`font-medium ${
                          task.status === 'completed'
                            ? 'line-through opacity-60'
                            : ''
                        }`}
                      >
                        {task.title}
                      </h3>

                      <div className="flex flex-wrap items-center gap-2 mt-2 text-sm text-muted-foreground">
                        {/* Priority Badge */}
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-medium ${
                            task.priority === 1
                              ? 'bg-red-500/10 text-red-500'
                              : task.priority === 2
                              ? 'bg-orange-500/10 text-orange-500'
                              : 'bg-blue-500/10 text-blue-500'
                          }`}
                        >
                          P{task.priority}
                        </span>

                        {/* Deadline */}
                        {task.deadline && (
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3.5 w-3.5" />
                            {format(new Date(task.deadline), 'dd MMM', {
                              locale: ptBR,
                            })}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* New Task Dialog */}
      <Dialog open={newTaskDialogOpen} onOpenChange={setNewTaskDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nova Tarefa</DialogTitle>
            <DialogDescription>
              Criar uma nova tarefa para {bigRock.name}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Título *</label>
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
                {[1, 2, 3].map((priority) => (
                  <Button
                    key={priority}
                    type="button"
                    variant={newTaskPriority === priority ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setNewTaskPriority(priority as 1 | 2 | 3)}
                    className="flex-1"
                  >
                    P{priority} - {priority === 1 ? 'Alta' : priority === 2 ? 'Média' : 'Baixa'}
                  </Button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Prazo</label>
              <DatePicker
                value={newTaskDeadline}
                onChange={setNewTaskDeadline}
                placeholder="Selecione uma data"
              />
            </div>
          </div>
          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button variant="outline" onClick={() => setNewTaskDialogOpen(false)} className="w-full sm:w-auto">
              Cancelar
            </Button>
            <Button onClick={handleCreateTask} className="w-full sm:w-auto">Criar Tarefa</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
