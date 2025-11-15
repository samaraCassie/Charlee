"""
Script para popular o banco de dados com dados de teste.

Uso:
    python seed_database.py

O script detecta automaticamente se está usando SQLite ou PostgreSQL
e ajusta as queries conforme necessário.
"""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from api.auth.password import hash_password
from database.config import SessionLocal
from database.models import (
    AuditLog,
    BigRock,
    CyclePatterns,
    DailyLog,
    MenstrualCycle,
    RefreshToken,
    Task,
    User,
    Workload,
)


def clear_database(db: Session):
    """Limpa todos os dados do banco (ordem importante devido às FKs)."""
    print("🗑️  Limpando dados existentes...")

    db.query(AuditLog).delete()
    db.query(RefreshToken).delete()
    db.query(DailyLog).delete()
    db.query(Workload).delete()
    db.query(CyclePatterns).delete()
    db.query(MenstrualCycle).delete()
    db.query(Task).delete()
    db.query(BigRock).delete()
    db.query(User).delete()

    db.commit()
    print("✅ Dados limpos com sucesso!")


def seed_users(db: Session):
    """Cria usuários de teste."""
    print("\n👥 Criando usuários...")

    # Senha padrão para todos: "TestPass123"
    password_hash = hash_password("TestPass123")

    users = [
        User(
            username="samara",
            email="samara@charlee.app",
            hashed_password=password_hash,
            full_name="Samara Cassie",
            is_active=True,
            is_superuser=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=90),
            last_login=datetime.now(timezone.utc) - timedelta(hours=2),
        ),
        User(
            username="maria.silva",
            email="maria.silva@gmail.com",
            hashed_password=password_hash,
            full_name="Maria Silva",
            is_active=True,
            is_superuser=False,
            oauth_provider="google",
            oauth_id="google_123456789",
            avatar_url="https://lh3.googleusercontent.com/a/default-user",
            created_at=datetime.now(timezone.utc) - timedelta(days=60),
            last_login=datetime.now(timezone.utc) - timedelta(days=1),
        ),
        User(
            username="joaodev",
            email="joao@example.com",
            hashed_password=password_hash,
            full_name="João Desenvolvedor",
            is_active=True,
            is_superuser=False,
            oauth_provider="github",
            oauth_id="987654321",
            avatar_url="https://avatars.githubusercontent.com/u/987654321",
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
            last_login=datetime.now(timezone.utc) - timedelta(days=5),
        ),
        User(
            username="ana",
            email="ana@example.com",
            hashed_password=password_hash,
            full_name="Ana Oliveira",
            is_active=False,
            is_superuser=False,
            created_at=datetime.now(timezone.utc) - timedelta(days=180),
            last_login=datetime.now(timezone.utc) - timedelta(days=180),
        ),
    ]

    db.add_all(users)
    db.commit()

    for user in users:
        db.refresh(user)

    print(f"✅ {len(users)} usuários criados!")
    return users


