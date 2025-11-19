import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { useToast } from '@/hooks/use-toast';
import { notificationSourcesService } from '@/services/notificationSourcesService';
import type { NotificationSourceAPI } from '@/services/notificationSourcesService';
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
import {
  Mail,
  Github,
  MessageSquare,
  Send,
  Hash,
  Trello,
  FileText,
  Phone,
  Linkedin,
  Plus,
  Trash2,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
} from 'lucide-react';

const sourceTypeIcons: Record<string, any> = {
  email: Mail,
  github: Github,
  slack: MessageSquare,
  discord: Hash,
  telegram: Send,
  trello: Trello,
  notion: FileText,
  whatsapp: Phone,
  linkedin: Linkedin,
};

const sourceTypeLabels: Record<string, string> = {
  email: 'Email (IMAP)',
  github: 'GitHub',
  slack: 'Slack',
  discord: 'Discord',
  telegram: 'Telegram',
  trello: 'Trello',
  notion: 'Notion',
  whatsapp: 'WhatsApp Business',
  linkedin: 'LinkedIn',
};

export default function NotificationSources() {
  const { toast } = useToast();
  const [sources, setSources] = useState<NotificationSourceAPI[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingSource, setEditingSource] = useState<NotificationSourceAPI | null>(null);
  const [collectingSourceId, setCollectingSourceId] = useState<number | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    source_type: 'email',
    name: '',
    enabled: true,
    credentials: {} as Record<string, string>,
    settings: {} as Record<string, any>,
  });

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    setLoading(true);
    try {
      const response = await notificationSourcesService.getSources();
      setSources(response.sources);
    } catch (error) {
      console.error('Error loading sources:', error);
      toast({
        title: 'Erro ao carregar',
        description: 'Não foi possível carregar as fontes de notificação',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleToggleEnabled = async (sourceId: number, enabled: boolean) => {
    try {
      await notificationSourcesService.updateSource(sourceId, { enabled });
      setSources(sources.map((s) => (s.id === sourceId ? { ...s, enabled } : s)));
      toast({
        title: 'Fonte atualizada',
        description: `Fonte ${enabled ? 'ativada' : 'desativada'} com sucesso`,
      });
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Não foi possível atualizar a fonte',
        variant: 'destructive',
      });
    }
  };

  const handleTestAuth = async (sourceId: number) => {
    try {
      const result = await notificationSourcesService.testAuthentication(sourceId);
      toast({
        title: result.success ? 'Autenticação bem-sucedida' : 'Falha na autenticação',
        description: result.message,
        variant: result.success ? 'default' : 'destructive',
      });
    } catch (error) {
      toast({
        title: 'Erro ao testar',
        description: 'Não foi possível testar a autenticação',
        variant: 'destructive',
      });
    }
  };

  const handleCollectNow = async (sourceId: number) => {
    setCollectingSourceId(sourceId);
    try {
      const result = await notificationSourcesService.collectNow(sourceId);
      toast({
        title: 'Coleta concluída',
        description: `${result.collected} notificações coletadas, ${result.spam_filtered} filtradas como spam`,
      });
      // Atualizar last_sync
      setSources(
        sources.map((s) =>
          s.id === sourceId ? { ...s, last_sync: new Date().toISOString() } : s
        )
      );
    } catch (error) {
      toast({
        title: 'Erro na coleta',
        description: 'Não foi possível coletar notificações',
        variant: 'destructive',
      });
    } finally {
      setCollectingSourceId(null);
    }
  };

  const handleDelete = async (sourceId: number) => {
    if (!confirm('Tem certeza que deseja excluir esta fonte?')) return;

    try {
      await notificationSourcesService.deleteSource(sourceId);
      setSources(sources.filter((s) => s.id !== sourceId));
      toast({
        title: 'Fonte excluída',
        description: 'A fonte foi removida com sucesso',
      });
    } catch (error) {
      toast({
        title: 'Erro ao excluir',
        description: 'Não foi possível excluir a fonte',
        variant: 'destructive',
      });
    }
  };

  const openAddDialog = () => {
    setEditingSource(null);
    setFormData({
      source_type: 'email',
      name: '',
      enabled: true,
      credentials: {},
      settings: {},
    });
    setIsDialogOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingSource) {
        await notificationSourcesService.updateSource(editingSource.id, {
          name: formData.name,
          enabled: formData.enabled,
          credentials: formData.credentials,
          settings: formData.settings,
        });
      } else {
        await notificationSourcesService.createSource(formData);
      }

      await loadSources();
      setIsDialogOpen(false);
      toast({
        title: editingSource ? 'Fonte atualizada' : 'Fonte criada',
        description: 'Operação concluída com sucesso',
      });
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Não foi possível salvar a fonte',
        variant: 'destructive',
      });
    }
  };

  const renderCredentialFields = () => {
    switch (formData.source_type) {
      case 'email':
        return (
          <>
            <div className="grid gap-2">
              <Label htmlFor="imap_server">Servidor IMAP</Label>
              <Input
                id="imap_server"
                placeholder="imap.gmail.com"
                value={formData.credentials.imap_server || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    credentials: { ...formData.credentials, imap_server: e.target.value },
                  })
                }
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="username">Email/Usuário</Label>
              <Input
                id="username"
                type="email"
                value={formData.credentials.username || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    credentials: { ...formData.credentials, username: e.target.value },
                  })
                }
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Senha/App Password</Label>
              <Input
                id="password"
                type="password"
                value={formData.credentials.password || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    credentials: { ...formData.credentials, password: e.target.value },
                  })
                }
              />
            </div>
          </>
        );

      case 'github':
        return (
          <div className="grid gap-2">
            <Label htmlFor="token">Token de Acesso Pessoal</Label>
            <Input
              id="token"
              type="password"
              placeholder="ghp_..."
              value={formData.credentials.token || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  credentials: { ...formData.credentials, token: e.target.value },
                })
              }
            />
            <p className="text-xs text-muted-foreground">
              Crie em: Settings → Developer settings → Personal access tokens
            </p>
          </div>
        );

      case 'slack':
        return (
          <div className="grid gap-2">
            <Label htmlFor="token">Bot User OAuth Token</Label>
            <Input
              id="token"
              type="password"
              placeholder="xoxb-..."
              value={formData.credentials.token || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  credentials: { ...formData.credentials, token: e.target.value },
                })
              }
            />
            <p className="text-xs text-muted-foreground">
              Configure um app Slack e obtenha o token do bot
            </p>
          </div>
        );

      case 'discord':
        return (
          <div className="grid gap-2">
            <Label htmlFor="token">Bot Token</Label>
            <Input
              id="token"
              type="password"
              value={formData.credentials.token || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  credentials: { ...formData.credentials, token: e.target.value },
                })
              }
            />
            <p className="text-xs text-muted-foreground">
              Crie um bot no Discord Developer Portal
            </p>
          </div>
        );

      case 'telegram':
        return (
          <div className="grid gap-2">
            <Label htmlFor="bot_token">Bot Token</Label>
            <Input
              id="bot_token"
              type="password"
              value={formData.credentials.bot_token || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  credentials: { ...formData.credentials, bot_token: e.target.value },
                })
              }
            />
            <p className="text-xs text-muted-foreground">
              Crie um bot usando @BotFather no Telegram
            </p>
          </div>
        );

      case 'trello':
        return (
          <>
            <div className="grid gap-2">
              <Label htmlFor="api_key">API Key</Label>
              <Input
                id="api_key"
                type="password"
                value={formData.credentials.api_key || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    credentials: { ...formData.credentials, api_key: e.target.value },
                  })
                }
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="token">Token</Label>
              <Input
                id="token"
                type="password"
                value={formData.credentials.token || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    credentials: { ...formData.credentials, token: e.target.value },
                  })
                }
              />
            </div>
            <p className="text-xs text-muted-foreground">
              Obtenha em: https://trello.com/app-key
            </p>
          </>
        );

      case 'notion':
        return (
          <div className="grid gap-2">
            <Label htmlFor="token">Integration Token</Label>
            <Input
              id="token"
              type="password"
              placeholder="secret_..."
              value={formData.credentials.token || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  credentials: { ...formData.credentials, token: e.target.value },
                })
              }
            />
            <p className="text-xs text-muted-foreground">
              Crie uma integração em: https://www.notion.so/my-integrations
            </p>
          </div>
        );

      case 'whatsapp':
        return (
          <>
            <div className="grid gap-2">
              <Label htmlFor="access_token">Access Token</Label>
              <Input
                id="access_token"
                type="password"
                value={formData.credentials.access_token || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    credentials: { ...formData.credentials, access_token: e.target.value },
                  })
                }
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="phone_number_id">Phone Number ID</Label>
              <Input
                id="phone_number_id"
                value={formData.credentials.phone_number_id || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    credentials: { ...formData.credentials, phone_number_id: e.target.value },
                  })
                }
              />
            </div>
            <p className="text-xs text-muted-foreground">
              Configure WhatsApp Business Cloud API
            </p>
          </>
        );

      case 'linkedin':
        return (
          <div className="grid gap-2">
            <Label htmlFor="access_token">Access Token</Label>
            <Input
              id="access_token"
              type="password"
              value={formData.credentials.access_token || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  credentials: { ...formData.credentials, access_token: e.target.value },
                })
              }
            />
            <p className="text-xs text-muted-foreground">
              Obtenha via OAuth 2.0 do LinkedIn
            </p>
          </div>
        );

      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
          <p className="text-muted-foreground">Carregando fontes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Fontes de Notificação</h1>
          <p className="mt-2 text-muted-foreground">
            Conecte e gerencie suas fontes externas de notificações
          </p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openAddDialog}>
              <Plus className="mr-2 h-4 w-4" />
              Adicionar Fonte
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>{editingSource ? 'Editar Fonte' : 'Nova Fonte'}</DialogTitle>
              <DialogDescription>
                Configure uma fonte externa para coletar notificações automaticamente
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="source_type">Tipo de Fonte</Label>
                <Select
                  value={formData.source_type}
                  onValueChange={(value) =>
                    setFormData({ ...formData, source_type: value, credentials: {} })
                  }
                  disabled={!!editingSource}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(sourceTypeLabels).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="name">Nome da Fonte</Label>
                <Input
                  id="name"
                  placeholder="Ex: Email Pessoal, GitHub Work, etc."
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>

              {renderCredentialFields()}

              <div className="flex items-center space-x-2">
                <Switch
                  id="enabled"
                  checked={formData.enabled}
                  onCheckedChange={(checked) => setFormData({ ...formData, enabled: checked })}
                />
                <Label htmlFor="enabled">Habilitar coleta automática</Label>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSubmit}>
                {editingSource ? 'Atualizar' : 'Criar'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {sources.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <MessageSquare className="mx-auto mb-4 h-12 w-12 opacity-50" />
            <h3 className="mb-2 text-lg font-semibold">Nenhuma fonte configurada</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Adicione fontes externas para começar a coletar notificações
            </p>
            <Button onClick={openAddDialog}>
              <Plus className="mr-2 h-4 w-4" />
              Adicionar Primeira Fonte
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {sources.map((source) => {
            const Icon = sourceTypeIcons[source.source_type] || MessageSquare;
            const label = sourceTypeLabels[source.source_type] || source.source_type;

            return (
              <Card key={source.id}>
                <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                  <div className="flex items-center gap-2">
                    <Icon className="h-5 w-5" />
                    <div>
                      <CardTitle className="text-base">{source.name}</CardTitle>
                      <CardDescription className="text-xs">{label}</CardDescription>
                    </div>
                  </div>
                  <Switch
                    checked={source.enabled}
                    onCheckedChange={(checked) => handleToggleEnabled(source.id, checked)}
                  />
                </CardHeader>
                <CardContent className="space-y-3">
                  {source.last_sync && (
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      <span>
                        Última sincronização:{' '}
                        {new Date(source.last_sync).toLocaleString('pt-BR')}
                      </span>
                    </div>
                  )}

                  {source.last_error && (
                    <div className="flex items-center gap-2 text-xs text-destructive">
                      <XCircle className="h-3 w-3" />
                      <span>{source.last_error}</span>
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1"
                      onClick={() => handleTestAuth(source.id)}
                    >
                      <CheckCircle className="mr-1 h-3 w-3" />
                      Testar
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1"
                      onClick={() => handleCollectNow(source.id)}
                      disabled={collectingSourceId === source.id}
                    >
                      <RefreshCw
                        className={`mr-1 h-3 w-3 ${collectingSourceId === source.id ? 'animate-spin' : ''}`}
                      />
                      Coletar
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDelete(source.id)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
