"""Core Charlee Agent - Agente principal do sistema."""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PgAgentStorage
from sqlalchemy.orm import Session
from typing import Optional
from database.config import settings
from database import crud, schemas


class CharleeAgent(Agent):
    """
    Charlee - Agente principal do sistema de inteligência pessoal.

    O Charlee é o segundo cérebro de Samara, ajudando com:
    - Gestão de tarefas e Big Rocks
    - Priorização inteligente
    - Inbox rápido
    - Planejamento estratégico
    """

    def __init__(self, db: Session):
        """Initialize Charlee agent with database session."""
        self.db = db

        # Initialize with GPT-4o mini model
        super().__init__(
            name="Charlee",
            model=OpenAIChat(id="gpt-4o-mini"),
            markdown=True,
            show_tool_calls=True,
            instructions=[
                "Você é Charlee, o sistema de inteligência pessoal de Samara.",
                "Seu papel é ajudar Samara a gerenciar suas tarefas, Big Rocks (pilares de vida) e prioridades.",
                "Seja concisa, direta e empática.",
                "Use linguagem natural e brasileira.",
                "Quando criar tarefas, sempre pergunte qual Big Rock está associado.",
                "Priorize clareza e ação sobre explicações longas.",
            ],
            storage=self._create_storage() if settings.database_url else None,
        )

        # Add tools
        self.register_function(self.listar_big_rocks)
        self.register_function(self.criar_big_rock)
        self.register_function(self.listar_tarefas)
        self.register_function(self.criar_tarefa)
        self.register_function(self.marcar_tarefa_concluida)
        self.register_function(self.atualizar_tarefa)

    def _create_storage(self) -> PgAgentStorage:
        """Create PostgreSQL storage for agent memory."""
        return PgAgentStorage(
            table_name="charlee_sessions",
            db_url=settings.database_url
        )

    # ==================== Big Rocks Tools ====================

    def listar_big_rocks(self, ativo_apenas: bool = True) -> str:
        """
        Lista todos os Big Rocks (pilares de vida) cadastrados.

        Args:
            ativo_apenas: Se True, lista apenas Big Rocks ativos
        """
        big_rocks = crud.get_big_rocks(self.db, ativo_apenas=ativo_apenas)

        if not big_rocks:
            return "Nenhum Big Rock cadastrado ainda."

        resultado = "🎯 **Big Rocks:**\n\n"
        for br in big_rocks:
            status = "✅" if br.ativo else "❌"
            resultado += f"{status} **{br.nome}** (ID: {br.id})\n"

        return resultado

    def criar_big_rock(self, nome: str, cor: Optional[str] = None) -> str:
        """
        Cria um novo Big Rock (pilar de vida).

        Args:
            nome: Nome do Big Rock (ex: "Syssa - Estágio", "Crise Lunelli")
            cor: Cor para UI futura (opcional, ex: "#FF5733")
        """
        try:
            big_rock_data = schemas.BigRockCreate(nome=nome, cor=cor)
            new_big_rock = crud.create_big_rock(self.db, big_rock_data)

            return f"✅ Big Rock **'{new_big_rock.nome}'** criado com sucesso! (ID: {new_big_rock.id})"
        except Exception as e:
            return f"❌ Erro ao criar Big Rock: {str(e)}"

    # ==================== Tarefas Tools ====================

    def listar_tarefas(
        self,
        status: Optional[str] = None,
        big_rock_id: Optional[int] = None,
        limite: int = 20
    ) -> str:
        """
        Lista tarefas com filtros opcionais.

        Args:
            status: Filtrar por status ("Pendente", "Em Progresso", "Concluída", "Cancelada")
            big_rock_id: Filtrar por ID do Big Rock
            limite: Número máximo de tarefas a retornar
        """
        tarefas = crud.get_tarefas(
            self.db,
            status=status,
            big_rock_id=big_rock_id,
            limit=limite
        )

        if not tarefas:
            filtros = []
            if status:
                filtros.append(f"status '{status}'")
            if big_rock_id:
                filtros.append(f"Big Rock ID {big_rock_id}")

            filtro_str = " com " + " e ".join(filtros) if filtros else ""
            return f"Nenhuma tarefa encontrada{filtro_str}."

        resultado = f"📋 **Tarefas** (mostrando {len(tarefas)}):\n\n"

        for tarefa in tarefas:
            status_emoji = {
                "Pendente": "⏳",
                "Em Progresso": "🔄",
                "Concluída": "✅",
                "Cancelada": "❌"
            }.get(tarefa.status, "❓")

            big_rock_nome = tarefa.big_rock.nome if tarefa.big_rock else "Sem Big Rock"
            deadline_str = f" | 📅 {tarefa.deadline}" if tarefa.deadline else ""

            resultado += f"{status_emoji} **[{tarefa.id}]** {tarefa.descricao}\n"
            resultado += f"   📁 {big_rock_nome}{deadline_str}\n\n"

        return resultado

    def criar_tarefa(
        self,
        descricao: str,
        big_rock_id: Optional[int] = None,
        tipo: str = "Tarefa",
        deadline: Optional[str] = None
    ) -> str:
        """
        Cria uma nova tarefa.

        Args:
            descricao: Descrição da tarefa
            big_rock_id: ID do Big Rock associado (opcional)
            tipo: Tipo da tarefa ("Tarefa", "Compromisso Fixo", "Contínuo")
            deadline: Data limite no formato YYYY-MM-DD (opcional)
        """
        try:
            from datetime import datetime

            deadline_date = None
            if deadline:
                try:
                    deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
                except ValueError:
                    return "❌ Formato de data inválido. Use YYYY-MM-DD (ex: 2025-01-15)"

            tarefa_data = schemas.TarefaCreate(
                descricao=descricao,
                big_rock_id=big_rock_id,
                tipo=tipo,
                deadline=deadline_date
            )

            new_tarefa = crud.create_tarefa(self.db, tarefa_data)

            big_rock_info = ""
            if new_tarefa.big_rock:
                big_rock_info = f" no Big Rock **{new_tarefa.big_rock.nome}**"

            return f"✅ Tarefa criada com sucesso{big_rock_info}! (ID: {new_tarefa.id})"

        except Exception as e:
            return f"❌ Erro ao criar tarefa: {str(e)}"

    def marcar_tarefa_concluida(self, tarefa_id: int) -> str:
        """
        Marca uma tarefa como concluída.

        Args:
            tarefa_id: ID da tarefa
        """
        try:
            tarefa = crud.marcar_tarefa_concluida(self.db, tarefa_id)

            if not tarefa:
                return f"❌ Tarefa com ID {tarefa_id} não encontrada."

            return f"✅ Tarefa **'{tarefa.descricao}'** marcada como concluída! 🎉"

        except Exception as e:
            return f"❌ Erro ao marcar tarefa como concluída: {str(e)}"

    def atualizar_tarefa(
        self,
        tarefa_id: int,
        descricao: Optional[str] = None,
        status: Optional[str] = None,
        big_rock_id: Optional[int] = None,
        deadline: Optional[str] = None
    ) -> str:
        """
        Atualiza uma tarefa existente.

        Args:
            tarefa_id: ID da tarefa
            descricao: Nova descrição (opcional)
            status: Novo status (opcional)
            big_rock_id: Novo Big Rock ID (opcional)
            deadline: Nova deadline no formato YYYY-MM-DD (opcional)
        """
        try:
            from datetime import datetime

            deadline_date = None
            if deadline:
                try:
                    deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
                except ValueError:
                    return "❌ Formato de data inválido. Use YYYY-MM-DD"

            update_data = schemas.TarefaUpdate(
                descricao=descricao,
                status=status,
                big_rock_id=big_rock_id,
                deadline=deadline_date
            )

            tarefa = crud.update_tarefa(self.db, tarefa_id, update_data)

            if not tarefa:
                return f"❌ Tarefa com ID {tarefa_id} não encontrada."

            return f"✅ Tarefa **'{tarefa.descricao}'** atualizada com sucesso!"

        except Exception as e:
            return f"❌ Erro ao atualizar tarefa: {str(e)}"


def create_charlee_agent(db: Session) -> CharleeAgent:
    """Factory function to create a Charlee agent instance."""
    return CharleeAgent(db)
