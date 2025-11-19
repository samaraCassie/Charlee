import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { useToast } from '@/hooks/use-toast';
import { notificationRulesService } from '@/services/notificationRulesService';
import type { NotificationRuleAPI } from '@/services/notificationRulesService';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Plus, Trash2, ArrowUp, ArrowDown, Zap, Filter } from 'lucide-react';

export default function NotificationRules() {
  const { toast } = useToast();
  const [rules, setRules] = useState<NotificationRuleAPI[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<NotificationRuleAPI | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    enabled: true,
    priority: 1,
    // Conditions
    condition_type: 'sender_contains',
    condition_value: '',
    // Actions
    action_type: 'categorize',
    action_value: '',
  });

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    setLoading(true);
    try {
      const response = await notificationRulesService.getRules();
      setRules(response.rules.sort((a, b) => b.priority - a.priority));
    } catch (error) {
      console.error('Error loading rules:', error);
      toast({
        title: 'Erro ao carregar',
        description: 'Não foi possível carregar as regras',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleToggleEnabled = async (ruleId: number, enabled: boolean) => {
    try {
      await notificationRulesService.updateRule(ruleId, { enabled });
      setRules(rules.map((r) => (r.id === ruleId ? { ...r, enabled } : r)));
      toast({
        title: 'Regra atualizada',
        description: `Regra ${enabled ? 'ativada' : 'desativada'} com sucesso`,
      });
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Não foi possível atualizar a regra',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (ruleId: number) => {
    if (!confirm('Tem certeza que deseja excluir esta regra?')) return;

    try {
      await notificationRulesService.deleteRule(ruleId);
      setRules(rules.filter((r) => r.id !== ruleId));
      toast({
        title: 'Regra excluída',
        description: 'A regra foi removida com sucesso',
      });
    } catch (error) {
      toast({
        title: 'Erro ao excluir',
        description: 'Não foi possível excluir a regra',
        variant: 'destructive',
      });
    }
  };

  const handleChangePriority = async (ruleId: number, delta: number) => {
    const rule = rules.find((r) => r.id === ruleId);
    if (!rule) return;

    const newPriority = Math.max(1, rule.priority + delta);

    try {
      await notificationRulesService.updateRule(ruleId, { priority: newPriority });
      setRules(
        rules
          .map((r) => (r.id === ruleId ? { ...r, priority: newPriority } : r))
          .sort((a, b) => b.priority - a.priority)
      );
      toast({
        title: 'Prioridade atualizada',
        description: 'A ordem das regras foi alterada',
      });
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Não foi possível atualizar a prioridade',
        variant: 'destructive',
      });
    }
  };

  const openAddDialog = () => {
    setEditingRule(null);
    setFormData({
      name: '',
      enabled: true,
      priority: 1,
      condition_type: 'sender_contains',
      condition_value: '',
      action_type: 'categorize',
      action_value: '',
    });
    setIsDialogOpen(true);
  };

  const handleSubmit = async () => {
    if (!formData.name || !formData.condition_value || !formData.action_value) {
      toast({
        title: 'Campos obrigatórios',
        description: 'Preencha todos os campos necessários',
        variant: 'destructive',
      });
      return;
    }

    try {
      const conditions = {
        [formData.condition_type]: formData.condition_value,
      };

      const actions = {
        [formData.action_type]: formData.action_value,
      };

      if (editingRule) {
        await notificationRulesService.updateRule(editingRule.id, {
          name: formData.name,
          enabled: formData.enabled,
          priority: formData.priority,
          conditions,
          actions,
        });
      } else {
        await notificationRulesService.createRule({
          name: formData.name,
          enabled: formData.enabled,
          priority: formData.priority,
          conditions,
          actions,
        });
      }

      await loadRules();
      setIsDialogOpen(false);
      toast({
        title: editingRule ? 'Regra atualizada' : 'Regra criada',
        description: 'Operação concluída com sucesso',
      });
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Não foi possível salvar a regra',
        variant: 'destructive',
      });
    }
  };

  const getConditionDescription = (conditions: Record<string, any>) => {
    const entries = Object.entries(conditions);
    if (entries.length === 0) return 'Nenhuma condição';

    const [type, value] = entries[0];
    const descriptions: Record<string, string> = {
      sender_contains: `Remetente contém "${value}"`,
      subject_contains: `Assunto contém "${value}"`,
      source_type: `Tipo de fonte é "${value}"`,
      category: `Categoria é "${value}"`,
      priority_greater_than: `Prioridade maior que ${value}`,
    };

    return descriptions[type] || `${type}: ${value}`;
  };

  const getActionDescription = (actions: Record<string, any>) => {
    const entries = Object.entries(actions);
    if (entries.length === 0) return 'Nenhuma ação';

    const [type, value] = entries[0];
    const descriptions: Record<string, string> = {
      categorize: `Categorizar como "${value}"`,
      archive: 'Arquivar automaticamente',
      mark_read: 'Marcar como lida',
      set_priority: `Definir prioridade ${value}`,
      add_tag: `Adicionar tag "${value}"`,
    };

    return descriptions[type] || `${type}: ${value}`;
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
          <p className="text-muted-foreground">Carregando regras...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Regras de Automação</h1>
          <p className="mt-2 text-muted-foreground">
            Configure regras para processar notificações automaticamente
          </p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openAddDialog}>
              <Plus className="mr-2 h-4 w-4" />
              Nova Regra
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>{editingRule ? 'Editar Regra' : 'Nova Regra'}</DialogTitle>
              <DialogDescription>
                Crie regras para automatizar o processamento de notificações
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Nome da Regra</Label>
                <Input
                  id="name"
                  placeholder="Ex: Filtrar emails de trabalho, Arquivar spam, etc."
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="priority">Prioridade</Label>
                <Input
                  id="priority"
                  type="number"
                  min="1"
                  max="100"
                  value={formData.priority}
                  onChange={(e) =>
                    setFormData({ ...formData, priority: parseInt(e.target.value) || 1 })
                  }
                />
                <p className="text-xs text-muted-foreground">
                  Regras com maior prioridade são executadas primeiro
                </p>
              </div>

              <div className="space-y-2 rounded-lg border p-4">
                <div className="flex items-center gap-2 text-sm font-semibold">
                  <Filter className="h-4 w-4" />
                  Condição
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="condition_type">Quando</Label>
                  <Select
                    value={formData.condition_type}
                    onValueChange={(value) => setFormData({ ...formData, condition_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sender_contains">Remetente contém</SelectItem>
                      <SelectItem value="subject_contains">Assunto contém</SelectItem>
                      <SelectItem value="source_type">Tipo de fonte é</SelectItem>
                      <SelectItem value="category">Categoria é</SelectItem>
                      <SelectItem value="priority_greater_than">Prioridade maior que</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="condition_value">Valor</Label>
                  <Input
                    id="condition_value"
                    placeholder="Digite o valor da condição..."
                    value={formData.condition_value}
                    onChange={(e) => setFormData({ ...formData, condition_value: e.target.value })}
                  />
                </div>
              </div>

              <div className="space-y-2 rounded-lg border p-4">
                <div className="flex items-center gap-2 text-sm font-semibold">
                  <Zap className="h-4 w-4" />
                  Ação
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="action_type">Executar</Label>
                  <Select
                    value={formData.action_type}
                    onValueChange={(value) => setFormData({ ...formData, action_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="categorize">Categorizar como</SelectItem>
                      <SelectItem value="archive">Arquivar</SelectItem>
                      <SelectItem value="mark_read">Marcar como lida</SelectItem>
                      <SelectItem value="set_priority">Definir prioridade</SelectItem>
                      <SelectItem value="add_tag">Adicionar tag</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="action_value">Valor</Label>
                  {formData.action_type === 'categorize' ? (
                    <Select
                      value={formData.action_value}
                      onValueChange={(value) => setFormData({ ...formData, action_value: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione uma categoria" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="urgente">Urgente</SelectItem>
                        <SelectItem value="importante">Importante</SelectItem>
                        <SelectItem value="social">Social</SelectItem>
                        <SelectItem value="trabalho">Trabalho</SelectItem>
                        <SelectItem value="spam">Spam</SelectItem>
                        <SelectItem value="outros">Outros</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : formData.action_type === 'set_priority' ? (
                    <Input
                      id="action_value"
                      type="number"
                      min="1"
                      max="10"
                      placeholder="1-10"
                      value={formData.action_value}
                      onChange={(e) => setFormData({ ...formData, action_value: e.target.value })}
                    />
                  ) : (
                    <Input
                      id="action_value"
                      placeholder="Digite o valor da ação..."
                      value={formData.action_value}
                      onChange={(e) => setFormData({ ...formData, action_value: e.target.value })}
                    />
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="enabled"
                  checked={formData.enabled}
                  onCheckedChange={(checked) => setFormData({ ...formData, enabled: checked })}
                />
                <Label htmlFor="enabled">Ativar regra imediatamente</Label>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSubmit}>
                {editingRule ? 'Atualizar' : 'Criar'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {rules.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Zap className="mx-auto mb-4 h-12 w-12 opacity-50" />
            <h3 className="mb-2 text-lg font-semibold">Nenhuma regra configurada</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Crie regras para automatizar o processamento de notificações
            </p>
            <Button onClick={openAddDialog}>
              <Plus className="mr-2 h-4 w-4" />
              Criar Primeira Regra
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {rules.map((rule, index) => (
            <Card key={rule.id}>
              <CardHeader className="flex flex-row items-start justify-between space-y-0">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-base">{rule.name}</CardTitle>
                    <span className="rounded-full bg-muted px-2 py-1 text-xs font-medium">
                      Prioridade: {rule.priority}
                    </span>
                    {!rule.enabled && (
                      <span className="rounded-full bg-destructive/10 px-2 py-1 text-xs font-medium text-destructive">
                        Desativada
                      </span>
                    )}
                  </div>
                  <CardDescription className="mt-2 space-y-1">
                    <div className="flex items-center gap-2">
                      <Filter className="h-3 w-3" />
                      <span>{getConditionDescription(rule.conditions)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Zap className="h-3 w-3" />
                      <span>{getActionDescription(rule.actions)}</span>
                    </div>
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex flex-col gap-1">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleChangePriority(rule.id, 1)}
                      disabled={index === 0}
                      className="h-6 w-6 p-0"
                    >
                      <ArrowUp className="h-3 w-3" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleChangePriority(rule.id, -1)}
                      disabled={index === rules.length - 1}
                      className="h-6 w-6 p-0"
                    >
                      <ArrowDown className="h-3 w-3" />
                    </Button>
                  </div>
                  <Switch
                    checked={rule.enabled}
                    onCheckedChange={(checked) => handleToggleEnabled(rule.id, checked)}
                  />
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleDelete(rule.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </CardHeader>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
