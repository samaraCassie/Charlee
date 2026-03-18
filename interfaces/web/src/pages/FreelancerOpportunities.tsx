import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useFreelancerStore } from '../stores/freelancerStore';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import {
  Plus,
  Filter,
  TrendingUp,
  DollarSign,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  MessageSquare,
  ExternalLink,
  ClipboardPaste,
  Bookmark,
  PlayCircle,
  RefreshCw,
  Shield,
  Settings,
} from 'lucide-react';
import type { FreelanceOpportunity } from '../types/freelancer';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { SmartPasteDialog } from '../components/SmartPasteDialog';
import { bookmarkletOpportunity, type BookmarkletRequest } from '../services/freelancerService';
import { useToast } from '../hooks/use-toast';

export default function FreelancerOpportunities() {
  const {
    opportunities,
    platforms,
    stats,
    loading,
    error,
    fetchOpportunities,
    fetchPlatforms,
    fetchStats,
    createOpportunity,
    processOpportunity,
    analyzeAllNewOpportunities,
  } = useFreelancerStore();

  const { toast } = useToast();
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showSmartPasteDialog, setShowSmartPasteDialog] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [processingId, setProcessingId] = useState<number | null>(null);
  const [analyzingAll, setAnalyzingAll] = useState(false);

  useEffect(() => {
    fetchOpportunities();
    fetchPlatforms();
    fetchStats();
  }, []);

  // Process bookmarklet data from sessionStorage
  useEffect(() => {
    const bookmarkletDataEncoded = sessionStorage.getItem('charlee_bookmarklet_data');
    console.log('[Charlee Debug] sessionStorage data:', bookmarkletDataEncoded ? 'present' : 'null');

    if (bookmarkletDataEncoded) {
      try {
        // Clear immediately to avoid reprocessing
        sessionStorage.removeItem('charlee_bookmarklet_data');

        // Decode URI encoded JSON string
        const bookmarkletDataStr = decodeURIComponent(bookmarkletDataEncoded);
        console.log('[Charlee Debug] Decoded data length:', bookmarkletDataStr.length);

        const data: BookmarkletRequest = JSON.parse(bookmarkletDataStr);
        console.log('[Charlee Debug] Parsed data:', data);

        // Call bookmarklet API
        console.log('[Charlee Debug] Calling bookmarkletOpportunity API...');
        bookmarkletOpportunity(data)
          .then((result) => {
            console.log('[Charlee Debug] API success:', result);
            toast({
              title: 'Oportunidade importada!',
              description: `"${result.title}" foi adicionada com sucesso.`,
            });
            fetchOpportunities();
            fetchStats();
          })
          .catch((error) => {
            console.error('[Charlee Debug] API error:', error);
            toast({
              title: 'Erro ao importar',
              description: error.message || 'Não foi possível importar a oportunidade.',
              variant: 'destructive',
            });
          });
      } catch (error) {
        console.error('[Charlee Debug] Failed to decode/parse bookmarklet data:', error);
        toast({
          title: 'Erro ao processar dados',
          description: 'Dados do bookmarklet inválidos.',
          variant: 'destructive',
        });
      }
    }
  }, [fetchOpportunities, fetchStats, toast]);

  const handleProcessOpportunity = async (id: number) => {
    setProcessingId(id);
    try {
      await processOpportunity(id);
      await fetchOpportunities();
    } finally {
      setProcessingId(null);
    }
  };

  const handleAnalyzeAll = async () => {
    const newCount = opportunities.filter((o) => o.status === 'new').length;
    if (newCount === 0) {
      toast({
        title: 'Nenhuma oportunidade nova',
        description: 'Não há oportunidades com status "nova" para analisar.',
      });
      return;
    }

    setAnalyzingAll(true);
    try {
      const result = await analyzeAllNewOpportunities();
      if (result) {
        toast({
          title: 'Análise em lote concluída!',
          description: `${result.success} de ${result.total} oportunidades analisadas com sucesso.`,
        });
        fetchStats();
      }
    } catch (error: any) {
      toast({
        title: 'Erro na análise em lote',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setAnalyzingAll(false);
    }
  };

  const newOpportunitiesCount = opportunities.filter((o) => o.status === 'new').length;

  const getRiskLevelColor = (level?: string) => {
    switch (level) {
      case 'low':
        return 'success';
      case 'medium':
        return 'warning';
      case 'high':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  const getStatusIcon = (status: FreelanceOpportunity['status']) => {
    switch (status) {
      case 'accepted':
        return <CheckCircle className="h-4 w-4" />;
      case 'rejected':
        return <XCircle className="h-4 w-4" />;
      case 'negotiating':
        return <MessageSquare className="h-4 w-4" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: FreelanceOpportunity['status']) => {
    switch (status) {
      case 'accepted':
        return 'success';
      case 'rejected':
        return 'destructive';
      case 'negotiating':
        return 'warning';
      case 'completed':
        return 'info';
      default:
        return 'secondary';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Oportunidades Freelancer</h1>
          <p className="text-muted-foreground">
            Gerencie e avalie projetos de plataformas freelance com análise automatizada
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
            <Filter className="h-4 w-4" />
            Filtros
          </Button>
          {newOpportunitiesCount > 0 && (
            <Button
              variant="default"
              onClick={handleAnalyzeAll}
              disabled={analyzingAll}
            >
              {analyzingAll ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Analisando...
                </>
              ) : (
                <>
                  <PlayCircle className="h-4 w-4" />
                  Analisar Todas ({newOpportunitiesCount})
                </>
              )}
            </Button>
          )}
          <Button variant="outline" onClick={() => setShowSmartPasteDialog(true)}>
            <ClipboardPaste className="h-4 w-4" />
            Smart Paste
          </Button>
          <Button variant="outline" asChild>
            <a href="/bookmarklet-setup.html" target="_blank" rel="noopener noreferrer">
              <Bookmark className="h-4 w-4" />
              Bookmarklet
            </a>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/freelancer/criteria">
              <Shield className="h-4 w-4" />
              Critérios
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/freelancer/pricing">
              <Settings className="h-4 w-4" />
              Pricing
            </Link>
          </Button>
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4" />
                Nova Oportunidade
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <CreateOpportunityForm
                platforms={platforms}
                onSubmit={async (data) => {
                  await createOpportunity(data);
                  setShowCreateDialog(false);
                  fetchOpportunities();
                }}
              />
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Oportunidades</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
              <p className="text-xs text-muted-foreground">
                {stats.pending} pendentes · {stats.accepted} aceitas
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Orçamento Médio</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.avg_budget.toFixed(0)}</div>
              <p className="text-xs text-muted-foreground">Por projeto</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Receita Total</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.total_revenue.toFixed(0)}</div>
              <p className="text-xs text-muted-foreground">{stats.completed} projetos concluídos</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Taxa de Aceitação</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.total > 0 ? ((stats.accepted / stats.total) * 100).toFixed(1) : 0}%
              </div>
              <p className="text-xs text-muted-foreground">
                {stats.accepted} de {stats.total} oportunidades
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Error State */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              <p>{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Opportunities List */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {loading && opportunities.length === 0 ? (
          <div className="col-span-full text-center py-12 text-muted-foreground">Carregando oportunidades...</div>
        ) : opportunities.length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="pt-6 text-center">
              <p className="text-muted-foreground">Nenhuma oportunidade encontrada</p>
              <Button className="mt-4" onClick={() => setShowCreateDialog(true)}>
                <Plus className="h-4 w-4" />
                Adicionar Primeira Oportunidade
              </Button>
            </CardContent>
          </Card>
        ) : (
          opportunities.map((opportunity) => (
            <Card key={opportunity.id} className="flex flex-col">
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-lg line-clamp-2">{opportunity.title}</CardTitle>
                    <CardDescription className="flex items-center gap-2 mt-2">
                      {opportunity.platform?.name && (
                        <Badge variant="outline">{opportunity.platform.name}</Badge>
                      )}
                      <Badge variant={getStatusColor(opportunity.status)} className="flex items-center gap-1">
                        {getStatusIcon(opportunity.status)}
                        {opportunity.status}
                      </Badge>
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="flex-1">
                <p className="text-sm text-muted-foreground line-clamp-3 mb-4">{opportunity.description}</p>

                <div className="space-y-2">
                  {opportunity.client_budget && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Orçamento:</span>
                      <span className="font-semibold">${opportunity.client_budget.toFixed(0)}</span>
                    </div>
                  )}

                  {opportunity.estimated_hours && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Horas estimadas:</span>
                      <span className="font-semibold">{opportunity.estimated_hours}h</span>
                    </div>
                  )}

                  {opportunity.risk_assessment && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Risco:</span>
                      <Badge variant={getRiskLevelColor(opportunity.risk_assessment.risk_level)}>
                        {opportunity.risk_assessment.risk_level}
                      </Badge>
                    </div>
                  )}

                  {opportunity.pricing_suggestion && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Preço sugerido:</span>
                      <span className="font-semibold text-green-600">
                        ${opportunity.pricing_suggestion.suggested_value.toFixed(0)}
                      </span>
                    </div>
                  )}
                </div>

                {opportunity.skills_required && opportunity.skills_required.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-1">
                    {opportunity.skills_required.slice(0, 3).map((skill) => (
                      <Badge key={skill} variant="secondary" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                    {opportunity.skills_required.length > 3 && (
                      <Badge variant="secondary" className="text-xs">
                        +{opportunity.skills_required.length - 3}
                      </Badge>
                    )}
                  </div>
                )}
              </CardContent>

              <CardFooter className="flex gap-2">
                <Link
                  to={`/freelancer/opportunities/${opportunity.id}`}
                  className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-8 px-3 flex-1"
                >
                  <ExternalLink className="h-4 w-4" />
                  Ver Detalhes
                </Link>
                {!opportunity.risk_assessment && (
                  <Button
                    size="sm"
                    onClick={() => handleProcessOpportunity(opportunity.id)}
                    disabled={processingId === opportunity.id}
                  >
                    {processingId === opportunity.id ? 'Processando...' : 'Analisar'}
                  </Button>
                )}
              </CardFooter>
            </Card>
          ))
        )}
      </div>

      {/* Smart Paste Dialog */}
      <SmartPasteDialog
        open={showSmartPasteDialog}
        onOpenChange={setShowSmartPasteDialog}
        onSuccess={(_opportunityId) => {
          fetchOpportunities();
          fetchStats();
        }}
      />
    </div>
  );
}

