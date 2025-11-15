"""Sistema de Priorização Inteligente de Tarefas."""

from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from database.models import Task


class SistemaPriorizacao:
    """
    Sistema de priorização baseado em múltiplos fatores.

    Fatores considerados:
    - Urgência (deadline próximo)
    - Importância (Big Rock estratégico)
    - Complexidade estimada
    - Tempo sem movimento
    - Dependências
    """

    def __init__(self, db: Session):
        self.db = db

    def calcular_prioridade(self, tarefa: Task) -> float:
        """
        Calcula score de prioridade para uma tarefa.

        Score maior = mais prioritário
        """
        score = 0.0

        # Fator 1: Urgência do deadline (40%)
        score += self._calcular_urgencia(tarefa) * 0.4

        # Fator 2: Importância do Big Rock (30%)
        score += self._calcular_importancia(tarefa) * 0.3

        # Fator 3: Tempo sem movimento (20%)
        score += self._calcular_abandono(tarefa) * 0.2

        # Fator 4: Tipo de tarefa (10%)
        score += self._calcular_tipo(tarefa) * 0.1

        return score

    def _calcular_urgencia(self, tarefa: Task) -> float:
        """
        Calcula score de urgência baseado no deadline.

        Score: 0.0 (não urgente) a 1.0 (muito urgente)
        """
        if not tarefa.deadline:
            return 0.3  # Tarefas sem deadline têm prioridade baixa

        hoje = date.today()
        dias_ate_deadline = (tarefa.deadline - hoje).days

        if dias_ate_deadline < 0:
            # Já passou do prazo!
            return 1.0

        elif dias_ate_deadline == 0:
            # Vence hoje
            return 0.95

        elif dias_ate_deadline <= 2:
            # 1-2 dias
            return 0.9

        elif dias_ate_deadline <= 7:
            # 1 semana
            return 0.7

        elif dias_ate_deadline <= 14:
            # 2 semanas
            return 0.5

        elif dias_ate_deadline <= 30:
            # 1 mês
            return 0.3

        else:
            # Mais de 1 mês
            return 0.1

    def _calcular_importancia(self, tarefa: Task) -> float:
        """
        Calcula score de importância baseado no Big Rock.

        Score: 0.0 a 1.0
        """
        if not tarefa.big_rock:
            return 0.5  # Neutro

        # Você pode ajustar isso baseado em prioridades de Big Rocks
        # Por exemplo, Big Rocks estratégicos podem ter score maior
        big_rocks_estrategicos = ["Syssa - Estágio", "Crise Lunelli"]

        if tarefa.big_rock.nome in big_rocks_estrategicos:
            return 1.0
        else:
            return 0.6

    def _calcular_abandono(self, tarefa: Task) -> float:
        """
        Calcula score de abandono (tempo sem atualização).

        Score: 0.0 a 1.0
        """
        hoje = datetime.now(timezone.utc)
        dias_sem_atualizacao = (hoje - tarefa.atualizado_em).days

        if dias_sem_atualizacao > 30:
            # Mais de 1 mês sem mexer - precisa atenção
            return 0.8

        elif dias_sem_atualizacao > 14:
            # Mais de 2 semanas
            return 0.6

        elif dias_sem_atualizacao > 7:
            # Mais de 1 semana
            return 0.4

        else:
            return 0.2

    def _calcular_tipo(self, tarefa: Task) -> float:
        """
        Calcula score baseado no tipo de tarefa.

        Compromisso Fixo > Task > Contínuo
        """
        tipo_scores = {"Compromisso Fixo": 1.0, "Task": 0.7, "Contínuo": 0.4}

        return tipo_scores.get(tarefa.tipo, 0.5)

    def priorizar_tarefas(
        self, status: str = "Pendente", big_rock_id: Optional[int] = None, limite: int = 20
    ) -> List[Task]:
        """
        Retorna lista de tarefas priorizadas.

        Args:
            status: Filtrar por status
            big_rock_id: Filtrar por Big Rock
            limite: Número máximo de tarefas
        """
        # Buscar tarefas
        query = self.db.query(Task).filter(Task.status == status)

        if big_rock_id:
            query = query.filter(Task.big_rock_id == big_rock_id)

        tarefas = query.all()

        # Calcular prioridades
        for tarefa in tarefas:
            score = self.calcular_prioridade(tarefa)
            tarefa.pontuacao_prioridade = score

            # Converter score para nível 1-10 (1 = mais prioritário)
            # Score vai de 0.0 a 1.0, então invertemos
            tarefa.prioridade_calculada = max(1, min(10, int((1.0 - score) * 10) + 1))

        # Commit das atualizações
        self.db.commit()

        # Ordenar por score (maior = mais prioritário)
        tarefas_priorizadas = sorted(tarefas, key=lambda t: t.pontuacao_prioridade, reverse=True)

        return tarefas_priorizadas[:limite]

    def gerar_inbox_rapido(self, limite: int = 10) -> str:
        """
        Gera inbox rápido com as tarefas mais urgentes.

        Returns:
            String formatada com as tarefas priorizadas
        """
        tarefas = self.priorizar_tarefas(limite=limite)

        if not tarefas:
            return "📭 Inbox vazio! Nenhuma tarefa pendente."

        result = f"📥 **INBOX RÁPIDO** - Top {min(len(tarefas), limite)} tarefas\n\n"

        for i, tarefa in enumerate(tarefas, 1):
            # Emoji de prioridade
            if tarefa.prioridade_calculada <= 3:
                emoji_prioridade = "🔴"
            elif tarefa.prioridade_calculada <= 6:
                emoji_prioridade = "🟡"
            else:
                emoji_prioridade = "🟢"

            # Big Rock
            big_rock_nome = tarefa.big_rock.nome if tarefa.big_rock else "Sem categoria"

            # Deadline
            if tarefa.deadline:
                hoje = date.today()
                dias_restantes = (tarefa.deadline - hoje).days

                if dias_restantes < 0:
                    deadline_str = f"⚠️ ATRASADO ({abs(dias_restantes)}d)"
                elif dias_restantes == 0:
                    deadline_str = "🔥 HOJE"
                elif dias_restantes <= 2:
                    deadline_str = f"📅 {dias_restantes}d"
                else:
                    deadline_str = f"📅 {tarefa.deadline.strftime('%d/%m')}"
            else:
                deadline_str = ""

            result += f"{emoji_prioridade} **{i}. {tarefa.descricao}**\n"
            result += f"   📁 {big_rock_nome}"

            if deadline_str:
                result += f" | {deadline_str}"

            result += f" | P{tarefa.prioridade_calculada}\n\n"

        return result


def create_sistema_priorizacao(db: Session) -> SistemaPriorizacao:
    """Factory function."""
    return SistemaPriorizacao(db)
