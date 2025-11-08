import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  ArrowLeft,
  TrendingUp,
  CheckCircle2,
  Clock,
  BarChart3,
} from 'lucide-react';
import { useTaskStore } from '@/stores/taskStore';
import { useBigRockStore } from '@/stores/bigRockStore';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

export default function BigRockAnalytics() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { tasks, fetchTasks } = useTaskStore();
  const { fetchBigRocks, getBigRockById } = useBigRockStore();

  useEffect(() => {
    fetchTasks();
    fetchBigRocks();
  }, [fetchTasks, fetchBigRocks]);

  const bigRock = getBigRockById(id || '');
  const rockTasks = tasks.filter((t) => t.bigRockId === id);

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

  // Calculate stats
  const totalTasks = rockTasks.length;
  const completedTasks = rockTasks.filter((t) => t.status === 'completed').length;
  const pendingTasks = rockTasks.filter((t) => t.status === 'pending').length;
  const inProgressTasks = rockTasks.filter((t) => t.status === 'in_progress').length;
  const completionRate = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

  // Priority distribution
  const priorityData = [
    {
      name: 'Alta (P1)',
      value: rockTasks.filter((t) => t.priority === 1).length,
      color: '#ef4444',
    },
    {
      name: 'Média (P2)',
      value: rockTasks.filter((t) => t.priority === 2).length,
      color: '#f59e0b',
    },
    {
      name: 'Baixa (P3)',
      value: rockTasks.filter((t) => t.priority === 3).length,
      color: '#3b82f6',
    },
  ].filter((p) => p.value > 0);

  // Status distribution
  const statusData = [
    { name: 'Pendentes', value: pendingTasks },
    { name: 'Em Progresso', value: inProgressTasks },
    { name: 'Concluídas', value: completedTasks },
  ];

  // Mock weekly progress data (in a real app, this would come from the backend)
  const weeklyData = [
    { day: 'Seg', completed: 2, pending: 1 },
    { day: 'Ter', completed: 3, pending: 2 },
    { day: 'Qua', completed: 1, pending: 1 },
    { day: 'Qui', completed: 4, pending: 3 },
    { day: 'Sex', completed: 2, pending: 1 },
    { day: 'Sáb', completed: 1, pending: 0 },
    { day: 'Dom', completed: 0, pending: 0 },
  ];

  const stats = [
    {
      label: 'Total de Tarefas',
      value: totalTasks.toString(),
      icon: BarChart3,
      color: 'text-blue-500',
    },
    {
      label: 'Taxa de Conclusão',
      value: `${completionRate.toFixed(0)}%`,
      icon: CheckCircle2,
      color: 'text-green-500',
    },
    {
      label: 'Em Progresso',
      value: inProgressTasks.toString(),
      icon: Clock,
      color: 'text-orange-500',
    },
    {
      label: 'Concluídas',
      value: completedTasks.toString(),
      icon: CheckCircle2,
      color: 'text-green-500',
    },
  ];

  return (
    <div className="space-y-6 md:space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(`/big-rocks/${id}`)}>
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
              Analytics: {bigRock.name}
            </h1>
            <p className="text-muted-foreground mt-1">
              Análise de desempenho e produtividade
            </p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl md:text-3xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Distribuição por Status</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={statusData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Priority Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Distribuição por Prioridade</CardTitle>
          </CardHeader>
          <CardContent>
            {priorityData.length === 0 ? (
              <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                <p>Nenhuma tarefa para exibir</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={priorityData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) =>
                      `${name}: ${(Number(percent) * 100).toFixed(0)}%`
                    }
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {priorityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Weekly Progress */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Progresso Semanal</CardTitle>
            <p className="text-sm text-muted-foreground">
              Tarefas concluídas vs pendentes por dia
            </p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="day" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="completed"
                  stroke="#22c55e"
                  strokeWidth={2}
                  name="Concluídas"
                  dot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="pending"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  name="Pendentes"
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Progress Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Progresso Geral
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Taxa de Conclusão</span>
                <span className="font-medium">{completionRate.toFixed(1)}%</span>
              </div>
              <div className="relative h-4 bg-secondary/20 rounded-full overflow-hidden">
                <div
                  className={`absolute top-0 left-0 h-full ${bigRock.color} transition-all`}
                  style={{ width: `${completionRate}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 pt-4">
              <div className="text-center p-4 rounded-lg bg-secondary/20">
                <div className="text-2xl font-bold text-green-500">{completedTasks}</div>
                <div className="text-xs text-muted-foreground mt-1">Concluídas</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-secondary/20">
                <div className="text-2xl font-bold text-orange-500">{inProgressTasks}</div>
                <div className="text-xs text-muted-foreground mt-1">Em Progresso</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-secondary/20">
                <div className="text-2xl font-bold text-blue-500">{pendingTasks}</div>
                <div className="text-xs text-muted-foreground mt-1">Pendentes</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
