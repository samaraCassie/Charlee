# 📚 Índice de Documentação - Charlee

Guia completo de toda a documentação do projeto.

---

## 🚀 Início Rápido

**Novo no projeto? Comece aqui:**

1. **[QUICKSTART.md](QUICKSTART.md)** ⚡ - Setup em 3 comandos
2. **[README.md](README.md)** - Visão geral do projeto
3. **[MODULES_STATUS.md](MODULES_STATUS.md)** 📊 - Status de implementação de cada módulo

---

## 🔧 Setup e Configuração

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[SETUP.md](SETUP.md)** | Guia completo de instalação e configuração | Setup detalhado com troubleshooting |
| **[QUICKSTART.md](QUICKSTART.md)** | Setup rápido e automatizado | Primeiro setup ou reinstalação |
| **[VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)** | Checklist pós-instalação | Validar que tudo está funcionando |
| **[docker/.env.example](docker/.env.example)** | Template de variáveis de ambiente | Configurar credenciais |

**Scripts de Setup:**
- `scripts/setup_complete.sh` - Setup automático completo
- `scripts/update_env.sh` - Atualizar .env com novas variáveis

---

## 📊 Status e Roadmap

| Documento | Descrição | Atualização |
|-----------|-----------|-------------|
| **[MODULES_STATUS.md](MODULES_STATUS.md)** | Estado de cada módulo (completo/parcial/planejado) | A cada sprint |
| **[docs/ROADMAP_BRANCHES.md](docs/ROADMAP_BRANCHES.md)** | Roadmap de desenvolvimento por versão | Mensal |
| **[PROJECT_STATUS.md](PROJECT_STATUS.md)** | Status detalhado do projeto (inglês) | Semanal |
| **[STATUS_PROJETO.md](STATUS_PROJETO.md)** | Status detalhado (português) | Semanal |

---

## 📖 Documentação Técnica por Versão

### V1.0 - Sistema Base
- **[docs/V1_IMPLEMENTATION.md](docs/V1_IMPLEMENTATION.md)** - Big Rocks, Tasks, CRUD

### V2.0 - Wellness + Capacity
- **[docs/V2_IMPLEMENTATION.md](docs/V2_IMPLEMENTATION.md)** - Cycle-aware, Capacity Guard

### V2.1 - Memória
- **[docs/MEMORY_IMPLEMENTATION.md](docs/MEMORY_IMPLEMENTATION.md)** - Redis, Sessions, Persistência

### V3.1 - Integration Layer
- **[docs/V3.1_INTEGRATION_LAYER.md](docs/V3.1_INTEGRATION_LAYER.md)** - Event Bus, Context Manager, Orchestrator

### V3.2 - Calendar Integration
- Documentação integrada em MODULES_STATUS.md

### V3.3 - Multimodal Input
- Documentação integrada em MODULES_STATUS.md

---

## 🤖 Documentação de Agentes Especializados

### Módulos Implementados (V5.0+)

| Documento | Agente | Status |
|-----------|--------|--------|
| **[docs/CHARLEE_LISTENER.md](docs/CHARLEE_LISTENER.md)** | Listener (Escuta Ativa) | 📋 Planejado |
| **[docs/CHARLEE_DIPLOMAT.md](docs/CHARLEE_DIPLOMAT.md)** | Diplomat (Networking) | 📋 Planejado |
| **[docs/CHARLEE_BRAND.md](docs/CHARLEE_BRAND.md)** | Brand (Personal Branding) | 📋 Planejado |
| **[docs/CHARLEE_WEALTH.md](docs/CHARLEE_WEALTH.md)** | Wealth (Finanças) | 📋 Planejado |
| **[docs/CHARLEE_ROUTINES.md](docs/CHARLEE_ROUTINES.md)** | Routines (Automação) | 📋 Planejado |
| **[docs/CHARLEE_WARDROBE.md](docs/CHARLEE_WARDROBE.md)** | Wardrobe (Estilo) | 📋 Planejado |
| **[docs/CHARLEE_PODER_FEMININO.md](docs/CHARLEE_PODER_FEMININO.md)** | Poder Feminino | 📋 Planejado |

### Freelance/Projects (Parcialmente Implementado)

- **[docs/Charlee_modulo_gerenciamento_projetos_e_freelancers.md](docs/Charlee_modulo_gerenciamento_projetos_e_freelancers.md)** - Sistema freelance
- **[docs/Charlee_modulo_gestao_de_notificacao.md](docs/Charlee_modulo_gestao_de_notificacao.md)** - Notificações
- **[docs/Charlee_integracao_modulos.md](docs/Charlee_integracao_modulos.md)** - Integração entre módulos

---

## 🏗️ Documentação de Arquitetura

### Backend

| Documento | Descrição |
|-----------|-----------|
| **[backend/README.md](backend/README.md)** | Estrutura do backend (se existir) |
| **[backend/database/models.py](backend/database/models.py)** | 25+ models do banco de dados |
| **[backend/agent/](backend/agent/)** | 12 agentes AI especializados |

### Frontend

| Documento | Descrição |
|-----------|-----------|
| **[interfaces/web/README.md](interfaces/web/README.md)** | Frontend React (se existir) |
| **[interfaces/web/package.json](interfaces/web/package.json)** | Dependências e scripts |

### Infraestrutura

