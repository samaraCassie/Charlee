import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { useToast } from '@/hooks/use-toast';
import { useNotificationStore } from '@/stores/notificationStore';
import {
  Bell,
  BellOff,
  Mail,
  Smartphone,
  Clock,
  AlertTriangle,
  Calendar,
  TrendingUp,
  Award,
  Info,
} from 'lucide-react';

export default function NotificationSettings() {
  const { toast } = useToast();
  const { preferences, fetchPreferences, updatePreference, loading } = useNotificationStore();
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchPreferences();
  }, [fetchPreferences]);

  const notificationTypeInfo = {
    task_due_soon: {
      icon: Clock,
      color: 'text-orange-500',
      label: 'Tarefa com Prazo Próximo',
      description: 'Notificações quando uma tarefa está próxima do prazo',
    },
    capacity_overload: {
      icon: AlertTriangle,
      color: 'text-red-500',
      label: 'Sobrecarga de Capacidade',
      description: 'Alertas quando você está com muitas tarefas',
    },
    cycle_phase_change: {
      icon: Calendar,
      color: 'text-purple-500',
      label: 'Mudança de Fase do Ciclo',
      description: 'Notificações de transição entre fases do ciclo menstrual',
    },
    freelance_invoice_ready: {
      icon: TrendingUp,
      color: 'text-green-500',
      label: 'Fatura Freelance Pronta',
      description: 'Quando uma fatura de freelance está pronta para envio',
    },
    system: {
      icon: Info,
      color: 'text-blue-500',
      label: 'Notificações do Sistema',
      description: 'Atualizações e avisos importantes do sistema',
    },
    achievement: {
      icon: Award,
      color: 'text-yellow-500',
      label: 'Conquistas',
      description: 'Celebração de metas alcançadas e marcos importantes',
    },
  };

  const handleToggleEnabled = async (notificationType: string, enabled: boolean) => {
    setSaving(true);
    try {
      await updatePreference(notificationType, { enabled });
      toast({
        title: 'Preferência atualizada',
        description: `Notificações de "${
          notificationTypeInfo[notificationType as keyof typeof notificationTypeInfo]?.label ||
          notificationType
        }" ${enabled ? 'ativadas' : 'desativadas'}`,
      });
    } catch (error) {
      toast({
        title: 'Erro ao atualizar',
        description: 'Não foi possível atualizar a preferência. Tente novamente.',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  const handleToggleChannel = async (
    notificationType: string,
    channel: 'in_app_enabled' | 'email_enabled' | 'push_enabled',
    value: boolean
  ) => {
    setSaving(true);
    try {
      const updates: Record<string, boolean> = {};
      updates[channel] = value;
      await updatePreference(notificationType, updates);
      toast({
        title: 'Canal atualizado',
        description: 'Preferência de canal atualizada com sucesso',
      });
    } catch (error) {
      toast({
        title: 'Erro ao atualizar',
        description: 'Não foi possível atualizar o canal. Tente novamente.',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
          <p className="text-muted-foreground">Carregando preferências...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Configurações de Notificações</h1>
          <p className="mt-2 text-muted-foreground">
            Gerencie como você deseja receber notificações do Charlee
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Tipos de Notificações
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {preferences.length === 0 ? (
            <div className="py-8 text-center text-muted-foreground">
              <BellOff className="mx-auto mb-4 h-12 w-12 opacity-50" />
              <p>Nenhuma preferência de notificação configurada</p>
              <Button
                onClick={() => fetchPreferences()}
                variant="outline"
                className="mt-4"
              >
                Criar Preferências Padrão
              </Button>
            </div>
          ) : (
            preferences.map((pref) => {
              const typeInfo =
                notificationTypeInfo[
                  pref.notificationType as keyof typeof notificationTypeInfo
                ];
              const Icon = typeInfo?.icon || Bell;

              return (
                <div
                  key={pref.id}
                  className="space-y-4 rounded-lg border p-4 transition-colors hover:bg-muted/50"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={`mt-1 ${typeInfo?.color || 'text-gray-500'}`}>
                        <Icon className="h-6 w-6" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold">
                          {typeInfo?.label || pref.notificationType}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          {typeInfo?.description || 'Notificações do sistema'}
                        </p>
                      </div>
                    </div>
                    <Switch
                      checked={pref.enabled}
                      onCheckedChange={(checked) =>
                        handleToggleEnabled(pref.notificationType, checked)
                      }
                      disabled={saving}
                    />
                  </div>

                  {pref.enabled && (
                    <div className="ml-10 space-y-3 border-l-2 border-muted pl-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Bell className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">No aplicativo</span>
                        </div>
                        <Switch
                          checked={pref.inAppEnabled}
                          onCheckedChange={(checked) =>
                            handleToggleChannel(
                              pref.notificationType,
                              'in_app_enabled',
                              checked
                            )
                          }
                          disabled={saving}
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Mail className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">Por e-mail</span>
                        </div>
                        <Switch
                          checked={pref.emailEnabled}
                          onCheckedChange={(checked) =>
                            handleToggleChannel(
                              pref.notificationType,
                              'email_enabled',
                              checked
                            )
                          }
                          disabled={saving}
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Smartphone className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">Push (celular)</span>
                        </div>
                        <Switch
                          checked={pref.pushEnabled}
                          onCheckedChange={(checked) =>
                            handleToggleChannel(
                              pref.notificationType,
                              'push_enabled',
                              checked
                            )
                          }
                          disabled={saving}
                        />
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Sobre as Notificações</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm text-muted-foreground">
          <div className="flex items-start gap-3">
            <Bell className="mt-0.5 h-4 w-4 shrink-0" />
            <p>
              <strong>No aplicativo:</strong> Você receberá notificações dentro do Charlee,
              visíveis no ícone de sino no topo da página.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <Mail className="mt-0.5 h-4 w-4 shrink-0" />
            <p>
              <strong>Por e-mail:</strong> Notificações serão enviadas para o e-mail cadastrado
              na sua conta.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <Smartphone className="mt-0.5 h-4 w-4 shrink-0" />
            <p>
              <strong>Push:</strong> Notificações push serão enviadas para dispositivos móveis
              quando o app estiver instalado (em desenvolvimento).
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
