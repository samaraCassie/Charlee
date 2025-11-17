import { useState, useEffect } from 'react';
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
import { analyticsService } from '@/services/analyticsService';
import { useCycleStore } from '@/stores/cycleStore';
import { MultimodalAnalytics } from '@/components/MultimodalAnalytics';
import type {
  WeeklyStats,
  MonthlyStats,
  BigRockDistribution,
  ProductivityStats,
  CycleProductivity,
} from '@/services/analyticsService';

export default function Analytics() {
  const [weeklyData, setWeeklyData] = useState<WeeklyStats[]>([]);
  const [monthlyData, setMonthlyData] = useState<MonthlyStats[]>([]);
  const [bigRocksData, setBigRocksData] = useState<BigRockDistribution[]>([]);
  const [productivityStats, setProductivityStats] = useState<ProductivityStats | null>(null);
  const [cycleProductivity, setCycleProductivity] = useState<CycleProductivity | null>(null);
  const [loading, setLoading] = useState(true);

  const { currentPhase, getCurrentPhase } = useCycleStore();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [weekly, monthly, bigRocks, productivity, cycle] = await Promise.all([
          analyticsService.getWeeklyStats(),
          analyticsService.getMonthlyStats(),
          analyticsService.getBigRocksDistribution(),
          analyticsService.getProductivityStats(),
          analyticsService.getCycleProductivity(),
        ]);

        setWeeklyData(weekly);
        setMonthlyData(monthly);
        setBigRocksData(bigRocks);
        setProductivityStats(productivity);
        setCycleProductivity(cycle);
      } catch (error) {
        console.error('Error fetching analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    getCurrentPhase();
  }, [getCurrentPhase]);

  const stats = productivityStats
    ? [
        {
          label: 'Taxa de Conclusão',
          value: `${productivityStats.completion_rate.toFixed(0)}%`,
          icon: CheckCircle2,
          color: 'text-green-500',
        },
        {
          label: 'Tempo Médio/Tarefa',
          value: `${productivityStats.avg_time_per_task.toFixed(1)}h`,
          icon: Clock,
          color: 'text-blue-500',
        },
        {
          label: 'Produtividade',
          value: `${productivityStats.productivity_trend > 0 ? '+' : ''}${productivityStats.productivity_trend.toFixed(0)}%`,
          icon: TrendingUp,
          color: 'text-teal-500',
        },
        {
          label: 'Tarefas Atrasadas',
          value: productivityStats.overdue_tasks.toString(),
          icon: Activity,
          color: 'text-orange-500',
        },
      ]
    : [];

  const phaseLabels: { [key: string]: string } = {
    menstrual: 'Menstruação',
    follicular: 'Fase Folicular',
    ovulation: 'Ovulação',
    luteal: 'Fase Lútea',
  };

  const phaseRecommendations: { [key: string]: string } = {
    menstrual: 'Energia reduzida. Foque em descanso e tarefas leves.',
    follicular: 'Energia alta e foco aumentado. Ótimo momento para tarefas complexas!',
    ovulation: 'Pico de energia e clareza mental. Aproveite para projetos importantes!',
    luteal: 'Energia em declínio. Priorize finalização de tarefas existentes.',
  };

  if (loading) {
    return (
      <div className="space-y-6 md:space-y-8">
        <div>
          <h1 className="text-2xl md:text-4xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground mt-1 md:mt-2 text-sm md:text-base">
            Visualize seu desempenho e produtividade ao longo do tempo.
          </p>
        </div>
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">Carregando analytics...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

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
                  data={bigRocksData.map(item => ({ ...item }))}
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
            {cycleProductivity ? (
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Fase Folicular</span>
                    <span className="text-sm text-muted-foreground">
                      {cycleProductivity.follicular.toFixed(0)}% produtividade
                    </span>
                  </div>
                  <div className="relative h-2 bg-secondary/20 rounded-full overflow-hidden">
                    <div
                      className="absolute top-0 left-0 h-full bg-pink-500 transition-all"
                      style={{ width: `${cycleProductivity.follicular}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Ovulação</span>
                    <span className="text-sm text-muted-foreground">
                      {cycleProductivity.ovulation.toFixed(0)}% produtividade
                    </span>
                  </div>
                  <div className="relative h-2 bg-secondary/20 rounded-full overflow-hidden">
                    <div
                      className="absolute top-0 left-0 h-full bg-pink-600 transition-all"
                      style={{ width: `${cycleProductivity.ovulation}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Fase Lútea</span>
                    <span className="text-sm text-muted-foreground">
                      {cycleProductivity.luteal.toFixed(0)}% produtividade
                    </span>
                  </div>
                  <div className="relative h-2 bg-secondary/20 rounded-full overflow-hidden">
                    <div
                      className="absolute top-0 left-0 h-full bg-pink-400 transition-all"
                      style={{ width: `${cycleProductivity.luteal}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Menstruação</span>
                    <span className="text-sm text-muted-foreground">
                      {cycleProductivity.menstrual.toFixed(0)}% produtividade
                    </span>
                  </div>
                  <div className="relative h-2 bg-secondary/20 rounded-full overflow-hidden">
                    <div
                      className="absolute top-0 left-0 h-full bg-pink-300 transition-all"
                      style={{ width: `${cycleProductivity.menstrual}%` }}
                    />
                  </div>
                </div>

                <div className="mt-6 p-4 rounded-lg bg-pink-500/10 border border-pink-500/20">
                  <div className="flex items-start gap-3">
                    <Calendar className="h-5 w-5 text-pink-500 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">
                        Fase Atual: {phaseLabels[currentPhase] || 'N/A'}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {phaseRecommendations[currentPhase] || 'Acompanhe seu ciclo para insights personalizados.'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <p>Dados de ciclo não disponíveis</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Multimodal Analytics */}
      <div className="pt-8 border-t">
        <MultimodalAnalytics />
      </div>
    </div>
  );
}
