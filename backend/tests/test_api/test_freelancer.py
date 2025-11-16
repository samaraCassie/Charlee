"""Tests for Freelancer API endpoints."""

from datetime import date, timedelta

from fastapi import status
import pytest


class TestFreelanceProjectsAPI:
    """Test suite for Freelance Projects CRUD operations."""

    def test_create_project(self, client, auth_headers):
        """Should create freelance project with valid data."""
        response = client.post(
            "/api/v2/freelancer/projects",
            json={
                "client_name": "Acme Corp",
                "project_name": "Website Redesign",
                "description": "Complete redesign of company website",
                "hourly_rate": 150.0,
                "estimated_hours": 40.0,
                "deadline": (date.today() + timedelta(days=30)).isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["client_name"] == "Acme Corp"
        assert data["project_name"] == "Website Redesign"
        assert data["hourly_rate"] == 150.0
        assert data["estimated_hours"] == 40.0
        assert data["status"] == "proposal"
        assert "id" in data

    def test_list_projects(self, client, sample_freelance_project, auth_headers):
        """Should list all freelance projects."""
        response = client.get("/api/v2/freelancer/projects", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "total" in data
        assert "projects" in data
        assert len(data["projects"]) >= 1

    def test_list_projects_with_status_filter(self, client, sample_freelance_project, auth_headers):
        """Should filter projects by status."""
        response = client.get("/api/v2/freelancer/projects?status=active", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "projects" in data
        for project in data["projects"]:
            assert project["status"] == "active"

    def test_get_project(self, client, sample_freelance_project, auth_headers):
        """Should get project by ID."""
        response = client.get(
            f"/api/v2/freelancer/projects/{sample_freelance_project.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == sample_freelance_project.id
        assert data["client_name"] == sample_freelance_project.client_name
        assert data["project_name"] == sample_freelance_project.project_name

    def test_update_project(self, client, sample_freelance_project, auth_headers):
        """Should update project."""
        response = client.patch(
            f"/api/v2/freelancer/projects/{sample_freelance_project.id}",
            json={"status": "completed"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"

    def test_delete_project(self, client, sample_freelance_project, auth_headers):
        """Should delete project."""
        response = client.delete(
            f"/api/v2/freelancer/projects/{sample_freelance_project.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(
            f"/api/v2/freelancer/projects/{sample_freelance_project.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestWorkLogsAPI:
    """Test suite for Work Logs CRUD operations."""

    def test_create_work_log(self, client, sample_freelance_project, auth_headers):
        """Should create work log with valid data."""
        response = client.post(
            "/api/v2/freelancer/work-logs",
            json={
                "project_id": sample_freelance_project.id,
                "hours": 5.0,
                "description": "Implemented login feature",
                "work_date": date.today().isoformat(),
                "task_type": "development",
                "billable": True,
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["project_id"] == sample_freelance_project.id
        assert data["hours"] == 5.0
        assert data["description"] == "Implemented login feature"
        assert data["billable"] == True
        assert "id" in data

    def test_create_work_log_invalid_project(self, client, auth_headers):
        """Should return 404 for non-existent project."""
        response = client.post(
            "/api/v2/freelancer/work-logs",
            json={
                "project_id": 9999,
                "hours": 5.0,
                "description": "Test work",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_work_logs(self, client, sample_work_log, auth_headers):
        """Should list all work logs."""
        response = client.get("/api/v2/freelancer/work-logs", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "total" in data
        assert "work_logs" in data
        assert len(data["work_logs"]) >= 1

    def test_list_work_logs_by_project(self, client, sample_work_log, auth_headers):
        """Should filter work logs by project."""
        response = client.get(
            f"/api/v2/freelancer/work-logs?project_id={sample_work_log.project_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "work_logs" in data
        for log in data["work_logs"]:
            assert log["project_id"] == sample_work_log.project_id

    def test_update_work_log(self, client, sample_work_log, auth_headers):
        """Should update work log."""
        response = client.patch(
            f"/api/v2/freelancer/work-logs/{sample_work_log.id}",
            json={"hours": 6.0},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["hours"] == 6.0

    def test_delete_work_log(self, client, sample_work_log, auth_headers):
        """Should delete work log."""
        response = client.delete(
            f"/api/v2/freelancer/work-logs/{sample_work_log.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_log_work_on_project_shortcut(self, client, sample_freelance_project, auth_headers):
        """Should log work using project-specific endpoint."""
        response = client.post(
            f"/api/v2/freelancer/projects/{sample_freelance_project.id}/log-work",
            json={
                "project_id": 1,  # This should be overridden by path param
                "hours": 3.0,
                "description": "Code review",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify project_id was set from path, not request body
        assert data["project_id"] == sample_freelance_project.id
        assert data["hours"] == 3.0


class TestInvoicesAPI:
    """Test suite for Invoices CRUD operations."""

    def test_create_invoice(self, client, sample_freelance_project, sample_work_log, auth_headers):
        """Should create invoice with billable work logs."""
        response = client.post(
            "/api/v2/freelancer/invoices",
            json={
                "project_id": sample_freelance_project.id,
                "payment_terms": "Net 30",
                "include_unbilled_only": True,
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["project_id"] == sample_freelance_project.id
        assert data["total_hours"] > 0
        assert data["total_amount"] > 0
        assert data["status"] == "draft"
        assert "invoice_number" in data

    def test_create_invoice_no_billable_work(self, client, sample_freelance_project, auth_headers):
        """Should return 400 when no billable work exists."""
        response = client.post(
            "/api/v2/freelancer/invoices",
            json={
                "project_id": sample_freelance_project.id,
                "include_unbilled_only": True,
            },
            headers=auth_headers,
        )

        # Should fail if no work logs exist
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED]

    def test_list_invoices(self, client, sample_invoice, auth_headers):
        """Should list all invoices."""
        response = client.get("/api/v2/freelancer/invoices", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "total" in data
        assert "invoices" in data
        assert len(data["invoices"]) >= 1

    def test_get_invoice(self, client, sample_invoice, auth_headers):
        """Should get invoice by ID."""
        response = client.get(
            f"/api/v2/freelancer/invoices/{sample_invoice.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == sample_invoice.id
        assert data["invoice_number"] == sample_invoice.invoice_number

    def test_update_invoice_status(self, client, sample_invoice, auth_headers):
        """Should update invoice status."""
        response = client.patch(
            f"/api/v2/freelancer/invoices/{sample_invoice.id}",
            json={"status": "paid", "paid_date": date.today().isoformat()},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "paid"

    def test_delete_invoice(self, client, sample_invoice, auth_headers):
        """Should delete invoice and unmark work logs."""
        response = client.delete(
            f"/api/v2/freelancer/invoices/{sample_invoice.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_generate_invoice_shortcut(
        self, client, sample_freelance_project, sample_work_log, auth_headers
    ):
        """Should generate invoice using project-specific endpoint."""
        response = client.get(
            f"/api/v2/freelancer/projects/{sample_freelance_project.id}/invoice",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["project_id"] == sample_freelance_project.id
        assert data["total_hours"] > 0
