import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { attachmentsService, type Attachment } from '@/services/attachmentsService';
import { LoadingState } from './LoadingState';
import {
  FileAudio,
  FileImage,
  TrendingUp,
  Calendar,
  Clock,
  BarChart3,
} from 'lucide-react';
import { format, startOfWeek, startOfMonth, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface MultimodalStats {
  totalAttachments: number;
  audioCount: number;
  imageCount: number;
  thisWeek: number;
  thisMonth: number;
  averagePerDay: number;
  mostActiveDay: string;
  recentActivity: {
    date: string;
    count: number;
  }[];
}

export const MultimodalAnalytics = () => {
  const [stats, setStats] = useState<MultimodalStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const data = await attachmentsService.getAllAttachments({ limit: 500 });
      setAttachments(data);
      calculateStats(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (data: Attachment[]) => {
    if (data.length === 0) {
      setStats({
        totalAttachments: 0,
        audioCount: 0,
        imageCount: 0,
        thisWeek: 0,
        thisMonth: 0,
        averagePerDay: 0,
        mostActiveDay: '—',
        recentActivity: [],
      });
      return;
    }

    const now = new Date();
    const weekStart = startOfWeek(now, { locale: ptBR });
    const monthStart = startOfMonth(now);

    // Count by type
    const audioCount = data.filter((a) => a.file_type === 'audio').length;
    const imageCount = data.filter((a) => a.file_type === 'image').length;

    // Count this week and month
    const thisWeek = data.filter(
      (a) => parseISO(a.created_at) >= weekStart
    ).length;
    const thisMonth = data.filter(
      (a) => parseISO(a.created_at) >= monthStart
    ).length;

    // Calculate average per day (last 30 days)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const last30Days = data.filter(
      (a) => parseISO(a.created_at) >= thirtyDaysAgo
    );
    const averagePerDay = last30Days.length / 30;

    // Find most active day
    const dayCount: Record<string, number> = {};
    data.forEach((a) => {
      const day = format(parseISO(a.created_at), 'EEEE', { locale: ptBR });
      dayCount[day] = (dayCount[day] || 0) + 1;
    });
    const mostActiveDay =
      Object.entries(dayCount).sort((a, b) => b[1] - a[1])[0]?.[0] || '—';

    // Recent activity (last 7 days)
    const last7Days: { date: string; count: number }[] = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = format(date, 'dd/MM');

      const count = data.filter((a) => {
        const attachmentDate = parseISO(a.created_at);
        return (
          attachmentDate.getDate() === date.getDate() &&
          attachmentDate.getMonth() === date.getMonth() &&
          attachmentDate.getFullYear() === date.getFullYear()
        );
      }).length;

      last7Days.push({ date: dateStr, count });
    }

    setStats({
      totalAttachments: data.length,
      audioCount,
      imageCount,
      thisWeek,
      thisMonth,
      averagePerDay: Math.round(averagePerDay * 10) / 10,
      mostActiveDay,
      recentActivity: last7Days,
    });
  };

  if (loading) {
    return <LoadingState message="Carregando analytics..." variant="card" />;
  }

  if (!stats) {
    return null;
  }

  const maxActivity = Math.max(...stats.recentActivity.map((a) => a.count), 1);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Multimodal Analytics</h2>
        <p className="text-muted-foreground mt-1">
          Estatísticas de uso de transcrições de áudio e análise de imagens.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total</p>
                <h3 className="text-2xl font-bold">{stats.totalAttachments}</h3>
                <p className="text-xs text-muted-foreground mt-1">anexos processados</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-blue-500/10 flex items-center justify-center">
                <BarChart3 className="h-6 w-6 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Audio */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Áudios</p>
                <h3 className="text-2xl font-bold">{stats.audioCount}</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  {stats.totalAttachments > 0
                    ? `${Math.round((stats.audioCount / stats.totalAttachments) * 100)}%`
                    : '0%'}{' '}
                  do total
                </p>
              </div>
              <div className="h-12 w-12 rounded-full bg-purple-500/10 flex items-center justify-center">
                <FileAudio className="h-6 w-6 text-purple-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Images */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Imagens</p>
                <h3 className="text-2xl font-bold">{stats.imageCount}</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  {stats.totalAttachments > 0
                    ? `${Math.round((stats.imageCount / stats.totalAttachments) * 100)}%`
                    : '0%'}{' '}
                  do total
                </p>
              </div>
              <div className="h-12 w-12 rounded-full bg-green-500/10 flex items-center justify-center">
                <FileImage className="h-6 w-6 text-green-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Average */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Média/Dia</p>
                <h3 className="text-2xl font-bold">{stats.averagePerDay}</h3>
                <p className="text-xs text-muted-foreground mt-1">últimos 30 dias</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-orange-500/10 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-orange-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Activity Chart and Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">Atividade Recente (7 dias)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {stats.recentActivity.map((day, index) => (
                <div key={index} className="flex items-center gap-3">
                  <span className="text-sm text-muted-foreground w-12">{day.date}</span>
                  <div className="flex-1 h-8 bg-muted rounded-md overflow-hidden">
                    <div
                      className="h-full bg-primary/80 transition-all"
                      style={{
                        width: `${(day.count / maxActivity) * 100}%`,
                        minWidth: day.count > 0 ? '2%' : '0',
                      }}
                    />
                  </div>
                  <span className="text-sm font-medium w-8 text-right">{day.count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Insights</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="h-10 w-10 rounded-full bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                <Calendar className="h-5 w-5 text-blue-500" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">Esta Semana</p>
                <p className="text-2xl font-bold">{stats.thisWeek}</p>
                <p className="text-xs text-muted-foreground">anexos processados</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="h-10 w-10 rounded-full bg-purple-500/10 flex items-center justify-center flex-shrink-0">
                <Calendar className="h-5 w-5 text-purple-500" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">Este Mês</p>
                <p className="text-2xl font-bold">{stats.thisMonth}</p>
                <p className="text-xs text-muted-foreground">anexos processados</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="h-10 w-10 rounded-full bg-green-500/10 flex items-center justify-center flex-shrink-0">
                <Clock className="h-5 w-5 text-green-500" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">Dia Mais Ativo</p>
                <p className="text-lg font-bold capitalize">{stats.mostActiveDay}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
