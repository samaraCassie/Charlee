"""FreelancerAgent - Agente para gerenciamento de projetos freelance."""

from datetime import date, datetime, timedelta
from typing import List, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import FreelanceProject, Invoice, WorkLog


class FreelancerAgent(Agent):
    """
    Agente para gerenciamento de projetos freelance.

    Funções:
    - Gerencia projetos e clientes
    - Faz timetracking de horas trabalhadas
    - Gera invoices baseados em horas
    - Verifica disponibilidade antes de aceitar projetos
    - Sugere aceite/rejeição considerando capacidade e ciclo
    """

    def __init__(self, db: Session):
        """Initialize FreelancerAgent."""
        self.database = db

        super().__init__(
            name="Freelancer Manager",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "Você é o gerente de projetos freelance.",
                "Ajude a organizar projetos, clientes e faturamento.",
                "Faça timetracking preciso de horas trabalhadas.",
                "Gere invoices profissionais.",
                "Proteja contra sobrecarga ao aceitar novos projetos.",
                "Considere o ciclo menstrual ao sugerir timing de projetos.",
            ],
            tools=[
                self.criar_projeto_freelance,
                self.listar_projetos,
                self.registrar_horas_trabalhadas,
                self.calcular_invoice,
                self.verificar_disponibilidade,
                self.sugerir_aceite_projeto,
                self.atualizar_status_projeto,
                self.gerar_relatorio_mensal,
            ],
        )

    def criar_projeto_freelance(
        self,
        user_id: int,
        client_name: str,
        project_name: str,
        hourly_rate: float,
        estimated_hours: float,
        description: Optional[str] = None,
        deadline: Optional[str] = None,
        start_date: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> str:
        """
        Cria um novo projeto freelance.

        Args:
            user_id: ID do usuário
            client_name: Nome do cliente
            project_name: Nome do projeto
            hourly_rate: Taxa por hora (R$)
            estimated_hours: Horas estimadas
            description: Descrição do projeto (opcional)
            deadline: Data de entrega no formato YYYY-MM-DD (opcional)
            start_date: Data de início no formato YYYY-MM-DD (opcional)
            tags: Tags separadas por vírgula (opcional)

        Returns:
            str: Mensagem de confirmação com detalhes do projeto
        """
        try:
            # Parse dates if provided
            deadline_date = None
            if deadline:
                deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()

            start_date_obj = None
            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()

            # Create project
            project = FreelanceProject(
                user_id=user_id,
                client_name=client_name,
                project_name=project_name,
                description=description,
                hourly_rate=hourly_rate,
                estimated_hours=estimated_hours,
                deadline=deadline_date,
                start_date=start_date_obj,
                tags=tags,
                status="proposal",
            )

            self.database.add(project)
            self.database.commit()
            self.database.refresh(project)

            estimated_value = project.calculate_estimated_value()

            result = f"✅ **Projeto Criado com Sucesso!**\n\n"
            result += f"📁 **Projeto**: {project_name}\n"
            result += f"👤 **Cliente**: {client_name}\n"
            result += f"💰 **Taxa/hora**: R$ {hourly_rate:.2f}\n"
            result += f"⏱️ **Horas estimadas**: {estimated_hours}h\n"
            result += f"💵 **Valor estimado**: R$ {estimated_value:.2f}\n"

            if deadline_date:
                result += f"📅 **Deadline**: {deadline_date.strftime('%d/%m/%Y')}\n"

            if start_date_obj:
                result += f"🚀 **Início**: {start_date_obj.strftime('%d/%m/%Y')}\n"

            result += f"\n🆔 **ID do Projeto**: {project.id}\n"
            result += f"📊 **Status**: Proposta\n"

            return result

        except ValueError as e:
            return f"❌ Erro no formato da data: {str(e)}. Use YYYY-MM-DD (ex: 2025-12-31)"
        except Exception as e:
            self.database.rollback()
            return f"❌ Erro ao criar projeto: {str(e)}"

    def listar_projetos(
        self, user_id: int, status: Optional[str] = None, limit: int = 20
    ) -> str:
        """
        Lista projetos freelance com filtros opcionais.

        Args:
            user_id: ID do usuário
            status: Filtrar por status (proposal, active, completed, cancelled)
            limit: Número máximo de projetos a retornar

        Returns:
            str: Lista formatada de projetos
        """
        try:
            query = self.database.query(FreelanceProject).filter(
                FreelanceProject.user_id == user_id
            )

            if status:
                query = query.filter(FreelanceProject.status == status)

            projects = query.order_by(FreelanceProject.created_at.desc()).limit(limit).all()

            if not projects:
                filter_msg = f" com status '{status}'" if status else ""
                return f"📂 Nenhum projeto encontrado{filter_msg}."

            result = f"📋 **Projetos Freelance**"
            if status:
                result += f" (Status: {status})"
            result += f"\n\n"

            total_value = 0
            total_hours = 0

            for project in projects:
                status_emoji = {
                    "proposal": "📝",
                    "active": "🔄",
                    "completed": "✅",
                    "cancelled": "❌",
                }.get(project.status, "❓")

                current_value = project.calculate_total_value()
                estimated_value = project.calculate_estimated_value()

                result += f"{status_emoji} **{project.project_name}**\n"
                result += f"   👤 Cliente: {project.client_name}\n"
                result += f"   ⏱️ Horas: {project.actual_hours:.1f}h / {project.estimated_hours:.1f}h\n"
                result += f"   💰 Valor: R$ {current_value:.2f} / R$ {estimated_value:.2f}\n"

                if project.deadline:
                    days_until = (project.deadline - date.today()).days
                    if days_until < 0:
                        result += f"   ⚠️ Deadline: {project.deadline.strftime('%d/%m/%Y')} (atrasado {abs(days_until)} dias)\n"
                    elif days_until <= 7:
                        result += f"   🔥 Deadline: {project.deadline.strftime('%d/%m/%Y')} ({days_until} dias)\n"
                    else:
                        result += f"   📅 Deadline: {project.deadline.strftime('%d/%m/%Y')}\n"

                result += f"   🆔 ID: {project.id}\n\n"

                if project.status in ["active", "completed"]:
                    total_value += current_value
                    total_hours += project.actual_hours

            result += f"📊 **Resumo**:\n"
            result += f"• Total de projetos: {len(projects)}\n"
            if total_hours > 0:
                result += f"• Horas trabalhadas: {total_hours:.1f}h\n"
                result += f"• Valor total: R$ {total_value:.2f}\n"

            return result

        except Exception as e:
            return f"❌ Erro ao listar projetos: {str(e)}"

    def registrar_horas_trabalhadas(
        self,
        user_id: int,
        project_id: int,
        hours: float,
        description: str,
        work_date: Optional[str] = None,
        task_type: Optional[str] = None,
        billable: bool = True,
    ) -> str:
        """
        Registra horas trabalhadas em um projeto.

        Args:
            user_id: ID do usuário
            project_id: ID do projeto
            hours: Número de horas trabalhadas
            description: Descrição do trabalho realizado
            work_date: Data do trabalho (YYYY-MM-DD, padrão: hoje)
            task_type: Tipo de tarefa (development, design, meeting, etc.)
            billable: Se as horas são cobráveis (padrão: True)

        Returns:
            str: Confirmação com resumo das horas
        """
        try:
            # Verify project exists and belongs to user
            project = (
                self.database.query(FreelanceProject)
                .filter(
                    FreelanceProject.id == project_id, FreelanceProject.user_id == user_id
                )
                .first()
            )

            if not project:
                return f"❌ Projeto {project_id} não encontrado."

            # Parse work date
            if work_date:
                work_date_obj = datetime.strptime(work_date, "%Y-%m-%d").date()
            else:
                work_date_obj = date.today()

            # Create work log
            work_log = WorkLog(
                user_id=user_id,
                project_id=project_id,
                work_date=work_date_obj,
                hours=hours,
                description=description,
                task_type=task_type,
                billable=billable,
            )

            self.database.add(work_log)

            # Update project actual hours
            project.update_actual_hours(self.database)

            self.database.commit()
            self.database.refresh(work_log)
            self.database.refresh(project)

            # Calculate amount
            amount = work_log.calculate_amount()

            result = f"✅ **Horas Registradas!**\n\n"
            result += f"📁 **Projeto**: {project.project_name}\n"
            result += f"👤 **Cliente**: {project.client_name}\n"
            result += f"📅 **Data**: {work_date_obj.strftime('%d/%m/%Y')}\n"
            result += f"⏱️ **Horas**: {hours}h\n"

            if task_type:
                result += f"🏷️ **Tipo**: {task_type}\n"

            result += f"💰 **Valor**: R$ {amount:.2f}\n"
            result += f"💵 **Cobrável**: {'Sim' if billable else 'Não'}\n"
            result += f"\n📝 **Descrição**: {description}\n"

            result += f"\n📊 **Total do Projeto**:\n"
            result += f"• Horas trabalhadas: {project.actual_hours:.1f}h / {project.estimated_hours:.1f}h\n"

            progress_pct = (project.actual_hours / project.estimated_hours * 100) if project.estimated_hours > 0 else 0
            result += f"• Progresso: {progress_pct:.1f}%\n"

            total_value = project.calculate_total_value()
            estimated_value = project.calculate_estimated_value()
            result += f"• Valor acumulado: R$ {total_value:.2f} / R$ {estimated_value:.2f}\n"

            if project.actual_hours > project.estimated_hours:
                result += f"\n⚠️ **Atenção**: Projeto ultrapassou as horas estimadas!\n"

            return result

        except ValueError as e:
            return f"❌ Erro no formato da data: {str(e)}. Use YYYY-MM-DD"
        except Exception as e:
            self.database.rollback()
            return f"❌ Erro ao registrar horas: {str(e)}"

    def calcular_invoice(
        self,
        user_id: int,
        project_id: int,
        invoice_number: Optional[str] = None,
        payment_terms: Optional[str] = "Net 30",
        include_unbilled_only: bool = True,
    ) -> str:
        """
        Gera um invoice para um projeto baseado nas horas trabalhadas.

        Args:
            user_id: ID do usuário
            project_id: ID do projeto
            invoice_number: Número da invoice (gerado automaticamente se não fornecido)
            payment_terms: Termos de pagamento (padrão: Net 30)
            include_unbilled_only: Incluir apenas horas não faturadas (padrão: True)

        Returns:
            str: Detalhes da invoice gerada
        """
        try:
            # Verify project
            project = (
                self.database.query(FreelanceProject)
                .filter(
                    FreelanceProject.id == project_id, FreelanceProject.user_id == user_id
                )
                .first()
            )

            if not project:
                return f"❌ Projeto {project_id} não encontrado."

            # Get work logs
            query = self.database.query(WorkLog).filter(
                WorkLog.project_id == project_id,
                WorkLog.billable == True,  # noqa: E712
            )

            if include_unbilled_only:
                query = query.filter(WorkLog.invoiced == False)  # noqa: E712

            work_logs = query.all()

            if not work_logs:
                return f"❌ Nenhuma hora cobrável encontrada para este projeto."

            # Calculate totals
            total_hours = sum(log.hours for log in work_logs)
            total_amount = sum(log.calculate_amount() for log in work_logs)

            # Generate invoice number if not provided
            if not invoice_number:
                today = date.today()
                count = (
                    self.database.query(Invoice)
                    .filter(Invoice.user_id == user_id)
                    .count()
                )
                invoice_number = f"INV-{today.strftime('%Y%m')}-{count + 1:04d}"

            # Create invoice
            invoice = Invoice(
                user_id=user_id,
                project_id=project_id,
                invoice_number=invoice_number,
                issue_date=date.today(),
                due_date=date.today() + timedelta(days=30),  # Default Net 30
                total_amount=total_amount,
                total_hours=total_hours,
                hourly_rate=project.hourly_rate,
                payment_terms=payment_terms,
                status="draft",
            )

            self.database.add(invoice)
            self.database.commit()
            self.database.refresh(invoice)

            # Mark work logs as invoiced
            for log in work_logs:
                log.invoiced = True
                log.invoice_id = invoice.id

            self.database.commit()

            result = f"📄 **Invoice Gerada!**\n\n"
            result += f"🔢 **Número**: {invoice_number}\n"
            result += f"📅 **Data de emissão**: {invoice.issue_date.strftime('%d/%m/%Y')}\n"
            result += f"📅 **Vencimento**: {invoice.due_date.strftime('%d/%m/%Y')}\n\n"

            result += f"📁 **Projeto**: {project.project_name}\n"
            result += f"👤 **Cliente**: {project.client_name}\n\n"

            result += f"⏱️ **Total de horas**: {total_hours:.1f}h\n"
            result += f"💰 **Taxa/hora**: R$ {project.hourly_rate:.2f}\n"
            result += f"💵 **Valor total**: R$ {total_amount:.2f}\n\n"

            result += f"📋 **Termos de pagamento**: {payment_terms}\n"
            result += f"📊 **Status**: {invoice.status}\n\n"

            result += f"🔖 **Itens incluídos**: {len(work_logs)} registros de trabalho\n"

            return result

        except Exception as e:
            self.database.rollback()
            return f"❌ Erro ao gerar invoice: {str(e)}"

    def verificar_disponibilidade(self, user_id: int, estimated_hours: float) -> str:
        """
        Verifica a disponibilidade atual para aceitar um novo projeto.

        Args:
            user_id: ID do usuário
            estimated_hours: Horas estimadas do novo projeto

        Returns:
            str: Análise de disponibilidade
        """
        try:
            # Count active projects
            active_projects = (
                self.database.query(FreelanceProject)
                .filter(
                    FreelanceProject.user_id == user_id,
                    FreelanceProject.status.in_(["proposal", "active"]),
                )
                .all()
            )

            # Calculate total estimated remaining hours
            total_remaining_hours = 0
            for project in active_projects:
                remaining = max(0, project.estimated_hours - project.actual_hours)
                total_remaining_hours += remaining

            # Assume 20 hours/week capacity (adjust based on user settings)
            weekly_capacity = 20
            weeks_needed_current = total_remaining_hours / weekly_capacity if weekly_capacity > 0 else 0
            weeks_needed_with_new = (total_remaining_hours + estimated_hours) / weekly_capacity if weekly_capacity > 0 else 0

            result = f"📊 **Análise de Disponibilidade**\n\n"
            result += f"🔄 **Projetos ativos**: {len(active_projects)}\n"
            result += f"⏱️ **Horas restantes em projetos ativos**: {total_remaining_hours:.1f}h\n"
            result += f"⏱️ **Novo projeto**: +{estimated_hours:.1f}h\n"
            result += f"⏱️ **Total projetado**: {total_remaining_hours + estimated_hours:.1f}h\n\n"

            result += f"📅 **Tempo necessário**:\n"
            result += f"• Projetos atuais: ~{weeks_needed_current:.1f} semanas\n"
            result += f"• Com novo projeto: ~{weeks_needed_with_new:.1f} semanas\n\n"

            # Decision logic
            if total_remaining_hours + estimated_hours <= weekly_capacity * 2:
                result += "✅ **RECOMENDAÇÃO: ACEITAR**\n\n"
                result += "Você tem boa disponibilidade para este projeto.\n"
            elif total_remaining_hours + estimated_hours <= weekly_capacity * 4:
                result += "⚠️ **RECOMENDAÇÃO: AVALIAR COM CUIDADO**\n\n"
                result += "Você tem disponibilidade, mas:\n"
                result += "• A carga ficará moderada\n"
                result += "• Considere negociar prazos flexíveis\n"
                result += "• Certifique-se de que consegue cumprir os deadlines\n"
            else:
                result += "🚨 **RECOMENDAÇÃO: NÃO ACEITAR (sem ajustes)**\n\n"
                result += "Você está com alta carga de trabalho:\n"
                result += "• Considere finalizar projetos atuais primeiro\n"
                result += "• Ou negocie redução de escopo/prazo estendido\n"
                result += "• Risco de sobrecarga e qualidade comprometida\n"

            # List active projects
            if active_projects:
                result += f"\n📁 **Projetos ativos**:\n"
                for p in active_projects:
                    remaining = max(0, p.estimated_hours - p.actual_hours)
                    result += f"• {p.project_name} ({p.client_name}): {remaining:.1f}h restantes\n"

            return result

        except Exception as e:
            return f"❌ Erro ao verificar disponibilidade: {str(e)}"

    def sugerir_aceite_projeto(
        self,
        user_id: int,
        project_name: str,
        estimated_hours: float,
        deadline_days: Optional[int] = None,
    ) -> str:
        """
        Sugere se deve aceitar um projeto considerando capacidade e ciclo menstrual.

        Args:
            user_id: ID do usuário
            project_name: Nome do projeto
            estimated_hours: Horas estimadas
            deadline_days: Dias até o deadline (opcional)

        Returns:
            str: Análise completa com sugestão
        """
        try:
            result = f"🤔 **Análise de Aceite: '{project_name}'**\n\n"

            # 1. Check capacity
            availability = self.verificar_disponibilidade(user_id, estimated_hours)
            result += availability
            result += "\n" + "=" * 50 + "\n\n"

            # 2. Check cycle (if available)
            try:
                from database.models import MenstrualCycle

                # Get latest cycle entry
                latest_cycle = (
                    self.database.query(MenstrualCycle)
                    .filter(MenstrualCycle.user_id == user_id)
                    .order_by(MenstrualCycle.start_date.desc())
                    .first()
                )

                if latest_cycle:
                    result += f"🌸 **Contexto de Ciclo**:\n"
                    result += f"• Fase atual: {latest_cycle.phase}\n"

                    if latest_cycle.energy_level:
                        result += f"• Energia: {latest_cycle.energy_level}/10\n"
                    if latest_cycle.focus_level:
                        result += f"• Foco: {latest_cycle.focus_level}/10\n"

                    # Phase-specific recommendations
                    if latest_cycle.phase == "menstrual":
                        result += f"\n💭 **Consideração**: Você está na fase menstrual.\n"
                        result += "• Energia pode estar mais baixa\n"
                        result += "• Considere negociar prazos mais flexíveis\n"
                        result += "• Evite projetos muito intensos agora\n"
                    elif latest_cycle.phase == "follicular":
                        result += f"\n💭 **Consideração**: Fase folicular - energia crescente!\n"
                        result += "• Ótima fase para começar novos projetos\n"
                        result += "• Energia e criatividade em alta\n"
                    elif latest_cycle.phase == "ovulation":
                        result += f"\n💭 **Consideração**: Fase de ovulação - pico de energia!\n"
                        result += "• Melhor momento do ciclo\n"
                        result += "• Alta energia, foco e comunicação\n"
                        result += "• Aproveite para projetos desafiadores\n"
                    elif latest_cycle.phase == "luteal":
                        result += f"\n💭 **Consideração**: Fase lútea.\n"
                        result += "• Energia começa a diminuir\n"
                        result += "• Boa para projetos de finalização\n"
                        result += "• Evite deadlines muito apertados\n"

                    result += "\n" + "=" * 50 + "\n\n"
            except ImportError:
                pass  # Cycle tracking not available

            # 3. Final recommendation
            result += f"🎯 **Recomendação Final**:\n\n"

            # Extract decision from availability check
            if "ACEITAR**" in availability and "NÃO" not in availability:
                result += "✅ **SUGESTÃO: ACEITAR o projeto**\n\n"
                result += "Condições favoráveis:\n"
                result += "✓ Boa disponibilidade de tempo\n"
                result += "✓ Carga de trabalho gerenciável\n"
            elif "AVALIAR COM CUIDADO" in availability:
                result += "⚠️ **SUGESTÃO: ACEITAR COM RESSALVAS**\n\n"
                result += "Considere:\n"
                result += "• Negociar prazo mais longo\n"
                result += "• Solicitar adiantamento\n"
                result += "• Deixar claro os limites de disponibilidade\n"
            else:
                result += "🚨 **SUGESTÃO: RECUSAR ou NEGOCIAR**\n\n"
                result += "Recomendações:\n"
                result += "• Termine projetos atuais primeiro\n"
                result += "• Ou negocie escopo reduzido\n"
                result += "• Ou prazo muito mais longo\n"

            if deadline_days and deadline_days < 7:
                result += f"\n⚠️ **Alerta**: Deadline muito curto ({deadline_days} dias)!\n"
                result += "Avalie se é realista entregar com qualidade.\n"

            return result

        except Exception as e:
            return f"❌ Erro ao sugerir aceite: {str(e)}"

    def atualizar_status_projeto(
        self, user_id: int, project_id: int, new_status: str
    ) -> str:
        """
        Atualiza o status de um projeto.

        Args:
            user_id: ID do usuário
            project_id: ID do projeto
            new_status: Novo status (proposal, active, completed, cancelled)

        Returns:
            str: Confirmação da atualização
        """
        try:
            valid_statuses = ["proposal", "active", "completed", "cancelled"]
            if new_status not in valid_statuses:
                return f"❌ Status inválido. Use: {', '.join(valid_statuses)}"

            project = (
                self.database.query(FreelanceProject)
                .filter(
                    FreelanceProject.id == project_id, FreelanceProject.user_id == user_id
                )
                .first()
            )

            if not project:
                return f"❌ Projeto {project_id} não encontrado."

            old_status = project.status
            project.status = new_status

            if new_status == "completed" and not project.completed_date:
                project.completed_date = date.today()

            self.database.commit()
            self.database.refresh(project)

            status_emoji = {
                "proposal": "📝",
                "active": "🔄",
                "completed": "✅",
                "cancelled": "❌",
            }.get(new_status, "❓")

            result = f"✅ **Status Atualizado!**\n\n"
            result += f"📁 **Projeto**: {project.project_name}\n"
            result += f"👤 **Cliente**: {project.client_name}\n"
            result += f"📊 **Status anterior**: {old_status}\n"
            result += f"{status_emoji} **Novo status**: {new_status}\n"

            if new_status == "completed":
                result += f"\n🎉 **Projeto concluído!**\n"
                result += f"• Horas trabalhadas: {project.actual_hours:.1f}h\n"
                result += f"• Valor total: R$ {project.calculate_total_value():.2f}\n"

            return result

        except Exception as e:
            self.database.rollback()
            return f"❌ Erro ao atualizar status: {str(e)}"

    def gerar_relatorio_mensal(self, user_id: int, month: Optional[int] = None, year: Optional[int] = None) -> str:
        """
        Gera relatório mensal de projetos e faturamento.

        Args:
            user_id: ID do usuário
            month: Mês (1-12, padrão: mês atual)
            year: Ano (padrão: ano atual)

        Returns:
            str: Relatório mensal detalhado
        """
        try:
            today = date.today()
            target_month = month or today.month
            target_year = year or today.year

            # Date range for the month
            start_date = date(target_year, target_month, 1)
            if target_month == 12:
                end_date = date(target_year + 1, 1, 1)
            else:
                end_date = date(target_year, target_month + 1, 1)

            # Get work logs for the month
            work_logs = (
                self.database.query(WorkLog)
                .filter(
                    WorkLog.user_id == user_id,
                    WorkLog.work_date >= start_date,
                    WorkLog.work_date < end_date,
                )
                .all()
            )

            # Get invoices issued in the month
            invoices = (
                self.database.query(Invoice)
                .filter(
                    Invoice.user_id == user_id,
                    Invoice.issue_date >= start_date,
                    Invoice.issue_date < end_date,
                )
                .all()
            )

            month_name = start_date.strftime("%B %Y")

            result = f"📊 **Relatório Mensal - {month_name}**\n\n"

            # Work logs summary
            total_hours = sum(log.hours for log in work_logs)
            billable_hours = sum(log.hours for log in work_logs if log.billable)
            total_earned = sum(log.calculate_amount() for log in work_logs if log.billable)

            result += f"⏱️ **Horas Trabalhadas**:\n"
            result += f"• Total: {total_hours:.1f}h\n"
            result += f"• Cobráveis: {billable_hours:.1f}h\n"
            result += f"• Não cobráveis: {total_hours - billable_hours:.1f}h\n\n"

            # Group by project
            project_hours = {}
            for log in work_logs:
                if log.project_id not in project_hours:
                    project_hours[log.project_id] = {"hours": 0, "project": log.project}
                project_hours[log.project_id]["hours"] += log.hours

            if project_hours:
                result += f"📁 **Por Projeto**:\n"
                for proj_data in sorted(
                    project_hours.values(), key=lambda x: x["hours"], reverse=True
                ):
                    project = proj_data["project"]
                    hours = proj_data["hours"]
                    result += f"• {project.project_name} ({project.client_name}): {hours:.1f}h\n"
                result += "\n"

            # Invoices summary
            result += f"💰 **Faturamento**:\n"
            result += f"• Valor ganho: R$ {total_earned:.2f}\n"
            result += f"• Invoices emitidas: {len(invoices)}\n"

            if invoices:
                total_invoiced = sum(inv.total_amount for inv in invoices)
                paid_invoices = [inv for inv in invoices if inv.status == "paid"]
                total_paid = sum(inv.total_amount for inv in paid_invoices)

                result += f"• Total faturado: R$ {total_invoiced:.2f}\n"
                result += f"• Total pago: R$ {total_paid:.2f}\n"
                result += f"• Pendente: R$ {total_invoiced - total_paid:.2f}\n\n"

                result += f"📄 **Invoices**:\n"
                for inv in invoices:
                    status_emoji = {
                        "draft": "📝",
                        "sent": "📤",
                        "paid": "✅",
                        "overdue": "⚠️",
                        "cancelled": "❌",
                    }.get(inv.status, "❓")

                    result += f"{status_emoji} {inv.invoice_number}: R$ {inv.total_amount:.2f} ({inv.status})\n"

            # Stats
            if billable_hours > 0:
                avg_rate = total_earned / billable_hours
                result += f"\n📈 **Estatísticas**:\n"
                result += f"• Taxa média: R$ {avg_rate:.2f}/h\n"

                working_days = 20  # Assume ~20 working days per month
                hours_per_day = billable_hours / working_days
                result += f"• Média diária: {hours_per_day:.1f}h/dia\n"

            return result

        except Exception as e:
            return f"❌ Erro ao gerar relatório: {str(e)}"


def create_freelancer_agent(db: Session) -> FreelancerAgent:
    """Factory function to create a FreelancerAgent instance."""
    return FreelancerAgent(db)
