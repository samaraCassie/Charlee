# 📚 Índice de Documentação - Charlee

Guia completo de toda a documentação do projeto.

---

## 🚀 Início Rápido

**Novo no projeto? Comece aqui:**

1. **[QUICKSTART.md](QUICKSTART.md)** ⚡ - Setup em 3 comandos
2. **[README.md](README.md)** - Visão geral do projeto
3. **[docs/status-modulos.md](docs/status-modulos.md)** 📊 - Status de implementação de cada módulo
4. **[docs/status-projeto.md](docs/status-projeto.md)** 📈 - Status completo e métricas do projeto

---

## 🔧 Setup e Configuração

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[SETUP.md](SETUP.md)** | Guia completo de instalação e configuração | Setup detalhado com troubleshooting |
| **[QUICKSTART.md](QUICKSTART.md)** | Setup rápido e automatizado | Primeiro setup ou reinstalação |
| **[docs/qualidade/checklist-verificacao.md](docs/qualidade/checklist-verificacao.md)** | Checklist pós-instalação | Validar que tudo está funcionando |
| **[docker/.env.example](docker/.env.example)** | Template de variáveis de ambiente | Configurar credenciais |

**Scripts de Setup:**
- `scripts/setup_complete.sh` - Setup automático completo
- `scripts/update_env.sh` - Atualizar .env com novas variáveis

---

## 📊 Status e Roadmap

| Documento | Descrição | Atualização |
|-----------|-----------|-------------|
| **[docs/status-modulos.md](docs/status-modulos.md)** | Estado de cada módulo (completo/parcial/planejado) | A cada sprint |
| **[docs/status-projeto.md](docs/status-projeto.md)** | Status detalhado do projeto (português) ✨ | Semanal |
| **[docs/roadmap-branches.md](docs/roadmap-branches.md)** | Roadmap de desenvolvimento por versão | Mensal |
| **[docs/qualidade/roadmap.md](docs/qualidade/roadmap.md)** | Roadmap de qualidade e melhorias | Trimestral |
| **[docs/qualidade/analise.md](docs/qualidade/analise.md)** | Análise de qualidade do código | Sob demanda |

---

## 🎯 Planejamento Estratégico

**Visão de longo prazo do produto (V1-V6+)**

| Documento | Descrição | Tipo |
|-----------|-----------|------|
| **[docs/planejamento/visao-produto-completa.md](docs/planejamento/visao-produto-completa.md)** | Visão completa do produto Charlee - Roadmap V1 a V6+ (4060 linhas) | 📋 Planejamento |

> ℹ️ Este documento representa o **plano original e idealizado** do projeto criado em Novembro 2025.
> Descreve a visão completa desde MVP (V1) até features avançadas (V6+).
> **Para o estado atual da implementação**, consulte [Status do Projeto](docs/status-projeto.md) e [Status dos Módulos](docs/status-modulos.md).

---

## 🏗️ Arquitetura do Sistema

**Documentação técnica da arquitetura implementada**

| Documento | Descrição | Status |
|-----------|-----------|--------|
| **[docs/arquitetura/camada-integracao.md](docs/arquitetura/camada-integracao.md)** | Integração entre módulos | 📖 Arquitetura |
| **[docs/arquitetura/v3.1-camada-integracao.md](docs/arquitetura/v3.1-camada-integracao.md)** | Event Bus, Context Manager, Orchestrator | 📖 V3.1 |

---

## 📖 Implementações por Versão

### V1.0 - Sistema Base
- **[docs/implementacao/v1-sistema-base.md](docs/implementacao/v1-sistema-base.md)** - Big Rocks, Tasks, CRUD

### V2.0 - Wellness + Capacity
- **[docs/implementacao/v2-wellness-capacidade.md](docs/implementacao/v2-wellness-capacidade.md)** - Cycle-aware, Capacity Guard

### V2.1 - Sistema de Memória
- **[docs/implementacao/sistema-memoria.md](docs/implementacao/sistema-memoria.md)** - Redis, Sessions, Persistência

### V3.0+ - Sistema de Notificações
- **[docs/implementacao/sistema-notificacoes.md](docs/implementacao/sistema-notificacoes.md)** - Multi-source, AI Classification, Rule Engine

### V3.2 - Calendar Integration
- Documentação integrada em status-modulos.md

### V3.3 - Multimodal Input
- Documentação integrada em status-modulos.md

---

## 🔐 Segurança e Autenticação

| Documento | Descrição | Status |
|-----------|-----------|--------|
| **[docs/seguranca/recursos-auth-avancados.md](docs/seguranca/recursos-auth-avancados.md)** | Features avançadas de autenticação | ✅ Implementado |
| **[docs/seguranca/guia-migracao-auth.md](docs/seguranca/guia-migracao-auth.md)** | Guia de migração de auth | 📖 Referência |
| **[backend/api/SECURITY_SANITIZATION.md](backend/api/SECURITY_SANITIZATION.md)** | Sanitização e prevenção XSS | ✅ Implementado |
| **[docs/qualidade/padroes.md](docs/qualidade/padroes.md)** | Padrões de qualidade e segurança | 📋 Guia |

---

## 🚀 Deploy e Produção

| Documento | Descrição | Status |
|-----------|-----------|--------|
| **[docs/deploy/guia-producao.md](docs/deploy/guia-producao.md)** | Guia completo de deploy em produção | ✅ Pronto |
| **[docs/qualidade/roadmap.md](docs/qualidade/roadmap.md)** | Roadmap de melhorias para produção | 📋 Planejamento |
| **[docker/README.md](docker/README.md)** | Setup Docker e compose | ✅ Funcionando |