interface CreateOpportunityFormProps {
  platforms: any[];
  onSubmit: (data: any) => Promise<void>;
}

function CreateOpportunityForm({ platforms, onSubmit }: CreateOpportunityFormProps) {
  const [formData, setFormData] = useState({
    platform_id: '',
    external_id: '',
    title: '',
    description: '',
    client_budget: '',
    client_rating: '',
    estimated_hours: '',
  });

  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit({
        ...formData,
        platform_id: parseInt(formData.platform_id),
        client_budget: formData.client_budget ? parseFloat(formData.client_budget) : undefined,
        client_rating: formData.client_rating ? parseFloat(formData.client_rating) : undefined,
        estimated_hours: formData.estimated_hours ? parseInt(formData.estimated_hours) : undefined,
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <DialogHeader>
        <DialogTitle>Nova Oportunidade Freelancer</DialogTitle>
      </DialogHeader>

      <div className="space-y-4">
        <div>
          <label className="text-sm font-medium">Plataforma</label>
          <Select value={formData.platform_id} onValueChange={(value) => setFormData({ ...formData, platform_id: value })}>
            <SelectTrigger>
              <SelectValue placeholder="Selecione a plataforma" />
            </SelectTrigger>
            <SelectContent>
              {platforms.map((platform) => (
                <SelectItem key={platform.id} value={platform.id.toString()}>
                  {platform.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-sm font-medium">ID Externo</label>
          <Input
            value={formData.external_id}
            onChange={(e) => setFormData({ ...formData, external_id: e.target.value })}
            placeholder="ID da plataforma"
            required
          />
        </div>

        <div>
          <label className="text-sm font-medium">Título</label>
          <Input
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Título do projeto"
            required
          />
        </div>

        <div>
          <label className="text-sm font-medium">Descrição</label>
          <textarea
            className="flex min-h-[120px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Descrição completa do projeto"
            required
          />
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="text-sm font-medium">Orçamento (USD)</label>
            <Input
              type="number"
              value={formData.client_budget}
              onChange={(e) => setFormData({ ...formData, client_budget: e.target.value })}
              placeholder="5000"
            />
          </div>

          <div>
            <label className="text-sm font-medium">Rating Cliente</label>
            <Input
              type="number"
              step="0.1"
              max="5"
              value={formData.client_rating}
              onChange={(e) => setFormData({ ...formData, client_rating: e.target.value })}
              placeholder="4.5"
            />
          </div>

          <div>
            <label className="text-sm font-medium">Horas Estimadas</label>
            <Input
              type="number"
              value={formData.estimated_hours}
              onChange={(e) => setFormData({ ...formData, estimated_hours: e.target.value })}
              placeholder="100"
            />
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={() => setFormData({
          platform_id: '',
          external_id: '',
          title: '',
          description: '',
          client_budget: '',
          client_rating: '',
          estimated_hours: '',
        })}>
          Limpar
        </Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Criando...' : 'Criar Oportunidade'}
        </Button>
      </div>
    </form>
  );
}
