import { useEffect, useState } from 'react';
import { useFreelancerStore } from '../stores/freelancerStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Settings, DollarSign, Save, RotateCcw, TrendingUp, AlertCircle } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

export default function PricingParameters() {
  const { pricingParameters, fetchPricingParameters, updatePricingParameters, loading } = useFreelancerStore();
  const { toast } = useToast();

  const [formData, setFormData] = useState<any>(null);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    fetchPricingParameters();
  }, []);

  useEffect(() => {
    if (pricingParameters && !formData) {
      setFormData({
        base_hourly_rate: pricingParameters.base_hourly_rate,
        minimum_margin: pricingParameters.minimum_margin,
        currency: pricingParameters.currency,
        minimum_project_value: pricingParameters.minimum_project_value,
        minimum_deadline_days: pricingParameters.minimum_deadline_days,
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
        currency: pricingParameters.currency,
        minimum_project_value: pricingParameters.minimum_project_value,
        minimum_deadline_days: pricingParameters.minimum_deadline_days,
        complexity_factors: { ...pricingParameters.complexity_factors },
        specialization_factors: { ...pricingParameters.specialization_factors },
        deadline_factors: { ...pricingParameters.deadline_factors },
        client_factors: { ...pricingParameters.client_factors },
      });
      setHasChanges(false);
    }
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
          <CardDescription>Valores base para cálculos de precificação</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div>
              <label className="text-sm font-medium mb-2 block">Taxa Horária Base</label>
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
              <p className="text-xs text-muted-foreground mt-1">Sua taxa horária padrão</p>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Margem Mínima</label>
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
              <label className="text-sm font-medium mb-2 block">Moeda</label>
              <Input
                value={formData.currency}
                onChange={(e) => handleChange('currency', e.target.value)}
                placeholder="USD"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Valor Mínimo de Projeto</label>
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
              <p className="text-xs text-muted-foreground mt-1">Valor mínimo para aceitar projeto</p>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Prazo Mínimo (dias)</label>
              <Input
                type="number"
                value={formData.minimum_deadline_days}
                onChange={(e) => handleChange('minimum_deadline_days', parseInt(e.target.value))}
              />
              <p className="text-xs text-muted-foreground mt-1">Número mínimo de dias para entrega</p>
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
          </CardTitle>
          <CardDescription>Multiplicadores baseados na complexidade do projeto (1-10)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Object.entries(formData.complexity_factors).map(([key, value]: [string, any]) => (
              <div key={key}>
                <label className="text-sm font-medium mb-2 block">
                  Complexidade {key}
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
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Specialization Factors */}
      <Card>
        <CardHeader>
          <CardTitle>Fatores de Especialização</CardTitle>
          <CardDescription>Multiplicadores por área de expertise</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Object.entries(formData.specialization_factors).map(([key, value]: [string, any]) => (
              <div key={key}>
                <label className="text-sm font-medium mb-2 block capitalize">
                  {key.replace('_', ' / ')}
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
                  {value > 1 ? `+${((value - 1) * 100).toFixed(0)}%` : 'Base'}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Deadline Factors */}
      <Card>
        <CardHeader>
          <CardTitle>Fatores de Prazo</CardTitle>
          <CardDescription>Multiplicadores baseados no prazo de entrega</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Object.entries(formData.deadline_factors).map(([key, value]: [string, any]) => (
              <div key={key}>
                <label className="text-sm font-medium mb-2 block capitalize">{key}</label>
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
                  <li><strong>Urgent:</strong> &lt; 1 semana</li>
                  <li><strong>Short:</strong> 1-2 semanas</li>
                  <li><strong>Normal:</strong> 2-4 semanas</li>
                  <li><strong>Long:</strong> &gt; 4 semanas</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Client Factors */}
      <Card>
        <CardHeader>
          <CardTitle>Fatores de Cliente</CardTitle>
          <CardDescription>Multiplicadores baseados no perfil do cliente</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {Object.entries(formData.client_factors).map(([key, value]: [string, any]) => (
              <div key={key}>
                <label className="text-sm font-medium mb-2 block capitalize">{key}</label>
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
                  <li><strong>New:</strong> Primeiro projeto, maior risco</li>
                  <li><strong>Verified:</strong> Cliente verificado pela plataforma</li>
                  <li><strong>Premium:</strong> Cliente recorrente com histórico positivo</li>
                </ul>
              </div>
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
