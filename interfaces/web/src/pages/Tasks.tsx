import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { DatePicker } from '@/components/ui/date-picker';
import {
  Plus,
  Calendar,
  Filter,
  CheckCircle2,
  Circle,
  Clock,
  Trash2,
  AlertCircle,
  Pencil
} from 'lucide-react';
import { useTaskStore } from '@/stores/taskStore';
import { useBigRockStore } from '@/stores/bigRockStore';
import { useToast } from '@/hooks/use-toast';
import { format, isToday, isPast, isFuture } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export default function Tasks() {
  const [searchParams] = useSearchParams();
  const { toast } = useToast();

  const [newTaskDialogOpen, setNewTaskDialogOpen] = useState(false);

  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState<1 | 2 | 3>(2);
  const [newTaskDeadline, setNewTaskDeadline] = useState('');
  const [newTaskBigRock, setNewTaskBigRock] = useState<string>('');

  const [editTaskDialogOpen, setEditTaskDialogOpen] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [editTaskTitle, setEditTaskTitle] = useState('');
  const [editTaskPriority, setEditTaskPriority] = useState<1 | 2 | 3>(2);
  const [editTaskDeadline, setEditTaskDeadline] = useState('');
  const [editTaskBigRock, setEditTaskBigRock] = useState<string>('');

  const [deleteConfirmDialogOpen, setDeleteConfirmDialogOpen] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<string | null>(null);

  const [filterStatus, setFilterStatus] = useState<string>(searchParams.get('filter') || 'all');
  const [filterBigRock, setFilterBigRock] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');

  const {
    tasks,
    fetchTasks,
    addTask,
    updateTask,
    deleteTask,
    toggleTaskStatus,
    loading
  } = useTaskStore();

  const { bigRocks, fetchBigRocks } = useBigRockStore();

  useEffect(() => {
    fetchTasks();
    fetchBigRocks();
  }, [fetchTasks, fetchBigRocks]);

  // Filter tasks
  const filteredTasks = tasks.filter((task) => {
    // Status filter
    if (filterStatus === 'pending' && task.status === 'completed') return false;
    if (filterStatus === 'completed' && task.status !== 'completed') return false;
    if (filterStatus === 'overdue' && (!task.deadline || !isPast(new Date(task.deadline)) || task.status === 'completed')) return false;
    if (filterStatus === 'today' && (!task.deadline || !isToday(new Date(task.deadline)))) return false;

    // Big Rock filter
    if (filterBigRock !== 'all' && task.bigRockId !== filterBigRock) return false;

    // Priority filter
    if (filterPriority !== 'all' && task.priority !== parseInt(filterPriority)) return false;

    return true;
  });

  // Group tasks
  const groupedTasks = {
    overdue: filteredTasks.filter(t => t.deadline && isPast(new Date(t.deadline)) && t.status !== 'completed'),
    today: filteredTasks.filter(t => t.deadline && isToday(new Date(t.deadline))),
    upcoming: filteredTasks.filter(t => t.deadline && isFuture(new Date(t.deadline)) && !isToday(new Date(t.deadline))),
    noDeadline: filteredTasks.filter(t => !t.deadline),
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
        bigRockId: newTaskBigRock || undefined,
      });

      toast({
        title: 'Tarefa criada',
        description: 'Nova tarefa adicionada com sucesso!',
      });

      setNewTaskTitle('');
      setNewTaskPriority(2);
      setNewTaskDeadline('');
      setNewTaskBigRock('');
      setNewTaskDialogOpen(false);
    } catch {
      toast({
        title: 'Erro',
        description: 'Não foi possível criar a tarefa.',
        variant: 'destructive',
      });
    }
  };

  const handleToggleTask = async (id: string) => {
    try {
      await toggleTaskStatus(id);
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

  const handleOpenDeleteConfirm = (id: string) => {
    setTaskToDelete(id);
    setDeleteConfirmDialogOpen(true);
  };

  const handleDeleteTask = async () => {
    if (!taskToDelete) return;

    try {
      await deleteTask(taskToDelete);
      toast({
        title: 'Tarefa excluída',
        description: 'A tarefa foi removida com sucesso.',
      });
      setDeleteConfirmDialogOpen(false);
      setTaskToDelete(null);
    } catch {
      toast({
        title: 'Erro',
        description: 'Não foi possível excluir a tarefa.',
        variant: 'destructive',
      });
    }
  };

  const handleOpenEditTask = (task: typeof tasks[0]) => {
    setSelectedTaskId(task.id);
    setEditTaskTitle(task.title);
    setEditTaskPriority(task.priority);
    setEditTaskDeadline(task.deadline ? task.deadline.split('T')[0] : '');
    setEditTaskBigRock(task.bigRockId || '');
    setEditTaskDialogOpen(true);
  };

  const handleUpdateTask = async () => {
    if (!selectedTaskId) return;

    if (!editTaskTitle.trim()) {
      toast({
        title: 'Erro',
        description: 'Digite um título para a tarefa.',
        variant: 'destructive',
      });
      return;
    }

    try {
      await updateTask(selectedTaskId, {
        title: editTaskTitle,
        deadline: editTaskDeadline || undefined,
        bigRockId: editTaskBigRock || undefined,
      });

      toast({
        title: 'Tarefa atualizada',
        description: 'Alterações salvas com sucesso!',
      });

      setEditTaskDialogOpen(false);
      setSelectedTaskId(null);
      setEditTaskTitle('');
      setEditTaskPriority(2);
      setEditTaskDeadline('');
      setEditTaskBigRock('');
    } catch {
      toast({
        title: 'Erro',
        description: 'Não foi possível atualizar a tarefa.',
        variant: 'destructive',
      });
    }
  };

  const TaskCard = ({ task }: { task: typeof tasks[0] }) => {
    const rock = bigRocks.find(r => r.id === task.bigRockId);
    const isOverdue = task.deadline && isPast(new Date(task.deadline)) && task.status !== 'completed';

    return (
      <div className={`p-4 rounded-lg border bg-card hover:shadow-md transition-all ${
        isOverdue ? 'border-red-500/50 bg-red-500/5' : ''
      }`}>
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
            <div className="flex items-start justify-between gap-2">
              <h3 className={`font-medium ${
                task.status === 'completed' ? 'line-through opacity-60' : ''
              }`}>
                {task.title}
              </h3>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 shrink-0"
                  onClick={() => handleOpenEditTask(task)}
                >
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 shrink-0 text-destructive"
                  onClick={() => handleOpenDeleteConfirm(task.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2 mt-2 text-sm text-muted-foreground">
              {/* Priority Badge */}
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                task.priority === 1
                  ? 'bg-red-500/10 text-red-500'
                  : task.priority === 2
                  ? 'bg-orange-500/10 text-orange-500'
                  : 'bg-blue-500/10 text-blue-500'
              }`}>
                P{task.priority}
              </span>

              {/* Big Rock */}
              {rock && (
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${rock.color} text-white`}>
                  {rock.name}
                </span>
              )}

              {/* Deadline */}
              {task.deadline && (
                <span className={`flex items-center gap-1 ${
                  isOverdue ? 'text-red-500 font-medium' : ''
                }`}>
                  <Calendar className="h-3.5 w-3.5" />
                  {format(new Date(task.deadline), "dd MMM", { locale: ptBR })}
                  {isOverdue && <AlertCircle className="h-3.5 w-3.5" />}
                </span>
              )}

              {/* Status */}
              {task.status === 'in_progress' && (
                <span className="flex items-center gap-1 text-blue-500">
                  <Clock className="h-3.5 w-3.5" />
                  Em progresso
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6 md:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-4xl font-bold tracking-tight">Tarefas</h1>
          <p className="text-muted-foreground mt-1 md:mt-2 text-sm md:text-base">
            Gerencie todas as suas tarefas em um só lugar.
          </p>
        </div>
        <Button onClick={() => setNewTaskDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Nova Tarefa
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Filter className="h-5 w-5" />
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Status</label>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas</SelectItem>
                  <SelectItem value="pending">Pendentes</SelectItem>
                  <SelectItem value="completed">Concluídas</SelectItem>
                  <SelectItem value="overdue">Atrasadas</SelectItem>
                  <SelectItem value="today">Hoje</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Big Rock</label>
              <Select value={filterBigRock} onValueChange={setFilterBigRock}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  {bigRocks.map((rock) => (
                    <SelectItem key={rock.id} value={rock.id}>
                      {rock.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Prioridade</label>
              <Select value={filterPriority} onValueChange={setFilterPriority}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas</SelectItem>
                  <SelectItem value="1">Alta (P1)</SelectItem>
                  <SelectItem value="2">Média (P2)</SelectItem>
                  <SelectItem value="3">Baixa (P3)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Task Groups */}
      {loading ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">Carregando tarefas...</p>
          </CardContent>
        </Card>
      ) : filteredTasks.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <CheckCircle2 className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
            <h3 className="text-lg font-medium mb-2">Nenhuma tarefa encontrada</h3>
            <p className="text-sm text-muted-foreground mb-4">
              {filterStatus !== 'all' || filterBigRock !== 'all' || filterPriority !== 'all'
                ? 'Tente ajustar os filtros ou crie uma nova tarefa.'
                : 'Crie sua primeira tarefa para começar.'}
            </p>
            <Button onClick={() => setNewTaskDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Nova Tarefa
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* Overdue Tasks */}
          {groupedTasks.overdue.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-red-500">
                <AlertCircle className="h-5 w-5" />
                <h2 className="text-lg font-semibold">Atrasadas ({groupedTasks.overdue.length})</h2>
              </div>
              <div className="space-y-2">
                {groupedTasks.overdue.map(task => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            </div>
          )}

          {/* Today's Tasks */}
          {groupedTasks.today.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-lg font-semibold">Hoje ({groupedTasks.today.length})</h2>
              <div className="space-y-2">
                {groupedTasks.today.map(task => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            </div>
          )}

          {/* Upcoming Tasks */}
          {groupedTasks.upcoming.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-lg font-semibold">Próximas ({groupedTasks.upcoming.length})</h2>
              <div className="space-y-2">
                {groupedTasks.upcoming.map(task => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            </div>
          )}

          {/* No Deadline Tasks */}
          {groupedTasks.noDeadline.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-lg font-semibold">Sem prazo ({groupedTasks.noDeadline.length})</h2>
              <div className="space-y-2">
                {groupedTasks.noDeadline.map(task => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* New Task Dialog */}
      <Dialog open={newTaskDialogOpen} onOpenChange={setNewTaskDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nova Tarefa</DialogTitle>
            <DialogDescription>Crie uma nova tarefa para adicionar ao seu inbox.</DialogDescription>
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

            <div className="space-y-2">
              <label className="text-sm font-medium">Big Rock (opcional)</label>
              <div className="flex gap-2">
                <Select value={newTaskBigRock || undefined} onValueChange={setNewTaskBigRock}>
                  <SelectTrigger className="flex-1">
                    <SelectValue placeholder="Nenhum" />
                  </SelectTrigger>
                  <SelectContent>
                    {bigRocks.map((rock) => (
                      <SelectItem key={rock.id} value={rock.id}>
                        {rock.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {newTaskBigRock && (
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={() => setNewTaskBigRock('')}
                    title="Limpar seleção"
                  >
                    ✕
                  </Button>
                )}
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

      {/* Edit Task Dialog */}
      <Dialog open={editTaskDialogOpen} onOpenChange={setEditTaskDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar Tarefa</DialogTitle>
            <DialogDescription>Atualize as informações da tarefa.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Título *</label>
              <input
                type="text"
                value={editTaskTitle}
                onChange={(e) => setEditTaskTitle(e.target.value)}
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
                    variant={editTaskPriority === priority ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setEditTaskPriority(priority as 1 | 2 | 3)}
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
                value={editTaskDeadline}
                onChange={setEditTaskDeadline}
                placeholder="Selecione uma data"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Big Rock (opcional)</label>
              <div className="flex gap-2">
                <Select value={editTaskBigRock || undefined} onValueChange={setEditTaskBigRock}>
                  <SelectTrigger className="flex-1">
                    <SelectValue placeholder="Nenhum" />
                  </SelectTrigger>
                  <SelectContent>
                    {bigRocks.map((rock) => (
                      <SelectItem key={rock.id} value={rock.id}>
                        {rock.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {editTaskBigRock && (
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={() => setEditTaskBigRock('')}
                    title="Limpar seleção"
                  >
                    ✕
                  </Button>
                )}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditTaskDialogOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleUpdateTask}>Salvar Alterações</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmDialogOpen} onOpenChange={setDeleteConfirmDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmar Exclusão</DialogTitle>
            <DialogDescription>
              Tem certeza de que deseja excluir esta tarefa? Esta ação não pode ser desfeita.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirmDialogOpen(false)}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleDeleteTask}>
              Excluir
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
