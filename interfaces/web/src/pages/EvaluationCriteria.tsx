import { useEffect, useState } from 'react';
import { useFreelancerStore } from '../stores/freelancerStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Settings, Shield, Save, RotateCcw, TrendingDown, TrendingUp, AlertCircle, Trash2, Plus, HelpCircle } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const SCORE_WEIGHT_LABELS: Record<string, { label: string; help: string }> = {
  viability: {
    label: 'Viabilidade',
    help: 'Avalia se o projeto é viável financeiramente: orçamento adequado, prazo realista, escopo claro. Quanto maior o peso, mais o sistema prioriza projetos com boa relação custo-benefício.',
  },
  alignment: {
    label: 'Alinhamento',
    help: 'Mede o quanto o projeto se alinha com suas habilidades e experiência. Peso maior significa que o sistema favorece projetos na sua área de expertise.',
  },
  strategic: {
    label: 'Estratégico',
    help: 'Considera o valor estratégico: potencial de recorrência, visibilidade, aprendizado de novas tecnologias. Peso maior prioriza crescimento profissional a longo prazo.',
  },
};

export default function EvaluationCriteria() {
  const {
    evaluationCriteria,
    fetchEvaluationCriteria,
    updateEvaluationCriteria,
    optimizeEvaluationCriteria,
    loading,
  } = useFreelancerStore();
  const { toast } = useToast();

  const [formData, setFormData] = useState<any>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [showAddRedFlag, setShowAddRedFlag] = useState(false);
  const [showAddGreenFlag, setShowAddGreenFlag] = useState(false);
  const [newRedFlag, setNewRedFlag] = useState({ id: '', name: '', weight: -15, severity: 'medium' as string, keywords: '' });
  const [newGreenFlag, setNewGreenFlag] = useState({ id: '', name: '', weight: 10, keywords: '' });
  const [optimizing, setOptimizing] = useState(false);
  const [expandedHelp, setExpandedHelp] = useState<string | null>(null);

  useEffect(() => {
    fetchEvaluationCriteria();
  }, []);

  useEffect(() => {
    if (evaluationCriteria && !formData) {
      setFormData({
        minimum_risk_score: evaluationCriteria.minimum_risk_score,
        minimum_final_score: evaluationCriteria.minimum_final_score,
        risk_tolerance: evaluationCriteria.risk_tolerance,
        auto_adjust_enabled: evaluationCriteria.auto_adjust_enabled,
        score_weights: { ...evaluationCriteria.score_weights },
        red_flags: { ...evaluationCriteria.red_flags },
        green_flags: { ...evaluationCriteria.green_flags },
      });
    }
  }, [evaluationCriteria]);

  const handleChange = (field: string, value: any) => {
    setFormData({ ...formData, [field]: value });
    setHasChanges(true);
  };

  const handleScoreWeightChange = (key: string, value: string) => {
    const numValue = parseFloat(value);
    setFormData({
      ...formData,
      score_weights: {
        ...formData.score_weights,
        [key]: isNaN(numValue) ? 0 : numValue,
      },
    });
    setHasChanges(true);
  };

  const handleFlagWeightChange = (flagType: 'red_flags' | 'green_flags', flagId: string, value: string) => {
    const numValue = parseFloat(value);
    setFormData({
      ...formData,
      [flagType]: {
        ...formData[flagType],
        [flagId]: {
          ...formData[flagType][flagId],
          weight: isNaN(numValue) ? 0 : numValue,
        },
      },
    });
    setHasChanges(true);
  };

  const handleAddRedFlag = () => {
    if (!newRedFlag.id.trim() || !newRedFlag.name.trim()) return;
    const flagKey = newRedFlag.id.trim().toLowerCase().replace(/\s+/g, '_');
    if (formData.red_flags[flagKey]) {
      toast({ title: 'Erro', description: `Flag "${flagKey}" já existe.`, variant: 'destructive' });
      return;
    }
    const flag: any = {
      name: newRedFlag.name.trim(),
      weight: newRedFlag.weight,
      severity: newRedFlag.severity,
    };
    if (newRedFlag.keywords.trim()) {
      flag.keywords = newRedFlag.keywords.split(',').map((k: string) => k.trim()).filter(Boolean);
    }
    setFormData({
      ...formData,
      red_flags: { ...formData.red_flags, [flagKey]: flag },
    });
    setHasChanges(true);
    setShowAddRedFlag(false);
    setNewRedFlag({ id: '', name: '', weight: -15, severity: 'medium', keywords: '' });
  };

  const handleAddGreenFlag = () => {
    if (!newGreenFlag.id.trim() || !newGreenFlag.name.trim()) return;
    const flagKey = newGreenFlag.id.trim().toLowerCase().replace(/\s+/g, '_');
    if (formData.green_flags[flagKey]) {
      toast({ title: 'Erro', description: `Flag "${flagKey}" já existe.`, variant: 'destructive' });
      return;
    }
    const flag: any = {
      name: newGreenFlag.name.trim(),
      weight: newGreenFlag.weight,
    };
    if (newGreenFlag.keywords.trim()) {
      flag.keywords = newGreenFlag.keywords.split(',').map((k: string) => k.trim()).filter(Boolean);
    }
    setFormData({
      ...formData,
      green_flags: { ...formData.green_flags, [flagKey]: flag },
    });
    setHasChanges(true);
    setShowAddGreenFlag(false);
    setNewGreenFlag({ id: '', name: '', weight: 10, keywords: '' });
  };

  const handleRemoveFlag = (flagType: 'red_flags' | 'green_flags', flagId: string) => {
    const { [flagId]: _, ...rest } = formData[flagType];
    setFormData({ ...formData, [flagType]: rest });
    setHasChanges(true);
  };

  const handleOptimize = async () => {
    setOptimizing(true);
    try {
      const report = await optimizeEvaluationCriteria();
      if (report) {
        const isWarning = report.startsWith('⚠');
        toast({
          title: isWarning ? 'Aviso' : 'Auto-otimização concluída',
          description: report.length > 200 ? report.substring(0, 200) + '...' : report,
          variant: isWarning ? 'destructive' : 'default',
        });
        // Only reset form if optimization actually changed criteria
        if (!isWarning) {
          setFormData(null);
          setHasChanges(false);
        }
      }
    } catch {
      toast({
        title: 'Erro na otimização',
        description: 'Falha ao otimizar critérios. Verifique se há oportunidades analisadas suficientes.',
        variant: 'destructive',
      });
    } finally {
      setOptimizing(false);
    }
  };

  const handleSave = async () => {
    try {
      // Validate score weights sum to 1.0
      const totalWeight = Object.values(formData.score_weights).reduce((sum: number, val) => sum + (val as number), 0);
      if (Math.abs(totalWeight - 1.0) > 0.01) {
        toast({
          title: 'Erro de validação',
          description: `Os pesos devem somar 1.0. Soma atual: ${totalWeight.toFixed(2)}`,
          variant: 'destructive',
        });
        return;
      }

      await updateEvaluationCriteria(formData);
      setHasChanges(false);
      toast({
        title: 'Critérios salvos!',
        description: 'Seus critérios de avaliação foram atualizados.',
      });
    } catch (error: any) {
      toast({
        title: 'Erro ao salvar',
        description: error.message,
        variant: 'destructive',
      });
    }
  };

  const handleReset = () => {
    if (evaluationCriteria) {
      setFormData({
        minimum_risk_score: evaluationCriteria.minimum_risk_score,
        minimum_final_score: evaluationCriteria.minimum_final_score,
        risk_tolerance: evaluationCriteria.risk_tolerance,
        auto_adjust_enabled: evaluationCriteria.auto_adjust_enabled,
        score_weights: { ...evaluationCriteria.score_weights },
        red_flags: { ...evaluationCriteria.red_flags },
        green_flags: { ...evaluationCriteria.green_flags },
      });
      setHasChanges(false);
    }
  };

  const toggleHelp = (field: string) => {
    setExpandedHelp(expandedHelp === field ? null : field);
  };

  if (!formData || loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-muted-foreground">Carregando critérios...</p>
      </div>
    );
  }

  const totalWeight = Object.values(formData.score_weights).reduce((sum: number, val) => sum + (val as number), 0);
  const isWeightValid = Math.abs(totalWeight - 1.0) <= 0.01;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Shield className="h-8 w-8" />
            Critérios de Avaliação
          </h1>
          <p className="text-muted-foreground">Configure os critérios para avaliar risco e compatibilidade de oportunidades</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleOptimize} disabled={optimizing || loading}>
            <Settings className="h-4 w-4" />
            {optimizing ? 'Otimizando...' : 'Auto-Otimizar'}
          </Button>
          {hasChanges && (
            <>
              <Button variant="outline" onClick={handleReset}>
                <RotateCcw className="h-4 w-4" />
                Desfazer
              </Button>
              <Button onClick={handleSave} disabled={!isWeightValid}>
                <Save className="h-4 w-4" />
                Salvar Alterações
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Version Info */}
      {evaluationCriteria && (
        <Card className="border-blue-500">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Versão Atual</p>
                <p className="text-2xl font-bold">v{evaluationCriteria.version}</p>
              </div>
              <div className="flex gap-2">
                <Badge variant={evaluationCriteria.active ? 'success' : 'secondary'}>
                  {evaluationCriteria.active ? 'Ativo' : 'Inativo'}
                </Badge>
                <Badge variant={formData.risk_tolerance === 'conservative' ? 'default' : formData.risk_tolerance === 'aggressive' ? 'destructive' : 'secondary'}>
                  {formData.risk_tolerance === 'conservative' ? 'Conservador' : formData.risk_tolerance === 'aggressive' ? 'Agressivo' : 'Moderado'}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Basic Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Configuração Geral
          </CardTitle>
          <CardDescription>Limites e tolerância ao risco para a avaliação automática de oportunidades</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div>
              <div className="flex items-center gap-1 mb-2">
                <label className="text-sm font-medium">Score Mínimo de Risco</label>
                <button onClick={() => toggleHelp('min_risk')} className="text-muted-foreground hover:text-foreground">
                  <HelpCircle className="h-3.5 w-3.5" />
                </button>
              </div>
              {expandedHelp === 'min_risk' && (
                <p className="text-xs text-blue-600 dark:text-blue-400 mb-2 p-2 bg-blue-50 dark:bg-blue-950 rounded">
                  Score de risco do cliente (0-100). Oportunidades com score abaixo desse valor serão sinalizadas como arriscadas.
                  Ex: valor 40 significa que clientes com score de risco menor que 40 receberão alerta.
                </p>
              )}
              <Input
                type="number"
                value={formData.minimum_risk_score}
                onChange={(e) => handleChange('minimum_risk_score', parseFloat(e.target.value))}
                step="1"
                min="0"
                max="100"
              />
              <p className="text-xs text-muted-foreground mt-1">Mínimo aceitável (0-100)</p>
            </div>

            <div>
              <div className="flex items-center gap-1 mb-2">
                <label className="text-sm font-medium">Score Final Mínimo</label>
                <button onClick={() => toggleHelp('min_final')} className="text-muted-foreground hover:text-foreground">
                  <HelpCircle className="h-3.5 w-3.5" />
                </button>
              </div>
              {expandedHelp === 'min_final' && (
                <p className="text-xs text-blue-600 dark:text-blue-400 mb-2 p-2 bg-blue-50 dark:bg-blue-950 rounded">
                  Score final combinado (viabilidade + alinhamento + estratégico) necessário para que o sistema recomende aceitar a oportunidade.
                  Ex: valor 60 significa que apenas oportunidades com score final acima de 60 receberão recomendação de aceitação.
                </p>
              )}
              <Input
                type="number"
                value={formData.minimum_final_score}
                onChange={(e) => handleChange('minimum_final_score', parseFloat(e.target.value))}
                step="1"
                min="0"
                max="100"
              />
              <p className="text-xs text-muted-foreground mt-1">Para recomendar aceitação</p>
            </div>

            <div>
              <div className="flex items-center gap-1 mb-2">
                <label className="text-sm font-medium">Tolerância ao Risco</label>
                <button onClick={() => toggleHelp('risk_tolerance')} className="text-muted-foreground hover:text-foreground">
                  <HelpCircle className="h-3.5 w-3.5" />
                </button>
              </div>
              {expandedHelp === 'risk_tolerance' && (
                <p className="text-xs text-blue-600 dark:text-blue-400 mb-2 p-2 bg-blue-50 dark:bg-blue-950 rounded">
                  Define o perfil geral de aceitação de risco:
                  <strong> Conservador</strong> — rejeita projetos com qualquer sinal de alerta;
                  <strong> Moderado</strong> — aceita riscos médios se o retorno compensar;
                  <strong> Agressivo</strong> — aceita riscos maiores buscando maior retorno.
                </p>
              )}
              <select
                value={formData.risk_tolerance}
                onChange={(e) => handleChange('risk_tolerance', e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="conservative">Conservador</option>
                <option value="moderate">Moderado</option>
                <option value="aggressive">Agressivo</option>
              </select>
              <p className="text-xs text-muted-foreground mt-1">Perfil de aceitação de risco</p>
            </div>
          </div>

          <div className="flex items-start gap-2">
            <input
              type="checkbox"
              id="auto-adjust"
              checked={formData.auto_adjust_enabled}
              onChange={(e) => handleChange('auto_adjust_enabled', e.target.checked)}
              className="rounded mt-1"
            />
            <div>
              <label htmlFor="auto-adjust" className="text-sm font-medium cursor-pointer">
                Ativar auto-ajuste baseado em avaliações
              </label>
              <p className="text-xs text-muted-foreground">
                Quando ativado, o sistema ajusta automaticamente os pesos com base nas suas decisões de aceitar/rejeitar oportunidades
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Score Weights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Pesos dos Scores
            <button onClick={() => toggleHelp('weights_info')} className="text-muted-foreground hover:text-foreground">
              <HelpCircle className="h-4 w-4" />
            </button>
          </CardTitle>
          <CardDescription>
            Distribuição de importância entre dimensões {!isWeightValid && <span className="text-red-500">(devem somar 1.0 — atual: {totalWeight.toFixed(2)})</span>}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {expandedHelp === 'weights_info' && (
            <div className="text-xs text-blue-600 dark:text-blue-400 mb-4 p-3 bg-blue-50 dark:bg-blue-950 rounded">
              <p className="font-medium mb-1">Como os pesos funcionam:</p>
              <p>O score final de cada oportunidade é calculado como: <code className="bg-blue-100 dark:bg-blue-900 px-1 rounded">final = (viabilidade × peso) + (alinhamento × peso) + (estratégico × peso)</code></p>
              <p className="mt-1">A soma dos três pesos deve ser exatamente 1.0 (100%). Ajuste conforme o que é mais importante para você.</p>
            </div>
          )}
          <div className="grid gap-4 md:grid-cols-3">
            {Object.entries(formData.score_weights).map(([key, value]: [string, any]) => {
              const info = SCORE_WEIGHT_LABELS[key];
              return (
                <div key={key}>
                  <div className="flex items-center gap-1 mb-2">
                    <label className="text-sm font-medium">{info?.label || key}</label>
                    {info && (
                      <button onClick={() => toggleHelp(`weight_${key}`)} className="text-muted-foreground hover:text-foreground">
                        <HelpCircle className="h-3.5 w-3.5" />
                      </button>
                    )}
                  </div>
                  {expandedHelp === `weight_${key}` && info && (
                    <p className="text-xs text-blue-600 dark:text-blue-400 mb-2 p-2 bg-blue-50 dark:bg-blue-950 rounded">
                      {info.help}
                    </p>
                  )}
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      value={value}
                      onChange={(e) => handleScoreWeightChange(key, e.target.value)}
                      step="0.05"
                      min="0"
                      max="1"
                    />
                    <Badge variant="outline">{(value * 100).toFixed(0)}%</Badge>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Red Flags */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingDown className="h-5 w-5 text-red-600" />
            Red Flags (Sinais de Alerta)
            <button onClick={() => toggleHelp('red_flags_info')} className="text-muted-foreground hover:text-foreground">
              <HelpCircle className="h-4 w-4" />
            </button>
          </CardTitle>
          <CardDescription>Fatores negativos detectados na análise que reduzem o score de risco do cliente</CardDescription>
        </CardHeader>
        <CardContent>
          {expandedHelp === 'red_flags_info' && (
            <div className="text-xs text-blue-600 dark:text-blue-400 mb-4 p-3 bg-blue-50 dark:bg-blue-950 rounded">
              <p className="font-medium mb-1">Como Red Flags funcionam:</p>
              <p>Quando o sistema analisa uma oportunidade, busca padrões negativos no perfil do cliente e na descrição do projeto.
              Cada red flag detectada <strong>subtrai pontos</strong> do score de risco. Quanto mais negativo o peso, maior o impacto.</p>
              <ul className="mt-2 space-y-1 list-disc list-inside">
                <li><strong>Peso:</strong> Quantos pontos são subtraídos quando detectada (use valores negativos)</li>
                <li><strong>Severidade:</strong> Classifica a gravidade — critical e high recebem destaque visual</li>
                <li><strong>Keywords:</strong> Palavras-chave que ativam esta flag na análise automática</li>
              </ul>
            </div>
          )}
          <div className="grid gap-4 md:grid-cols-2">
            {Object.entries(formData.red_flags).map(([flagId, flag]: [string, any]) => (
              <div key={flagId} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-medium">{flag.name}</p>
                    <Badge variant={flag.severity === 'critical' ? 'destructive' : 'secondary'} className="text-xs mt-1">
                      {flag.severity === 'critical' ? 'Crítico' : flag.severity === 'high' ? 'Alto' : flag.severity === 'medium' ? 'Médio' : 'Baixo'}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      value={flag.weight}
                      onChange={(e) => handleFlagWeightChange('red_flags', flagId, e.target.value)}
                      className="w-24"
                      step="5"
                    />
                    <span className="text-sm text-muted-foreground">pts</span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-red-500 hover:text-red-700"
                      onClick={() => handleRemoveFlag('red_flags', flagId)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {!showAddRedFlag ? (
            <Button variant="outline" className="mt-4" onClick={() => setShowAddRedFlag(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Adicionar Red Flag
            </Button>
          ) : (
            <div className="border rounded-lg p-4 mt-4 space-y-3 bg-red-50 dark:bg-red-950">
              <p className="font-medium text-sm">Nova Red Flag</p>
              <div className="grid gap-3 md:grid-cols-2">
                <div>
                  <label className="text-xs font-medium block mb-1">ID (chave única)</label>
                  <Input
                    placeholder="ex: high_turnover"
                    value={newRedFlag.id}
                    onChange={(e) => setNewRedFlag({ ...newRedFlag, id: e.target.value })}
                  />
                  <p className="text-xs text-muted-foreground mt-1">Identificador interno, sem espaços</p>
                </div>
                <div>
                  <label className="text-xs font-medium block mb-1">Nome</label>
                  <Input
                    placeholder="ex: Alta Rotatividade"
                    value={newRedFlag.name}
                    onChange={(e) => setNewRedFlag({ ...newRedFlag, name: e.target.value })}
                  />
                  <p className="text-xs text-muted-foreground mt-1">Nome exibido na interface</p>
                </div>
                <div>
                  <label className="text-xs font-medium block mb-1">Peso (negativo)</label>
                  <Input
                    type="number"
                    value={newRedFlag.weight}
                    onChange={(e) => setNewRedFlag({ ...newRedFlag, weight: parseInt(e.target.value) || 0 })}
                    step="5"
                  />
                  <p className="text-xs text-muted-foreground mt-1">Pontos subtraídos do score</p>
                </div>
                <div>
                  <label className="text-xs font-medium block mb-1">Severidade</label>
                  <select
                    value={newRedFlag.severity}
                    onChange={(e) => setNewRedFlag({ ...newRedFlag, severity: e.target.value })}
                    className="w-full px-3 py-2 border rounded-md text-sm"
                  >
                    <option value="low">Baixo</option>
                    <option value="medium">Médio</option>
                    <option value="high">Alto</option>
                    <option value="critical">Crítico</option>
                  </select>
                  <p className="text-xs text-muted-foreground mt-1">Nível de gravidade do alerta</p>
                </div>
                <div className="md:col-span-2">
                  <label className="text-xs font-medium block mb-1">Palavras-chave (separadas por vírgula)</label>
                  <Input
                    placeholder="ex: turnover, rotating, multiple developers"
                    value={newRedFlag.keywords}
                    onChange={(e) => setNewRedFlag({ ...newRedFlag, keywords: e.target.value })}
                  />
                  <p className="text-xs text-muted-foreground mt-1">Termos que ativam esta flag automaticamente na análise</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={handleAddRedFlag}>Adicionar</Button>
                <Button size="sm" variant="outline" onClick={() => setShowAddRedFlag(false)}>Cancelar</Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Green Flags */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-600" />
            Green Flags (Sinais Positivos)
            <button onClick={() => toggleHelp('green_flags_info')} className="text-muted-foreground hover:text-foreground">
              <HelpCircle className="h-4 w-4" />
            </button>
          </CardTitle>
          <CardDescription>Fatores positivos detectados na análise que aumentam o score de confiança</CardDescription>
        </CardHeader>
        <CardContent>
          {expandedHelp === 'green_flags_info' && (
            <div className="text-xs text-blue-600 dark:text-blue-400 mb-4 p-3 bg-blue-50 dark:bg-blue-950 rounded">
              <p className="font-medium mb-1">Como Green Flags funcionam:</p>
              <p>Padrões positivos que <strong>adicionam pontos</strong> ao score de risco, indicando maior confiabilidade.
              Clientes com verificação, bom histórico ou projetos claros recebem estes bônus.</p>
              <ul className="mt-2 space-y-1 list-disc list-inside">
                <li><strong>Peso:</strong> Quantos pontos são adicionados quando detectada (use valores positivos)</li>
                <li><strong>Keywords:</strong> Palavras-chave que ativam esta flag na análise automática</li>
              </ul>
            </div>
          )}
          <div className="grid gap-4 md:grid-cols-2">
            {Object.entries(formData.green_flags).map(([flagId, flag]: [string, any]) => (
              <div key={flagId} className="border rounded-lg p-4 bg-green-50 dark:bg-green-950">
                <div className="flex items-start justify-between mb-2">
                  <p className="font-medium">{flag.name}</p>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-green-600">+</span>
                    <Input
                      type="number"
                      value={flag.weight}
                      onChange={(e) => handleFlagWeightChange('green_flags', flagId, e.target.value)}
                      className="w-24"
                      step="5"
                    />
                    <span className="text-sm text-muted-foreground">pts</span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-red-500 hover:text-red-700"
                      onClick={() => handleRemoveFlag('green_flags', flagId)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {!showAddGreenFlag ? (
            <Button variant="outline" className="mt-4" onClick={() => setShowAddGreenFlag(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Adicionar Green Flag
            </Button>
          ) : (
            <div className="border rounded-lg p-4 mt-4 space-y-3 bg-green-50 dark:bg-green-950">
              <p className="font-medium text-sm">Nova Green Flag</p>
              <div className="grid gap-3 md:grid-cols-2">
                <div>
                  <label className="text-xs font-medium block mb-1">ID (chave única)</label>
                  <Input
                    placeholder="ex: repeat_client"
                    value={newGreenFlag.id}
                    onChange={(e) => setNewGreenFlag({ ...newGreenFlag, id: e.target.value })}
                  />
                  <p className="text-xs text-muted-foreground mt-1">Identificador interno, sem espaços</p>
                </div>
                <div>
                  <label className="text-xs font-medium block mb-1">Nome</label>
                  <Input
                    placeholder="ex: Cliente Recorrente"
                    value={newGreenFlag.name}
                    onChange={(e) => setNewGreenFlag({ ...newGreenFlag, name: e.target.value })}
                  />
                  <p className="text-xs text-muted-foreground mt-1">Nome exibido na interface</p>
                </div>
                <div>
                  <label className="text-xs font-medium block mb-1">Peso (positivo)</label>
                  <Input
                    type="number"
                    value={newGreenFlag.weight}
                    onChange={(e) => setNewGreenFlag({ ...newGreenFlag, weight: parseInt(e.target.value) || 0 })}
                    step="5"
                  />
                  <p className="text-xs text-muted-foreground mt-1">Pontos adicionados ao score</p>
                </div>
                <div>
                  <label className="text-xs font-medium block mb-1">Palavras-chave (separadas por vírgula)</label>
                  <Input
                    placeholder="ex: returning, repeat, loyal"
                    value={newGreenFlag.keywords}
                    onChange={(e) => setNewGreenFlag({ ...newGreenFlag, keywords: e.target.value })}
                  />
                  <p className="text-xs text-muted-foreground mt-1">Termos que ativam esta flag automaticamente</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={handleAddGreenFlag}>Adicionar</Button>
                <Button size="sm" variant="outline" onClick={() => setShowAddGreenFlag(false)}>Cancelar</Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card className="border-blue-500 bg-blue-50 dark:bg-blue-950">
        <CardContent className="pt-6">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="text-sm text-blue-900 dark:text-blue-100">
              <p className="font-medium mb-2">Como a avaliação funciona:</p>
              <ul className="space-y-1 list-disc list-inside">
                <li>Cada oportunidade recebe 3 scores: <strong>Viabilidade</strong>, <strong>Alinhamento</strong> e <strong>Estratégico</strong> (0-100)</li>
                <li>O <strong>score final</strong> é a média ponderada dos 3, usando os pesos que você definiu acima</li>
                <li>Red flags <strong>subtraem</strong> pontos do score de risco do cliente (penalizam clientes problemáticos)</li>
                <li>Green flags <strong>adicionam</strong> pontos ao score de risco (bonificam clientes confiáveis)</li>
                <li>Se o score final for maior que o <strong>score mínimo</strong>, o sistema recomenda aceitação</li>
                <li><strong>Auto-Otimizar</strong> analisa suas decisões passadas e ajusta os pesos automaticamente (requer 15+ oportunidades analisadas)</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Save Footer */}
      {hasChanges && (
        <div className="sticky bottom-0 bg-background border-t p-4 flex items-center justify-between shadow-lg">
          <div>
            <p className="text-sm text-muted-foreground">Você tem alterações não salvas</p>
            {!isWeightValid && (
              <p className="text-sm text-red-500">Pesos devem somar 1.0</p>
            )}
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleReset}>
              <RotateCcw className="h-4 w-4" />
              Desfazer
            </Button>
            <Button onClick={handleSave} disabled={!isWeightValid}>
              <Save className="h-4 w-4" />
              Salvar Alterações
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
