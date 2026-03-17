import { useEffect, useState } from 'react';
import { useFreelancerStore } from '../stores/freelancerStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Settings, DollarSign, Save, RotateCcw, TrendingUp, AlertCircle, HelpCircle } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const SPECIALIZATION_LABELS: Record<string, string> = {
  'web_development': 'Desenvolvimento Web',
  'mobile': 'Mobile',
  'devops': 'DevOps',
  'data_science': 'Ciência de Dados',
  'machine_learning': 'Machine Learning',
  'blockchain': 'Blockchain',
  'security': 'Segurança',
  'design': 'Design',
  'iot': 'IoT',
  'robotics': 'Robótica',
};

export default function PricingParameters() {
  const { pricingParameters, fetchPricingParameters, updatePricingParameters, loading } = useFreelancerStore();
  const { toast } = useToast();

  const [formData, setFormData] = useState<any>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [expandedHelp, setExpandedHelp] = useState<string | null>(null);

  useEffect(() => {
    fetchPricingParameters();
  }, []);

  useEffect(() => {
    if (pricingParameters && !formData) {
      setFormData({
        base_hourly_rate: pricingParameters.base_hourly_rate,
        minimum_margin: pricingParameters.minimum_margin,
        minimum_project_value: pricingParameters.minimum_project_value,
        complexity_factors: { ...pricingParameters.complexity_factors },
        specialization_factors: { ...pricingParameters.specialization_factors },
        deadline_factors: { ...pricingParameters.deadline_factors },
        client_factors: { ...pricingParameters.client_factors },
      });
    }
  }, [pricingParameters]);

  const handleChange = (field: string, value: any) => {
    setFormData({ ...formData, [field]: value });
    setHasChanges(true);
  };

  const handleFactorChange = (category: string, key: string, value: string) => {
    const numValue = parseFloat(value);
    setFormData({
      ...formData,
      [category]: {
        ...formData[category],
        [key]: isNaN(numValue) ? 1.0 : numValue,
      },
    });
    setHasChanges(true);
  };

  const handleSave = async () => {
    try {
      await updatePricingParameters(formData);
      setHasChanges(false);
      toast({
        title: 'Parâmetros salvos!',
        description: 'Suas configurações de precificação foram atualizadas.',
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
    if (pricingParameters) {
      setFormData({
        base_hourly_rate: pricingParameters.base_hourly_rate,
        minimum_margin: pricingParameters.minimum_margin,
        minimum_project_value: pricingParameters.minimum_project_value,
        complexity_factors: { ...pricingParameters.complexity_factors },
        specialization_factors: { ...pricingParameters.specialization_factors },
        deadline_factors: { ...pricingParameters.deadline_factors },
        client_factors: { ...pricingParameters.client_factors },
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
        <p className="text-muted-foreground">Carregando parâmetros...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Settings className="h-8 w-8" />
            Parâmetros de Precificação
          </h1>
          <p className="text-muted-foreground">Configure os fatores que influenciam o cálculo automático de preços</p>
        </div>
        <div className="flex gap-2">
          {hasChanges && (
            <>
              <Button variant="outline" onClick={handleReset}>
                <RotateCcw className="h-4 w-4" />
                Desfazer
              </Button>
              <Button onClick={handleSave}>
                <Save className="h-4 w-4" />
                Salvar Alterações
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Version Info */}
      {pricingParameters && (
        <Card className="border-blue-500">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Versão Atual</p>
                <p className="text-2xl font-bold">v{pricingParameters.version}</p>
              </div>
              <div>
                <Badge variant={pricingParameters.active ? 'success' : 'secondary'}>
                  {pricingParameters.active ? 'Ativo' : 'Inativo'}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Base Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Configuração Base
          </CardTitle>
          <CardDescription>Valores fundamentais usados como ponto de partida para todos os cálculos de preço</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div>
              <div className="flex items-center gap-1 mb-2">
                <label className="text-sm font-medium">Taxa Horária Base</label>
                <button onClick={() => toggleHelp('hourly_rate')} className="text-muted-foreground hover:text-foreground">
                  <HelpCircle className="h-3.5 w-3.5" />
                </button>
              </div>
              {expandedHelp === 'hourly_rate' && (
                <p className="text-xs text-blue-600 dark:text-blue-400 mb-2 p-2 bg-blue-50 dark:bg-blue-950 rounded">
                  Sua taxa horária padrão em USD. Este é o valor base antes de aplicar multiplicadores de complexidade, especialização e prazo.
                  O preço sugerido final será: <code className="bg-blue-100 dark:bg-blue-900 px-1 rounded">taxa_base × complexidade × especialização × prazo × cliente</code>
                </p>
              )}
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="number"
                  value={formData.base_hourly_rate}
                  onChange={(e) => handleChange('base_hourly_rate', parseFloat(e.target.value))}
                  className="pl-9"
                  step="0.01"
                />
              </div>
              <p className="text-xs text-muted-foreground mt-1">Valor por hora em USD</p>
            </div>

            <div>
              <div className="flex items-center gap-1 mb-2">
                <label className="text-sm font-medium">Margem Mínima</label>
                <button onClick={() => toggleHelp('margin')} className="text-muted-foreground hover:text-foreground">
                  <HelpCircle className="h-3.5 w-3.5" />
                </button>
              </div>
              {expandedHelp === 'margin' && (
                <p className="text-xs text-blue-600 dark:text-blue-400 mb-2 p-2 bg-blue-50 dark:bg-blue-950 rounded">
                  Margem de lucro mínima que você aceita. Ex: 0.20 = 20%. Se o projeto não atingir essa margem considerando seus custos, receberá alerta de preço baixo.
                  Inclua aqui impostos, custos operacionais e margem de segurança.
                </p>
              )}
              <div className="relative">
                <Input
                  type="number"
                  value={formData.minimum_margin}
                  onChange={(e) => handleChange('minimum_margin', parseFloat(e.target.value))}
                  step="0.01"
                  max="1"
                  min="0"
                />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">
                  {(formData.minimum_margin * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">Margem de lucro mínima aceitável</p>
            </div>

            <div>
              <div className="flex items-center gap-1 mb-2">
                <label className="text-sm font-medium">Valor Mínimo de Projeto</label>
                <button onClick={() => toggleHelp('min_value')} className="text-muted-foreground hover:text-foreground">
                  <HelpCircle className="h-3.5 w-3.5" />
                </button>
              </div>
              {expandedHelp === 'min_value' && (
                <p className="text-xs text-blue-600 dark:text-blue-400 mb-2 p-2 bg-blue-50 dark:bg-blue-950 rounded">
                  Valor mínimo (USD) para considerar um projeto. Projetos abaixo desse valor serão sinalizados como não compensatórios,
                  independente da taxa horária. Considere o custo de setup, comunicação e gestão de cada projeto.
                </p>
              )}
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="number"
                  value={formData.minimum_project_value}
                  onChange={(e) => handleChange('minimum_project_value', parseFloat(e.target.value))}
                  className="pl-9"
                  step="100"
                />
              </div>
              <p className="text-xs text-muted-foreground mt-1">Valor mínimo para aceitar projeto (USD)</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Complexity Factors */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Fatores de Complexidade
            <button onClick={() => toggleHelp('complexity_info')} className="text-muted-foreground hover:text-foreground">
              <HelpCircle className="h-4 w-4" />
            </button>
          </CardTitle>
          <CardDescription>Multiplicadores aplicados conforme a complexidade do projeto (escala 1-10)</CardDescription>
        </CardHeader>
        <CardContent>
          {expandedHelp === 'complexity_info' && (
            <div className="text-xs text-blue-600 dark:text-blue-400 mb-4 p-3 bg-blue-50 dark:bg-blue-950 rounded">
              <p className="font-medium mb-1">Como funciona:</p>
              <p>Cada nível de complexidade (1 a 10) tem um multiplicador. A taxa horária base é multiplicada por esse fator.</p>
              <p className="mt-1">Ex: complexidade 5 com fator 1.5 e taxa base $50/h = preço sugerido de $75/h para esse nível.</p>
              <p className="mt-1">Recomendação: nível 1 = 1.0x (sem acréscimo), níveis maiores progressivamente mais altos.</p>
            </div>
          )}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Object.entries(formData.complexity_factors).map(([key, value]: [string, any]) => (
              <div key={key}>
                <label className="text-sm font-medium mb-2 block">
                  Nível {key}
                </label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={value}
                    onChange={(e) => handleFactorChange('complexity_factors', key, e.target.value)}
                    step="0.1"
                  />
                  <Badge variant="outline">{value}x</Badge>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {value > 1 ? `+${((value - 1) * 100).toFixed(0)}% sobre a base` : 'Valor base'}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Specialization Factors */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Fatores de Especialização
            <button onClick={() => toggleHelp('spec_info')} className="text-muted-foreground hover:text-foreground">
              <HelpCircle className="h-4 w-4" />
            </button>
          </CardTitle>
          <CardDescription>Multiplicadores por área de expertise — áreas com maior demanda ou raridade podem cobrar mais</CardDescription>
        </CardHeader>
        <CardContent>
          {expandedHelp === 'spec_info' && (
            <div className="text-xs text-blue-600 dark:text-blue-400 mb-4 p-3 bg-blue-50 dark:bg-blue-950 rounded">
              <p className="font-medium mb-1">Como funciona:</p>
              <p>Cada área de especialização tem um multiplicador. Áreas mais valorizadas ou raras devem ter fatores maiores.</p>
              <p className="mt-1">Ex: Machine Learning com fator 1.5 significa que projetos dessa área recebem +50% no preço sugerido.</p>
              <p className="mt-1">Fator 1.0 = sem acréscimo. Ajuste conforme sua experiência e o mercado.</p>
            </div>
          )}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Object.entries(formData.specialization_factors).map(([key, value]: [string, any]) => (
              <div key={key}>
                <label className="text-sm font-medium mb-2 block">
                  {SPECIALIZATION_LABELS[key] || key.replace(/_/g, ' ')}
                </label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={value}
                    onChange={(e) => handleFactorChange('specialization_factors', key, e.target.value)}
                    step="0.1"
                  />
                  <Badge variant="outline">{value}x</Badge>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {value > 1 ? `+${((value - 1) * 100).toFixed(0)}% sobre a base` : 'Valor base'}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Deadline Factors */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Fatores de Prazo
            <button onClick={() => toggleHelp('deadline_info')} className="text-muted-foreground hover:text-foreground">
              <HelpCircle className="h-4 w-4" />
            </button>
          </CardTitle>
          <CardDescription>Multiplicadores baseados na urgência de entrega — prazos curtos justificam cobrar mais</CardDescription>
        </CardHeader>
        <CardContent>
          {expandedHelp === 'deadline_info' && (
            <div className="text-xs text-blue-600 dark:text-blue-400 mb-4 p-3 bg-blue-50 dark:bg-blue-950 rounded">
              <p className="font-medium mb-1">Como funciona:</p>
              <p>Projetos urgentes demandam reorganização da agenda e trabalho intensivo. O multiplicador compensa isso.</p>
              <p className="mt-1">Ex: prazo urgente com fator 1.5 = +50% no preço. Prazo longo com fator 0.9 = desconto de 10% por flexibilidade.</p>
            </div>
          )}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Object.entries(formData.deadline_factors).map(([key, value]: [string, any]) => (
              <div key={key}>
                <label className="text-sm font-medium mb-2 block">
                  {key === 'urgent' ? 'Urgente' : key === 'short' ? 'Curto' : key === 'normal' ? 'Normal' : key === 'long' ? 'Longo' : key}
                </label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={value}
                    onChange={(e) => handleFactorChange('deadline_factors', key, e.target.value)}
                    step="0.1"
                  />
                  <Badge variant="outline">{value}x</Badge>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-blue-600 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-blue-900 dark:text-blue-100">Definições de Prazo:</p>
                <ul className="mt-2 space-y-1 text-blue-800 dark:text-blue-200">
                  <li><strong>Urgente:</strong> Menos de 1 semana — exige dedicação exclusiva</li>
                  <li><strong>Curto:</strong> 1-2 semanas — prazo apertado mas gerenciável</li>
                  <li><strong>Normal:</strong> 2-4 semanas — prazo padrão de mercado</li>
                  <li><strong>Longo:</strong> Mais de 4 semanas — maior flexibilidade de organização</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Client Factors */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Fatores de Cliente
            <button onClick={() => toggleHelp('client_info')} className="text-muted-foreground hover:text-foreground">
              <HelpCircle className="h-4 w-4" />
            </button>
          </CardTitle>
          <CardDescription>Multiplicadores baseados no perfil e histórico do cliente</CardDescription>
        </CardHeader>
        <CardContent>
          {expandedHelp === 'client_info' && (
            <div className="text-xs text-blue-600 dark:text-blue-400 mb-4 p-3 bg-blue-50 dark:bg-blue-950 rounded">
              <p className="font-medium mb-1">Como funciona:</p>
              <p>O tipo de cliente influencia o risco e o esforço de comunicação. Clientes novos têm mais risco (fator maior = cobra mais).
              Clientes premium podem ter desconto como incentivo à recorrência (fator menor).</p>
            </div>
          )}
          <div className="grid gap-4 md:grid-cols-3">
            {Object.entries(formData.client_factors).map(([key, value]: [string, any]) => (
              <div key={key}>
                <label className="text-sm font-medium mb-2 block">
                  {key === 'new' ? 'Novo' : key === 'verified' ? 'Verificado' : key === 'premium' ? 'Premium' : key}
                </label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={value}
                    onChange={(e) => handleFactorChange('client_factors', key, e.target.value)}
                    step="0.05"
                  />
                  <Badge variant="outline">{value}x</Badge>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-yellow-900 dark:text-yellow-100">Tipos de Cliente:</p>
                <ul className="mt-2 space-y-1 text-yellow-800 dark:text-yellow-200">
                  <li><strong>Novo:</strong> Primeiro projeto — maior risco de comunicação e pagamento</li>
                  <li><strong>Verificado:</strong> Cliente verificado pela plataforma — risco moderado</li>
                  <li><strong>Premium:</strong> Cliente recorrente com histórico positivo — menor risco, possível desconto</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* How Pricing Works */}
      <Card className="border-blue-500 bg-blue-50 dark:bg-blue-950">
        <CardContent className="pt-6">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="text-sm text-blue-900 dark:text-blue-100">
              <p className="font-medium mb-2">Como o cálculo de preço funciona:</p>
              <ul className="space-y-1 list-disc list-inside">
                <li>O sistema calcula: <strong>Taxa Base × Complexidade × Especialização × Prazo × Cliente</strong></li>
                <li>Exemplo: $50/h × 1.3 (complexidade 5) × 1.2 (ML) × 1.5 (urgente) × 1.0 (verificado) = <strong>$117/h</strong></li>
                <li>Se o valor total do projeto ficar abaixo do <strong>valor mínimo</strong>, você receberá um alerta</li>
                <li>Se a margem calculada ficar abaixo da <strong>margem mínima</strong>, o sistema sugere negociar valor maior</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Save Footer */}
      {hasChanges && (
        <div className="sticky bottom-0 bg-background border-t p-4 flex items-center justify-between shadow-lg">
          <p className="text-sm text-muted-foreground">Você tem alterações não salvas</p>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleReset}>
              <RotateCcw className="h-4 w-4" />
              Desfazer
            </Button>
            <Button onClick={handleSave}>
              <Save className="h-4 w-4" />
              Salvar Alterações
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