def seed_big_rocks(db: Session, users: list[User]):
    """Cria Big Rocks para os usuários."""
    print("\n🪨 Criando Big Rocks...")

    big_rocks = [
        # Big Rocks da Samara (user 0)
        BigRock(
            user_id=users[0].id,
            name="Saúde & Bem-estar",
            color="#22c55e",
            active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=90),
        ),
        BigRock(
            user_id=users[0].id,
            name="Carreira & Desenvolvimento",
            color="#3b82f6",
            active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=90),
        ),
        BigRock(
            user_id=users[0].id,
            name="Relacionamentos",
            color="#ec4899",
            active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=90),
        ),
        BigRock(
            user_id=users[0].id,
            name="Finanças",
            color="#f59e0b",
            active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=90),
        ),
        BigRock(
            user_id=users[0].id,
            name="Aprendizado Contínuo",
            color="#8b5cf6",
            active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=60),
        ),
        BigRock(
            user_id=users[0].id,
            name="Hobbies & Lazer",
            color="#06b6d4",
            active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        ),
        # Big Rocks da Maria (user 1)
        BigRock(
            user_id=users[1].id,
            name="Saúde Mental",
            color="#10b981",
            active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=60),
        ),
        BigRock(
            user_id=users[1].id,
            name="Trabalho",
            color="#6366f1",
            active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=60),
        ),
        BigRock(
            user_id=users[1].id,
            name="Família",
            color="#f43f5e",
            active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=60),
        ),
        BigRock(
            user_id=users[1].id,
            name="Casa",
            color="#14b8a6",
            active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=45),
        ),
        # Big Rocks do João (user 2)
        BigRock(
            user_id=users[2].id,
            name="Projetos Open Source",
            color="#8b5cf6",
            active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        ),
        BigRock(
            user_id=users[2].id,
            name="Fitness",
            color="#22c55e",
            active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        ),
        BigRock(
            user_id=users[2].id,
            name="Estudos",
            color="#3b82f6",
            active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=20),
        ),
    ]

    db.add_all(big_rocks)
    db.commit()

    for br in big_rocks:
        db.refresh(br)

    print(f"✅ {len(big_rocks)} Big Rocks criados!")
    return big_rocks


