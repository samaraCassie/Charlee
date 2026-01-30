# 🔧 Postman Desktop Agent - Solução Rápida

## Problema
```
Cloud agent error: cannot send request.
When testing an API locally, you need to use the Postman Desktop Agent.
```

---

## ✅ Solução 1: Instalar Postman Desktop (Recomendado)

### **Linux (Ubuntu/Debian)**

```bash
# Baixar Postman Desktop
wget https://dl.pstmn.io/download/latest/linux64 -O postman-linux-x64.tar.gz

# Extrair
sudo tar -xzf postman-linux-x64.tar.gz -C /opt

# Criar symlink
sudo ln -s /opt/Postman/Postman /usr/bin/postman

# Executar
postman
```

### **Ou via Snap (mais fácil)**

```bash
sudo snap install postman
postman
```

### **Depois de instalar:**

1. Abra Postman Desktop
2. **Import** → Arraste `postman_collection_freelancer.json`
3. **Import** → Arraste `postman_environment_local.json`
4. Selecione environment **"Charlee - Local Development"**
5. Rode requests normalmente - funcionará com localhost!

---

## ✅ Solução 2: Usar Postman Desktop Agent (Web)

Se preferir continuar usando Postman Web, instale o Desktop Agent:

### **Passo 1: Baixe o Desktop Agent**

1. No Postman Web, clique no aviso do erro
2. Click em **"Download Desktop Agent"**
3. Ou acesse: https://www.postman.com/downloads/postman-agent/

### **Passo 2: Instale**

```bash
# Linux
wget https://dl.pstmn.io/download/latest/linux64/postman-agent -O postman-agent
chmod +x postman-agent
./postman-agent
```

### **Passo 3: Configure no Postman Web**

1. No canto inferior direito, clique no ícone de **Settings** ⚙️
2. Em **"Agent"**, selecione **"Desktop Agent"**
3. Agora você pode fazer requests para localhost!

---

## ✅ Solução 3: Use cURL no Terminal (Alternativa Rápida)

Se não quiser instalar nada agora, use o script bash com cURL:

```bash
# 1. Certifique-se que backend está rodando
cd /home/sam-cassie/GitHub/Charlee/backend
source venv/bin/activate
uvicorn main:app --reload &

# 2. Aguarde 5 segundos
sleep 5

# 3. Teste health check
curl http://localhost:8000/health | jq '.'

# 4. Rode o script completo
./scripts/test_freelancer_api.sh
```

**Nota:** Você precisará editar o script para adicionar o token JWT após fazer login.

---

## 🎯 Recomendação

**Para uso de verdade:** Instale **Postman Desktop** via snap:

```bash
sudo snap install postman
postman
```

É a forma mais fácil e confiável para testar APIs localhost.

---

## 🐛 Troubleshooting

### **Postman Desktop não abre**
```bash
# Verifique instalação
which postman

# Rode com logs
postman --verbose
```

### **Desktop Agent não conecta**
1. Verifique se está rodando: `ps aux | grep postman-agent`
2. Reinicie o agent
3. No Postman Web, recarregue a página

### **Ainda com problemas?**
Use a **Solução 3** (cURL) que sempre funciona!

---

## 📚 Alternativas ao Postman

Se não quiser usar Postman, temos outras opções prontas:

### **1. Swagger UI (Já incluído no FastAPI)**
```bash
# Backend rodando em:
http://localhost:8000/docs

# Tudo que está no Postman está aqui também!
```

### **2. Script Python Interativo**
```bash
python3 scripts/test_freelancer_interactive.py
```

### **3. Jupyter Notebook**
```bash
jupyter notebook notebooks/test_freelancer_system.ipynb
```

### **4. Testes Automatizados**
```bash
pytest tests/test_freelancer_mvp.py -v
```

---

## ✅ Resumo Rápido

| Opção | Prós | Contras | Comando |
|-------|------|---------|---------|
| Postman Desktop | ✅ GUI, fácil, visual | Precisa instalar | `snap install postman` |
| Desktop Agent | ✅ Usa Postman Web | Setup extra | Download do site |
| Swagger UI | ✅ Já funciona, nada instalar | Menos features | `http://localhost:8000/docs` |
| cURL Script | ✅ Terminal, sem install | Menos visual | `./scripts/test_freelancer_api.sh` |

**Nossa recomendação:** Swagger UI para começar (sem instalar nada) ou Postman Desktop para uso completo.
