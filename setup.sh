#!/bin/bash

echo "🌸 Charlee - Setup Inicial"
echo "=========================="
echo ""

# Verifica se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Instale o Docker Compose primeiro."
    exit 1
fi

echo "✅ Docker e Docker Compose encontrados"
echo ""

# Cria .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cp backend/.env.example .env
    echo "⚠️  IMPORTANTE: Edite o arquivo .env com suas credenciais!"
    echo ""
else
    echo "✅ Arquivo .env já existe"
    echo ""
fi

# Pergunta se quer iniciar os containers
read -p "🚀 Deseja iniciar os containers Docker agora? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🐳 Iniciando containers..."
    docker-compose up -d

    echo ""
    echo "✅ Setup concluído!"
    echo ""
    echo "📊 Status dos serviços:"
    docker-compose ps
    echo ""
    echo "🔗 Serviços disponíveis:"
    echo "   - Backend API: http://localhost:8000"
    echo "   - PostgreSQL: localhost:5432"
    echo "   - Redis: localhost:6379"
    echo ""
    echo "📝 Próximos passos:"
    echo "   1. Edite o arquivo .env com suas credenciais"
    echo "   2. Execute: docker-compose restart backend"
    echo "   3. Acesse http://localhost:8000/docs para ver a API"
else
    echo "⏭️  Setup concluído! Execute 'docker-compose up -d' quando estiver pronto."
fi

echo ""
echo "📚 Documentação completa: README.md"
