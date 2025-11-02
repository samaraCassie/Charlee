import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, CheckCircle2, Clock, TrendingUp, Calendar } from 'lucide-react';
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

export default function Analytics() {
  // Dados de exemplo para os gráficos
  const weeklyData = [
    { day: 'Seg', completed: 4, pending: 2 },
    { day: 'Ter', completed: 6, pending: 3 },
    { day: 'Qua', completed: 5, pending: 1 },
    { day: 'Qui', completed: 8, pending: 4 },
    { day: 'Sex', completed: 7, pending: 2 },
    { day: 'Sab', completed: 3, pending: 1 },
    { day: 'Dom', completed: 2, pending: 0 },
  ];

  const monthlyData = [
    { month: 'Jan', tasks: 45 },
    { month: 'Fev', tasks: 52 },
    { month: 'Mar', tasks: 48 },
    { month: 'Abr', tasks: 61 },
    { month: 'Mai', tasks: 55 },
    { month: 'Jun', tasks: 67 },
  ];

  const bigRocksData = [
    { name: 'Syssa - Estágio', value: 45, color: '#3b82f6' },
    { name: 'Estudos', value: 30, color: '#a855f7' },
    { name: 'Saúde', value: 15, color: '#22c55e' },
    { name: 'Outros', value: 10, color: '#94a3b8' },
  ];

  const stats = [
    { label: 'Taxa de Conclusão', value: '87%', icon: CheckCircle2, color: 'text-green-500' },
    { label: 'Tempo Médio/Tarefa', value: '2.3h', icon: Clock, color: 'text-blue-500' },
    { label: 'Produtividade', value: '+12%', icon: TrendingUp, color: 'text-teal-500' },
    { label: 'Tarefas Atrasadas', value: '3', icon: Activity, color: 'text-orange-500' },
  ];

  return (
    <div className="space-y-6 md:space-y-8">
      <div>
        <h1 className="text-2xl md:text-4xl font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground mt-1 md:mt-2 text-sm md:text-base">
          Visualize seu desempenho e produtividade ao longo do tempo.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-3 md:gap-4 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="hover:shadow-lg transition-shadow">
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
      <div className="grid gap-4 md:gap-6 lg:grid-cols-2">
        {/* Weekly Progress */}
        <Card className="col-span-full lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg md:text-xl">Progresso Semanal</CardTitle>
            <p className="text-xs md:text-sm text-muted-foreground">
              Tarefas concluídas vs pendentes por dia
            </p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={weeklyData}>
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
                <Bar dataKey="completed" fill="#22c55e" name="Concluídas" radius={[8, 8, 0, 0]} />
                <Bar dataKey="pending" fill="#f59e0b" name="Pendentes" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Monthly Trend */}
        <Card className="col-span-full lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg md:text-xl">Tendência Mensal</CardTitle>
            <p className="text-xs md:text-sm text-muted-foreground">
              Total de tarefas concluídas por mês
            </p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="month" className="text-xs" />
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
                  dataKey="tasks"
                  stroke="#3b82f6"
                  strokeWidth={3}
                  name="Tarefas"
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Big Rocks Distribution */}
        <Card className="col-span-full lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg md:text-xl">Distribuição por Big Rock</CardTitle>
            <p className="text-xs md:text-sm text-muted-foreground">
              Tempo dedicado a cada área
            </p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={bigRocksData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(Number(percent) * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {bigRocksData.map((entry, index) => (
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
          </CardContent>
        </Card>

        {/* Cycle Analysis */}
        <Card className="col-span-full lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg md:text-xl">Análise do Ciclo Menstrual</CardTitle>
            <p className="text-xs md:text-sm text-muted-foreground">
              Produtividade por fase do ciclo
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Fase Folicular</span>
                  <span className="text-sm text-muted-foreground">92% produtividade</span>
                </div>
                <div className="relative h-2 bg-secondary/20 rounded-full overflow-hidden">
                  <div
                    className="absolute top-0 left-0 h-full bg-pink-500 transition-all"
                    style={{ width: '92%' }}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Ovulação</span>
                  <span className="text-sm text-muted-foreground">95% produtividade</span>
                </div>
                <div className="relative h-2 bg-secondary/20 rounded-full overflow-hidden">
                  <div
                    className="absolute top-0 left-0 h-full bg-pink-600 transition-all"
                    style={{ width: '95%' }}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Fase Lútea</span>
                  <span className="text-sm text-muted-foreground">78% produtividade</span>
                </div>
                <div className="relative h-2 bg-secondary/20 rounded-full overflow-hidden">
                  <div
                    className="absolute top-0 left-0 h-full bg-pink-400 transition-all"
                    style={{ width: '78%' }}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Menstruação</span>
                  <span className="text-sm text-muted-foreground">65% produtividade</span>
                </div>
                <div className="relative h-2 bg-secondary/20 rounded-full overflow-hidden">
                  <div
                    className="absolute top-0 left-0 h-full bg-pink-300 transition-all"
                    style={{ width: '65%' }}
                  />
                </div>
              </div>

              <div className="mt-6 p-4 rounded-lg bg-pink-500/10 border border-pink-500/20">
                <div className="flex items-start gap-3">
                  <Calendar className="h-5 w-5 text-pink-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Fase Atual: Folicular</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Energia alta e foco aumentado. Ótimo momento para tarefas complexas!
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
