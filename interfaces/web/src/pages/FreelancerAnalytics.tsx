import { useEffect } from 'react';
import { useFreelancerStore } from '../stores/freelancerStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import {
  TrendingUp,
  DollarSign,
  Target,
  Award,
  BarChart3,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Activity,
} from 'lucide-react';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function FreelancerAnalytics() {
  const { careerInsights, learningPerformance, fetchCareerInsights, fetchLearningPerformance, loading } =
    useFreelancerStore();

  useEffect(() => {
    fetchCareerInsights();
    fetchLearningPerformance();
  }, []);

  const handleRefresh = () => {
    fetchCareerInsights();
    fetchLearningPerformance();
  };

  if (loading && !careerInsights) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-4">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
          <p className="text-muted-foreground">Carregando analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics Freelancer</h1>
          <p className="text-muted-foreground">Insights de carreira e performance dos componentes de aprendizado</p>
        </div>
        <Button onClick={handleRefresh} disabled={loading}>
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {/* Career Insights */}
      {careerInsights && (
        <>
          {/* Overview Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total de Oportunidades</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{careerInsights.total_opportunities}</div>
                <p className="text-xs text-muted-foreground">
                  {careerInsights.total_accepted} aceitas · {careerInsights.total_rejected} rejeitadas
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Taxa de Aceitação</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{(careerInsights.acceptance_rate * 100).toFixed(1)}%</div>
                <p className="text-xs text-muted-foreground">
                  {careerInsights.total_accepted} de {careerInsights.total_opportunities}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Receita Total</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${careerInsights.total_revenue.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">
                  Média: ${careerInsights.avg_project_value.toFixed(0)}/projeto
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Taxa Horária Média</CardTitle>
                <Award className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${careerInsights.avg_hourly_rate.toFixed(0)}/h</div>
                <p className="text-xs text-muted-foreground">Calculado dos projetos aceitos</p>
              </CardContent>
            </Card>
          </div>

          {/* Revenue Trends */}
          {careerInsights.revenue_by_month && careerInsights.revenue_by_month.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Tendência de Receita</CardTitle>
                <CardDescription>Receita e número de projetos por mês</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={careerInsights.revenue_by_month}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="revenue"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      name="Receita ($)"
                    />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="projects"
                      stroke="#10b981"
                      strokeWidth={2}
                      name="Projetos"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          <div className="grid gap-6 md:grid-cols-2">
            {/* Top Skills */}
            {careerInsights.top_skills && careerInsights.top_skills.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Top Skills</CardTitle>
                  <CardDescription>Skills mais demandadas e lucrativas</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {careerInsights.top_skills.slice(0, 5).map((skill, index) => (
                      <div key={skill.skill} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary">{index + 1}</Badge>
                            <span className="font-medium">{skill.skill}</span>
                          </div>
                          <span className="text-sm font-semibold text-green-600">${skill.avg_value.toFixed(0)}</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <div className="flex-1 bg-secondary rounded-full h-2">
                            <div
                              className="bg-primary rounded-full h-2"
                              style={{
                                width: `${(skill.count / careerInsights.top_skills[0].count) * 100}%`,
                              }}
                            />
                          </div>
                          <span>{skill.count} projetos</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Top Platforms */}
            {careerInsights.top_platforms && careerInsights.top_platforms.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Top Plataformas</CardTitle>
                  <CardDescription>Receita por plataforma</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={careerInsights.top_platforms}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name}: $${Number(value).toFixed(0)}`}
                        nameKey="platform"
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="revenue"
                      >
                        {careerInsights.top_platforms.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="mt-4 space-y-2">
                    {careerInsights.top_platforms.map((platform, index) => (
                      <div key={platform.platform} className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                          <span>{platform.platform}</span>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-muted-foreground">{platform.count} projetos</span>
                          <span className="font-semibold">${platform.revenue.toFixed(0)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </>
      )}

      {/* Learning Components Performance */}
      {learningPerformance && (
        <>
          <div className="border-t pt-6">
            <h2 className="text-2xl font-bold mb-4">Performance dos Componentes de Aprendizado</h2>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {/* Pricing Accuracy */}
            {learningPerformance.pricing_accuracy && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <DollarSign className="h-5 w-5" />
                    Pricing Accuracy
                  </CardTitle>
                  <CardDescription>Precisão da precificação automática</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-muted-foreground">Accuracy Score</span>
                      <Badge
                        variant={
                          learningPerformance.pricing_accuracy.avg_accuracy_score >= 0.75
                            ? 'success'
                            : learningPerformance.pricing_accuracy.avg_accuracy_score >= 0.5
                            ? 'warning'
                            : 'destructive'
                        }
                      >
                        {(learningPerformance.pricing_accuracy.avg_accuracy_score * 100).toFixed(1)}%
                      </Badge>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          learningPerformance.pricing_accuracy.avg_accuracy_score >= 0.75
                            ? 'bg-green-500'
                            : learningPerformance.pricing_accuracy.avg_accuracy_score >= 0.5
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{
                          width: `${learningPerformance.pricing_accuracy.avg_accuracy_score * 100}%`,
                        }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Margem de Erro Média</span>
                    <span className="font-semibold">
                      {(learningPerformance.pricing_accuracy.avg_error_margin * 100).toFixed(1)}%
                    </span>
                  </div>

                  {learningPerformance.pricing_accuracy.needs_adjustment && (
                    <div className="flex items-center gap-2 text-yellow-600 text-sm">
                      <AlertTriangle className="h-4 w-4" />
                      <span>Ajuste recomendado</span>
                    </div>
                  )}

                  {!learningPerformance.pricing_accuracy.needs_adjustment && (
                    <div className="flex items-center gap-2 text-green-600 text-sm">
                      <CheckCircle className="h-4 w-4" />
                      <span>Performance ótima</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Rejection Patterns */}
            {learningPerformance.rejection_patterns && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5" />
                    Rejection Patterns
                  </CardTitle>
                  <CardDescription>Análise de padrões de rejeição</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Taxa de Rejeição</span>
                    <span className="text-2xl font-bold text-red-600">
                      {(learningPerformance.rejection_patterns.rejection_rate * 100).toFixed(1)}%
                    </span>
                  </div>

                  <div className="space-y-2">
                    <p className="text-sm font-medium">Top Red Flags:</p>
                    {learningPerformance.rejection_patterns.high_risk_flags.slice(0, 3).map((flag) => (
                      <div key={flag.flag} className="flex items-center justify-between text-sm">
                        <Badge variant="destructive" className="text-xs">
                          {flag.flag}
                        </Badge>
                        <span className="text-muted-foreground">
                          {(flag.rejection_probability * 100).toFixed(0)}% rejeição
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="text-xs text-muted-foreground">
                    {learningPerformance.rejection_patterns.rejected_count} de{' '}
                    {learningPerformance.rejection_patterns.total_opportunities} oportunidades rejeitadas
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Hourly Rate Optimization */}
            {learningPerformance.hourly_rate_optimization && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Hourly Rate Optimization
                  </CardTitle>
                  <CardDescription>Otimização da taxa horária</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Taxa Sugerida</p>
                    <p className="text-2xl font-bold text-green-600">
                      ${learningPerformance.hourly_rate_optimization.suggested_rate.toFixed(0)}/h
                    </p>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Faixa Ótima</span>
                    <Badge variant="info">{learningPerformance.hourly_rate_optimization.optimal_range}</Badge>
                  </div>

                  {learningPerformance.hourly_rate_optimization.current_acceptance_rate > 0 && (
                    <div>
                      <div className="flex items-center justify-between mb-2 text-sm">
                        <span className="text-muted-foreground">Taxa de Aceitação Atual</span>
                        <span className="font-semibold">
                          {(learningPerformance.hourly_rate_optimization.current_acceptance_rate * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-secondary rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{
                            width: `${learningPerformance.hourly_rate_optimization.current_acceptance_rate * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  )}

                  <div className="flex items-center gap-2 text-blue-600 text-sm">
                    <Activity className="h-4 w-4" />
                    <span>Baseado em dados reais</span>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </>
      )}

      {/* Empty State */}
      {!careerInsights && !learningPerformance && !loading && (
        <Card>
          <CardContent className="pt-6 text-center">
            <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground mb-4">Nenhum dado disponível ainda</p>
            <p className="text-sm text-muted-foreground">Adicione e processe algumas oportunidades para ver os analytics</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
