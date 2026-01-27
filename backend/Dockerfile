FROM python:3.12-slim

WORKDIR /app

# Instala dependências do sistema
# Note: postgresql-client includes pg_dump for backups
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de dependências
COPY requirements.txt .
COPY pyproject.toml .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

# Expõe a porta
EXPOSE 8000

# Comando padrão
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