def seed_tasks(db: Session, users: list[User], big_rocks: list[BigRock]):
    """Cria tarefas de teste."""
    print("\n✅ Criando tarefas...")

    today = date.today()

    tasks = [
        # Tarefas da Samara - Saúde & Bem-estar
        Task(
            user_id=users[0].id,
            description="Caminhada matinal 30min",
            type="continuous",
            big_rock_id=big_rocks[0].id,
            status="in_progress",
            calculated_priority=3,
            priority_score=7.5,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        ),
        Task(
            user_id=users[0].id,
            description="Consulta com nutricionista",
            type="fixed_appointment",
            deadline=today + timedelta(days=7),
            big_rock_id=big_rocks[0].id,
            status="pending",
            calculated_priority=2,
            priority_score=8.2,
            created_at=datetime.now(timezone.utc) - timedelta(days=5),
        ),
        Task(
            user_id=users[0].id,
            description="Fazer exames de rotina",
            type="task",
            deadline=today + timedelta(days=15),
            big_rock_id=big_rocks[0].id,
            status="pending",
            calculated_priority=4,
            priority_score=6.8,
            created_at=datetime.now(timezone.utc) - timedelta(days=10),
        ),
        Task(
            user_id=users[0].id,
            description="Yoga às terças e quintas",
            type="continuous",
            big_rock_id=big_rocks[0].id,
            status="in_progress",
            calculated_priority=3,
            priority_score=7.0,
            created_at=datetime.now(timezone.utc) - timedelta(days=20),
        ),
        # Tarefas da Samara - Carreira
        Task(
            user_id=users[0].id,
            description="Reunião semanal com equipe",
            type="fixed_appointment",
            deadline=today + timedelta(days=2),
            big_rock_id=big_rocks[1].id,
            status="pending",
            calculated_priority=1,
            priority_score=9.5,
            created_at=datetime.now(timezone.utc) - timedelta(days=7),
        ),
        Task(
            user_id=users[0].id,
            description="Finalizar feature de autenticação OAuth",
            type="task",
            deadline=today + timedelta(days=3),
            big_rock_id=big_rocks[1].id,
            status="in_progress",
            calculated_priority=1,
            priority_score=9.2,
            created_at=datetime.now(timezone.utc) - timedelta(days=14),
        ),
        Task(
            user_id=users[0].id,
            description="Code review dos PRs pendentes",
            type="task",
            deadline=today + timedelta(days=1),
            big_rock_id=big_rocks[1].id,
            status="pending",
            calculated_priority=2,
            priority_score=8.5,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
        ),
        Task(
            user_id=users[0].id,
            description="Atualizar documentação técnica",
            type="task",
            deadline=today + timedelta(days=10),
            big_rock_id=big_rocks[1].id,
            status="pending",
            calculated_priority=4,
            priority_score=6.5,
            created_at=datetime.now(timezone.utc) - timedelta(days=5),
        ),
        # Tarefas da Samara - Relacionamentos
        Task(
            user_id=users[0].id,
            description="Jantar com família no domingo",
            type="fixed_appointment",
            deadline=today + timedelta(days=5),
            big_rock_id=big_rocks[2].id,
            status="pending",
            calculated_priority=3,
            priority_score=7.5,
            created_at=datetime.now(timezone.utc) - timedelta(days=3),
        ),
        Task(
            user_id=users[0].id,
            description="Ligar para a mãe",
            type="task",
            deadline=today + timedelta(days=2),
            big_rock_id=big_rocks[2].id,
            status="pending",
            calculated_priority=2,
            priority_score=8.0,
            created_at=datetime.now(timezone.utc) - timedelta(days=1),
        ),
        # Tarefas da Samara - Finanças
        Task(
            user_id=users[0].id,
            description="Pagar conta de luz",
            type="task",
            deadline=today + timedelta(days=5),
            big_rock_id=big_rocks[3].id,
            status="pending",
            calculated_priority=2,
            priority_score=8.3,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
        ),
        Task(
            user_id=users[0].id,
            description="Revisar investimentos mensais",
            type="task",
            deadline=today + timedelta(days=7),
            big_rock_id=big_rocks[3].id,
            status="pending",
            calculated_priority=3,
            priority_score=7.2,
            created_at=datetime.now(timezone.utc) - timedelta(days=5),
        ),
        # Tarefas da Samara - Aprendizado
        Task(
            user_id=users[0].id,
            description="Completar curso de FastAPI",
            type="task",
            deadline=today + timedelta(days=20),
            big_rock_id=big_rocks[4].id,
            status="in_progress",
            calculated_priority=4,
            priority_score=6.8,
            created_at=datetime.now(timezone.utc) - timedelta(days=15),
        ),
        Task(
            user_id=users[0].id,
            description='Ler "Clean Architecture"',
            type="continuous",
            big_rock_id=big_rocks[4].id,
            status="in_progress",
            calculated_priority=5,
            priority_score=6.2,
            created_at=datetime.now(timezone.utc) - timedelta(days=25),
        ),
        # Tarefas da Samara - Hobbies
        Task(
            user_id=users[0].id,
            description="Assistir filme recomendado",
            type="task",
            big_rock_id=big_rocks[5].id,
            status="pending",
            calculated_priority=8,
            priority_score=3.5,
            created_at=datetime.now(timezone.utc) - timedelta(days=5),
        ),
        Task(
            user_id=users[0].id,
            description="Continuar tricô do cachecol",
            type="continuous",
            big_rock_id=big_rocks[5].id,
            status="in_progress",
            calculated_priority=7,
            priority_score=4.0,
            created_at=datetime.now(timezone.utc) - timedelta(days=20),
        ),
        # Tarefas da Maria
        Task(
            user_id=users[1].id,
            description="Terapia semanal",
            type="fixed_appointment",
            deadline=today + timedelta(days=3),
            big_rock_id=big_rocks[6].id,
            status="pending",
            calculated_priority=1,
            priority_score=9.0,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        ),
        Task(
            user_id=users[1].id,
            description="Journaling diário",
            type="continuous",
            big_rock_id=big_rocks[6].id,
            status="in_progress",
            calculated_priority=4,
            priority_score=6.5,
            created_at=datetime.now(timezone.utc) - timedelta(days=40),
        ),
        Task(
            user_id=users[1].id,
            description="Apresentação para diretoria",
            type="fixed_appointment",
            deadline=today + timedelta(days=2),
            big_rock_id=big_rocks[7].id,
            status="in_progress",
            calculated_priority=1,
            priority_score=9.8,
            created_at=datetime.now(timezone.utc) - timedelta(days=10),
        ),
        Task(
            user_id=users[1].id,
            description="Revisar orçamento do projeto",
            type="task",
            deadline=today + timedelta(days=5),
            big_rock_id=big_rocks[7].id,
            status="pending",
            calculated_priority=2,
            priority_score=8.0,
            created_at=datetime.now(timezone.utc) - timedelta(days=3),
        ),
        # Tarefas do João
        Task(
            user_id=users[2].id,
            description="Contribuir para projeto FastAPI",
            type="task",
            deadline=today + timedelta(days=7),
            big_rock_id=big_rocks[10].id,
            status="in_progress",
            calculated_priority=3,
            priority_score=7.0,
            created_at=datetime.now(timezone.utc) - timedelta(days=10),
        ),
        Task(
            user_id=users[2].id,
            description="Academia 5x por semana",
            type="continuous",
            big_rock_id=big_rocks[11].id,
            status="in_progress",
            calculated_priority=4,
            priority_score=6.5,
            created_at=datetime.now(timezone.utc) - timedelta(days=20),
        ),
        Task(
            user_id=users[2].id,
            description="Completar curso de TypeScript avançado",
            type="task",
            deadline=today + timedelta(days=15),
            big_rock_id=big_rocks[12].id,
            status="in_progress",
            calculated_priority=5,
            priority_score=6.0,
            created_at=datetime.now(timezone.utc) - timedelta(days=12),
        ),
    ]

    db.add_all(tasks)
    db.commit()

    print(f"✅ {len(tasks)} tarefas criadas!")


