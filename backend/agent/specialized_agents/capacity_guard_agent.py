"""CapacityGuardAgent - Agente que protege contra sobrecarga."""

from datetime import date, timedelta
from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sqlalchemy.orm import Session

from database.models import BigRock, Task


class CapacityGuardAgent(Agent):
    """
    Agente guardião da capacidade de Samara.

    Funções:
    - Calcula carga de trabalho por Big Rock
    - Identifica sobrecargas ANTES que aconteçam
    - Force decisões conscientes sobre trade-offs
    - Protege Samara de si mesma
    """

    def __init__(self, db: Session):
        """Initialize CapacityGuardAgent."""
        self.database = db

        super().__init__(
            name="Capacity Guardian",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "Você é o guardião da capacidade de Samara.",
                "Calcule carga de trabalho e identifique sobrecargas.",
                "Force decisões conscientes sobre trade-offs.",
                "Seja firme mas empática ao alertar sobre limites.",
                "Ajude a proteger o bem-estar dela.",
            ],
            tools=[
                self.calcular_carga_atual,
                self.avaliar_novo_compromisso,
                self.sugerir_tradeoffs,
                self.analisar_big_rocks,
            ],
        )

    def calcular_carga_atual(self, proximas_semanas: int = 3) -> str:
        """
        Calcula a carga de trabalho atual por Big Rock.

        Args:
            proximas_semanas: Quantas semanas analisar (padrão: 3)
        """
        try:
            data_limite = date.today() + timedelta(weeks=proximas_semanas)

            # Buscar todos os Big Rocks ativos
            big_rocks = self.database.query(BigRock).filter(BigRock.ativo).all()

            result = f"📊 **Análise de Carga - Próximas {proximas_semanas} semanas**\n\n"

            total_tarefas = 0
            big_rocks_em_risco = []

            for br in big_rocks:
                # Contar tarefas pendentes deste Big Rock
                tarefas = (
                    self.database.query(Task)
                    .filter(Task.big_rock_id == br.id)
                    .filter(Task.status == "Pendente")
                    .filter(Task.deadline <= data_limite)
                    .all()
                )

                num_tarefas = len(tarefas)
                total_tarefas += num_tarefas

                # Análise de risco (mais de 10 tarefas em 3 semanas = risco)
                em_risco = num_tarefas > 10

                status_emoji = "🚨" if em_risco else "✅" if num_tarefas > 0 else "⚪"

                result += f"{status_emoji} **{br.nome}**: {num_tarefas} tarefas"

                if em_risco:
                    result += " ⚠️ SOBRECARGA"
                    big_rocks_em_risco.append(br.nome)

                result += "\n"

            result += f"\n📋 **Total**: {total_tarefas} tarefas\n"

            # Análise geral
            if total_tarefas > 30:
                result += "\n🚨 **ALERTA CRÍTICO: Sobrecarga geral detectada!**\n"
                result += "Você está com mais de 30 tarefas para as próximas semanas.\n"
                result += "É **impossível** fazer tudo com qualidade.\n\n"
                result += "💡 **Ação necessária**: Priorize ou adie tarefas."
            elif total_tarefas > 20:
                result += "\n⚠️ **Atenção**: Carga alta detectada.\n"
                result += "Monitore sua capacidade e esteja preparada para ajustes.\n"
            else:
                result += "\n✅ Carga equilibrada.\n"

            if big_rocks_em_risco:
                result += f"\n🔥 **Big Rocks em risco**: {', '.join(big_rocks_em_risco)}\n"

            return result

        except Exception as e:
            return f"❌ Erro: {str(e)}"

    def avaliar_novo_compromisso(
        self,
        nome_compromisso: str,
        tarefas_estimadas: int,
        big_rock_nome: Optional[str] = None,
    ) -> str:
        """
        Avalia se há capacidade para um novo compromisso.

        Args:
            nome_compromisso: Nome do novo projeto/compromisso
            tarefas_estimadas: Número estimado de tarefas
            big_rock_nome: Big Rock associado (opcional)
        """
        try:
            # Calcular carga atual
            data_limite = date.today() + timedelta(weeks=3)

            tarefas_atuais = (
                self.database.query(Task)
                .filter(Task.status == "Pendente")
                .filter(Task.deadline <= data_limite)
                .count()
            )

            # Capacidade máxima (considerando 5 tarefas/semana como saudável)
            capacidade_saudavel = 15  # 3 semanas * 5 tarefas
            capacidade_maxima = 25  # Limite absoluto

            carga_atual = tarefas_atuais
            carga_projetada = carga_atual + tarefas_estimadas
            percentual_atual = (carga_atual / capacidade_maxima) * 100
            percentual_projetado = (carga_projetada / capacidade_maxima) * 100

            result = f"🔍 **Avaliação: '{nome_compromisso}'**\n\n"
            result += "📊 **Análise de Capacidade (3 semanas):**\n"
            result += f"• Carga atual: {carga_atual} tarefas ({percentual_atual:.0f}%)\n"
            result += (
                f"• Com novo compromisso: {carga_projetada} tarefas ({percentual_projetado:.0f}%)\n"
            )
            result += f"• Capacidade saudável: {capacidade_saudavel} tarefas\n"
            result += f"• Limite máximo: {capacidade_maxima} tarefas\n\n"

            # Decisão
            if carga_projetada <= capacidade_saudavel:
                result += "✅ **DECISÃO: ACEITAR**\n\n"
                result += "Você tem capacidade confortável para este compromisso.\n"
                return result

            elif carga_projetada <= capacidade_maxima:
                result += "⚠️ **DECISÃO: ACEITAR COM RESSALVAS**\n\n"
                result += "Você pode aceitar, mas:\n"
                result += "• Sua carga ficará acima do ideal\n"
                result += "• Considere negociar prazos mais flexíveis\n"
                result += "• Monitore sinais de estresse\n\n"
                return result

            else:
                result += "🚨 **DECISÃO: NÃO ACEITAR (sem trade-offs)**\n\n"
                result += "⚠️ **SOBRECARGA DETECTADA!**\n\n"
                result += f"Para adicionar '{nome_compromisso}' ({tarefas_estimadas} tarefas), "
                result += "você **PRECISA** fazer trade-offs:\n\n"

                # Buscar opções de trade-off
                result += self._gerar_opcoes_tradeoff(tarefas_estimadas)

                return result

        except Exception as e:
            return f"❌ Erro: {str(e)}"

    def _gerar_opcoes_tradeoff(self, tarefas_necessarias: int) -> str:
        """Gera opções de trade-off baseado nas tarefas atuais."""
        try:
            # Buscar tarefas que podem ser adiadas (sem deadline urgente)
            data_limite_urgente = date.today() + timedelta(weeks=1)
            data_limite_total = date.today() + timedelta(weeks=3)

            tarefas_adiaveis = (
                self.database.query(Task)
                .filter(Task.status == "Pendente")
                .filter(Task.deadline > data_limite_urgente)
                .filter(Task.deadline <= data_limite_total)
                .limit(5)
                .all()
            )

            if not tarefas_adiaveis:
                return "❌ Todas as tarefas são urgentes. Impossível adicionar novo compromisso.\n"

            result = "⚖️ **Opções de Trade-off:**\n\n"
            result += f"Você precisa liberar espaço para **{tarefas_necessarias} tarefas**.\n"
            result += "Considere adiar uma destas:\n\n"

            for i, tarefa in enumerate(tarefas_adiaveis, 1):
                big_rock_nome = tarefa.big_rock.nome if tarefa.big_rock else "Sem Big Rock"
                result += f"{i}. **{tarefa.descricao[:50]}**\n"
                result += f"   📁 {big_rock_nome} | 📅 {tarefa.deadline}\n\n"

            result += "❓ **O que você decide?**\n"
            result += "1. Adiar uma das tarefas acima\n"
            result += "2. Não aceitar o novo compromisso agora\n"
            result += "3. Negociar redução de escopo\n"

            return result

        except Exception as e:
            return f"❌ Erro ao gerar trade-offs: {str(e)}"

    def sugerir_tradeoffs(self, num_tarefas_liberar: int = 5) -> str:
        """
        Sugere tarefas que podem ser adiadas para liberar capacidade.

        Args:
            num_tarefas_liberar: Quantas tarefas precisa liberar
        """
        return self._gerar_opcoes_tradeoff(num_tarefas_liberar)

    def analisar_big_rocks(self) -> str:
        """
        Analisa a distribuição de tarefas entre Big Rocks.
        Identifica se algum pilar está sendo negligenciado.
        """
        try:
            big_rocks = self.database.query(BigRock).filter(BigRock.ativo).all()

            # Contar tarefas por Big Rock (próximas 4 semanas)
            data_limite = date.today() + timedelta(weeks=4)

            result = "📊 **Análise de Big Rocks (4 semanas)**\n\n"

            distribuicao = []

            for br in big_rocks:
                num_tarefas = (
                    self.database.query(Task)
                    .filter(Task.big_rock_id == br.id)
                    .filter(Task.status == "Pendente")
                    .filter(Task.deadline <= data_limite)
                    .count()
                )

                distribuicao.append((br.nome, num_tarefas))

            # Ordenar por número de tarefas
            distribuicao.sort(key=lambda x: x[1], reverse=True)

            total = sum(t[1] for t in distribuicao)

            for nome, num in distribuicao:
                percentual = (num / total * 100) if total > 0 else 0
                barra = "█" * int(percentual / 5)  # Cada █ = 5%

                emoji = "🔥" if num > 15 else "✅" if num > 0 else "⚠️"

                result += f"{emoji} **{nome}**: {num} tarefas ({percentual:.0f}%)\n"
                result += f"   {barra}\n\n"

            # Análise de equilíbrio
            result += "💭 **Análise:**\n"

            # Big Rocks negligenciados (0 tarefas)
            negligenciados = [nome for nome, num in distribuicao if num == 0]
            if negligenciados:
                result += f"\n⚠️ **Pilares negligenciados**: {', '.join(negligenciados)}\n"
                result += "Considere adicionar pelo menos uma tarefa para manter o equilíbrio.\n"

            # Big Rocks sobrecarregados
            sobrecarregados = [nome for nome, num in distribuicao if num > 15]
            if sobrecarregados:
                result += f"\n🚨 **Pilares sobrecarregados**: {', '.join(sobrecarregados)}\n"
                result += "Risco de burnout nestes pilares. Considere redistribuir.\n"

            if not negligenciados and not sobrecarregados:
                result += "\n✅ Distribuição equilibrada entre os Big Rocks!\n"

            return result

        except Exception as e:
            return f"❌ Erro: {str(e)}"


def create_capacity_guard_agent(db: Session) -> CapacityGuardAgent:
    """Factory function to create a CapacityGuardAgent instance."""
    return CapacityGuardAgent(db)