| Documento | Descrição |
|-----------|-----------|
| **[docker/docker-compose.yml](docker/docker-compose.yml)** | Configuração de containers |
| **[backend/Dockerfile](backend/Dockerfile)** | Build do backend |

---

## 📏 Padrões e Standards

| Documento | Área | Atualização |
|-----------|------|-------------|
| **[standards/QUALITY_STANDARDS.md](standards/QUALITY_STANDARDS.md)** | Índice central de padrões | Mensal |
| **[standards/QUALITY_ROADMAP.md](standards/QUALITY_ROADMAP.md)** | Roadmap de melhorias (90 dias) | Trimestral |
| **[standards/BACKEND_STANDARDS.md](standards/BACKEND_STANDARDS.md)** | Padrões Python/FastAPI | Conforme necessário |
| **[standards/FRONTEND_STANDARDS.md](standards/FRONTEND_STANDARDS.md)** | Padrões React/TypeScript | Conforme necessário |
| **[standards/GIT_STANDARDS.md](standards/GIT_STANDARDS.md)** | Conventional Commits, branching | Conforme necessário |
| **[standards/TESTING_STANDARDS.md](standards/TESTING_STANDARDS.md)** | Pirâmide de testes, cobertura | Conforme necessário |
| **[standards/SECURITY_STANDARDS.md](standards/SECURITY_STANDARDS.md)** | OWASP Top 10, best practices | Conforme necessário |
| **[standards/CODE_REVIEW_CHECKLIST.md](standards/CODE_REVIEW_CHECKLIST.md)** | Checklist de code review | Conforme necessário |

---

## 🧪 Testes e Qualidade

### Backend
- **Cobertura:** 62% (meta: 80%)
- **Testes:** 90 testes (100% pass rate)
- **Localização:** `backend/tests/`

### Frontend
- **Cobertura:** 79.8% (✅ acima da meta de 78%)
- **Testes:** 173 testes
- **Localização:** `interfaces/web/src/__tests__/`

---

## 🔐 Segurança

- **[standards/SECURITY_STANDARDS.md](standards/SECURITY_STANDARDS.md)** - Práticas de segurança
- **[.github/workflows/ci.yml](.github/workflows/ci.yml)** - Security scanning (Trivy)
- **[.pre-commit-config.yaml](.pre-commit-config.yaml)** - Bandit security checks

---

## 🆘 Troubleshooting

| Problema | Documentação |
|----------|--------------|
| Setup inicial | [SETUP.md](SETUP.md) seção Troubleshooting |
| Verificação pós-setup | [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) |
| pgvector não funciona | [SETUP.md](SETUP.md#verificar-pgvector) |
| Backups falhando | [SETUP.md](SETUP.md#backups-não-funcionam) |
| Migrations com erro | [SETUP.md](SETUP.md#migrations-falham) |

---

## 📝 Documentação Legacy/Histórica

- **[docs/Charlee_Documentacao.docx.md](docs/Charlee_Documentacao.docx.md)** - Documentação original convertida
- **[docs/README.md](docs/README.md)** - Índice da pasta docs

---

## 🔄 Fluxo de Documentação Recomendado

### Para Novos Desenvolvedores

1. Ler [README.md](README.md) - Visão geral
2. Executar [QUICKSTART.md](QUICKSTART.md) - Setup rápido
3. Verificar com [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)
4. Estudar [MODULES_STATUS.md](MODULES_STATUS.md) - Entender o que está pronto
5. Ler [standards/](standards/) - Aprender padrões do projeto

### Para Implementação de Features

1. Verificar [MODULES_STATUS.md](MODULES_STATUS.md) - Status atual
2. Consultar doc específica da versão (V1, V2, V3.x)
3. Seguir [standards/](standards/) apropriados
4. Atualizar [MODULES_STATUS.md](MODULES_STATUS.md) quando concluir

### Para Deploy

1. Seguir [SETUP.md](SETUP.md) - Configuração completa
2. Usar [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) - Validação
3. Configurar backup via instruções em SETUP.md

---

## 📊 Estatísticas de Documentação

- **Total de arquivos .md:** 40+
- **Standards:** 6 documentos
- **Documentação técnica:** 8 versões/módulos
- **Guias de setup:** 3 documentos
- **Checklists:** 2 documentos
- **Docs de agentes planejados:** 8 documentos

---

## 🔗 Links Úteis

- **API Docs (Swagger):** http://localhost:8000/docs
- **GitHub Issues:** (adicionar link quando disponível)
- **Changelog:** Ver commits e PRs no Git

---

## 📅 Manutenção da Documentação

### Responsabilidades

- **MODULES_STATUS.md:** Atualizar a cada sprint ou release
- **ROADMAP_BRANCHES.md:** Atualizar mensalmente
- **PROJECT_STATUS.md:** Atualizar semanalmente
- **Standards:** Atualizar conforme necessário

### Antes de Cada Release

- [ ] Atualizar MODULES_STATUS.md com novos módulos
- [ ] Atualizar README.md com novas features
- [ ] Atualizar SETUP.md se houve mudanças de configuração
- [ ] Verificar VERIFICATION_CHECKLIST.md ainda está válido
- [ ] Atualizar PROJECT_STATUS.md com métricas atuais

---

**Última atualização deste índice:** 2024-12-24  
**Mantido por:** Samara Cassie
