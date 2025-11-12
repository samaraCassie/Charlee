"""CycleAwareAgent - Agente especializado em bem-estar e ciclo menstrual."""

from datetime import date, timedelta
from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sqlalchemy.orm import Session

from database.models import CyclePatterns, MenstrualCycle, Task


class CycleAwareAgent(Agent):
    """
    Agente que entende o ciclo menstrual e adapta recomendações.

    Características:
    - Adapta recomendações baseado na fase atual do ciclo
    - Aprende padrões de produtividade por fase
    - Sugere tipos de tarefas ideais para cada fase
    - Alerta sobre planejamento inadequado
    """

    def __init__(self, db: Session):
        """Initialize CycleAwareAgent."""
        self.database = db

        super().__init__(
            name="Wellness Coach",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "Você é especialista em produtividade consciente do ciclo menstrual.",
                "Adapte recomendações baseado na fase atual e padrões históricos.",
                "Priorize bem-estar sobre produtividade quando necessário.",
                "Seja empática e compreensiva.",
                "Use linguagem natural e brasileira.",
            ],
            tools=[
                self.registrar_fase_ciclo,
                self.obter_fase_atual,
                self.sugerir_tarefas_fase,
                self.analisar_carga_para_fase,
            ],
        )

    def registrar_fase_ciclo(
        self,
        data_inicio: str,
        fase: str,
        nivel_energia: Optional[int] = None,
        nivel_foco: Optional[int] = None,
        nivel_criatividade: Optional[int] = None,
        sintomas: Optional[str] = None,
        notas: Optional[str] = None,
    ) -> str:
        """
        Registra uma nova entrada do ciclo menstrual.

        Args:
            data_inicio: Data no formato YYYY-MM-DD
            fase: Fase do ciclo ('menstrual', 'folicular', 'ovulacao', 'lutea')
            nivel_energia: Nível de energia 1-10 (opcional)
            nivel_foco: Nível de foco 1-10 (opcional)
            nivel_criatividade: Nível de criatividade 1-10 (opcional)
            sintomas: Sintomas separados por vírgula (opcional)
            notas: Observações livres (opcional)
        """
        try:
            from datetime import datetime

            data = datetime.strptime(data_inicio, "%Y-%m-%d").date()

            ciclo = MenstrualCycle(
                data_inicio=data,
                fase=fase,
                nivel_energia=nivel_energia,
                nivel_foco=nivel_foco,
                nivel_criatividade=nivel_criatividade,
                sintomas=sintomas,
                notas=notas,
            )

            self.database.add(ciclo)
            self.database.commit()
            self.database.refresh(ciclo)

            return f"✅ Fase '{fase}' registrada para {data_inicio}!"

        except Exception as e:
            return f"❌ Erro ao registrar: {str(e)}"

    def obter_fase_atual(self) -> str:
        """
        Obtém a fase atual do ciclo baseada no último registro.
        """
        try:
            ultimo_registro = (
                self.database.query(MenstrualCycle)
                .filter(MenstrualCycle.data_inicio <= date.today())
                .order_by(MenstrualCycle.data_inicio.desc())
                .first()
            )

            if not ultimo_registro:
                return "📅 Nenhuma fase registrada ainda. Registre sua primeira fase!"

            dias_desde = (date.today() - ultimo_registro.data_inicio).days

            result = f"🌸 **Fase Atual: {ultimo_registro.fase.capitalize()}**\n\n"
            result += f"📅 Desde: {ultimo_registro.data_inicio} ({dias_desde} dias atrás)\n"

            if ultimo_registro.nivel_energia:
                result += f"⚡ Energia: {ultimo_registro.nivel_energia}/10\n"
            if ultimo_registro.nivel_foco:
                result += f"🎯 Foco: {ultimo_registro.nivel_foco}/10\n"
            if ultimo_registro.nivel_criatividade:
                result += f"💡 Criatividade: {ultimo_registro.nivel_criatividade}/10\n"

            if ultimo_registro.sintomas:
                result += f"\n🩺 Sintomas: {ultimo_registro.sintomas}\n"

            # Buscar padrões conhecidos para essa fase
            padroes = (
                self.database.query(CyclePatterns)
                .filter(CyclePatterns.fase == ultimo_registro.fase)
                .filter(CyclePatterns.confianca_score > 0.5)
                .first()
            )

            if padroes:
                result += "\n💭 **Padrões Conhecidos:**\n"
                result += f"• Produtividade média: {padroes.produtividade_media:.1f}x\n"
                result += f"• Energia média: {padroes.energia_media:.1f}x\n"

                if padroes.sugestoes:
                    result += "\n💡 **Sugestões:**\n"
                    for sug in padroes.sugestoes.split(";"):
                        result += f"• {sug.strip()}\n"

            return result

        except Exception as e:
            return f"❌ Erro: {str(e)}"

    def sugerir_tarefas_fase(self, fase: Optional[str] = None) -> str:
        """
        Sugere tipos de tarefas ideais para uma fase do ciclo.

        Args:
            fase: Fase específica (opcional, usa a atual se não informado)
        """
        # Configurações por fase
        fase_config = {
            "menstrual": {
                "energia": "🔋 Baixa (60%)",
                "tipos_ideais": [
                    "Tarefas administrativas leves",
                    "Reflexão e planejamento",
                    "Organização de arquivos",
                    "Revisão de documentos",
                ],
                "evitar": [
                    "Reuniões longas e intensas",
                    "Decisões estratégicas grandes",
                    "Apresentações importantes",
                ],
                "mensagem": "Fase de baixa energia. Priorize descanso e tarefas leves.",
            },
            "folicular": {
                "energia": "⚡ Alta (120%)",
                "tipos_ideais": [
                    "Trabalho criativo e estratégico",
                    "Planejamento de projetos novos",
                    "Networking e relacionamentos",
                    "Aprendizado de coisas novas",
                ],
                "evitar": [],
                "mensagem": "Fase de alta criatividade! Aproveite para tarefas estratégicas.",
            },
            "ovulacao": {
                "energia": "🚀 Máxima (140%)",
                "tipos_ideais": [
                    "Apresentações e reuniões importantes",
                    "Negociações críticas",
                    "Conversas difíceis",
                    "Tarefas que exigem comunicação",
                ],
                "evitar": [],
                "mensagem": "Pico de energia e comunicação! Agende as reuniões mais importantes.",
            },
            "lutea": {
                "energia": "🔋 Moderada (80%)",
                "tipos_ideais": [
                    "Execução e finalização",
                    "Organização e conclusão",
                    "Revisão de pendências",
                    "Tarefas detalhistas",
                ],
                "evitar": ["Iniciar projetos grandes e novos"],
                "mensagem": "Fase de finalização. Foque em concluir o que já está em andamento.",
            },
        }

        # Se não passou fase, usa a atual
        if not fase:
            ultimo_registro = (
                self.database.query(MenstrualCycle)
                .filter(MenstrualCycle.data_inicio <= date.today())
                .order_by(MenstrualCycle.data_inicio.desc())
                .first()
            )

            if not ultimo_registro:
                return "📅 Registre sua fase atual primeiro para receber sugestões personalizadas!"

            fase = ultimo_registro.fase

        if fase not in fase_config:
            return f"❌ Fase '{fase}' não reconhecida. Use: menstrual, folicular, ovulacao ou lutea"

        config = fase_config[fase]

        result = f"🌸 **Sugestões para Fase {fase.capitalize()}**\n\n"
        result += f"{config['energia']}\n\n"
        result += f"💭 {config['mensagem']}\n\n"

        result += "✅ **Tipos de tarefas ideais:**\n"
        for tipo in config["tipos_ideais"]:
            result += f"• {tipo}\n"

        if config["evitar"]:
            result += "\n⚠️ **Evitar:**\n"
            for evitar in config["evitar"]:
                result += f"• {evitar}\n"

        return result

    def analisar_carga_para_fase(self, dias_futuro: int = 7) -> str:
        """
        Analisa se a carga de trabalho está adequada para a fase atual.

        Args:
            dias_futuro: Quantos dias analisar à frente (padrão: 7)
        """
        try:
            # Obter fase atual
            ultimo_registro = (
                self.database.query(MenstrualCycle)
                .filter(MenstrualCycle.data_inicio <= date.today())
                .order_by(MenstrualCycle.data_inicio.desc())
                .first()
            )

            if not ultimo_registro:
                return "📅 Registre sua fase atual primeiro!"

            fase_atual = ultimo_registro.fase

            # Contar tarefas pendentes nos próximos X dias
            data_limite = date.today() + timedelta(days=dias_futuro)

            tarefas_proximas = (
                self.database.query(Task)
                .filter(Task.status == "Pendente")
                .filter(Task.deadline.isnot(None))
                .filter(Task.deadline <= data_limite)
                .all()
            )

            num_tarefas = len(tarefas_proximas)

            # Energia esperada para a fase
            energia_fase = {"menstrual": 0.6, "folicular": 1.2, "ovulacao": 1.4, "lutea": 0.8}.get(
                fase_atual, 1.0
            )

            # Análise
            result = f"📊 **Análise de Carga - Próximos {dias_futuro} dias**\n\n"
            result += f"🌸 Fase atual: **{fase_atual.capitalize()}**\n"
            result += f"⚡ Energia esperada: **{int(energia_fase * 100)}%**\n"
            result += f"📋 Tarefas pendentes: **{num_tarefas}**\n\n"

            # Capacidade ajustada
            capacidade_base = 5  # 5 tarefas por semana é uma base razoável
            capacidade_ajustada = capacidade_base * energia_fase

            if num_tarefas > capacidade_ajustada * 1.2:
                result += "🚨 **ALERTA: Sobrecarga detectada!**\n\n"
                result += f"Com sua energia de {int(energia_fase * 100)}% nesta fase, "
                result += (
                    f"você idealmente deveria ter no máximo {int(capacidade_ajustada)} tarefas.\n\n"
                )
                result += "💡 **Recomendação:**\n"
                result += "• Considere adiar algumas tarefas menos urgentes\n"
                result += "• Negocie prazos se possível\n"
                result += "• Foque no essencial durante esta fase\n"
            elif num_tarefas < capacidade_ajustada * 0.5:
                result += "😊 **Ótimo! Carga equilibrada.**\n\n"
                result += "Você está com uma carga leve para esta fase. "
                result += "Bom momento para respirar ou pegar tarefas estratégicas!\n"
            else:
                result += "✅ **Carga adequada para sua fase atual.**\n\n"
                result += "A quantidade de tarefas está compatível com sua energia esperada.\n"

            return result

        except Exception as e:
            return f"❌ Erro: {str(e)}"


def create_cycle_aware_agent(db: Session) -> CycleAwareAgent:
    """Factory function to create a CycleAwareAgent instance."""
    return CycleAwareAgent(db)
