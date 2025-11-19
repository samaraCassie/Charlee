import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Moon, Sun, Menu } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import BigRocks from './pages/BigRocks';
import BigRockDetail from './pages/BigRockDetail';
import BigRockAnalytics from './pages/BigRockAnalytics';
import Chat from './pages/Chat';
import Tasks from './pages/Tasks';
import Wellness from './pages/Wellness';
import TranscriptionHistory from './pages/TranscriptionHistory';
import NotificationSettings from './pages/NotificationSettings';
import NotificationSources from './pages/NotificationSources';
import NotificationRules from './pages/NotificationRules';
import NotificationDashboard from './pages/NotificationDashboard';
import { Button } from './components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from './components/ui/sheet';
import { Toaster } from './components/ui/toaster';

function AppContent() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode(!darkMode);

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 md:h-16 items-center justify-between px-4">
          <div className="flex items-center gap-3 md:gap-6">
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden h-9 w-9"
              onClick={() => setMobileMenuOpen(true)}
            >
              <Menu className="h-4 w-4" />
            </Button>
            <div className="flex items-center gap-2">
              <div className="h-7 w-7 md:h-8 md:w-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                C
              </div>
              <h1 className="text-lg md:text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Charlee
              </h1>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-6">
            <Link
              to="/"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isActive('/') ? '' : 'text-muted-foreground'
              }`}
            >
              Dashboard
            </Link>
            <Link
              to="/analytics"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isActive('/analytics') ? '' : 'text-muted-foreground'
              }`}
            >
              Analytics
            </Link>
            <Link
              to="/big-rocks"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isActive('/big-rocks') ? '' : 'text-muted-foreground'
              }`}
            >
              Big Rocks
            </Link>
            <Link
              to="/chat"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isActive('/chat') ? '' : 'text-muted-foreground'
              }`}
            >
              Chat
            </Link>
            <Link
              to="/transcriptions"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isActive('/transcriptions') ? '' : 'text-muted-foreground'
              }`}
            >
              Histórico
            </Link>
            <Link
              to="/notifications/dashboard"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isActive('/notifications/dashboard') ? '' : 'text-muted-foreground'
              }`}
            >
              Notificações
            </Link>
          </nav>

          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleDarkMode}
              className="rounded-full h-9 w-9 md:h-10 md:w-10"
            >
              {darkMode ? (
                <Sun className="h-4 w-4 md:h-5 md:w-5 transition-all" />
              ) : (
                <Moon className="h-4 w-4 md:h-5 md:w-5 transition-all" />
              )}
              <span className="sr-only">Toggle theme</span>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container px-4 py-4 md:py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/big-rocks" element={<BigRocks />} />
          <Route path="/big-rocks/:id" element={<BigRockDetail />} />
          <Route path="/big-rocks/:id/analytics" element={<BigRockAnalytics />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/wellness" element={<Wellness />} />
          <Route path="/transcriptions" element={<TranscriptionHistory />} />
          <Route path="/notifications/settings" element={<NotificationSettings />} />
          <Route path="/notifications/sources" element={<NotificationSources />} />
          <Route path="/notifications/rules" element={<NotificationRules />} />
          <Route path="/notifications/dashboard" element={<NotificationDashboard />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="border-t">
        <div className="container flex h-14 md:h-16 items-center justify-center px-4 text-xs md:text-sm text-muted-foreground">
          <p className="text-center">
            Feito com ❤️ por Samara · Powered by Charlee AI
          </p>
        </div>
      </footer>

      {/* Mobile Navigation Sheet */}
      <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
        <SheetContent side="left" className="w-[280px] sm:w-[320px]">
          <SheetHeader>
            <SheetTitle>
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                  C
                </div>
                <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Charlee
                </span>
              </div>
            </SheetTitle>
          </SheetHeader>
          <nav className="flex flex-col gap-4 mt-8">
            <Link
              to="/"
              className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors hover:bg-accent ${
                isActive('/') ? '' : 'text-muted-foreground hover:text-foreground'
              }`}
              onClick={() => setMobileMenuOpen(false)}
            >
              Dashboard
            </Link>
            <Link
              to="/analytics"
              className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors hover:bg-accent ${
                isActive('/analytics') ? '' : 'text-muted-foreground hover:text-foreground'
              }`}
              onClick={() => setMobileMenuOpen(false)}
            >
              Analytics
            </Link>
            <Link
              to="/big-rocks"
              className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors hover:bg-accent ${
                isActive('/big-rocks') ? '' : 'text-muted-foreground hover:text-foreground'
              }`}
              onClick={() => setMobileMenuOpen(false)}
            >
              Big Rocks
            </Link>
            <Link
              to="/chat"
              className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors hover:bg-accent ${
                isActive('/chat') ? '' : 'text-muted-foreground hover:text-foreground'
              }`}
              onClick={() => setMobileMenuOpen(false)}
            >
              Chat
            </Link>
            <Link
              to="/transcriptions"
              className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors hover:bg-accent ${
                isActive('/transcriptions') ? '' : 'text-muted-foreground hover:text-foreground'
              }`}
              onClick={() => setMobileMenuOpen(false)}
            >
              Histórico
            </Link>
            <Link
              to="/notifications/dashboard"
              className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors hover:bg-accent ${
                isActive('/notifications/dashboard') ? '' : 'text-muted-foreground hover:text-foreground'
              }`}
              onClick={() => setMobileMenuOpen(false)}
            >
              Notificações
            </Link>
          </nav>
        </SheetContent>
      </Sheet>
      <Toaster />
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}
