# ☁️ AWS Deployment Guide - Charlee

> AWS é mais caro? Análise completa de custos e opções

## 💰 Comparação de Custos: AWS vs Alternativas

### Cenário 1: MVP / Desenvolvimento

| Item | AWS | Supabase + Render | Diferença |
|------|-----|-------------------|-----------|
| **Banco de Dados** | RDS db.t3.micro: $15/mês | Supabase Free: $0 | +$15 |
| **Backend** | ECS Fargate: $15/mês | Render Free: $0 | +$15 |
| **Redis** | ElastiCache t4g.micro: $12/mês | Upstash Free: $0 | +$12 |
| **Load Balancer** | ALB: $16/mês | Incluído: $0 | +$16 |
| **TOTAL** | **~$58/mês** | **$0/mês** | **+$58** |

**Veredito:** ❌ AWS é **MUITO mais caro** para MVP

---

### Cenário 2: Produção Pequena (1-1000 usuários)

| Item | AWS | Supabase + Railway | Diferença |
|------|-----|---------------------|-----------|
| **Banco de Dados** | RDS db.t3.small: $30/mês | Supabase Pro: $25/mês | +$5 |
| **Backend** | ECS Fargate: $30/mês | Railway: $15/mês | +$15 |
| **Redis** | ElastiCache: $12/mês | Incluído Railway: $0 | +$12 |
| **S3 + CloudFront** | $5/mês | Vercel: $0 | +$5 |
| **TOTAL** | **~$77/mês** | **$40/mês** | **+$37** |

**Veredito:** ❌ AWS é **quase 2x mais caro**

---

### Cenário 3: Produção Média (1000-10k usuários)

| Item | AWS | Supabase + Cloud Run | Diferença |
|------|-----|----------------------|-----------|
| **Banco de Dados** | RDS db.t3.medium: $60/mês | Supabase Pro: $25/mês | +$35 |
| **Backend** | ECS Fargate (2 tasks): $60/mês | Cloud Run: $30/mês | +$30 |
| **Redis** | ElastiCache m6g.large: $80/mês | Upstash Pro: $10/mês | +$70 |
| **Load Balancer** | ALB: $16/mês | Incluído: $0 | +$16 |
| **TOTAL** | **~$216/mês** | **$65/mês** | **+$151** |

**Veredito:** ❌ AWS é **3x mais caro**

---

### Cenário 4: Alta Escala (100k+ usuários)

| Item | AWS | Alternativas | Diferença |
|------|-----|--------------|-----------|
| **Banco de Dados** | RDS Multi-AZ: $200/mês | Supabase Enterprise: $200/mês | ~$0 |
| **Backend** | ECS Fargate (10 tasks): $300/mês | Cloud Run: $150/mês | +$150 |
| **Redis** | ElastiCache Cluster: $200/mês | Upstash: $100/mês | +$100 |
| **Observability** | Incluído: $0 | Datadog: $100/mês | -$100 |
| **TOTAL** | **~$700/mês** | **~$550/mês** | **+$150** |

**Veredito:** ⚠️ AWS **ainda é mais caro**, mas gap menor

---

## 🎯 Quando Usar AWS?

### ✅ AWS FAZ SENTIDO se:

1. **Você já tem créditos AWS** (startups, estudantes)
2. **Empresa já usa AWS** (conhecimento interno)
3. **Compliance rigoroso** (HIPAA, SOC2, etc.)
4. **Tráfego global** (CloudFront + multi-region)
5. **Necessita serviços específicos** (Lambda, SageMaker, etc.)
6. **Alta escala** (100k+ requests/dia)

### ❌ NÃO use AWS se:

1. **Orçamento limitado** (use Supabase/Render)
2. **MVP ou protótipo** (overhead desnecessário)
3. **Time pequeno** (complexidade alta)
4. **Quer velocidade** (setup leva dias vs minutos)
5. **Sem experiência AWS** (curva de aprendizado íngreme)

---

## 🏗️ Opções de Deploy na AWS

### Opção 1: AWS Free Tier (12 meses grátis)

**Componentes:**
- RDS db.t3.micro (750h/mês grátis)
- EC2 t2.micro (750h/mês grátis)
- ElastiCache (não incluído no free tier)
- S3 (5GB grátis)

