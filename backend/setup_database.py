"""
Script completo para configurar e popular o banco de dados.

Uso:
    python setup_database.py

Este script:
1. Cria todas as tabelas (se não existirem)
2. Popula com dados de teste
3. Exibe resumo dos dados criados
"""

import sys

from database.config import Base, engine


def create_tables():
    """Cria todas as tabelas do banco de dados."""
    print("🔨 Criando tabelas do banco de dados...")

    try:
        # Limpar metadata cache para forçar recriação
        Base.metadata.clear()

        # Importar todos os modelos para garantir que estão registrados
        from database.models import (  # noqa: F401
            User,
            RefreshToken,
            AuditLog,
            BigRock,
            Task,
            MenstrualCycle,
            CyclePatterns,
            Workload,
            DailyLog,
        )

        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ Tabelas criadas com sucesso!\n")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False


def seed_data():
    """Popula o banco de dados com dados de teste."""
    print("🌱 Populando banco de dados com dados de teste...\n")

    try:
        # Importar e executar seed_database
        from seed_database import (
            clear_database,
            print_summary,
            seed_audit_logs,
            seed_big_rocks,
            seed_cycle_patterns,
            seed_daily_logs,
            seed_menstrual_cycles,
            seed_tasks,
            seed_users,
        )
        from database.config import SessionLocal

        db = SessionLocal()

        try:
            # Limpar dados existentes
            clear_database(db)

            # Popular dados
            users = seed_users(db)
            big_rocks = seed_big_rocks(db, users)
            seed_tasks(db, users, big_rocks)
            seed_menstrual_cycles(db, users)
            seed_cycle_patterns(db)
            seed_daily_logs(db, users)
            seed_audit_logs(db, users)

            # Resumo
            print_summary(db)

            return True

        except Exception as e:
            print(f"\n❌ Erro ao popular banco de dados: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Erro ao importar módulos: {e}")
        return False


def main():
    """Função principal."""
    print("=" * 60)
    print("🚀 SETUP COMPLETO DO BANCO DE DADOS CHARLEE")
    print("=" * 60)
    print()

    # Passo 1: Criar tabelas
    if not create_tables():
        print("\n❌ Falha ao criar tabelas. Abortando.")
        sys.exit(1)

    # Passo 2: Popular dados
    if not seed_data():
        print("\n❌ Falha ao popular dados. Abortando.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("🎉 SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print("\n📝 Você pode fazer login com:")
    print("   • Username: samara | Password: TestPass123")
    print("   • Username: maria.silva | Password: TestPass123")
    print("   • Username: joaodev | Password: TestPass123")
    print("\n🚀 Inicie o servidor com: uvicorn api.main:app --reload")
    print("=" * 60)


if __name__ == "__main__":
    main()
