/**
 * SmartPasteDialog - LLM-based opportunity extraction from pasted text (RF01)
 *
 * Allows users to paste raw text from any source (Upwork, email, WhatsApp, etc.)
 * and have the system automatically extract structured opportunity data.
 *
 * @see docs/modulos-planejados/gestao-projetos-freelancers.md section 2.2.1
 */

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Loader2, Sparkles, AlertTriangle, CheckCircle2, ClipboardPaste, Link } from 'lucide-react';
import {
  smartPasteOpportunity,
  type SmartPasteResponse,
  type SmartPasteExtractedData,
} from '@/services/freelancerService';

interface SmartPasteDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: (opportunityId: number) => void;
}

type Step = 'input' | 'loading' | 'confirm' | 'success' | 'error';

export function SmartPasteDialog({ open, onOpenChange, onSuccess }: SmartPasteDialogProps) {
  const [step, setStep] = useState<Step>('input');
  const [rawText, setRawText] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [extractedData, setExtractedData] = useState<SmartPasteExtractedData | null>(null);
  const [opportunityId, setOpportunityId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const resetState = () => {
    setStep('input');
    setRawText('');
    setSourceUrl('');
    setExtractedData(null);
    setOpportunityId(null);
    setError(null);
  };

  const handleClose = () => {
    resetState();
    onOpenChange(false);
  };

  const handleExtract = async () => {
    if (rawText.trim().length < 50) {
      setError('O texto deve ter pelo menos 50 caracteres para extracao significativa.');
      return;
    }

    setError(null);
    setStep('loading');

    try {
      const response: SmartPasteResponse = await smartPasteOpportunity({
        raw_text: rawText,
        source_url: sourceUrl || undefined,
      });

      setExtractedData(response.extracted);
      setOpportunityId(response.id);
      setStep('confirm');
    } catch (err: any) {
      console.error('Smart Paste error:', err);
      setError(err.response?.data?.detail || 'Falha ao extrair dados. Tente novamente.');
      setStep('error');
    }
  };

  const handleConfirm = () => {
    if (opportunityId) {
      setStep('success');
      setTimeout(() => {
        onSuccess(opportunityId);
        handleClose();
      }, 1500);
    }
  };

  const renderInputStep = () => (
    <>
      <DialogHeader>
        <DialogTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          Smart Paste
        </DialogTitle>
        <DialogDescription>
          Cole o texto do projeto (de Upwork, email, WhatsApp, etc.) e a IA extraira automaticamente
          os dados estruturados.
        </DialogDescription>
      </DialogHeader>

      <div className="space-y-4 py-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Texto do Projeto</label>
          <textarea
            className="w-full min-h-[200px] p-3 rounded-md border border-input bg-background text-sm resize-y focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Cole aqui a descricao do projeto..."
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
          />
          <p className="text-xs text-muted-foreground">
            {rawText.length} caracteres (minimo 50)
          </p>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium flex items-center gap-1">
            <Link className="h-3 w-3" />
            URL de Origem (opcional)
          </label>
          <input
            type="url"
            className="w-full p-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="https://upwork.com/jobs/..."
            value={sourceUrl}
            onChange={(e) => setSourceUrl(e.target.value)}
          />
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-md bg-destructive/10 text-destructive text-sm">
            <AlertTriangle className="h-4 w-4 flex-shrink-0" />
            {error}
          </div>
        )}
      </div>

      <DialogFooter>
        <Button variant="outline" onClick={handleClose}>
          Cancelar
        </Button>
        <Button onClick={handleExtract} disabled={rawText.trim().length < 50}>
          <ClipboardPaste className="mr-2 h-4 w-4" />
          Extrair Dados
        </Button>
      </DialogFooter>
    </>
  );

  const renderLoadingStep = () => (
    <div className="py-12 text-center">
      <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary mb-4" />
      <p className="text-lg font-medium">Analisando texto com IA...</p>
      <p className="text-sm text-muted-foreground mt-1">
        Extraindo titulo, skills, orcamento e mais
      </p>
    </div>
  );

  const renderConfirmStep = () => (
    <>
      <DialogHeader>
        <DialogTitle className="flex items-center gap-2">
          <CheckCircle2 className="h-5 w-5 text-green-500" />
          Dados Extraidos
        </DialogTitle>
        <DialogDescription>
          Revise os dados extraidos pela IA. A oportunidade ja foi criada no sistema.
        </DialogDescription>
      </DialogHeader>

      <div className="space-y-4 py-4 max-h-[400px] overflow-y-auto">
        {extractedData && (
          <>
            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">Titulo</label>
              <p className="font-medium">{extractedData.title}</p>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">Descricao</label>
              <p className="text-sm text-muted-foreground line-clamp-4">
                {extractedData.description}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {extractedData.budget_max && (
                <div className="space-y-1">
                  <label className="text-xs font-medium text-muted-foreground">Orcamento</label>
                  <p className="font-medium">
                    {extractedData.budget_min
                      ? `${extractedData.currency} ${extractedData.budget_min.toLocaleString()} - ${extractedData.budget_max.toLocaleString()}`
                      : `${extractedData.currency} ${extractedData.budget_max.toLocaleString()}`}
                  </p>
                </div>
              )}

              {extractedData.deadline_days && (
                <div className="space-y-1">
                  <label className="text-xs font-medium text-muted-foreground">Prazo</label>
                  <p className="font-medium">{extractedData.deadline_days} dias</p>
                </div>
              )}

              {extractedData.complexity_estimate && (
                <div className="space-y-1">
                  <label className="text-xs font-medium text-muted-foreground">Complexidade</label>
                  <p className="font-medium">{extractedData.complexity_estimate}/10</p>
                </div>
              )}

              {extractedData.category && (
                <div className="space-y-1">
                  <label className="text-xs font-medium text-muted-foreground">Categoria</label>
                  <p className="font-medium capitalize">{extractedData.category.replace('_', ' ')}</p>
                </div>
              )}
            </div>

            {extractedData.required_skills && extractedData.required_skills.length > 0 && (
              <div className="space-y-1">
                <label className="text-xs font-medium text-muted-foreground">Skills</label>
                <div className="flex flex-wrap gap-1">
                  {extractedData.required_skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 bg-primary/10 text-primary text-xs rounded-full"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {extractedData.red_flags && extractedData.red_flags.length > 0 && (
              <div className="space-y-1">
                <label className="text-xs font-medium text-destructive">Red Flags</label>
                <div className="flex flex-wrap gap-1">
                  {extractedData.red_flags.map((flag, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 bg-destructive/10 text-destructive text-xs rounded-full"
                    >
                      {flag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {extractedData.opportunities && extractedData.opportunities.length > 0 && (
              <div className="space-y-1">
                <label className="text-xs font-medium text-green-500">Oportunidades</label>
                <div className="flex flex-wrap gap-1">
                  {extractedData.opportunities.map((opp, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 bg-green-500/10 text-green-500 text-xs rounded-full"
                    >
                      {opp}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <DialogFooter>
        <Button variant="outline" onClick={() => setStep('input')}>
          Voltar e Editar
        </Button>
        <Button onClick={handleConfirm}>
          <CheckCircle2 className="mr-2 h-4 w-4" />
          Confirmar
        </Button>
      </DialogFooter>
    </>
  );

  const renderSuccessStep = () => (
    <div className="py-12 text-center">
      <CheckCircle2 className="h-16 w-16 text-green-500 mx-auto mb-4" />
      <p className="text-lg font-medium">Oportunidade Criada!</p>
      <p className="text-sm text-muted-foreground mt-1">
        Redirecionando para a lista...
      </p>
    </div>
  );

  const renderErrorStep = () => (
    <>
      <DialogHeader>
        <DialogTitle className="flex items-center gap-2 text-destructive">
          <AlertTriangle className="h-5 w-5" />
          Erro na Extracao
        </DialogTitle>
      </DialogHeader>

      <div className="py-8 text-center">
        <p className="text-muted-foreground">{error}</p>
      </div>

      <DialogFooter>
        <Button variant="outline" onClick={handleClose}>
          Cancelar
        </Button>
        <Button onClick={() => setStep('input')}>Tentar Novamente</Button>
      </DialogFooter>
    </>
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        {step === 'input' && renderInputStep()}
        {step === 'loading' && renderLoadingStep()}
        {step === 'confirm' && renderConfirmStep()}
        {step === 'success' && renderSuccessStep()}
        {step === 'error' && renderErrorStep()}
      </DialogContent>
    </Dialog>
  );
}

export default SmartPasteDialog;
