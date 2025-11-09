"""DailyTrackingAgent - Agente para registro diário e análise de padrões."""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from typing import Optional, Dict, List
from database.models import RegistroDiario, CicloMenstrual, Tarefa, PadroesCiclo
from sqlalchemy import func


class DailyTrackingAgent(Agent):
    """
    Agente especializado em tracking diário e identificação de padrões.

    Funções:
    - Coleta dados diários (sono, energia, produtividade)
    - Identifica padrões de comportamento
    - Correlaciona energia com fase do ciclo
    - Sugere otimizações baseadas em histórico
    - Aprende padrões de produtividade
    """

    def __init__(self, db: Session):
        """Initialize DailyTrackingAgent."""
        self.database = db

        super().__init__(
            name="Daily Tracker",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "Você é especialista em tracking de hábitos e produtividade.",
                "Ajude a usuária a registrar dados diários de forma natural.",
                "Identifique padrões nos dados históricos.",
                "Faça perguntas para coletar dados faltantes.",
                "Seja empática e incentivadora.",
                "Use linguagem natural e brasileira.",
            ],
            tools=[
                self.registrar_dia,
                self.obter_registro_hoje,
                self.analise_ultimos_dias,
                self.identificar_padroes,
                self.sugerir_otimizacoes
            ]
        )

    def registrar_dia(
        self,
        data: Optional[str] = None,
        horas_sono: Optional[float] = None,
        qualidade_sono: Optional[int] = None,
        energia_manha: Optional[int] = None,
        energia_tarde: Optional[int] = None,
        energia_noite: Optional[int] = None,
        horas_deep_work: Optional[float] = None,
        notas: Optional[str] = None
    ) -> str:
        """
        Registra dados do dia (hoje ou data específica).

        Args:
            data: Data no formato YYYY-MM-DD (opcional, padrão: hoje)
            horas_sono: Horas de sono (ex: 7.5)
            qualidade_sono: Qualidade do sono de 1-10
            energia_manha: Energia pela manhã de 1-10
            energia_tarde: Energia à tarde de 1-10
            energia_noite: Energia à noite de 1-10
            horas_deep_work: Horas de trabalho focado
            notas: Observações livres
        """
        try:
            # Parse data
            if data:
                data_obj = datetime.strptime(data, "%Y-%m-%d").date()
            else:
                data_obj = date.today()

            # Verificar se já existe registro
            registro = self.database.query(RegistroDiario).filter(
                RegistroDiario.data == data_obj
            ).first()

            # Contar tarefas completadas do dia
            tarefas_hoje = self.database.query(Tarefa).filter(
                Tarefa.status == "Concluída",
                func.date(Tarefa.concluido_em) == data_obj
            ).count()

            # Obter fase do ciclo
            ciclo_atual = self.database.query(CicloMenstrual).filter(
                CicloMenstrual.data_inicio <= data_obj
            ).order_by(CicloMenstrual.data_inicio.desc()).first()

            fase_ciclo = ciclo_atual.fase if ciclo_atual else None

            if registro:
                # Atualizar registro existente
                if horas_sono is not None:
                    registro.horas_sono = horas_sono
                if qualidade_sono is not None:
                    registro.qualidade_sono = qualidade_sono
                if energia_manha is not None:
                    registro.energia_manha = energia_manha
                if energia_tarde is not None:
                    registro.energia_tarde = energia_tarde
                if energia_noite is not None:
                    registro.energia_noite = energia_noite
                if horas_deep_work is not None:
                    registro.horas_deep_work = horas_deep_work
                if notas:
                    registro.notas_livre = notas

                registro.tarefas_completadas = tarefas_hoje
                registro.fase_ciclo = fase_ciclo

                self.database.commit()
                action = "atualizado"
            else:
                # Criar novo registro
                registro = RegistroDiario(
                    data=data_obj,
                    horas_sono=horas_sono,
                    qualidade_sono=qualidade_sono,
                    energia_manha=energia_manha,
                    energia_tarde=energia_tarde,
                    energia_noite=energia_noite,
                    horas_deep_work=horas_deep_work,
                    tarefas_completadas=tarefas_hoje,
                    fase_ciclo=fase_ciclo,
                    notas_livre=notas
                )
                self.database.add(registro)
                self.database.commit()
                action = "registrado"

            result = f"✅ Registro {action} para {data_obj}!\n\n"
            result += f"📊 **Resumo:**\n"
            if horas_sono:
                result += f"• Sono: {horas_sono}h"
                if qualidade_sono:
                    result += f" (qualidade: {qualidade_sono}/10)"
                result += "\n"
            if energia_manha:
                result += f"• Energia manhã: {energia_manha}/10\n"
            if energia_tarde:
                result += f"• Energia tarde: {energia_tarde}/10\n"
            if energia_noite:
                result += f"• Energia noite: {energia_noite}/10\n"
            if horas_deep_work:
                result += f"• Deep work: {horas_deep_work}h\n"
            result += f"• Tarefas concluídas: {tarefas_hoje}\n"
            if fase_ciclo:
                result += f"• Fase do ciclo: {fase_ciclo}\n"

            return result

        except Exception as e:
            return f"❌ Erro ao registrar: {str(e)}"

    def obter_registro_hoje(self) -> str:
        """
        Obtém o registro de hoje (se existir).
        """
        try:
            hoje = date.today()
            registro = self.database.query(RegistroDiario).filter(
                RegistroDiario.data == hoje
            ).first()

            if not registro:
                return "📅 Ainda não há registro para hoje. Vamos criar um?"

            result = f"📊 **Registro de Hoje ({hoje})**\n\n"

            if registro.horas_sono:
                result += f"💤 **Sono:** {registro.horas_sono}h"
                if registro.qualidade_sono:
                    result += f" (qualidade: {registro.qualidade_sono}/10)"
                result += "\n"

            result += "\n⚡ **Energia:**\n"
            if registro.energia_manha:
                result += f"• Manhã: {registro.energia_manha}/10\n"
            if registro.energia_tarde:
                result += f"• Tarde: {registro.energia_tarde}/10\n"
            if registro.energia_noite:
                result += f"• Noite: {registro.energia_noite}/10\n"

            result += f"\n🎯 **Produtividade:**\n"
            result += f"• Deep work: {registro.horas_deep_work or 0}h\n"
            result += f"• Tarefas concluídas: {registro.tarefas_completadas}\n"

            if registro.fase_ciclo:
                result += f"\n🌸 Fase do ciclo: {registro.fase_ciclo}\n"

            if registro.notas_livre:
                result += f"\n📝 **Notas:**\n{registro.notas_livre}\n"

            return result

        except Exception as e:
            return f"❌ Erro: {str(e)}"

    def analise_ultimos_dias(self, dias: int = 7) -> str:
        """
        Analisa tendências dos últimos N dias.

        Args:
            dias: Número de dias para analisar (padrão: 7)
        """
        try:
            data_inicio = date.today() - timedelta(days=dias)

            registros = self.database.query(RegistroDiario).filter(
                RegistroDiario.data >= data_inicio
            ).order_by(RegistroDiario.data.desc()).all()

            if not registros:
                return f"📅 Sem registros nos últimos {dias} dias."

            # Calcular médias
            total_registros = len(registros)
            soma_sono = sum(r.horas_sono for r in registros if r.horas_sono)
            soma_qualidade_sono = sum(r.qualidade_sono for r in registros if r.qualidade_sono)
            soma_energia_manha = sum(r.energia_manha for r in registros if r.energia_manha)
            soma_deep_work = sum(r.horas_deep_work for r in registros if r.horas_deep_work)
            soma_tarefas = sum(r.tarefas_completadas for r in registros)

            count_sono = sum(1 for r in registros if r.horas_sono)
            count_qual = sum(1 for r in registros if r.qualidade_sono)
            count_energia = sum(1 for r in registros if r.energia_manha)
            count_deep = sum(1 for r in registros if r.horas_deep_work)

            result = f"📊 **Análise dos Últimos {dias} Dias**\n\n"
            result += f"📅 Registros encontrados: {total_registros}\n\n"

            result += "📈 **Médias:**\n"
            if count_sono > 0:
                result += f"• Sono: {soma_sono/count_sono:.1f}h"
                if count_qual > 0:
                    result += f" (qualidade: {soma_qualidade_sono/count_qual:.1f}/10)"
                result += "\n"
            if count_energia > 0:
                result += f"• Energia matinal: {soma_energia_manha/count_energia:.1f}/10\n"
            if count_deep > 0:
                result += f"• Deep work: {soma_deep_work/count_deep:.1f}h/dia\n"
            result += f"• Tarefas concluídas: {soma_tarefas} total ({soma_tarefas/total_registros:.1f}/dia)\n"

            # Identificar melhor e pior dia
            registros_com_energia = [r for r in registros if r.energia_manha]
            if registros_com_energia:
                melhor_dia = max(registros_com_energia, key=lambda r: r.energia_manha)
                pior_dia = min(registros_com_energia, key=lambda r: r.energia_manha)

                result += f"\n🌟 **Melhor dia:** {melhor_dia.data} (energia: {melhor_dia.energia_manha}/10)\n"
                result += f"😴 **Pior dia:** {pior_dia.data} (energia: {pior_dia.energia_manha}/10)\n"

            return result

        except Exception as e:
            return f"❌ Erro: {str(e)}"

    def identificar_padroes(self) -> str:
        """
        Identifica padrões de produtividade baseados em dados históricos.

        Analisa:
        - Correlação entre sono e energia
        - Produtividade por fase do ciclo
        - Dias de melhor performance
        """
        try:
            # Buscar todos os registros com dados suficientes
            registros = self.database.query(RegistroDiario).filter(
                RegistroDiario.horas_sono.isnot(None),
                RegistroDiario.energia_manha.isnot(None)
            ).all()

            if len(registros) < 7:
                return f"📊 Ainda não há dados suficientes para identificar padrões.\nRegistros atuais: {len(registros)}/7 necessários."

            result = "🔍 **Padrões Identificados:**\n\n"

            # 1. Correlação sono vs energia
            media_sono = sum(r.horas_sono for r in registros) / len(registros)
            media_energia = sum(r.energia_manha for r in registros) / len(registros)

            dias_sono_bom = [r for r in registros if r.horas_sono >= media_sono]
            dias_sono_ruim = [r for r in registros if r.horas_sono < media_sono]

            if dias_sono_bom:
                energia_com_sono_bom = sum(r.energia_manha for r in dias_sono_bom) / len(dias_sono_bom)
            else:
                energia_com_sono_bom = 0

            if dias_sono_ruim:
                energia_com_sono_ruim = sum(r.energia_manha for r in dias_sono_ruim) / len(dias_sono_ruim)
            else:
                energia_com_sono_ruim = 0

            result += "💤 **Sono vs Energia:**\n"
            result += f"• Com sono ≥ {media_sono:.1f}h: energia média {energia_com_sono_bom:.1f}/10\n"
            result += f"• Com sono < {media_sono:.1f}h: energia média {energia_com_sono_ruim:.1f}/10\n"

            if energia_com_sono_bom > energia_com_sono_ruim + 1:
                result += f"💡 **Insight:** Dormir ≥{media_sono:.1f}h aumenta significativamente sua energia!\n"

            # 2. Produtividade por fase do ciclo
            fases = {}
            for registro in registros:
                if registro.fase_ciclo and registro.tarefas_completadas:
                    if registro.fase_ciclo not in fases:
                        fases[registro.fase_ciclo] = []
                    fases[registro.fase_ciclo].append(registro.tarefas_completadas)

            if fases:
                result += "\n🌸 **Produtividade por Fase do Ciclo:**\n"
                for fase, tarefas in fases.items():
                    media_tarefas = sum(tarefas) / len(tarefas)
                    result += f"• {fase.capitalize()}: {media_tarefas:.1f} tarefas/dia ({len(tarefas)} dias)\n"

                # Atualizar tabela de padrões
                self._atualizar_padroes_ciclo(fases)

            # 3. Melhor horário
            registros_manha = [r for r in registros if r.energia_manha and r.energia_manha >= 7]
            registros_tarde = [r for r in registros if r.energia_tarde and r.energia_tarde >= 7]

            result += f"\n⏰ **Períodos de Alta Energia:**\n"
            result += f"• Manhã com energia ≥7: {len(registros_manha)} dias\n"
            result += f"• Tarde com energia ≥7: {len(registros_tarde)} dias\n"

            if len(registros_manha) > len(registros_tarde):
                result += "💡 **Insight:** Você é mais produtiva pela manhã!\n"
            elif len(registros_tarde) > len(registros_manha):
                result += "💡 **Insight:** Você é mais produtiva à tarde!\n"

            return result

        except Exception as e:
            return f"❌ Erro: {str(e)}"

    def _atualizar_padroes_ciclo(self, fases_dados: Dict[str, List[int]]):
        """Atualiza tabela de padrões do ciclo com dados coletados."""
        try:
            for fase, tarefas_completadas in fases_dados.items():
                # Calcular métricas
                produtividade_media = sum(tarefas_completadas) / len(tarefas_completadas)
                amostras = len(tarefas_completadas)

                # Buscar ou criar padrão
                padrao = self.database.query(PadroesCiclo).filter(
                    PadroesCiclo.fase == fase
                ).first()

                if padrao:
                    # Atualizar existente (média móvel)
                    total_amostras = padrao.amostras_usadas + amostras
                    padrao.produtividade_media = (
                        (padrao.produtividade_media * padrao.amostras_usadas) +
                        (produtividade_media * amostras)
                    ) / total_amostras
                    padrao.amostras_usadas = total_amostras
                    padrao.confianca_score = min(total_amostras / 30, 1.0)  # Max confiança com 30 amostras
                else:
                    # Criar novo
                    padrao = PadroesCiclo(
                        fase=fase,
                        padrao_identificado=f"Média de {produtividade_media:.1f} tarefas por dia",
                        produtividade_media=produtividade_media,
                        amostras_usadas=amostras,
                        confianca_score=min(amostras / 30, 1.0)
                    )
                    self.database.add(padrao)

            self.database.commit()
        except Exception:
            pass  # Silently fail, this is background update

    def sugerir_otimizacoes(self) -> str:
        """
        Sugere otimizações baseadas nos padrões identificados.
        """
        try:
            # Primeiro identificar padrões
            padroes_text = self.identificar_padroes()

            # Buscar registros recentes
            data_inicio = date.today() - timedelta(days=14)
            registros = self.database.query(RegistroDiario).filter(
                RegistroDiario.data >= data_inicio
            ).all()

            if len(registros) < 7:
                return "📊 Ainda não há dados suficientes para sugestões personalizadas."

            result = "💡 **Sugestões de Otimização:**\n\n"

            # Análise de sono
            registros_sono = [r for r in registros if r.horas_sono]
            if registros_sono:
                media_sono = sum(r.horas_sono for r in registros_sono) / len(registros_sono)

                if media_sono < 7:
                    result += "💤 **Sono:**\n"
                    result += f"• Você está dormindo {media_sono:.1f}h em média (< 7h recomendadas)\n"
                    result += "• Sugestão: Tente ir para cama 30min mais cedo\n"
                    result += "• Benefício: Mais energia e foco no dia seguinte\n\n"

            # Análise de deep work
            registros_deep = [r for r in registros if r.horas_deep_work]
            if registros_deep:
                media_deep = sum(r.horas_deep_work for r in registros_deep) / len(registros_deep)

                if media_deep < 2:
                    result += "🎯 **Trabalho Focado:**\n"
                    result += f"• Média atual: {media_deep:.1f}h/dia de deep work\n"
                    result += "• Sugestão: Bloquear 2h de manhã para trabalho focado\n"
                    result += "• Use técnica Pomodoro (25min foco + 5min pausa)\n\n"

            # Análise de consistência
            dias_com_registro = len(registros)
            dias_periodo = 14

            if dias_com_registro < dias_periodo * 0.7:  # < 70% de consistência
                result += "📊 **Consistência de Registro:**\n"
                result += f"• Você registrou {dias_com_registro} de {dias_periodo} dias ({dias_com_registro/dias_periodo*100:.0f}%)\n"
                result += "• Sugestão: Configure um lembrete diário às 21h\n"
                result += "• Benefício: Dados mais precisos = insights melhores\n\n"

            # Sugestões baseadas em fase do ciclo
            ciclo = self.database.query(CicloMenstrual).filter(
                CicloMenstrual.data_inicio <= date.today()
            ).order_by(CicloMenstrual.data_inicio.desc()).first()

            if ciclo:
                result += f"🌸 **Adaptação ao Ciclo (Fase {ciclo.fase}):**\n"

                if ciclo.fase == "menstrual":
                    result += "• Reduza reuniões e compromissos sociais\n"
                    result += "• Foque em tarefas administrativas leves\n"
                    result += "• Priorize descanso e autocuidado\n"
                elif ciclo.fase == "folicular":
                    result += "• Ótimo momento para projetos criativos!\n"
                    result += "• Planeje novos projetos estratégicos\n"
                    result += "• Aproveite alta energia para tarefas complexas\n"
                elif ciclo.fase == "ovulacao":
                    result += "• Pico de energia - agende reuniões importantes!\n"
                    result += "• Bom momento para negociações\n"
                    result += "• Apresentações e conversas difíceis\n"
                elif ciclo.fase == "lutea":
                    result += "• Foque em concluir projetos em andamento\n"
                    result += "• Evite iniciar projetos grandes e novos\n"
                    result += "• Organize e finalize pendências\n"

            return result

        except Exception as e:
            return f"❌ Erro: {str(e)}"


def create_daily_tracking_agent(db: Session) -> DailyTrackingAgent:
    """Factory function to create a DailyTrackingAgent instance."""
    return DailyTrackingAgent(db)