**Custo após 12 meses:** ~$50/mês

**Setup:**
```bash
# Via AWS Console (mais fácil para começar)
1. RDS PostgreSQL → db.t3.micro
2. EC2 t2.micro → Docker
3. Usar Redis local no EC2 (não recomendado)
```

**Prós:**
- ✅ 12 meses grátis
- ✅ Aprende AWS

**Contras:**
- ❌ Redis não incluído (precisa ElastiCache = $12/mês extra)
- ❌ Setup complexo
- ❌ Após 12 meses: $50/mês

---

### Opção 2: AWS Lightsail (Simplificado)

**O que é?**
- AWS simplificado (como DigitalOcean)
- Preços fixos e previsíveis
- Menos features, mais fácil

**Planos:**

| Plano | CPU | RAM | Storage | Preço |
|-------|-----|-----|---------|-------|
| Nano | 0.5 vCPU | 512MB | 20GB | $3.50/mês |
| Micro | 1 vCPU | 1GB | 40GB | $5/mês |
| Small | 1 vCPU | 2GB | 60GB | $10/mês |
| Medium | 2 vCPU | 4GB | 80GB | $20/mês |

**Stack Lightsail:**
- **App**: Lightsail Small ($10/mês)
- **Database**: Lightsail PostgreSQL Micro ($15/mês)
- **Total**: $25/mês (sem Redis)

**Setup:**
```bash
# Via AWS CLI
aws lightsail create-instance \
  --instance-name charlee-backend \
  --blueprint-id ubuntu_22_04 \
  --bundle-id small_2_0

aws lightsail create-relational-database \
  --relational-database-name charlee-db \
  --relational-database-blueprint-id postgres_14 \
  --relational-database-bundle-id micro_2_0
```

**Prós:**
- ✅ Mais barato que RDS/ECS
- ✅ Preços fixos
- ✅ Mais simples que AWS "tradicional"

**Contras:**
- ❌ Limitado em features
- ❌ Menos controle
- ❌ Ainda mais caro que Render/Railway

---

### Opção 3: ECS Fargate + RDS (Produção)

**Componentes:**
- **Backend**: ECS Fargate (serverless containers)
- **Database**: RDS PostgreSQL
- **Redis**: ElastiCache
- **Load Balancer**: Application Load Balancer
- **Frontend**: S3 + CloudFront

**Custo Estimado:** $60-100/mês (produção básica)

**Quando usar:**
- Tráfego alto e variável
- Precisa autoscaling
- Equipe experiente em AWS

**Setup** (via Terraform):
```hcl
# Simplified example
resource "aws_ecs_cluster" "charlee" {
  name = "charlee-cluster"
}

resource "aws_db_instance" "charlee" {
  identifier        = "charlee-db"
  engine            = "postgres"
  instance_class    = "db.t3.small"
  allocated_storage = 20
}

resource "aws_elasticache_cluster" "charlee" {
  cluster_id      = "charlee-redis"
  engine          = "redis"
  node_type       = "cache.t4g.micro"
  num_cache_nodes = 1
}
```

---

### Opção 4: AWS Amplify (Full-Stack)

**O que é?**
- Plataforma full-stack da AWS
- Parecido com Vercel + Render

**Custo:**
- **Hosting**: $0.15/GB stored + $0.15/GB served
- **Database**: RDS separado (não incluído)
- **Típico**: $10-30/mês

**Prós:**
- ✅ Deploy automático do GitHub
- ✅ CI/CD integrado
- ✅ Mais simples que ECS

**Contras:**
- ❌ Banco precisa configurar separado
- ❌ Menos controle
- ❌ Pricing complicado

---

## 💡 AWS para Estudantes e Startups

### AWS Educate (Estudantes)

**Benefícios:**
- $100 créditos/ano
- Acesso a todos serviços
- Cursos gratuitos

**Como conseguir:**
1. Acessar: https://aws.amazon.com/education/awseducate/
2. Cadastrar com email .edu
3. Aguardar aprovação

**Vale a pena?** ✅ SIM! Com $100 de crédito, pode rodar 6+ meses grátis

---

### AWS Activate (Startups)

**Benefícios:**
- Até $100,000 em créditos
- Suporte técnico
- Treinamento

**Requisitos:**
- Startup registrada
- Estar em incubadora/aceleradora
- Ou ter investimento VC

