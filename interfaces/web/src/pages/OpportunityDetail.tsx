import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useFreelancerStore } from '../stores/freelancerStore';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  MessageSquare,
  DollarSign,
  AlertTriangle,
  TrendingUp,
  Clock,
  User,
  MapPin,
  Star,
  Briefcase,
  Calendar,
  RefreshCw,
} from 'lucide-react';
import * as freelancerService from '../services/freelancerService';
import { useToast } from '../hooks/use-toast';

export default function OpportunityDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { selectedOpportunity, fetchOpportunityById, updateOpportunityStatus } = useFreelancerStore();

  const [processing, setProcessing] = useState(false);
  const [negotiating, setNegotiating] = useState(false);
  const [negotiationResult, setNegotiationResult] = useState<any>(null);

  useEffect(() => {
    if (id) {
      fetchOpportunityById(parseInt(id));
    }
  }, [id]);

  const handleProcessOpportunity = async () => {
    if (!selectedOpportunity) return;

    setProcessing(true);
    try {
      const result = await freelancerService.processOpportunity({ opportunity_id: selectedOpportunity.id });
      await fetchOpportunityById(selectedOpportunity.id);

      toast({
        title: 'Oportunidade processada!',
        description: `Recomendação: ${result.risk_assessment.recommendation}`,
      });
    } catch (error: any) {
      toast({
        title: 'Erro ao processar',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleGenerateNegotiation = async () => {
    if (!selectedOpportunity) return;

    setNegotiating(true);
    try {
      const result = await freelancerService.generateNegotiation({
        opportunity_id: selectedOpportunity.id,
      });
      setNegotiationResult(result);

      toast({
        title: 'Negociação gerada!',
        description: `Contra-oferta: $${result.counter_offer}`,
      });
    } catch (error: any) {
      toast({
        title: 'Erro ao gerar negociação',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setNegotiating(false);
    }
  };

  const handleStatusChange = async (status: any) => {
    if (!selectedOpportunity) return;

    try {
      await updateOpportunityStatus(selectedOpportunity.id, status);
      toast({
        title: 'Status atualizado!',
        description: `Oportunidade marcada como ${status}`,
      });
    } catch (error: any) {
      toast({
        title: 'Erro ao atualizar status',
        description: error.message,
        variant: 'destructive',
      });
    }
  };

  if (!selectedOpportunity) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-muted-foreground">Carregando...</p>
      </div>
    );
  }

  const risk = selectedOpportunity.risk_assessment;
  const pricing = selectedOpportunity.pricing_suggestion;
  const financial = selectedOpportunity.financial_calculation;

  const getRiskColor = (level?: string) => {
    switch (level) {
      case 'low':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'high':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/freelancer/opportunities')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{selectedOpportunity.title}</h1>
            <p className="text-muted-foreground">
              {selectedOpportunity.platform?.name} · ID: {selectedOpportunity.external_id}
            </p>
          </div>
        </div>

        {!risk && (
          <Button onClick={handleProcessOpportunity} disabled={processing}>
            {processing ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                Processando...
              </>
            ) : (
              <>
                <TrendingUp className="h-4 w-4" />
                Analisar Oportunidade
              </>
            )}
          </Button>
        )}
      </div>

      {/* Status and Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Status e Ações</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Badge
              variant={
                selectedOpportunity.status === 'accepted'
                  ? 'success'
                  : selectedOpportunity.status === 'rejected'
                  ? 'destructive'
                  : 'secondary'
              }
            >
              {selectedOpportunity.status}
            </Badge>

            {selectedOpportunity.status === 'pending' && risk && (
              <>
                {risk.recommendation === 'accept' && (
                  <Button size="sm" onClick={() => handleStatusChange('accepted')}>
                    <CheckCircle className="h-4 w-4" />
                    Aceitar
                  </Button>
                )}
                {risk.recommendation === 'negotiate' && (
                  <Button size="sm" variant="outline" onClick={handleGenerateNegotiation} disabled={negotiating}>
                    <MessageSquare className="h-4 w-4" />
                    {negotiating ? 'Gerando...' : 'Negociar'}
                  </Button>
                )}
                <Button size="sm" variant="destructive" onClick={() => handleStatusChange('rejected')}>
                  <XCircle className="h-4 w-4" />
                  Rejeitar
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Project Details */}
        <Card>
          <CardHeader>
            <CardTitle>Detalhes do Projeto</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-muted-foreground mb-2">Descrição</h4>
              <p className="text-sm whitespace-pre-wrap">{selectedOpportunity.description}</p>
            </div>

            {selectedOpportunity.skills_required && selectedOpportunity.skills_required.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">Skills Necessárias</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedOpportunity.skills_required.map((skill) => (
                    <Badge key={skill} variant="secondary">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              {selectedOpportunity.client_budget && (
                <div className="flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-xs text-muted-foreground">Orçamento</p>
                    <p className="font-semibold">${selectedOpportunity.client_budget}</p>
                  </div>
                </div>
              )}

              {selectedOpportunity.estimated_hours && (
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-xs text-muted-foreground">Horas Est.</p>
                    <p className="font-semibold">{selectedOpportunity.estimated_hours}h</p>
                  </div>
                </div>
              )}
            </div>

            <div className="text-xs text-muted-foreground">
              <Calendar className="h-3 w-3 inline mr-1" />
              Criado em {new Date(selectedOpportunity.created_at).toLocaleDateString('pt-BR')}
            </div>
          </CardContent>
        </Card>

        {/* Client Information */}
        <Card>
          <CardHeader>
            <CardTitle>Informações do Cliente</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {selectedOpportunity.client_rating && (
              <div className="flex items-center gap-2">
                <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                <div>
                  <p className="text-xs text-muted-foreground">Rating</p>
                  <p className="font-semibold">{selectedOpportunity.client_rating}/5.0</p>
                </div>
              </div>
            )}

            {selectedOpportunity.client_projects_count !== undefined && (
              <div className="flex items-center gap-2">
                <Briefcase className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">Projetos Anteriores</p>
                  <p className="font-semibold">{selectedOpportunity.client_projects_count}</p>
                </div>
              </div>
            )}

            {selectedOpportunity.client_country && (
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">País</p>
                  <p className="font-semibold">{selectedOpportunity.client_country}</p>
                </div>
              </div>
            )}

            {selectedOpportunity.client_payment_verified !== undefined && (
              <div className="flex items-center gap-2">
                {selectedOpportunity.client_payment_verified ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <XCircle className="h-4 w-4 text-red-600" />
                )}
                <p className="text-sm">
                  Pagamento {selectedOpportunity.client_payment_verified ? 'Verificado' : 'Não Verificado'}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Risk Assessment */}
      {risk && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Avaliação de Risco
            </CardTitle>
            <CardDescription>Análise automática de riscos do cliente e projeto</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Nível de Risco</p>
                <Badge variant={risk.risk_level === 'low' ? 'success' : risk.risk_level === 'medium' ? 'warning' : 'destructive'} className="text-lg">
                  {risk.risk_level}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Score de Risco</p>
                <p className={`text-2xl font-bold ${getRiskColor(risk.risk_level)}`}>{risk.risk_score.toFixed(1)}/10</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Recomendação</p>
                <Badge variant={risk.recommendation === 'accept' ? 'success' : risk.recommendation === 'negotiate' ? 'warning' : 'destructive'}>
                  {risk.recommendation}
                </Badge>
              </div>
            </div>

            {risk.red_flags && risk.red_flags.length > 0 && (
              <div>
                <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                  <XCircle className="h-4 w-4 text-red-600" />
                  Red Flags
                </h4>
                <div className="space-y-1">
                  {risk.red_flags.map((flag) => (
                    <Badge key={flag} variant="destructive" className="mr-2">
                      {flag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {risk.green_flags && risk.green_flags.length > 0 && (
              <div>
                <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  Green Flags
                </h4>
                <div className="space-y-1">
                  {risk.green_flags.map((flag) => (
                    <Badge key={flag} variant="success" className="mr-2">
                      {flag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Pricing and Financial */}
      <div className="grid gap-6 md:grid-cols-2">
        {pricing && (
          <Card>
            <CardHeader>
              <CardTitle>Precificação Sugerida</CardTitle>
              <CardDescription>Cálculo baseado nos seus parâmetros</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Valor Sugerido</p>
                <p className="text-3xl font-bold text-green-600">${pricing.suggested_value.toFixed(2)}</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Taxa horária: ${pricing.suggested_hourly_rate.toFixed(2)}/h
                </p>
              </div>

              {pricing.breakdown && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium">Breakdown</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Taxa Base:</span>
                      <span>${pricing.breakdown.base_rate}/h</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Multiplicador Complexidade:</span>
                      <span>{pricing.breakdown.complexity_multiplier}x</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Multiplicador Especialização:</span>
                      <span>{pricing.breakdown.specialization_multiplier}x</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Multiplicador Deadline:</span>
                      <span>{pricing.breakdown.deadline_multiplier}x</span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {financial && (
          <Card>
            <CardHeader>
              <CardTitle>Cálculo Financeiro</CardTitle>
              <CardDescription>Conversão USD → BRL com impostos</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Bruto (USD):</span>
                  <span className="font-semibold">${financial.gross_usd.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Câmbio:</span>
                  <span className="font-semibold">R$ {financial.exchange_rate.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Bruto (BRL):</span>
                  <span className="font-semibold">R$ {financial.gross_brl.toFixed(2)}</span>
                </div>
                {financial.platform_fee_brl && (
                  <div className="flex justify-between text-red-600">
                    <span className="text-sm">Taxa Plataforma:</span>
                    <span className="font-semibold">- R$ {financial.platform_fee_brl.toFixed(2)}</span>
                  </div>
                )}
                <div className="flex justify-between text-red-600">
                  <span className="text-sm">Impostos ({financial.tax_regime}):</span>
                  <span className="font-semibold">- R$ {financial.tax_brl.toFixed(2)}</span>
                </div>
                <div className="border-t pt-2 flex justify-between">
                  <span className="font-semibold">Líquido (BRL):</span>
                  <span className="text-2xl font-bold text-green-600">R$ {financial.net_brl.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Taxa Efetiva:</span>
                  <span className="text-muted-foreground">{(financial.effective_tax_rate * 100).toFixed(1)}%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Negotiation Result */}
      {negotiationResult && (
        <Card className="border-blue-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Proposta de Negociação
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-muted-foreground">Orçamento Original</p>
                <p className="text-xl font-bold">${negotiationResult.original_budget.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Contra-oferta</p>
                <p className="text-xl font-bold text-blue-600">${negotiationResult.counter_offer.toFixed(2)}</p>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium mb-2">Raciocínio</h4>
              <p className="text-sm text-muted-foreground">{negotiationResult.reasoning}</p>
            </div>

            <div>
              <h4 className="text-sm font-medium mb-2">Mensagem Sugerida</h4>
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm whitespace-pre-wrap">{negotiationResult.message_template}</p>
              </div>
            </div>

            <div>
              <Badge variant="outline">{negotiationResult.negotiation_strategy}</Badge>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
