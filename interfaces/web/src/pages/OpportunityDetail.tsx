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
  MapPin,
  Star,
  Briefcase,
  Calendar,
  RefreshCw,
  Trash2,
  Pencil,
  Shield,
  Settings,
} from 'lucide-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '../components/ui/alert-dialog';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import * as freelancerService from '../services/freelancerService';
import type { NegotiationResponse, FreelanceOpportunity } from '../types/freelancer';
import { useToast } from '../hooks/use-toast';

export default function OpportunityDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { selectedOpportunity, fetchOpportunityById, updateOpportunityStatus, acceptOpportunity, updateOpportunity, deleteOpportunity } = useFreelancerStore();

  const [processing, setProcessing] = useState(false);
  const [negotiating, setNegotiating] = useState(false);
  const [negotiationResult, setNegotiationResult] = useState<NegotiationResponse | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editForm, setEditForm] = useState({
    title: '',
    description: '',
    client_budget: 0,
    client_name: '',
    client_country: '',
  });
  const [saving, setSaving] = useState(false);
  const [accepting, setAccepting] = useState(false);

  useEffect(() => {
    if (id) {
      fetchOpportunityById(parseInt(id));
    }
  }, [id]);

  useEffect(() => {
    if (selectedOpportunity) {
      setEditForm({
        title: selectedOpportunity.title || '',
        description: selectedOpportunity.description || '',
        client_budget: selectedOpportunity.client_budget || 0,
        client_name: selectedOpportunity.client_name || '',
        client_country: selectedOpportunity.client_country || '',
      });
    }
  }, [selectedOpportunity]);

  const handleProcessOpportunity = async () => {
    if (!selectedOpportunity) return;

    setProcessing(true);
    try {
      const result = await freelancerService.analyzeOpportunity(selectedOpportunity.id);
      await fetchOpportunityById(selectedOpportunity.id);

      toast({
        title: 'Oportunidade analisada!',
        description: `Recomendação: ${result.opportunity.recommendation || result.analysis.final_recommendation?.decision}`,
      });
    } catch (error: unknown) {
      toast({
        title: 'Erro ao analisar',
        description: error instanceof Error ? error.message : 'Erro desconhecido',
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
    } catch (error: unknown) {
      toast({
        title: 'Erro ao gerar negociação',
        description: error instanceof Error ? error.message : 'Erro desconhecido',
        variant: 'destructive',
      });
    } finally {
      setNegotiating(false);
    }
  };

  const handleAcceptOpportunity = async () => {
    if (!selectedOpportunity) return;

    setAccepting(true);
    try {
      const result = await acceptOpportunity(selectedOpportunity.id);
      if (result) {
        toast({
          title: 'Oportunidade aceita!',
          description: result.message,
        });
      }
    } catch (error: unknown) {
      toast({
        title: 'Erro ao aceitar',
        description: error instanceof Error ? error.message : 'Erro desconhecido',
        variant: 'destructive',
      });
    } finally {
      setAccepting(false);
    }
  };

  const handleStatusChange = async (status: FreelanceOpportunity['status']) => {
    if (!selectedOpportunity) return;

    try {
      await updateOpportunityStatus(selectedOpportunity.id, status);
      toast({
        title: 'Status atualizado!',
        description: `Oportunidade marcada como ${status}`,
      });
    } catch (error: unknown) {
      toast({
        title: 'Erro ao atualizar status',
        description: error instanceof Error ? error.message : 'Erro desconhecido',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async () => {
    if (!selectedOpportunity) return;

    setDeleting(true);
    try {
      await deleteOpportunity(selectedOpportunity.id);
      toast({
        title: 'Oportunidade excluída!',
        description: 'A oportunidade foi removida com sucesso.',
      });
      navigate('/freelancer/opportunities');
    } catch (error: unknown) {
      toast({
        title: 'Erro ao excluir',
        description: error instanceof Error ? error.message : 'Erro desconhecido',
        variant: 'destructive',
      });
    } finally {
      setDeleting(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!selectedOpportunity) return;

    setSaving(true);
    try {
      // Clean up form data - convert empty/zero values to null for backend validation
      const cleanedData: Record<string, string | number> = {};
      if (editForm.title?.trim()) cleanedData.title = editForm.title.trim();
      if (editForm.description?.trim()) cleanedData.description = editForm.description.trim();
      if (editForm.client_budget && editForm.client_budget > 0) cleanedData.client_budget = editForm.client_budget;
      if (editForm.client_name?.trim()) cleanedData.client_name = editForm.client_name.trim();
      if (editForm.client_country?.trim()) cleanedData.client_country = editForm.client_country.trim();

      await updateOpportunity(selectedOpportunity.id, cleanedData);
      setEditDialogOpen(false);
      toast({
        title: 'Oportunidade atualizada!',
        description: 'As alterações foram salvas com sucesso.',
      });
    } catch (error: unknown) {
      toast({
        title: 'Erro ao salvar',
        description: error instanceof Error ? error.message : 'Erro desconhecido',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  if (!selectedOpportunity) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-muted-foreground">Carregando...</p>
      </div>
    );
  }

  // Build risk object from opportunity data
  // Check if opportunity has been analyzed
  const hasRecommendation = selectedOpportunity.recommendation && selectedOpportunity.recommendation !== '';
  const hasRedFlags = selectedOpportunity.red_flags && Array.isArray(selectedOpportunity.red_flags) && selectedOpportunity.red_flags.length > 0;
  const hasRiskAssessment = selectedOpportunity.risk_assessment !== undefined && selectedOpportunity.risk_assessment !== null;
  const hasExtractedContext = selectedOpportunity.extracted_context?.risk_score !== undefined;

  const hasAnalysis = hasRecommendation || hasRedFlags || hasRiskAssessment || hasExtractedContext;

  console.log('[OpportunityDetail] Analysis check:', {
    hasRecommendation,
    hasRedFlags,
    hasRiskAssessment,
    hasExtractedContext,
    hasAnalysis,
    recommendation: selectedOpportunity.recommendation,
    red_flags: selectedOpportunity.red_flags
  });

  const risk = hasAnalysis ? {
    risk_score: selectedOpportunity.extracted_context?.risk_score ||
                selectedOpportunity.final_score ||
                (selectedOpportunity.recommendation === 'reject' ? 8.0 :
                 selectedOpportunity.recommendation === 'negotiate' ? 5.0 : 2.0),
    risk_level: selectedOpportunity.extracted_context?.risk_level ||
                (selectedOpportunity.recommendation === 'reject' ? 'high' :
                 selectedOpportunity.recommendation === 'negotiate' ? 'medium' : 'low'),
    recommendation: selectedOpportunity.recommendation,
    recommendation_reason: selectedOpportunity.recommendation_reason,
    red_flags: selectedOpportunity.red_flags || [],
    green_flags: selectedOpportunity.opportunities || [],
    ...selectedOpportunity.risk_assessment
  } : null;

  console.log('[OpportunityDetail] Risk object:', risk);

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

      {/* Status and Actions */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle>Status e Ações</CardTitle>
            <Badge
              variant={
                selectedOpportunity.status === 'accepted'
                  ? 'success'
                  : selectedOpportunity.status === 'rejected'
                  ? 'destructive'
                  : selectedOpportunity.status === 'analyzed'
                  ? 'default'
                  : 'secondary'
              }
              className="text-sm"
            >
              {selectedOpportunity.status === 'new' ? 'Nova' :
               selectedOpportunity.status === 'analyzed' ? 'Analisada' :
               selectedOpportunity.status === 'accepted' ? 'Aceita' :
               selectedOpportunity.status === 'rejected' ? 'Rejeitada' :
               selectedOpportunity.status}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {/* Action Buttons - Organized in rows */}
          <div className="flex flex-col gap-4">
            {/* Primary Actions Row */}
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                {/* Analyze Button */}
                <Button
                  onClick={handleProcessOpportunity}
                  disabled={processing}
                  variant={hasAnalysis ? "outline" : "default"}
                >
                  {processing ? (
                    <>
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      Processando...
                    </>
                  ) : (
                    <>
                      {hasAnalysis ? <RefreshCw className="h-4 w-4" /> : <TrendingUp className="h-4 w-4" />}
                      {hasAnalysis ? 'Re-analisar' : 'Analisar'}
                    </>
                  )}
                </Button>

                {/* Accept/Negotiate/Reject buttons - show after analysis or for any non-decided status */}
                {selectedOpportunity.status !== 'accepted' && selectedOpportunity.status !== 'rejected' && selectedOpportunity.status !== 'completed' && (
                  <>
                    <Button onClick={handleAcceptOpportunity} disabled={accepting}>
                      <CheckCircle className="h-4 w-4" />
                      {accepting ? 'Aceitando...' : 'Aceitar'}
                    </Button>
                    <Button variant="outline" onClick={handleGenerateNegotiation} disabled={negotiating || !hasAnalysis}>
                      <MessageSquare className="h-4 w-4" />
                      {negotiating ? 'Gerando...' : 'Negociar'}
                    </Button>
                    <Button variant="outline" onClick={() => handleStatusChange('rejected')}>
                      <XCircle className="h-4 w-4" />
                      Rejeitar
                    </Button>
                  </>
                )}
              </div>

              {/* Management Actions - Right aligned */}
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" asChild>
                  <Link to="/freelancer/criteria">
                    <Shield className="h-4 w-4" />
                    Critérios
                  </Link>
                </Button>
                <Button variant="ghost" size="sm" asChild>
                  <Link to="/freelancer/pricing">
                    <Settings className="h-4 w-4" />
                    Pricing
                  </Link>
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setEditDialogOpen(true)}
                >
                  <Pencil className="h-4 w-4" />
                  Editar
                </Button>

                {/* Delete Button with Confirmation */}
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button size="sm" variant="ghost" className="text-destructive hover:text-destructive" disabled={deleting}>
                      <Trash2 className="h-4 w-4" />
                      {deleting ? 'Excluindo...' : 'Excluir'}
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Excluir oportunidade?</AlertDialogTitle>
                      <AlertDialogDescription>
                        Essa ação não pode ser desfeita. A oportunidade será permanentemente removida.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancelar</AlertDialogCancel>
                  <AlertDialogAction onClick={handleDelete}>
                    Excluir
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
              </div>
            </div>
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

            {selectedOpportunity.client_total_spent !== undefined && selectedOpportunity.client_total_spent > 0 && (
              <div className="flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-green-600" />
                <div>
                  <p className="text-xs text-muted-foreground">Total Gasto</p>
                  <p className="font-semibold">
                    ${selectedOpportunity.client_total_spent >= 1000
                      ? `${(selectedOpportunity.client_total_spent / 1000).toFixed(0)}K`
                      : selectedOpportunity.client_total_spent.toFixed(0)}
                  </p>
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
                  {risk.red_flags.map((flag: string | { name?: string; type?: string }, idx: number) => (
                    <Badge key={idx} variant="destructive" className="mr-2">
                      {typeof flag === 'string' ? flag : flag.name || flag.type}
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
                  {risk.green_flags.map((flag: string | { name?: string; type?: string }, idx: number) => (
                    <Badge key={idx} variant="success" className="mr-2">
                      {typeof flag === 'string' ? flag : flag.name || flag.type}
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

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Editar Oportunidade</DialogTitle>
            <DialogDescription>
              Faça alterações nas informações da oportunidade.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Título</label>
              <Input
                value={editForm.title}
                onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                placeholder="Título da oportunidade"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Descrição</label>
              <textarea
                className="flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={editForm.description}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                placeholder="Descrição do projeto"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Orçamento (USD)</label>
                <Input
                  type="number"
                  value={editForm.client_budget}
                  onChange={(e) => setEditForm({ ...editForm, client_budget: parseFloat(e.target.value) || 0 })}
                  placeholder="0.00"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Nome do Cliente</label>
                <Input
                  value={editForm.client_name}
                  onChange={(e) => setEditForm({ ...editForm, client_name: e.target.value })}
                  placeholder="Nome do cliente"
                />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">País do Cliente</label>
              <Input
                value={editForm.client_country}
                onChange={(e) => setEditForm({ ...editForm, client_country: e.target.value })}
                placeholder="País"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleSaveEdit} disabled={saving}>
              {saving ? 'Salvando...' : 'Salvar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
