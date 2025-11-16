"""FreelancerAgent - Agent for freelance project management."""

from datetime import date, datetime, timedelta
from typing import List, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import FreelanceProject, Invoice, WorkLog


class FreelancerAgent(Agent):
    """
    Agent for freelance project management.

    Functions:
    - Manage projects and clients
    - Track time worked on projects
    - Generate invoices based on hours
    - Check availability before accepting projects
    - Suggest project acceptance considering capacity and cycle
    """

    def __init__(self, db: Session):
        """Initialize FreelancerAgent."""
        self.database = db

        super().__init__(
            name="Freelancer Manager",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "You are the freelance project manager.",
                "Help organize projects, clients, and billing.",
                "Track time worked accurately.",
                "Generate professional invoices.",
                "Protect against overload when accepting new projects.",
                "Consider menstrual cycle when suggesting project timing.",
            ],
            tools=[
                self.create_freelance_project,
                self.list_projects,
                self.log_work_hours,
                self.calculate_invoice,
                self.check_availability,
                self.suggest_project_acceptance,
                self.update_project_status,
                self.generate_monthly_report,
            ],
        )

    def create_freelance_project(
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
        Create a new freelance project.

        Args:
            user_id: User ID
            client_name: Client name
            project_name: Project name
            hourly_rate: Hourly rate (R$)
            estimated_hours: Estimated hours
            description: Project description (optional)
            deadline: Deadline in YYYY-MM-DD format (optional)
            start_date: Start date in YYYY-MM-DD format (optional)
            tags: Comma-separated tags (optional)

        Returns:
            str: Confirmation message with project details
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

            result = f"✅ **Project Created Successfully!**\n\n"
            result += f"📁 **Project**: {project_name}\n"
            result += f"👤 **Client**: {client_name}\n"
            result += f"💰 **Hourly Rate**: R$ {hourly_rate:.2f}\n"
            result += f"⏱️ **Estimated Hours**: {estimated_hours}h\n"
            result += f"💵 **Estimated Value**: R$ {estimated_value:.2f}\n"

            if deadline_date:
                result += f"📅 **Deadline**: {deadline_date.strftime('%d/%m/%Y')}\n"

            if start_date_obj:
                result += f"🚀 **Start Date**: {start_date_obj.strftime('%d/%m/%Y')}\n"

            result += f"\n🆔 **Project ID**: {project.id}\n"
            result += f"📊 **Status**: Proposal\n"

            return result

        except ValueError as e:
            return f"❌ Date format error: {str(e)}. Use YYYY-MM-DD (e.g., 2025-12-31)"
        except Exception as e:
            self.database.rollback()
            return f"❌ Error creating project: {str(e)}"

    def list_projects(self, user_id: int, status: Optional[str] = None, limit: int = 20) -> str:
        """
        List freelance projects with optional filters.

        Args:
            user_id: User ID
            status: Filter by status (proposal, active, completed, cancelled)
            limit: Maximum number of projects to return

        Returns:
            str: Formatted list of projects
        """
        try:
            query = self.database.query(FreelanceProject).filter(
                FreelanceProject.user_id == user_id
            )

            if status:
                query = query.filter(FreelanceProject.status == status)

            projects = query.order_by(FreelanceProject.created_at.desc()).limit(limit).all()

            if not projects:
                filter_msg = f" with status '{status}'" if status else ""
                return f"📂 No projects found{filter_msg}."

            result = f"📋 **Freelance Projects**"
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
                result += f"   👤 Client: {project.client_name}\n"
                result += (
                    f"   ⏱️ Hours: {project.actual_hours:.1f}h / {project.estimated_hours:.1f}h\n"
                )
                result += f"   💰 Value: R$ {current_value:.2f} / R$ {estimated_value:.2f}\n"

                if project.deadline:
                    days_until = (project.deadline - date.today()).days
                    if days_until < 0:
                        result += f"   ⚠️ Deadline: {project.deadline.strftime('%d/%m/%Y')} (overdue {abs(days_until)} days)\n"
                    elif days_until <= 7:
                        result += f"   🔥 Deadline: {project.deadline.strftime('%d/%m/%Y')} ({days_until} days)\n"
                    else:
                        result += f"   📅 Deadline: {project.deadline.strftime('%d/%m/%Y')}\n"

                result += f"   🆔 ID: {project.id}\n\n"

                if project.status in ["active", "completed"]:
                    total_value += current_value
                    total_hours += project.actual_hours

            result += f"📊 **Summary**:\n"
            result += f"• Total projects: {len(projects)}\n"
            if total_hours > 0:
                result += f"• Hours worked: {total_hours:.1f}h\n"
                result += f"• Total value: R$ {total_value:.2f}\n"

            return result

        except Exception as e:
            return f"❌ Error listing projects: {str(e)}"

    def log_work_hours(
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
        Log hours worked on a project.

        Args:
            user_id: User ID
            project_id: Project ID
            hours: Number of hours worked
            description: Description of work performed
            work_date: Work date (YYYY-MM-DD, default: today)
            task_type: Type of task (development, design, meeting, etc.)
            billable: Whether hours are billable (default: True)

        Returns:
            str: Confirmation with work summary
        """
        try:
            # Verify project exists and belongs to user
            project = (
                self.database.query(FreelanceProject)
                .filter(FreelanceProject.id == project_id, FreelanceProject.user_id == user_id)
                .first()
            )

            if not project:
                return f"❌ Project {project_id} not found."

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

            result = f"✅ **Hours Logged!**\n\n"
            result += f"📁 **Project**: {project.project_name}\n"
            result += f"👤 **Client**: {project.client_name}\n"
            result += f"📅 **Date**: {work_date_obj.strftime('%d/%m/%Y')}\n"
            result += f"⏱️ **Hours**: {hours}h\n"

            if task_type:
                result += f"🏷️ **Type**: {task_type}\n"

            result += f"💰 **Value**: R$ {amount:.2f}\n"
            result += f"💵 **Billable**: {'Yes' if billable else 'No'}\n"
            result += f"\n📝 **Description**: {description}\n"

            result += f"\n📊 **Project Total**:\n"
            result += (
                f"• Hours worked: {project.actual_hours:.1f}h / {project.estimated_hours:.1f}h\n"
            )

            progress_pct = (
                (project.actual_hours / project.estimated_hours * 100)
                if project.estimated_hours > 0
                else 0
            )
            result += f"• Progress: {progress_pct:.1f}%\n"

            total_value = project.calculate_total_value()
            estimated_value = project.calculate_estimated_value()
            result += f"• Accumulated value: R$ {total_value:.2f} / R$ {estimated_value:.2f}\n"

            if project.actual_hours > project.estimated_hours:
                result += f"\n⚠️ **Warning**: Project exceeded estimated hours!\n"

            return result

        except ValueError as e:
            return f"❌ Date format error: {str(e)}. Use YYYY-MM-DD"
        except Exception as e:
            self.database.rollback()
            return f"❌ Error logging hours: {str(e)}"

    def calculate_invoice(
        self,
        user_id: int,
        project_id: int,
        invoice_number: Optional[str] = None,
        payment_terms: Optional[str] = "Net 30",
        include_unbilled_only: bool = True,
    ) -> str:
        """
        Generate an invoice for a project based on hours worked.

        Args:
            user_id: User ID
            project_id: Project ID
            invoice_number: Invoice number (auto-generated if not provided)
            payment_terms: Payment terms (default: Net 30)
            include_unbilled_only: Include only unbilled hours (default: True)

        Returns:
            str: Invoice details
        """
        try:
            # Verify project
            project = (
                self.database.query(FreelanceProject)
                .filter(FreelanceProject.id == project_id, FreelanceProject.user_id == user_id)
                .first()
            )

            if not project:
                return f"❌ Project {project_id} not found."

            # Get work logs
            query = self.database.query(WorkLog).filter(
                WorkLog.project_id == project_id,
                WorkLog.billable == True,  # noqa: E712
            )

            if include_unbilled_only:
                query = query.filter(WorkLog.invoiced == False)  # noqa: E712

            work_logs = query.all()

            if not work_logs:
                return f"❌ No billable hours found for this project."

            # Calculate totals
            total_hours = sum(log.hours for log in work_logs)
            total_amount = sum(log.calculate_amount() for log in work_logs)

            # Generate invoice number if not provided
            if not invoice_number:
                today = date.today()
                count = self.database.query(Invoice).filter(Invoice.user_id == user_id).count()
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

            result = f"📄 **Invoice Generated!**\n\n"
            result += f"🔢 **Number**: {invoice_number}\n"
            result += f"📅 **Issue Date**: {invoice.issue_date.strftime('%d/%m/%Y')}\n"
            result += f"📅 **Due Date**: {invoice.due_date.strftime('%d/%m/%Y')}\n\n"

            result += f"📁 **Project**: {project.project_name}\n"
            result += f"👤 **Client**: {project.client_name}\n\n"

            result += f"⏱️ **Total Hours**: {total_hours:.1f}h\n"
            result += f"💰 **Hourly Rate**: R$ {project.hourly_rate:.2f}\n"
            result += f"💵 **Total Amount**: R$ {total_amount:.2f}\n\n"

            result += f"📋 **Payment Terms**: {payment_terms}\n"
            result += f"📊 **Status**: {invoice.status}\n\n"

            result += f"🔖 **Items Included**: {len(work_logs)} work records\n"

            return result

        except Exception as e:
            self.database.rollback()
            return f"❌ Error generating invoice: {str(e)}"

    def check_availability(self, user_id: int, estimated_hours: float) -> str:
        """
        Check current availability to accept a new project.

        Args:
            user_id: User ID
            estimated_hours: Estimated hours for new project

        Returns:
            str: Availability analysis
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
            weeks_needed_current = (
                total_remaining_hours / weekly_capacity if weekly_capacity > 0 else 0
            )
            weeks_needed_with_new = (
                (total_remaining_hours + estimated_hours) / weekly_capacity
                if weekly_capacity > 0
                else 0
            )

            result = f"📊 **Availability Analysis**\n\n"
            result += f"🔄 **Active Projects**: {len(active_projects)}\n"
            result += f"⏱️ **Remaining Hours in Active Projects**: {total_remaining_hours:.1f}h\n"
            result += f"⏱️ **New Project**: +{estimated_hours:.1f}h\n"
            result += f"⏱️ **Projected Total**: {total_remaining_hours + estimated_hours:.1f}h\n\n"

            result += f"📅 **Time Required**:\n"
            result += f"• Current projects: ~{weeks_needed_current:.1f} weeks\n"
            result += f"• With new project: ~{weeks_needed_with_new:.1f} weeks\n\n"

            # Decision logic
            if total_remaining_hours + estimated_hours <= weekly_capacity * 2:
                result += "✅ **RECOMMENDATION: ACCEPT**\n\n"
                result += "You have good availability for this project.\n"
            elif total_remaining_hours + estimated_hours <= weekly_capacity * 4:
                result += "⚠️ **RECOMMENDATION: EVALUATE CAREFULLY**\n\n"
                result += "You have availability, but:\n"
                result += "• Workload will be moderate\n"
                result += "• Consider negotiating flexible deadlines\n"
                result += "• Make sure you can meet deadlines\n"
            else:
                result += "🚨 **RECOMMENDATION: DO NOT ACCEPT (without adjustments)**\n\n"
                result += "You have high workload:\n"
                result += "• Consider finishing current projects first\n"
                result += "• Or negotiate reduced scope/extended deadline\n"
                result += "• Risk of overload and compromised quality\n"

            # List active projects
            if active_projects:
                result += f"\n📁 **Active Projects**:\n"
                for p in active_projects:
                    remaining = max(0, p.estimated_hours - p.actual_hours)
                    result += f"• {p.project_name} ({p.client_name}): {remaining:.1f}h remaining\n"

            return result

        except Exception as e:
            return f"❌ Error checking availability: {str(e)}"

    def suggest_project_acceptance(
        self,
        user_id: int,
        project_name: str,
        estimated_hours: float,
        deadline_days: Optional[int] = None,
    ) -> str:
        """
        Suggest whether to accept a project considering capacity and menstrual cycle.

        Args:
            user_id: User ID
            project_name: Project name
            estimated_hours: Estimated hours
            deadline_days: Days until deadline (optional)

        Returns:
            str: Complete analysis with suggestion
        """
        try:
            result = f"🤔 **Acceptance Analysis: '{project_name}'**\n\n"

            # 1. Check capacity
            availability = self.check_availability(user_id, estimated_hours)
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
                    result += f"🌸 **Cycle Context**:\n"
                    result += f"• Current phase: {latest_cycle.phase}\n"

                    if latest_cycle.energy_level:
                        result += f"• Energy: {latest_cycle.energy_level}/10\n"
                    if latest_cycle.focus_level:
                        result += f"• Focus: {latest_cycle.focus_level}/10\n"

                    # Phase-specific recommendations
                    if latest_cycle.phase == "menstrual":
                        result += f"\n💭 **Consideration**: You are in menstrual phase.\n"
                        result += "• Energy may be lower\n"
                        result += "• Consider negotiating more flexible deadlines\n"
                        result += "• Avoid very intense projects now\n"
                    elif latest_cycle.phase == "follicular":
                        result += f"\n💭 **Consideration**: Follicular phase - rising energy!\n"
                        result += "• Great phase to start new projects\n"
                        result += "• Energy and creativity rising\n"
                    elif latest_cycle.phase == "ovulation":
                        result += f"\n💭 **Consideration**: Ovulation phase - peak energy!\n"
                        result += "• Best time of cycle\n"
                        result += "• High energy, focus, and communication\n"
                        result += "• Take advantage for challenging projects\n"
                    elif latest_cycle.phase == "luteal":
                        result += f"\n💭 **Consideration**: Luteal phase.\n"
                        result += "• Energy starts to decrease\n"
                        result += "• Good for completion projects\n"
                        result += "• Avoid very tight deadlines\n"

                    result += "\n" + "=" * 50 + "\n\n"
            except ImportError:
                pass  # Cycle tracking not available

            # 3. Final recommendation
            result += f"🎯 **Final Recommendation**:\n\n"

            # Extract decision from availability check
            if "ACCEPT**" in availability and "NOT" not in availability:
                result += "✅ **SUGGESTION: ACCEPT the project**\n\n"
                result += "Favorable conditions:\n"
                result += "✓ Good time availability\n"
                result += "✓ Manageable workload\n"
            elif "EVALUATE CAREFULLY" in availability:
                result += "⚠️ **SUGGESTION: ACCEPT WITH CAVEATS**\n\n"
                result += "Consider:\n"
                result += "• Negotiate longer deadline\n"
                result += "• Request advance payment\n"
                result += "• Make availability limits clear\n"
            else:
                result += "🚨 **SUGGESTION: DECLINE or NEGOTIATE**\n\n"
                result += "Recommendations:\n"
                result += "• Finish current projects first\n"
                result += "• Or negotiate reduced scope\n"
                result += "• Or much longer deadline\n"

            if deadline_days and deadline_days < 7:
                result += f"\n⚠️ **Alert**: Very short deadline ({deadline_days} days)!\n"
                result += "Evaluate if realistic to deliver with quality.\n"

            return result

        except Exception as e:
            return f"❌ Error suggesting acceptance: {str(e)}"

    def update_project_status(self, user_id: int, project_id: int, new_status: str) -> str:
        """
        Update project status.

        Args:
            user_id: User ID
            project_id: Project ID
            new_status: New status (proposal, active, completed, cancelled)

        Returns:
            str: Confirmation of update
        """
        try:
            valid_statuses = ["proposal", "active", "completed", "cancelled"]
            if new_status not in valid_statuses:
                return f"❌ Invalid status. Use: {', '.join(valid_statuses)}"

            project = (
                self.database.query(FreelanceProject)
                .filter(FreelanceProject.id == project_id, FreelanceProject.user_id == user_id)
                .first()
            )

            if not project:
                return f"❌ Project {project_id} not found."

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

            result = f"✅ **Status Updated!**\n\n"
            result += f"📁 **Project**: {project.project_name}\n"
            result += f"👤 **Client**: {project.client_name}\n"
            result += f"📊 **Previous Status**: {old_status}\n"
            result += f"{status_emoji} **New Status**: {new_status}\n"

            if new_status == "completed":
                result += f"\n🎉 **Project Completed!**\n"
                result += f"• Hours worked: {project.actual_hours:.1f}h\n"
                result += f"• Total value: R$ {project.calculate_total_value():.2f}\n"

            return result

        except Exception as e:
            self.database.rollback()
            return f"❌ Error updating status: {str(e)}"

    def generate_monthly_report(
        self, user_id: int, month: Optional[int] = None, year: Optional[int] = None
    ) -> str:
        """
        Generate monthly report of projects and revenue.

        Args:
            user_id: User ID
            month: Month (1-12, default: current month)
            year: Year (default: current year)

        Returns:
            str: Detailed monthly report
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

            result = f"📊 **Monthly Report - {month_name}**\n\n"

            # Work logs summary
            total_hours = sum(log.hours for log in work_logs)
            billable_hours = sum(log.hours for log in work_logs if log.billable)
            total_earned = sum(log.calculate_amount() for log in work_logs if log.billable)

            result += f"⏱️ **Hours Worked**:\n"
            result += f"• Total: {total_hours:.1f}h\n"
            result += f"• Billable: {billable_hours:.1f}h\n"
            result += f"• Non-billable: {total_hours - billable_hours:.1f}h\n\n"

            # Group by project
            project_hours = {}
            for log in work_logs:
                if log.project_id not in project_hours:
                    project_hours[log.project_id] = {"hours": 0, "project": log.project}
                project_hours[log.project_id]["hours"] += log.hours

            if project_hours:
                result += f"📁 **By Project**:\n"
                for proj_data in sorted(
                    project_hours.values(), key=lambda x: x["hours"], reverse=True
                ):
                    project = proj_data["project"]
                    hours = proj_data["hours"]
                    result += f"• {project.project_name} ({project.client_name}): {hours:.1f}h\n"
                result += "\n"

            # Invoices summary
            result += f"💰 **Revenue**:\n"
            result += f"• Value earned: R$ {total_earned:.2f}\n"
            result += f"• Invoices issued: {len(invoices)}\n"

            if invoices:
                total_invoiced = sum(inv.total_amount for inv in invoices)
                paid_invoices = [inv for inv in invoices if inv.status == "paid"]
                total_paid = sum(inv.total_amount for inv in paid_invoices)

                result += f"• Total invoiced: R$ {total_invoiced:.2f}\n"
                result += f"• Total paid: R$ {total_paid:.2f}\n"
                result += f"• Pending: R$ {total_invoiced - total_paid:.2f}\n\n"

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
                result += f"\n📈 **Statistics**:\n"
                result += f"• Average rate: R$ {avg_rate:.2f}/h\n"

                working_days = 20  # Assume ~20 working days per month
                hours_per_day = billable_hours / working_days
                result += f"• Daily average: {hours_per_day:.1f}h/day\n"

            return result

        except Exception as e:
            return f"❌ Error generating report: {str(e)}"


def create_freelancer_agent(db: Session) -> FreelancerAgent:
    """Factory function to create a FreelancerAgent instance."""
    return FreelancerAgent(db)
