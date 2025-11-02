import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Activity, Heart, Target, TrendingUp, Calendar, CheckCircle2 } from 'lucide-react';

export default function Dashboard() {
  const stats = [
    { label: 'Tarefas Pendentes', value: '12', icon: Activity, color: 'text-blue-500' },
    { label: 'Big Rocks Ativos', value: '4', icon: Target, color: 'text-teal-500' },
    { label: 'Concluídas (Semana)', value: '28', icon: CheckCircle2, color: 'text-green-500' },
    { label: 'Fase do Ciclo', value: 'Folicular', icon: Heart, color: 'text-pink-500' },
  ];

  const tasks = [
    { id: 1, title: 'Revisar código do projeto', priority: 1, deadline: 'Hoje', rock: 'Syssa - Estágio' },
    { id: 2, title: 'Estudar React avançado', priority: 2, deadline: 'Amanhã', rock: 'Estudos' },
    { id: 3, title: 'Exercícios físicos', priority: 3, deadline: 'Hoje', rock: 'Saúde' },
  ];

  const bigRocks = [
    { id: 1, name: 'Syssa - Estágio', tasks: 15, capacity: 75, color: 'bg-blue-500' },
    { id: 2, name: 'Estudos', tasks: 8, capacity: 45, color: 'bg-purple-500' },
    { id: 3, name: 'Saúde', tasks: 5, capacity: 30, color: 'bg-green-500' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Bem-vinda de volta! Aqui está seu resumo de hoje.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Inbox Rápido */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl">Inbox Rápido</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  Tarefas priorizadas para hoje
                </p>
              </div>
              <Button size="sm">Ver Todas</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className="flex items-center gap-4 p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                >
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-gray-300"
                  />
                  <div className="flex-1">
                    <div className="font-medium">{task.title}</div>
                    <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        task.priority === 1 ? 'bg-red-500/10 text-red-500' :
                        task.priority === 2 ? 'bg-orange-500/10 text-orange-500' :
                        'bg-blue-500/10 text-blue-500'
                      }`}>
                        P{task.priority}
                      </span>
                      <span>{task.rock}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <Calendar className="h-4 w-4" />
                    {task.deadline}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Big Rocks */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Big Rocks</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">Pilares de vida</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {bigRocks.map((rock) => (
                <div key={rock.id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`h-8 w-8 rounded-full ${rock.color} flex items-center justify-center text-white text-sm font-bold`}>
                        {rock.name[0]}
                      </div>
                      <div>
                        <div className="font-medium">{rock.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {rock.tasks} tarefas
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="relative h-2 bg-secondary/20 rounded-full overflow-hidden">
                    <div
                      className={`absolute top-0 left-0 h-full ${rock.color} transition-all`}
                      style={{ width: `${rock.capacity}%` }}
                    />
                  </div>
                  <div className="text-xs text-muted-foreground text-right">
                    {rock.capacity}% de capacidade
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Ações Rápidas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <Button className="flex-1">
              <Activity className="mr-2 h-4 w-4" />
              Nova Tarefa
            </Button>
            <Button variant="outline" className="flex-1">
              <TrendingUp className="mr-2 h-4 w-4" />
              Ver Analytics
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
