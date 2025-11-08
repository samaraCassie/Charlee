import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Heart, Calendar, TrendingUp, Activity, Sparkles, Plus } from 'lucide-react';
import { useCycleStore } from '@/stores/cycleStore';
import { useToast } from '@/hooks/use-toast';
import { differenceInDays } from 'date-fns';

export default function Wellness() {
  const { toast } = useToast();
  const [newEntryDialogOpen, setNewEntryDialogOpen] = useState(false);
  const [energyLevel, setEnergyLevel] = useState(5);
  const [focusLevel, setFocusLevel] = useState(5);
  const [creativityLevel, setCreativityLevel] = useState(5);
  const [symptoms, setSymptoms] = useState('');
  const [notes, setNotes] = useState('');

  const {
    lastPeriodStart,
    averageCycleLength,
    currentPhase,
    getCurrentPhase,
    getPhaseRecommendations,
    setLastPeriodStart,
  } = useCycleStore();

  useEffect(() => {
    getCurrentPhase();
  }, [getCurrentPhase]);

  const recommendations = getPhaseRecommendations(currentPhase);

  const phaseInfo = {
    menstrual: {
      name: 'Menstrual',
      color: 'bg-red-500',
      icon: '🩸',
      description: 'Fase de renovação e introspecção',
      energy: 'Baixa a média',
      focus: 'Tarefas leves e autocuidado',
    },
    follicular: {
      name: 'Folicular',
      color: 'bg-green-500',
      icon: '🌱',
      description: 'Fase de crescimento e energia',
      energy: 'Alta',
      focus: 'Novos projetos e criatividade',
    },
    ovulation: {
      name: 'Ovulação',
      color: 'bg-yellow-500',
      icon: '⭐',
      description: 'Pico de energia e confiança',
      energy: 'Máxima',
      focus: 'Apresentações e networking',
    },
    luteal: {
      name: 'Lútea',
      color: 'bg-purple-500',
      icon: '🌙',
      description: 'Fase de finalização e desaceleração',
      energy: 'Decrescente',
      focus: 'Concluir projetos em andamento',
    },
  };

  const currentPhaseInfo = phaseInfo[currentPhase as keyof typeof phaseInfo] || phaseInfo.follicular;

  const daysSinceLastPeriod = lastPeriodStart
    ? differenceInDays(new Date(), new Date(lastPeriodStart))
    : 0;

  const dayInCycle = daysSinceLastPeriod % averageCycleLength;
  const daysUntilNextPeriod = averageCycleLength - dayInCycle;

  const handleSaveEntry = () => {
    toast({
      title: 'Registro salvo',
      description: 'Seus dados foram salvos com sucesso!',
    });

    setEnergyLevel(5);
    setFocusLevel(5);
    setCreativityLevel(5);
    setSymptoms('');
    setNotes('');
    setNewEntryDialogOpen(false);
  };

  const LevelSlider = ({
    label,
    value,
    onChange,
  }: {
    label: string;
    value: number;
    onChange: (value: number) => void;
  }) => (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium">{label}</label>
        <span className="text-sm text-muted-foreground">{value}/10</span>
      </div>
      <input
        type="range"
        min="1"
        max="10"
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
      />
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>Baixo</span>
        <span>Alto</span>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 md:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-4xl font-bold tracking-tight">Wellness</h1>
          <p className="text-muted-foreground mt-1 md:mt-2 text-sm md:text-base">
            Acompanhe seu ciclo menstrual e bem-estar.
          </p>
        </div>
        <Button onClick={() => setNewEntryDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Novo Registro
        </Button>
      </div>

      {/* Current Phase Card */}
      <Card className={`border-2 ${currentPhaseInfo.color}/20 bg-gradient-to-br from-${currentPhaseInfo.color}/5 to-transparent`}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`h-16 w-16 rounded-full ${currentPhaseInfo.color} flex items-center justify-center text-3xl`}>
                {currentPhaseInfo.icon}
              </div>
              <div>
                <CardTitle className="text-2xl">Fase {currentPhaseInfo.name}</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  {currentPhaseInfo.description}
                </p>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-card">
              <Activity className="h-8 w-8 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">Nível de Energia</p>
                <p className="font-semibold">{currentPhaseInfo.energy}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-card">
              <TrendingUp className="h-8 w-8 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">Foco em</p>
                <p className="font-semibold">{currentPhaseInfo.focus}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-card">
              <Calendar className="h-8 w-8 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">Próximo período em</p>
                <p className="font-semibold">{daysUntilNextPeriod} dias</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Cycle Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Informações do Ciclo
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Último período começou em</label>
              <input
                type="date"
                value={lastPeriodStart || ''}
                onChange={(e) => setLastPeriodStart(e.target.value)}
                className="w-full px-3 py-2 border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Duração média do ciclo (dias)</label>
              <input
                type="number"
                value={averageCycleLength}
                readOnly
                className="w-full px-3 py-2 border rounded-md bg-secondary/50 text-foreground cursor-not-allowed"
              />
              <p className="text-xs text-muted-foreground">
                Calculado automaticamente com base nos seus registros
              </p>
            </div>

            <div className="pt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Dia do ciclo atual</span>
                <span className="font-medium">{dayInCycle} de {averageCycleLength}</span>
              </div>
              <div className="relative h-2 bg-secondary/20 rounded-full overflow-hidden">
                <div
                  className={`absolute top-0 left-0 h-full ${currentPhaseInfo.color} transition-all`}
                  style={{ width: `${(dayInCycle / averageCycleLength) * 100}%` }}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recommendations */}
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Recomendações para Hoje
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {recommendations.map((rec, index) => (
                <li key={index} className="flex items-start gap-2">
                  <Heart className="h-5 w-5 text-primary mt-0.5 shrink-0" />
                  <span className="text-sm">{rec}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Cycle Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Linha do Tempo do Ciclo</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-2">
            {Object.entries(phaseInfo).map(([key, phase]) => {
              const isCurrentPhase = currentPhase === key;
              return (
                <div
                  key={key}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    isCurrentPhase
                      ? `${phase.color} border-current text-white`
                      : 'bg-secondary/20 border-transparent'
                  }`}
                >
                  <div className="text-center">
                    <div className="text-3xl mb-2">{phase.icon}</div>
                    <p className="font-semibold text-sm">{phase.name}</p>
                    <p className={`text-xs mt-1 ${isCurrentPhase ? 'text-white/80' : 'text-muted-foreground'}`}>
                      {phase.energy}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* New Entry Dialog */}
      <Dialog open={newEntryDialogOpen} onOpenChange={setNewEntryDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Novo Registro de Bem-estar</DialogTitle>
            <DialogDescription>
              Registre como você está se sentindo hoje.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6 py-4">
            <LevelSlider
              label="Nível de Energia"
              value={energyLevel}
              onChange={setEnergyLevel}
            />

            <LevelSlider
              label="Nível de Foco"
              value={focusLevel}
              onChange={setFocusLevel}
            />

            <LevelSlider
              label="Nível de Criatividade"
              value={creativityLevel}
              onChange={setCreativityLevel}
            />

            <div className="space-y-2">
              <label className="text-sm font-medium">Sintomas</label>
              <input
                type="text"
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                placeholder="Ex: Cólicas leves, dor de cabeça"
                className="w-full px-3 py-2 border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Notas</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Como você está se sentindo hoje?"
                rows={3}
                className="w-full px-3 py-2 border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setNewEntryDialogOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleSaveEntry}>Salvar Registro</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