**Como aplicar:**
1. https://aws.amazon.com/activate/
2. Aplicar via aceleradora (YC, 500 Startups, etc.)

**Vale a pena?** ✅ SIM! Se você tem acesso

---

## 📊 Comparação Final: AWS vs Alternativas

### Melhor para Começar (MVP)

| Rank | Stack | Custo/mês | Setup | Complexidade |
|------|-------|-----------|-------|--------------|
| 🥇 | **Supabase + Render + Vercel** | $0 | 20min | ⭐ |
| 🥈 | **Railway** | $5-10 | 10min | ⭐ |
| 🥉 | **Neon + Fly.io** | $0-5 | 30min | ⭐⭐ |
| 4️⃣ | **AWS Lightsail** | $25 | 2h | ⭐⭐⭐ |
| 5️⃣ | **AWS Free Tier** | $0 (12m) → $50 | 4h | ⭐⭐⭐⭐ |

**Recomendação:** ⭐ **Supabase + Render** (economize $50/mês)

---

### Melhor para Produção (1k-10k usuários)

| Rank | Stack | Custo/mês | Features | Escalabilidade |
|------|-------|-----------|----------|----------------|
| 🥇 | **Supabase Pro + Railway** | $40 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 🥈 | **Cloud Run + Supabase** | $50 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 🥉 | **AWS Lightsail** | $50 | ⭐⭐⭐ | ⭐⭐ |
| 4️⃣ | **AWS ECS + RDS** | $80 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Recomendação:** ⭐ **Railway** (melhor custo-benefício)

---

### Melhor para Alta Escala (100k+ usuários)

| Rank | Stack | Custo/mês | Performance | Controle |
|------|-------|-----------|-------------|----------|
| 🥇 | **AWS ECS + RDS Multi-AZ** | $500+ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 🥈 | **GCP Cloud Run + Cloud SQL** | $400+ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 🥉 | **Railway Enterprise** | $300+ | ⭐⭐⭐ | ⭐⭐⭐ |

**Recomendação:** ⭐ **AWS** (quando escala justifica)

---

## 🎯 Decisão Final

### Use AWS se:
- ✅ Tem créditos AWS (estudante/startup)
- ✅ Empresa já usa AWS
- ✅ Escala > 100k usuários
- ✅ Precisa compliance específico
- ✅ Equipe experiente

### NÃO use AWS se:
- ❌ Orçamento < $50/mês
- ❌ Time pequeno/inexperiente
- ❌ MVP ou teste
- ❌ Quer rapidez no deploy

### Recomendação Específica para Charlee:

```
🎯 Fase Atual (MVP/Testes):
   → Supabase + Render + Vercel = $0/mês

💰 Primeiros Usuários:
   → Railway = $15/mês

🚀 Crescimento (>1k usuários):
   → Supabase Pro + Cloud Run = $50/mês

📈 Alta Escala (>100k usuários):
   → AWS ECS + RDS = $300+/mês
```

---

## 📚 Recursos AWS

### Documentação
- [AWS Free Tier](https://aws.amazon.com/free/)
- [AWS Lightsail](https://aws.amazon.com/lightsail/)
- [AWS ECS](https://aws.amazon.com/ecs/)
- [AWS RDS](https://aws.amazon.com/rds/)

### Calculadora de Custos
- [AWS Pricing Calculator](https://calculator.aws/)

### Treinamento
- [AWS Skill Builder](https://skillbuilder.aws/) (grátis)

---

## 🔍 Conclusão

**AWS é mais caro?**

Para o Charlee especificamente:
- **MVP**: AWS = $50-60/mês vs Render = $0 → **60% mais caro**
- **Produção**: AWS = $80/mês vs Railway = $40 → **100% mais caro**
- **Alta Escala**: AWS = $500/mês vs Alternativas = $400 → **25% mais caro**

**Veredito:** ✅ Para seu caso, **Supabase + Render/Railway é muito melhor**

**Quando migrar para AWS?**
- Quando tiver > 50k usuários ativos
- Ou se conseguir créditos significativos (>$10k)
- Ou se empresa exigir por compliance

---

**Criado em:** 2025-11-13
**Recomendação:** 🎯 Comece com Supabase + Render ($0), migre para AWS apenas em escala