def seed_menstrual_cycles(db: Session, users: list[User]):
    """Cria registros de ciclo menstrual."""
    print("\n🌙 Criando registros de ciclo menstrual...")

    today = date.today()

    cycles = [
        # Ciclo atual da Samara
        MenstrualCycle(
            user_id=users[0].id,
            start_date=today - timedelta(days=3),
            phase="menstrual",
            symptoms="fadiga,dor_leve",
            energy_level=4,
            focus_level=5,
            creativity_level=6,
            notes="Primeiro dia mais intenso",
            created_at=datetime.now(timezone.utc) - timedelta(days=3),
        ),
        MenstrualCycle(
            user_id=users[0].id,
            start_date=today - timedelta(days=2),
            phase="menstrual",
            symptoms="fadiga",
            energy_level=5,
            focus_level=6,
            creativity_level=7,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
        ),
        # Ciclo anterior
        MenstrualCycle(
            user_id=users[0].id,
            start_date=today - timedelta(days=31),
            phase="menstrual",
            symptoms="fadiga,dor_moderada",
            energy_level=3,
            focus_level=4,
            creativity_level=5,
            created_at=datetime.now(timezone.utc) - timedelta(days=31),
        ),
        MenstrualCycle(
            user_id=users[0].id,
            start_date=today - timedelta(days=27),
            phase="follicular",
            symptoms="energia_alta",
            energy_level=8,
            focus_level=9,
            creativity_level=8,
            notes="Dia muito produtivo!",
            created_at=datetime.now(timezone.utc) - timedelta(days=27),
        ),
        MenstrualCycle(
            user_id=users[0].id,
            start_date=today - timedelta(days=17),
            phase="ovulation",
            symptoms="criatividade_alta,energia_alta",
            energy_level=9,
            focus_level=8,
            creativity_level=10,
            notes="Ótimas ideias!",
            created_at=datetime.now(timezone.utc) - timedelta(days=17),
        ),
        MenstrualCycle(
            user_id=users[0].id,
            start_date=today - timedelta(days=10),
            phase="luteal",
            symptoms="leve_fadiga",
            energy_level=6,
            focus_level=7,
            creativity_level=6,
            created_at=datetime.now(timezone.utc) - timedelta(days=10),
        ),
        # Ciclos da Maria
        MenstrualCycle(
            user_id=users[1].id,
            start_date=today - timedelta(days=5),
            phase="menstrual",
            symptoms="fadiga,dor_moderada",
            energy_level=3,
            focus_level=4,
            creativity_level=5,
            notes="Trabalho de casa",
            created_at=datetime.now(timezone.utc) - timedelta(days=5),
        ),
        MenstrualCycle(
            user_id=users[1].id,
            start_date=today - timedelta(days=20),
            phase="follicular",
            symptoms="energia_alta,foco_intenso",
            energy_level=9,
            focus_level=9,
            creativity_level=8,
            created_at=datetime.now(timezone.utc) - timedelta(days=20),
        ),
    ]

    db.add_all(cycles)
    db.commit()

    print(f"✅ {len(cycles)} registros de ciclo criados!")


