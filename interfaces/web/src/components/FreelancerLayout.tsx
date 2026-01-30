import { Link, useLocation } from 'react-router-dom';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Briefcase, BarChart3, Settings, TrendingUp } from 'lucide-react';
import { useFreelancerStore } from '../stores/freelancerStore';

export default function FreelancerLayout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const { stats } = useFreelancerStore();

  const isActive = (path: string) => location.pathname === path;

  const menuItems = [
    {
      path: '/freelancer/opportunities',
      label: 'Oportunidades',
      icon: Briefcase,
      badge: stats?.pending,
    },
    {
      path: '/freelancer/analytics',
      label: 'Analytics',
      icon: BarChart3,
    },
    {
      path: '/freelancer/pricing',
      label: 'Configurações',
      icon: Settings,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link to="/" className="hover:text-foreground transition-colors">
          Home
        </Link>
        <span>/</span>
        <span className="text-foreground font-medium">Freelancer</span>
      </div>

      {/* Header with Stats */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                <Briefcase className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Sistema Freelancer</h1>
                <p className="text-sm text-muted-foreground">
                  Gestão inteligente de projetos e oportunidades
                </p>
              </div>
            </div>

            {stats && (
              <div className="flex gap-6">
                <div className="text-center">
                  <p className="text-2xl font-bold">{stats.total}</p>
                  <p className="text-xs text-muted-foreground">Total</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
                  <p className="text-xs text-muted-foreground">Pendentes</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{stats.accepted}</p>
                  <p className="text-xs text-muted-foreground">Aceitas</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold">${(stats.total_revenue || 0).toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground">Receita</p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Submenu Navigation */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors whitespace-nowrap ${
                active
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span className="text-sm font-medium">{item.label}</span>
              {item.badge !== undefined && item.badge > 0 && (
                <Badge variant={active ? 'secondary' : 'default'} className="ml-1 h-5 px-1.5">
                  {item.badge}
                </Badge>
              )}
            </Link>
          );
        })}
      </div>

      {/* Main Content */}
      <div>{children}</div>
    </div>
  );
}
