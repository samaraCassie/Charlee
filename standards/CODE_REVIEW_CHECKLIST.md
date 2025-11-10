# ✅ Code Review Checklist

> **Projeto:** Charlee
> **Objetivo:** Garantir qualidade e consistência em todos os PRs
> **Status:** Obrigatório para todos os reviewers

---

## 🎯 Responsabilidades

### Autor do PR

- Preencher template de PR completamente
- Auto-review antes de solicitar review
- Testar localmente
- CI/CD verde antes de solicitar review
- Responder comentários prontamente

### Reviewer

- Review em até 24h (ideal: 8h)
- Ser construtivo e respeitoso
- Bloquear se houver problemas críticos
- Aprovar apenas se confiante

---

## 📋 Checklist Geral

### ✅ Pré-requisitos (Bloqueante)

Antes de iniciar review, verificar:

- [ ] **CI/CD Verde** - Todos os checks passando
- [ ] **Template Preenchido** - Descrição completa
- [ ] **Tamanho Razoável** - Máx 500 linhas (quebrar se maior)
- [ ] **Sem Merge Conflicts** - Branch atualizada

Se algum falhar: ❌ **Bloquear** e solicitar correção.

---

## 💻 Qualidade de Código

### Backend (Python)

- [ ] **Type hints** em todas as funções
  ```python
  # ❌ ERRADO
  def calculate(a, b):
      return a + b

  # ✅ CERTO
  def calculate(a: int, b: int) -> int:
      return a + b
  ```

- [ ] **Docstrings** em funções públicas
  ```python
  def create_task(task_data: TarefaCreate) -> Task:
      """
      Criar nova tarefa.

      Args:
          task_data: Dados da tarefa

      Returns:
          Tarefa criada

      Raises:
          HTTPException 404: Se Big Rock não existir
      """
  ```

- [ ] **Formatação Black** (100 chars)
- [ ] **Ruff linting** sem warnings
- [ ] **MyPy** type checking passando
- [ ] **Pydantic** para validação de inputs
- [ ] **Logging estruturado** (não `print()`)
- [ ] **Tratamento de erros** adequado

### Frontend (React/TypeScript)

- [ ] **TypeScript strict mode** sem erros
- [ ] **Interfaces** explícitas para props
  ```typescript
  // ✅ CERTO
  interface TaskCardProps {
    task: Task;
    onComplete: (id: string) => void;
  }

  export const TaskCard = ({ task, onComplete }: TaskCardProps) => {
    // ...
  };
  ```

- [ ] **ESLint** sem warnings
- [ ] **Componentes funcionais** (não classes)
- [ ] **Hooks** usados corretamente
- [ ] **Performance** considerada (memo, useMemo, useCallback)
- [ ] **Acessibilidade** (ARIA labels, keyboard navigation)
- [ ] **Responsividade** (mobile-first)

---

## 🧪 Testes

### Cobertura

- [ ] **Testes incluídos** para features novas
- [ ] **Testes atualizados** para código modificado
- [ ] **Coverage >= 80%** mantido
- [ ] **Casos edge** testados

### Qualidade dos Testes

```python
# ✅ BOM - Descritivo e focado
def test_create_task_with_valid_data(client, sample_big_rock):
    """Deve criar tarefa com dados válidos."""
    response = client.post(
        "/api/v1/tarefas",
        json={
            "descricao": "Nova tarefa",
            "big_rock_id": sample_big_rock.id
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["descricao"] == "Nova tarefa"
    assert "id" in data

# ❌ RUIM - Vago e testa múltiplas coisas
def test_tasks(client):
    """Test tasks."""
    # Testa criação, listagem, update, delete tudo junto
    # Difícil debugar se falhar
```

---

## 🔐 Segurança

### Secrets e Senhas

- [ ] **Sem secrets hardcoded**
  ```python
  # ❌ BLOQUEANTE
  API_KEY = "sk-1234567890"

  # ✅ CERTO
  API_KEY = os.getenv("OPENAI_API_KEY")
  ```

- [ ] **Sem senhas no código**
- [ ] **Sem .env commitado**
- [ ] **Sem chaves privadas**

### Validação e Sanitização

- [ ] **Inputs validados** com Pydantic/Zod
- [ ] **SQL injection** prevenido (ORM)
- [ ] **XSS** prevenido (React auto-escape)
- [ ] **CSRF** considerado se necessário

### Autenticação e Autorização

- [ ] **Endpoints protegidos** (se necessário)
- [ ] **Autorização verificada** (ownership check)
- [ ] **Rate limiting** considerado

---

## 📚 Documentação

- [ ] **README atualizado** (se necessário)
- [ ] **Comentários** em código complexo
  ```python
  # ✅ BOM - Explica "por quê"
  # Usa max() em vez de sorted() para melhor performance em listas grandes
  max_priority = max(task.priority for task in tasks)

  # ❌ RUIM - Explica "o quê" (óbvio)
  # Pega a prioridade máxima
  max_priority = max(task.priority for task in tasks)
  ```

- [ ] **Swagger/OpenAPI** atualizado (backend)
- [ ] **CHANGELOG** atualizado (se houver)
- [ ] **Migration guide** (se breaking change)

---

## 🏗️ Arquitetura e Design

### Padrões do Projeto

- [ ] **Estrutura de diretórios** seguida
- [ ] **Nomenclatura** consistente
- [ ] **Separação de concerns** (API, service, DB)
- [ ] **DRY** - Sem código duplicado desnecessário
- [ ] **SOLID principles** respeitados