def seed_cycle_patterns(db: Session):
    """Cria padrões de ciclo identificados."""
    print("\n📊 Criando padrões de ciclo...")

    patterns = [
        CyclePatterns(
            phase="menstrual",
            identified_pattern="Baixa energia e foco nos primeiros 2 dias",
            average_productivity=0.6,
            average_focus=0.5,
            average_energy=0.4,
            confidence_score=0.75,
            suggestions="Priorizar tarefas simples;Permitir mais descanso;Evitar reuniões importantes",
            samples_used=24,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        ),
        CyclePatterns(
            phase="follicular",
            identified_pattern="Alta energia e foco, ideal para tarefas complexas",
            average_productivity=1.3,
            average_focus=1.4,
            average_energy=1.3,
            confidence_score=0.85,
            suggestions="Tarefas desafiadoras;Aprendizado;Reuniões estratégicas",
            samples_used=28,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        ),
        CyclePatterns(
            phase="ovulation",
            identified_pattern="Pico de criatividade e comunicação",
            average_productivity=1.2,
            average_focus=1.2,
            average_energy=1.4,
            confidence_score=0.80,
            suggestions="Brainstorming;Apresentações;Networking",
            samples_used=15,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        ),
        CyclePatterns(
            phase="luteal",
            identified_pattern="Energia decrescente, foco em organização",
            average_productivity=0.9,
            average_focus=0.8,
            average_energy=0.7,
            confidence_score=0.70,
            suggestions="Tarefas organizacionais;Revisão;Documentação",
            samples_used=22,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        ),
    ]

    db.add_all(patterns)
    db.commit()

    print(f"✅ {len(patterns)} padrões de ciclo criados!")


