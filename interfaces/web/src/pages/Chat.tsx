import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Send, Sparkles, Calendar, Target, Activity, Heart, Loader2 } from 'lucide-react';
import { useChatStore } from '@/stores/chatStore';
import { useTaskStore } from '@/stores/taskStore';
import { useBigRockStore } from '@/stores/bigRockStore';
import { useCycleStore } from '@/stores/cycleStore';
import { useToast } from '@/hooks/use-toast';

export default function Chat() {
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, isTyping, sendMessage, error } = useChatStore();
  const { getPendingTasks } = useTaskStore();
  const { bigRocks } = useBigRockStore();
  const { currentPhase, getPhaseRecommendations } = useCycleStore();
  const { toast } = useToast();

  const quickActions = [
    {
      icon: Target,
      label: 'Planejar meu dia',
      prompt: 'Me ajude a planejar meu dia considerando meus Big Rocks e prioridades',
    },
    {
      icon: Calendar,
      label: 'Análise do ciclo',
      prompt: 'Como está minha produtividade em relação ao meu ciclo menstrual?',
    },
    {
      icon: Activity,
      label: 'Revisar tarefas',
      prompt: 'Mostre um resumo das minhas tarefas pendentes e atrasadas',
    },
    {
      icon: Heart,
      label: 'Bem-estar',
      prompt: 'Dê sugestões para melhorar meu bem-estar baseado no meu ciclo atual',
    },
  ];

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    try {
      await sendMessage(message);
      setMessage('');
    } catch (e) {
      toast({
        title: 'Erro',
        description: `Não foi possível enviar a mensagem. Tente novamente. ${e}`,
        variant: 'destructive',
      });
    }
  };

  const handleQuickAction = (prompt: string) => {
    setMessage(prompt);
  };

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  const pendingTasks = getPendingTasks();
  const recommendations = getPhaseRecommendations(currentPhase);

  // Auto-scroll to bottom when new message arrives
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Show error toast
  useEffect(() => {
    if (error) {
      toast({
        title: 'Erro',
        description: error,
        variant: 'destructive',
      });
    }
  }, [error, toast]);

  return (
    <div className="space-y-6 md:space-y-8">
      <div>
        <h1 className="text-2xl md:text-4xl font-bold tracking-tight">Chat com Charlee</h1>
        <p className="text-muted-foreground mt-1 md:mt-2 text-sm md:text-base">
          Converse com sua assistente pessoal alimentada por IA.
        </p>
      </div>

      <div className="grid gap-4 md:gap-6 lg:grid-cols-3">
        {/* Chat Area */}
        <Card className="lg:col-span-2 flex flex-col h-[600px]">
          <CardHeader className="border-b">
            <CardTitle className="flex items-center gap-2 text-lg md:text-xl">
              <Sparkles className="h-5 w-5 text-purple-500" />
              Charlee AI
            </CardTitle>
          </CardHeader>

          {/* Messages */}
          <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-foreground'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  <span className="text-xs opacity-70 mt-1 block">
                    {formatTime(msg.timestamp)}
                  </span>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-muted text-foreground rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Charlee está digitando...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </CardContent>

          {/* Input */}
          <div className="border-t p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isTyping && handleSendMessage()}
                placeholder="Digite sua mensagem..."
                disabled={isTyping}
                className="flex-1 px-4 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
              />
              <Button onClick={handleSendMessage} size="icon" disabled={isTyping || !message.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Card>

        {/* Quick Actions & Info */}
        <div className="space-y-4">
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Ações Rápidas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {quickActions.map((action, index) => {
                const Icon = action.icon;
                return (
                  <Button
                    key={index}
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => handleQuickAction(action.prompt)}
                    disabled={isTyping}
                  >
                    <Icon className="mr-2 h-4 w-4" />
                    {action.label}
                  </Button>
                );
              })}
            </CardContent>
          </Card>

          {/* Context Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Contexto Atual</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Tarefas Pendentes</span>
                <span className="font-medium">{pendingTasks.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Fase do Ciclo</span>
                <span className="font-medium capitalize">{currentPhase}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Big Rocks Ativos</span>
                <span className="font-medium">{bigRocks.length}</span>
              </div>
            </CardContent>
          </Card>

          {/* Tips */}
          <Card className="border-purple-500/20 bg-purple-500/5">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-purple-500" />
                Dica
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {recommendations[0] || 'Mantenha o foco nas suas prioridades!'}
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