### API Design (Backend)

- [ ] **Status codes** corretos (201 para POST, 204 para DELETE)
- [ ] **Versionamento** correto (/api/v1/, /api/v2/)
- [ ] **Paginação** implementada (se lista)
- [ ] **Error responses** padronizados

### State Management (Frontend)

- [ ] **Zustand store** usado corretamente
- [ ] **Selectors** otimizados (evitar re-renders)
- [ ] **Async actions** tratam errors

---

## ⚡ Performance

### Backend

- [ ] **N+1 queries** evitados (eager loading)
- [ ] **Database indexes** considerados
- [ ] **Caching** usado quando apropriado
- [ ] **Async** apenas para I/O bound

### Frontend

- [ ] **Code splitting** para rotas pesadas
- [ ] **Lazy loading** de componentes grandes
- [ ] **React.memo** em componentes caros
- [ ] **useMemo/useCallback** onde apropriado
- [ ] **Images otimizadas** (tamanho/formato)

---

## 🐛 Debugging e Manutenibilidade

- [ ] **Logs úteis** adicionados
- [ ] **Error messages** descritivas
- [ ] **TODO comments** linkados a issues
  ```python
  # ✅ BOM
  # TODO(#123): Implementar cache para esta query

  # ❌ RUIM
  # TODO: melhorar isso
  ```

- [ ] **Magic numbers** evitados (usar constantes)
  ```python
  # ❌ RUIM
  if task.priority > 7:

  # ✅ BOM
  HIGH_PRIORITY_THRESHOLD = 7
  if task.priority > HIGH_PRIORITY_THRESHOLD:
  ```

---

## 🚀 CI/CD e Deploy

- [ ] **Migrations** incluídas (se mudança no DB)
- [ ] **Environment variables** documentadas
- [ ] **Backward compatible** (ou migration guide)
- [ ] **Rollback strategy** considerada

---

## 💬 Comunicação e Feedback

### Como Dar Feedback

**Construtivo**:
```
✅ "Considere usar useMemo aqui para evitar recalcular em cada render.
   Exemplo: const sorted = useMemo(() => [...].sort(), [deps])"

❌ "Isso está errado."
```

**Específico**:
```
✅ "A função calculate_priority() está retornando float mas deveria
   retornar int baseado na especificação (linha 45 do design doc)."

❌ "Função errada."
```

**Priorizado**:
```
🔴 BLOQUEANTE: Security issue - API key hardcoded
🟡 IMPORTANTE: Falta tratamento de erro aqui
🟢 NITPICK: Typo no comentário
```

### Como Responder a Feedback

- ✅ Agradecer e corrigir
- ✅ Explicar se discordar (com justificativa)
- ✅ Marcar como resolvido após correção
- ❌ Ignorar comentários
- ❌ Ser defensivo

---

## 🎭 Cenários Comuns

### PR Muito Grande

```markdown
❌ BLOQUEAR

Este PR tem 800+ linhas. Por favor, quebrar em PRs menores:
1. PR1: Estrutura de dados e models
2. PR2: API endpoints
3. PR3: Frontend components
4. PR4: Testes

Facilita review e reduz risco de bugs.
```

### CI Failing

```markdown
❌ BLOQUEAR

CI/CD falhando:
- Backend tests: 3 failures
- ESLint: 12 warnings

Por favor, corrigir antes de review.
```

### Sem Testes

```markdown
❌ BLOQUEAR

Features novas requerem testes. Por favor, adicionar:
- Teste unitário para calculate_priority()
- Teste de API para POST /api/v1/tarefas
- Cobertura deve ser >= 80%
```

### Security Issue

```markdown
🔴 BLOQUEANTE - SECURITY

API key hardcoded na linha 45:
```python
OPENAI_API_KEY = "sk-proj-abc123..."
```

NUNCA commite secrets. Usar variável de ambiente:
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

Após corrigir, verificar histórico do git e revogar a key exposta.
```

---

## ✅ Template de Aprovação

Ao aprovar, confirme:

```markdown
✅ LGTM (Looks Good To Me)

Reviewed:
- [x] Código segue padrões
- [x] Testes passam com coverage adequado
- [x] Documentação atualizada
- [x] Sem security issues
- [x] Performance considerada

Sugestões opcionais (não bloqueiam merge):
- Considerar adicionar cache em X (pode ser issue futuro)
```

---

## ❌ Template de Bloqueio

Ao bloquear, seja específico:

```markdown
❌ REQUEST CHANGES

Problemas bloqueantes:
1. 🔴 SECURITY: Senha hardcoded (linha 123)
2. 🔴 TESTS: Coverage caiu de 88% para 65%
3. 🔴 BREAKING: Endpoint /api/v1/tasks mudou sem migration guide

Por favor, corrigir antes de re-review.

Sugestões não-bloqueantes:
- Considerar usar constant para PRIORITY_THRESHOLD
```

---

## 📊 Métricas de Review

Monitorar:

- **Tempo de review**: Ideal < 8h, Máx 24h
- **Taxa de aprovação**: ~80% (muito baixo ou alto indica problema)
- **Comentários por PR**: 5-15 (muito baixo = superficial, muito alto = PR grande demais)
- **Iterações**: Ideal 1-2, Máx 3

---

## 🎓 Recursos

- [Google Engineering Practices - Code Review](https://google.github.io/eng-practices/review/)
- [Conventional Comments](https://conventionalcomments.org/)
- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)

---

**Última atualização:** 2025-11-10
**Objetivo:** Manter qualidade sem sacrificar velocidade