def seed_daily_logs(db: Session, users: list[User]):
    """Cria logs diários."""
    print("\n📝 Criando logs diários...")

    today = date.today()

    logs = [
        # Logs da Samara (últimos 7 dias)
        DailyLog(
            user_id=users[0].id,
            date=today - timedelta(days=6),
            wake_time="07:00",
            sleep_time="23:30",
            sleep_hours=7.5,
            sleep_quality=8,
            morning_energy=7,
            afternoon_energy=7,
            evening_energy=6,
            deep_work_hours=4.5,
            completed_tasks=8,
            cycle_phase="folicular",
            free_notes="Dia produtivo",
            created_at=datetime.now(timezone.utc) - timedelta(days=6),
        ),
        DailyLog(
            user_id=users[0].id,
            date=today - timedelta(days=5),
            wake_time="07:15",
            sleep_time="00:00",
            sleep_hours=7.25,
            sleep_quality=6,
            morning_energy=6,
            afternoon_energy=6,
            evening_energy=5,
            deep_work_hours=3.0,
            completed_tasks=6,
            cycle_phase="folicular",
            free_notes="Um pouco cansada",
            created_at=datetime.now(timezone.utc) - timedelta(days=5),
        ),
        DailyLog(
            user_id=users[0].id,
            date=today - timedelta(days=4),
            wake_time="06:45",
            sleep_time="23:00",
            sleep_hours=7.75,
            sleep_quality=9,
            morning_energy=8,
            afternoon_energy=9,
            evening_energy=8,
            deep_work_hours=5.5,
            completed_tasks=10,
            cycle_phase="ovulatória",
            free_notes="Melhor dia!",
            created_at=datetime.now(timezone.utc) - timedelta(days=4),
        ),
        DailyLog(
            user_id=users[0].id,
            date=today - timedelta(days=3),
            wake_time="07:30",
            sleep_time="00:30",
            sleep_hours=7.0,
            sleep_quality=5,
            morning_energy=5,
            afternoon_energy=4,
            evening_energy=4,
            deep_work_hours=2.0,
            completed_tasks=4,
            cycle_phase="menstrual",
            special_events="Menstruação começou",
            free_notes="Baixa energia",
            created_at=datetime.now(timezone.utc) - timedelta(days=3),
        ),
        DailyLog(
            user_id=users[0].id,
            date=today - timedelta(days=2),
            wake_time="08:00",
            sleep_time="00:00",
            sleep_hours=8.0,
            sleep_quality=7,
            morning_energy=6,
            afternoon_energy=6,
            evening_energy=5,
            deep_work_hours=3.0,
            completed_tasks=5,
            cycle_phase="menstrual",
            free_notes="Melhorando",
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
        ),
        DailyLog(
            user_id=users[0].id,
            date=today - timedelta(days=1),
            wake_time="07:00",
            sleep_time="23:30",
            sleep_hours=7.5,
            sleep_quality=8,
            morning_energy=7,
            afternoon_energy=7,
            evening_energy=7,
            deep_work_hours=4.0,
            completed_tasks=7,
            cycle_phase="folicular",
            free_notes="Energia voltando",
            created_at=datetime.now(timezone.utc) - timedelta(days=1),
        ),
        DailyLog(
            user_id=users[0].id,
            date=today,
            wake_time="07:15",
            morning_energy=7,
            afternoon_energy=8,
            evening_energy=7,
            deep_work_hours=0.0,
            completed_tasks=0,
            cycle_phase="folicular",
            free_notes="Dia começando bem",
            created_at=datetime.now(timezone.utc),
        ),
        # Logs da Maria
        DailyLog(
            user_id=users[1].id,
            date=today - timedelta(days=2),
            wake_time="06:30",
            sleep_time="22:30",
            sleep_hours=8.0,
            sleep_quality=9,
            morning_energy=8,
            afternoon_energy=8,
            evening_energy=7,
            deep_work_hours=5.0,
            completed_tasks=9,
            cycle_phase="lútea",
            free_notes="Ótimo dia",
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
        ),
        DailyLog(
            user_id=users[1].id,
            date=today - timedelta(days=1),
            wake_time="06:45",
            sleep_time="23:00",
            sleep_hours=7.75,
            sleep_quality=7,
            morning_energy=7,
            afternoon_energy=7,
            evening_energy=6,
            deep_work_hours=4.0,
            completed_tasks=7,
            cycle_phase="lútea",
            free_notes="Dia normal",
            created_at=datetime.now(timezone.utc) - timedelta(days=1),
        ),
        DailyLog(
            user_id=users[1].id,
            date=today,
            wake_time="06:30",
            morning_energy=8,
            afternoon_energy=8,
            evening_energy=7,
            deep_work_hours=0.0,
            completed_tasks=0,
            cycle_phase="lútea",
            free_notes="Começando bem",
            created_at=datetime.now(timezone.utc),
        ),
    ]

    db.add_all(logs)
    db.commit()

    print(f"✅ {len(logs)} logs diários criados!")


