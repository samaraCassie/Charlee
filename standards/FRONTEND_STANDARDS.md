# ⚛️ Frontend Standards - React/TypeScript

> **Projeto:** Charlee
> **Stack:** React 19, TypeScript 5.9, Vite, Zustand, Tailwind CSS
> **Status:** Obrigatório

---

## 📋 Índice

1. [Estrutura de Código](#estrutura-de-código)
2. [TypeScript](#typescript)
3. [Componentes React](#componentes-react)
4. [State Management](#state-management-zustand)
5. [Estilização](#estilização-tailwind)
6. [Performance](#performance)
7. [Acessibilidade](#acessibilidade)
8. [Formatação e Linting](#formatação-e-linting)

---

## 🏗️ Estrutura de Código

### Organização de Diretórios

```
interfaces/web/src/
├── pages/                 # ← Páginas/rotas
│   ├── Dashboard.tsx
│   ├── Tasks.tsx
│   └── BigRocks.tsx
├── components/            # ← Componentes reutilizáveis
│   ├── ui/               # ← Componentes primitivos (Radix)
│   │   ├── Button.tsx
│   │   ├── Dialog.tsx
│   │   └── Select.tsx
│   ├── TaskCard.tsx
│   └── BigRockCard.tsx
├── stores/                # ← Estado global (Zustand)
│   ├── taskStore.ts
│   └── bigRockStore.ts
├── services/              # ← API clients
│   ├── api.ts            # ← Axios config
│   ├── taskService.ts
│   └── bigRockService.ts
├── hooks/                 # ← Custom hooks
│   ├── useTasks.ts
│   └── useDebounce.ts
├── utils/                 # ← Utilitários
│   ├── formatters.ts
│   └── validators.ts
├── types/                 # ← Type definitions
│   ├── task.ts
│   └── bigRock.ts
├── __tests__/             # ← Testes
│   ├── unit/
│   ├── integration/
│   └── setup.ts
├── App.tsx
└── main.tsx
```

### Nomenclatura de Arquivos

```bash
# ✅ CERTO
TaskCard.tsx          # Componentes: PascalCase
taskStore.ts          # Stores: camelCase
taskService.ts        # Services: camelCase
useTasks.ts           # Hooks: use + PascalCase
formatters.ts         # Utils: camelCase

# ❌ ERRADO
task-card.tsx         # Kebab-case não
task_card.tsx         # Snake_case não
TaskCard.ts           # .tsx para componentes React
```

---

## 🔷 TypeScript

### Strict Mode Obrigatório

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

### Interfaces vs Types

```typescript
// ✅ Interface para objetos e componentes
interface Task {
  id: string;
  title: string;
  status: TaskStatus;
}

interface TaskCardProps {
  task: Task;
  onComplete: (id: string) => void;
}

// ✅ Type para unions, intersections, utilities
type TaskStatus = 'pending' | 'in_progress' | 'completed';
type Optional<T> = T | null | undefined;
type ReadonlyTask = Readonly<Task>;

// ❌ EVITAR any
function process(data: any) { } // ← Nunca!

// ✅ Use unknown se tipo realmente desconhecido
function process(data: unknown) {
  if (typeof data === 'string') {
    // TypeScript sabe que é string aqui
  }
}
```

### Props Typing

```typescript
// ✅ CERTO - Interface explícita
interface TaskCardProps {
  task: Task;
  onComplete: (id: string) => void;
  onDelete?: (id: string) => void;  // ← Optional
  className?: string;
}

export const TaskCard = ({
  task,
  onComplete,
  onDelete,
  className
}: TaskCardProps) => {
  // ...
};

// ❌ ERRADO - Props inline (dificulta reutilização)
export const TaskCard = ({
  task,
  onComplete
}: {
  task: Task;
  onComplete: (id: string) => void;
}) => {
  // ...
};
```

### API Response Typing

```typescript
// types/api.ts
export interface ApiTask {
  id: number;
  descricao: string;
  status: string;
  criado_em: string;
  big_rock_id?: number;
}

export interface Task {
  id: string;
  title: string;
  status: 'pending' | 'in_progress' | 'completed';
  createdAt: Date;
  bigRockId?: string;
}

// services/taskService.ts
function apiToTask(apiTask: ApiTask): Task {
  return {
    id: apiTask.id.toString(),
    title: apiTask.descricao,
    status: mapStatus(apiTask.status),
    createdAt: new Date(apiTask.criado_em),
    bigRockId: apiTask.big_rock_id?.toString(),
  };
}
```

---

## ⚛️ Componentes React

### Componentes Funcionais com Hooks

```typescript
// ✅ CERTO - Componente funcional
interface TaskListProps {
  tasks: Task[];
  onTaskClick: (task: Task) => void;
}

export const TaskList = ({ tasks, onTaskClick }: TaskListProps) => {
  const [filter, setFilter] = useState<TaskStatus | 'all'>('all');

  const filteredTasks = useMemo(() => {
    if (filter === 'all') return tasks;
    return tasks.filter(task => task.status === filter);
  }, [tasks, filter]);

  return (
    <div className="space-y-2">
      <FilterSelect value={filter} onChange={setFilter} />
      {filteredTasks.map(task => (
        <TaskCard
          key={task.id}
          task={task}
          onClick={() => onTaskClick(task)}
        />
      ))}
    </div>
  );
};

// ❌ ERRADO - Class component (desatualizado)
class TaskList extends React.Component { }
```

### Composição > Herança

```typescript
// ✅ CERTO - Composição
interface CardProps {
  children: React.ReactNode;
  className?: string;
}

const Card = ({ children, className }: CardProps) => (
  <div className={`rounded-lg border p-4 ${className}`}>
    {children}
  </div>
);

const TaskCard = ({ task }: { task: Task }) => (
  <Card className="hover:shadow-lg">
    <h3>{task.title}</h3>
    <p>{task.description}</p>
  </Card>
);

// ❌ ERRADO - Herança (anti-pattern em React)
class TaskCard extends Card { }
```

### Custom Hooks

```typescript
// hooks/useTasks.ts

import { useTaskStore } from '@/stores/taskStore';
import { useEffect } from 'react';

export const useTasks = (filter?: TaskStatus) => {
  const {
    tasks,
    loading,
    error,
    fetchTasks
  } = useTaskStore();

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const filteredTasks = useMemo(() => {
    if (!filter) return tasks;
    return tasks.filter(task => task.status === filter);
  }, [tasks, filter]);

  return {
    tasks: filteredTasks,
    loading,
    error,
    refetch: fetchTasks,
  };
};

// Uso
const TasksPage = () => {
  const { tasks, loading, error } = useTasks('pending');

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return <TaskList tasks={tasks} />;
};
```

### Error Boundaries

```typescript
// components/ErrorBoundary.tsx

import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log para Sentry, etc.
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-4 bg-red-50 border border-red-200 rounded">
          <h2>Algo deu errado</h2>
          <p>{this.state.error?.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}

// Uso
<ErrorBoundary>
  <TasksPage />
</ErrorBoundary>
```

---

## 📦 State Management (Zustand)

### Store Pattern

```typescript
// stores/taskStore.ts

import { create } from 'zustand';
import { taskService } from '@/services/taskService';

interface Task {
  id: string;
  title: string;
  status: TaskStatus;
}

interface TaskState {
  // Estado
  tasks: Task[];
  loading: boolean;
  error: string | null;

  // Actions
  fetchTasks: () => Promise<void>;
  addTask: (task: Omit<Task, 'id'>) => Promise<void>;
  updateTask: (id: string, updates: Partial<Task>) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;

  // Selectors (computed)
  getPendingTasks: () => Task[];
  getCompletedTasks: () => Task[];
}

export const useTaskStore = create<TaskState>((set, get) => ({
  // Estado inicial
  tasks: [],
  loading: false,
  error: null,

  // Actions
  fetchTasks: async () => {
    set({ loading: true, error: null });
    try {
      const tasks = await taskService.getTasks();
      set({ tasks, loading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        loading: false
      });
    }
  },

  addTask: async (taskData) => {
    set({ loading: true });
    try {
      const newTask = await taskService.createTask(taskData);
      set(state => ({
        tasks: [...state.tasks, newTask],
        loading: false
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Erro ao criar tarefa',
        loading: false
      });
      throw error;
    }
  },

  updateTask: async (id, updates) => {
    try {
      const updated = await taskService.updateTask(id, updates);
      set(state => ({
        tasks: state.tasks.map(t =>
          t.id === id ? { ...t, ...updated } : t
        )
      }));
    } catch (error) {
      set({ error: 'Erro ao atualizar tarefa' });
      throw error;
    }
  },

  deleteTask: async (id) => {
    try {
      await taskService.deleteTask(id);
      set(state => ({
        tasks: state.tasks.filter(t => t.id !== id)
      }));
    } catch (error) {
      set({ error: 'Erro ao deletar tarefa' });
      throw error;
    }
  },

  // Selectors
  getPendingTasks: () => {
    return get().tasks.filter(t => t.status === 'pending');
  },

  getCompletedTasks: () => {
    return get().tasks.filter(t => t.status === 'completed');
  },
}));
```

### Uso em Componentes

```typescript
const TasksPage = () => {
  // ✅ Selecionar apenas o que precisa (evita re-renders)
  const tasks = useTaskStore(state => state.tasks);
  const loading = useTaskStore(state => state.loading);
  const fetchTasks = useTaskStore(state => state.fetchTasks);

  // ❌ EVITAR - Seleciona tudo (re-render desnecessário)
  const store = useTaskStore();

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return <TaskList tasks={tasks} loading={loading} />;
};
```

---

## 🎨 Estilização (Tailwind)

### Tailwind Utility Classes

```typescript
// ✅ CERTO - Classes utilitárias
const Button = ({ variant = 'primary', children }: ButtonProps) => {
  const baseClasses = 'px-4 py-2 rounded-lg font-medium transition-colors';
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700',
  };

  return (
    <button className={`${baseClasses} ${variantClasses[variant]}`}>
      {children}
    </button>
  );
};

// ✅ Melhor ainda - Use clsx ou cn() helper
import { clsx } from 'clsx';

const Button = ({ variant = 'primary', className, children }: ButtonProps) => {
  return (
    <button
      className={clsx(
        'px-4 py-2 rounded-lg font-medium transition-colors',
        {
          'bg-blue-600 text-white hover:bg-blue-700': variant === 'primary',
          'bg-gray-200 text-gray-800 hover:bg-gray-300': variant === 'secondary',
          'bg-red-600 text-white hover:bg-red-700': variant === 'danger',
        },
        className
      )}
    >
      {children}
    </button>
  );
};
```

### Responsividade

```typescript
// Mobile-first approach
<div className="
  p-4           // Base (mobile)
  md:p-6        // Tablet
  lg:p-8        // Desktop

  grid
  grid-cols-1   // 1 coluna mobile
  md:grid-cols-2 // 2 colunas tablet
  lg:grid-cols-3 // 3 colunas desktop

  gap-4
">
  {tasks.map(task => <TaskCard key={task.id} task={task} />)}
</div>
```

---

## ⚡ Performance

### React.memo

```typescript
// ✅ Componente caro que não muda frequentemente
export const TaskCard = React.memo(({ task, onClick }: TaskCardProps) => {
  return (
    <div onClick={() => onClick(task)}>
      <h3>{task.title}</h3>
      <p>{task.description}</p>
    </div>
  );
});

// Comparação customizada se necessário
export const TaskCard = React.memo(
  ({ task, onClick }: TaskCardProps) => { /* ... */ },
  (prevProps, nextProps) => {
    return prevProps.task.id === nextProps.task.id &&
           prevProps.task.title === nextProps.task.title;
  }
);
```

### useMemo e useCallback

```typescript
const TaskList = ({ tasks }: TaskListProps) => {
  // ✅ useMemo para computações caras
  const sortedTasks = useMemo(() => {
    return [...tasks].sort((a, b) =>
      a.priority - b.priority
    );
  }, [tasks]);

  // ✅ useCallback para funções passadas como props
  const handleTaskClick = useCallback((task: Task) => {
    console.log('Task clicked:', task.id);
  }, []);

  return (
    <div>
      {sortedTasks.map(task => (
        <TaskCard
          key={task.id}
          task={task}
          onClick={handleTaskClick}
        />
      ))}
    </div>
  );
};
```

### Code Splitting

```typescript
// ✅ Lazy load de rotas pesadas
import { lazy, Suspense } from 'react';

const Analytics = lazy(() => import('./pages/Analytics'));
const BigRockDetail = lazy(() => import('./pages/BigRockDetail'));

const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route
        path="/analytics"
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <Analytics />
          </Suspense>
        }
      />
    </Routes>
  </BrowserRouter>
);
```

---

## ♿ Acessibilidade

### ARIA Labels

```typescript
const TaskCard = ({ task }: TaskCardProps) => (
  <article
    role="article"
    aria-labelledby={`task-title-${task.id}`}
  >
    <h3 id={`task-title-${task.id}`}>
      {task.title}
    </h3>

    <button
      onClick={handleComplete}
      aria-label={`Marcar tarefa "${task.title}" como completa`}
    >
      ✓
    </button>
  </article>
);
```

### Keyboard Navigation

```typescript
const Dialog = ({ isOpen, onClose, children }: DialogProps) => {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      return () => document.removeEventListener('keydown', handleEsc);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      tabIndex={-1}
    >
      {children}
    </div>
  );
};
```

### Focus Management

```typescript
const Modal = ({ isOpen }: ModalProps) => {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && dialogRef.current) {
      // Focar primeiro elemento focável
      const firstFocusable = dialogRef.current.querySelector<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      firstFocusable?.focus();
    }
  }, [isOpen]);

  return <div ref={dialogRef}>{/* ... */}</div>;
};
```

---

## 🎨 Formatação e Linting

### ESLint

```javascript
// eslint.config.js
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';

export default [
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      ...tseslint.configs.recommended,
    ],
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
      'react-refresh/only-export-components': 'warn',
      '@typescript-eslint/no-unused-vars': ['error', {
        argsIgnorePattern: '^_'
      }],
    },
  },
];
```

### Prettier

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "avoid"
}
```

---

## ✅ Checklist de Qualidade

Antes de commitar código frontend:

- [ ] TypeScript strict mode sem erros
- [ ] ESLint sem warnings
- [ ] Componentes são funcionais (não classes)
- [ ] Props têm interfaces explícitas
- [ ] Loading e error states tratados
- [ ] Componentes responsivos (mobile-first)
- [ ] ARIA labels onde apropriado
- [ ] Testes unitários escritos
- [ ] Performance considerada (memo, useMemo, useCallback)

---

**Última atualização:** 2025-11-10