---

## 📊 Qualidade e Monitoramento

| Documento | Descrição | Status |
|-----------|-----------|--------|
| **[docs/qualidade/analise.md](docs/qualidade/analise.md)** | Análise de qualidade do código | 📈 Atualizar |
| **[docs/qualidade/padroes.md](docs/qualidade/padroes.md)** | Padrões de código e segurança | ✅ Guia |
| **[docs/qualidade/checklist-verificacao.md](docs/qualidade/checklist-verificacao.md)** | Checklist de verificação pós-deploy | ✅ Guia |

---

## 🤖 Módulos Planejados (V5.0+)

| Documento | Agente | Status |
|-----------|--------|--------|
| **[docs/modulos-planejados/charlee-listener.md](docs/modulos-planejados/charlee-listener.md)** | Listener (Escuta Ativa) | 📋 Planejado |
| **[docs/modulos-planejados/charlee-diplomat.md](docs/modulos-planejados/charlee-diplomat.md)** | Diplomat (Networking) | 📋 Planejado |
| **[docs/modulos-planejados/charlee-brand.md](docs/modulos-planejados/charlee-brand.md)** | Brand (Personal Branding) | 📋 Planejado |
| **[docs/modulos-planejados/charlee-wealth.md](docs/modulos-planejados/charlee-wealth.md)** | Wealth (Finanças) | 📋 Planejado |
| **[docs/modulos-planejados/charlee-routines.md](docs/modulos-planejados/charlee-routines.md)** | Routines (Automação) | 📋 Planejado |
| **[docs/modulos-planejados/charlee-wardrobe.md](docs/modulos-planejados/charlee-wardrobe.md)** | Wardrobe (Estilo) | 📋 Planejado |
| **[docs/modulos-planejados/charlee-poder-feminino.md](docs/modulos-planejados/charlee-poder-feminino.md)** | Poder Feminino | 📋 Planejado |
| **[docs/modulos-planejados/gestao-projetos-freelancers.md](docs/modulos-planejados/gestao-projetos-freelancers.md)** | Gestão Projetos/Freelancers | 📋 Planejado |
| **[docs/modulos-planejados/gestao-notificacoes.md](docs/modulos-planejados/gestao-notificacoes.md)** | Gestão de Notificações | 📋 Planejado |

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
| Verificação pós-setup | [docs/qualidade/checklist-verificacao.md](docs/qualidade/checklist-verificacao.md) |
| pgvector não funciona | [SETUP.md](SETUP.md#verificar-pgvector) |
| Backups falhando | [SETUP.md](SETUP.md#backups-não-funcionam) |
| Migrations com erro | [SETUP.md](SETUP.md#migrations-falham) |

---

## 🔄 Fluxo de Documentação Recomendado

### Para Novos Desenvolvedores

1. Ler [README.md](README.md) - Visão geral
2. Executar [QUICKSTART.md](QUICKSTART.md) - Setup rápido
3. Verificar com [docs/qualidade/checklist-verificacao.md](docs/qualidade/checklist-verificacao.md)
4. Estudar [docs/status-modulos.md](docs/status-modulos.md) - Entender o que está pronto
5. Ler [standards/](standards/) - Aprender padrões do projeto

### Para Implementação de Features

1. Verificar [docs/status-modulos.md](docs/status-modulos.md) - Status atual
2. Consultar doc específica da versão (V1, V2, V3.x) em [docs/implementacao/](docs/implementacao/)
3. Seguir [standards/](standards/) apropriados
4. Atualizar [docs/status-modulos.md](docs/status-modulos.md) quando concluir

### Para Deploy

1. Seguir [SETUP.md](SETUP.md) - Configuração completa
2. Usar [docs/qualidade/checklist-verificacao.md](docs/qualidade/checklist-verificacao.md) - Validação
3. Consultar [docs/deploy/guia-producao.md](docs/deploy/guia-producao.md) para produção

---

## 📊 Estatísticas de Documentação

- **Total de arquivos .md:** 26 documentos organizados
- **Estrutura:**
  - `docs/arquitetura/` - 3 documentos
  - `docs/implementacao/` - 4 documentos
  - `docs/modulos-planejados/` - 9 documentos
  - `docs/seguranca/` - 2 documentos
  - `docs/qualidade/` - 4 documentos
  - `docs/deploy/` - 1 documento
  - `docs/` (raiz) - 3 documentos de status
- **Standards:** 6 documentos em `/standards`
- **Guias de setup:** 3 documentos na raiz do projeto

---

## 🔗 Links Úteis

- **API Docs (Swagger):** http://localhost:8000/docs
- **GitHub Issues:** (adicionar link quando disponível)
- **Changelog:** Ver commits e PRs no Git

---

## 📅 Manutenção da Documentação

### Responsabilidades

- **status-modulos.md:** Atualizar a cada sprint ou release
- **roadmap-branches.md:** Atualizar mensalmente
- **status-projeto.md:** Atualizar semanalmente
- **Standards:** Atualizar conforme necessário

### Antes de Cada Release

- [ ] Atualizar status-modulos.md com novos módulos
- [ ] Atualizar README.md com novas features
- [ ] Atualizar SETUP.md se houve mudanças de configuração
- [ ] Verificar checklist-verificacao.md ainda está válido
- [ ] Atualizar status-projeto.md com métricas atuais

---

**Última atualização deste índice:** 2024-12-28
**Mantido por:** Samara Cassie