def seed_audit_logs(db: Session, users: list[User]):
    """Cria logs de auditoria."""
    print("\n🔍 Criando logs de auditoria...")

    logs = [
        # Samara
        AuditLog(
            user_id=users[0].id,
            event_type="register",
            event_status="success",
            event_message="Usuário registrado",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            request_path="/api/v1/auth/register",
            created_at=datetime.now(timezone.utc) - timedelta(days=90),
        ),
        AuditLog(
            user_id=users[0].id,
            event_type="login",
            event_status="success",
            event_message="Login bem-sucedido",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            request_path="/api/v1/auth/login",
            event_metadata='{"method": "password"}',
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
        ),
        AuditLog(
            user_id=users[0].id,
            event_type="password_change",
            event_status="success",
            event_message="Senha alterada",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            request_path="/api/v1/auth/change-password",
            created_at=datetime.now(timezone.utc) - timedelta(days=45),
        ),
        # Maria (OAuth)
        AuditLog(
            user_id=users[1].id,
            event_type="register",
            event_status="success",
            event_message="Registro via OAuth",
            ip_address="192.168.1.200",
            user_agent="Mozilla/5.0",
            request_path="/api/v1/auth/oauth/google/callback",
            event_metadata='{"provider": "google"}',
            created_at=datetime.now(timezone.utc) - timedelta(days=60),
        ),
        AuditLog(
            user_id=users[1].id,
            event_type="oauth_login",
            event_status="success",
            event_message="Login via Google",
            ip_address="192.168.1.200",
            user_agent="Mozilla/5.0",
            request_path="/api/v1/auth/oauth/google/callback",
            event_metadata='{"provider": "google"}',
            created_at=datetime.now(timezone.utc) - timedelta(days=1),
        ),
        # João (OAuth GitHub)
        AuditLog(
            user_id=users[2].id,
            event_type="register",
            event_status="success",
            event_message="Registro via OAuth",
            ip_address="192.168.1.150",
            user_agent="Mozilla/5.0",
            request_path="/api/v1/auth/oauth/github/callback",
            event_metadata='{"provider": "github"}',
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        ),
        AuditLog(
            user_id=users[2].id,
            event_type="oauth_login",
            event_status="success",
            event_message="Login via GitHub",
            ip_address="192.168.1.150",
            user_agent="Mozilla/5.0",
            request_path="/api/v1/auth/oauth/github/callback",
            event_metadata='{"provider": "github"}',
            created_at=datetime.now(timezone.utc) - timedelta(days=5),
        ),
        # Ana (conta inativa)
        AuditLog(
            user_id=users[3].id,
            event_type="register",
            event_status="success",
            event_message="Usuário registrado",
            ip_address="192.168.1.180",
            user_agent="Mozilla/5.0",
            request_path="/api/v1/auth/register",
            created_at=datetime.now(timezone.utc) - timedelta(days=180),
        ),
        AuditLog(
            user_id=users[3].id,
            event_type="login",
            event_status="blocked",
            event_message="Conta inativa",
            ip_address="192.168.1.180",
            user_agent="Mozilla/5.0",
            request_path="/api/v1/auth/login",
            event_metadata='{"reason": "inactive"}',
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        ),
    ]

    db.add_all(logs)
    db.commit()

    print(f"✅ {len(logs)} logs de auditoria criados!")


def print_summary(db: Session):
    """Imprime resumo dos dados criados."""
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS DADOS INSERIDOS")
    print("=" * 50)

    counts = {
        "Usuários": db.query(User).count(),
        "Big Rocks": db.query(BigRock).count(),
        "Tarefas": db.query(Task).count(),
        "Ciclos Menstruais": db.query(MenstrualCycle).count(),
        "Padrões de Ciclo": db.query(CyclePatterns).count(),
        "Logs Diários": db.query(DailyLog).count(),
        "Logs de Auditoria": db.query(AuditLog).count(),
    }

    for name, count in counts.items():
        print(f"  {name}: {count}")

    print("=" * 50)
    print("\n✨ Banco de dados populado com sucesso!")
    print("\n📝 Credenciais de teste:")
    print("  Username: samara | Password: TestPass123 (admin)")
    print("  Username: maria.silva | Password: TestPass123")
    print("  Username: joaodev | Password: TestPass123")
    print("  Username: ana | Password: TestPass123 (inativa)")
    print("=" * 50)


def main():
    """Função principal."""
    print("🌱 Iniciando seed do banco de dados Charlee...\n")

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

    except Exception as e:
        print(f"\n❌ Erro ao popular banco de dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
