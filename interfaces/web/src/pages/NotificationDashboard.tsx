import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { notificationStatsService } from '@/services/notificationStatsService';
import type { PatternInsightsResponse, DigestAPI } from '@/services/notificationStatsService';
import { notificationService } from '@/services/notificationService';
import { notificationSourcesService } from '@/services/notificationSourcesService';
import { notificationRulesService } from '@/services/notificationRulesService';
import {
  BarChart,
  Bell,
  BellOff,
  TrendingUp,
  TrendingDown,
  Zap,
  Database,
  FileText,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function NotificationDashboard() {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [generatingDigest, setGeneratingDigest] = useState<string | null>(null);

  // Stats
  const [totalNotifications, setTotalNotifications] = useState(0);
  const [unreadCount, setUnreadCount] = useState(0);
  const [sourcesCount, setSourcesCount] = useState(0);
  const [rulesCount, setRulesCount] = useState(0);
  const [patternInsights, setPatternInsights] = useState<PatternInsightsResponse | null>(null);

  // Digests
  const [dailyDigest, setDailyDigest] = useState<DigestAPI | null>(null);
  const [weeklyDigest, setWeeklyDigest] = useState<DigestAPI | null>(null);
  const [monthlyDigest, setMonthlyDigest] = useState<DigestAPI | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load all dashboard data in parallel
      const [notifs, sources, rules, insights, daily, weekly, monthly] = await Promise.all([
        notificationService.getNotifications(),
        notificationSourcesService.getSources(),
        notificationRulesService.getRules(),
        notificationStatsService.getPatternInsights(),
        notificationStatsService.getLatestDigest('daily'),
        notificationStatsService.getLatestDigest('weekly'),
        notificationStatsService.getLatestDigest('monthly'),
      ]);

      setTotalNotifications(notifs.total);
      setUnreadCount(notifs.unread_count);
      setSourcesCount(sources.total);
      setRulesCount(rules.total);
      setPatternInsights(insights);
      setDailyDigest(daily);
      setWeeklyDigest(weekly);
      setMonthlyDigest(monthly);
    } catch (error) {
      console.error('Error loading dashboard:', error);
      toast({
        title: 'Erro ao carregar',
        description: 'Não foi possível carregar os dados do dashboard',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateDigest = async (digestType: 'daily' | 'weekly' | 'monthly') => {
    setGeneratingDigest(digestType);
    try {
      const digest = await notificationStatsService.generateDigest(digestType);

      // Update state
      if (digestType === 'daily') setDailyDigest(digest);
      else if (digestType === 'weekly') setWeeklyDigest(digest);
      else setMonthlyDigest(digest);

      toast({
        title: 'Resumo gerado',
        description: `Resumo ${digestType === 'daily' ? 'diário' : digestType === 'weekly' ? 'semanal' : 'mensal'} criado com sucesso`,
      });
    } catch (error) {
      toast({
        title: 'Erro ao gerar',
        description: 'Não foi possível gerar o resumo',
        variant: 'destructive',
      });
    } finally {
      setGeneratingDigest(null);
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
          <p className="text-muted-foreground">Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard de Notificações</h1>
        <p className="mt-2 text-muted-foreground">
          Visão geral e insights sobre suas notificações
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Notificações</CardTitle>
            <Bell className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalNotifications}</div>
            <p className="text-xs text-muted-foreground">
              {unreadCount} não lidas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Fontes Conectadas</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{sourcesCount}</div>
            <p className="text-xs text-muted-foreground">
              Coletando automaticamente
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Regras Ativas</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{rulesCount}</div>
            <p className="text-xs text-muted-foreground">
              Automações configuradas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Padrões Aprendidos</CardTitle>
            <Sparkles className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{patternInsights?.total_patterns || 0}</div>
            <p className="text-xs text-muted-foreground">
              {patternInsights?.average_confidence
                ? `${(patternInsights.average_confidence * 100).toFixed(0)}% confiança média`
                : 'Nenhum padrão ainda'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Pattern Insights */}
      {patternInsights && patternInsights.total_patterns > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Padrões Mais Confiáveis
              </CardTitle>
              <CardDescription>
                Padrões identificados com maior confiança pela IA
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {patternInsights.most_confident_patterns.map((pattern, index) => (
                  <div key={index} className="flex items-center justify-between rounded-lg border p-3">
                    <div className="flex-1">
                      <div className="font-medium">{pattern.pattern_key}</div>
                      <div className="text-sm text-muted-foreground">
                        {pattern.pattern_type} • {pattern.frequency} ocorrências
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-green-600">
                        {(pattern.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart className="h-5 w-5" />
                Padrões Mais Frequentes
              </CardTitle>
              <CardDescription>
                Padrões que aparecem com mais frequência
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {patternInsights.most_frequent_patterns.map((pattern, index) => (
                  <div key={index} className="flex items-center justify-between rounded-lg border p-3">
                    <div className="flex-1">
                      <div className="font-medium">{pattern.pattern_key}</div>
                      <div className="text-sm text-muted-foreground">
                        {pattern.pattern_type} • {(pattern.confidence * 100).toFixed(0)}% confiança
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-blue-600">
                        {pattern.frequency}x
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Digests */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Resumos Inteligentes
          </CardTitle>
          <CardDescription>
            Resumos gerados por IA das suas notificações
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="daily" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="daily">Diário</TabsTrigger>
              <TabsTrigger value="weekly">Semanal</TabsTrigger>
              <TabsTrigger value="monthly">Mensal</TabsTrigger>
            </TabsList>

            <TabsContent value="daily" className="space-y-4">
              {dailyDigest ? (
                <div className="rounded-lg border p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <div className="text-sm text-muted-foreground">
                      {new Date(dailyDigest.start_date).toLocaleDateString('pt-BR')} -{' '}
                      {new Date(dailyDigest.end_date).toLocaleDateString('pt-BR')}
                    </div>
                    <div className="text-sm font-medium">
                      {dailyDigest.notification_count} notificações
                    </div>
                  </div>
                  <div className="whitespace-pre-wrap text-sm">{dailyDigest.summary}</div>
                </div>
              ) : (
                <div className="py-8 text-center text-muted-foreground">
                  <FileText className="mx-auto mb-4 h-12 w-12 opacity-50" />
                  <p>Nenhum resumo diário disponível</p>
                </div>
              )}
              <Button
                onClick={() => handleGenerateDigest('daily')}
                disabled={generatingDigest === 'daily'}
                className="w-full"
              >
                {generatingDigest === 'daily' ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Gerando...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Gerar Resumo Diário
                  </>
                )}
              </Button>
            </TabsContent>

            <TabsContent value="weekly" className="space-y-4">
              {weeklyDigest ? (
                <div className="rounded-lg border p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <div className="text-sm text-muted-foreground">
                      {new Date(weeklyDigest.start_date).toLocaleDateString('pt-BR')} -{' '}
                      {new Date(weeklyDigest.end_date).toLocaleDateString('pt-BR')}
                    </div>
                    <div className="text-sm font-medium">
                      {weeklyDigest.notification_count} notificações
                    </div>
                  </div>
                  <div className="whitespace-pre-wrap text-sm">{weeklyDigest.summary}</div>
                </div>
              ) : (
                <div className="py-8 text-center text-muted-foreground">
                  <FileText className="mx-auto mb-4 h-12 w-12 opacity-50" />
                  <p>Nenhum resumo semanal disponível</p>
                </div>
              )}
              <Button
                onClick={() => handleGenerateDigest('weekly')}
                disabled={generatingDigest === 'weekly'}
                className="w-full"
              >
                {generatingDigest === 'weekly' ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Gerando...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Gerar Resumo Semanal
                  </>
                )}
              </Button>
            </TabsContent>

            <TabsContent value="monthly" className="space-y-4">
              {monthlyDigest ? (
                <div className="rounded-lg border p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <div className="text-sm text-muted-foreground">
                      {new Date(monthlyDigest.start_date).toLocaleDateString('pt-BR')} -{' '}
                      {new Date(monthlyDigest.end_date).toLocaleDateString('pt-BR')}
                    </div>
                    <div className="text-sm font-medium">
                      {monthlyDigest.notification_count} notificações
                    </div>
                  </div>
                  <div className="whitespace-pre-wrap text-sm">{monthlyDigest.summary}</div>
                </div>
              ) : (
                <div className="py-8 text-center text-muted-foreground">
                  <FileText className="mx-auto mb-4 h-12 w-12 opacity-50" />
                  <p>Nenhum resumo mensal disponível</p>
                </div>
              )}
              <Button
                onClick={() => handleGenerateDigest('monthly')}
                disabled={generatingDigest === 'monthly'}
                className="w-full"
              >
                {generatingDigest === 'monthly' ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Gerando...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Gerar Resumo Mensal
                  </>
                )}
              </Button>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
