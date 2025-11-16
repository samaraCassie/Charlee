"""Tests for Projects Intelligence System MVP 3 - Career Insights & Portfolio API endpoints."""

from fastapi import status


class TestCareerInsightsAPI:
    """Test suite for Career Insights endpoints."""

    def test_get_career_summary(self, client, sample_project_execution, auth_headers):
        """Should return career summary with completed projects."""
        response = client.get(
            "/api/v2/projects/insights/career-summary?days=90",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "details" in data
        assert "Career Summary" in data["details"]

    def test_get_career_summary_custom_days(self, client, auth_headers):
        """Should accept custom days parameter."""
        response = client.get(
            "/api/v2/projects/insights/career-summary?days=30",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "30 days" in data["details"]

    def test_analyze_skills_progression(self, client, sample_project_execution, auth_headers):
        """Should return skills progression analysis."""
        response = client.get(
            "/api/v2/projects/insights/skills-progression",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "details" in data

    def test_analyze_skills_progression_specific_skill(self, client, auth_headers):
        """Should filter by specific skill."""
        response = client.get(
            "/api/v2/projects/insights/skills-progression?skill_name=Python",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "details" in data

    def test_identify_top_performing_projects(self, client, sample_project_execution, auth_headers):
        """Should return top performing projects."""
        response = client.get(
            "/api/v2/projects/insights/top-performing-projects?limit=5",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "details" in data

    def test_get_income_trends(self, client, sample_project_execution, auth_headers):
        """Should return income trends analysis."""
        response = client.get(
            "/api/v2/projects/insights/income-trends?months=6",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "details" in data
        assert "Income Trends" in data["details"]

    def test_generate_career_recommendations(self, client, auth_headers):
        """Should generate career recommendations."""
        response = client.get(
            "/api/v2/projects/insights/career-recommendations",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "details" in data
        assert "Career Recommendations" in data["details"]

    def test_career_insights_without_auth(self, client):
        """Should return 403 without authentication."""
        response = client.get("/api/v2/projects/insights/career-summary")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestPortfolioBuilderAPI:
    """Test suite for Portfolio Builder endpoints."""

    def test_build_full_portfolio(self, client, sample_project_execution, auth_headers):
        """Should build full portfolio from completed projects."""
        response = client.get(
            "/api/v2/projects/portfolio/full",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "details" in data
        assert "PORTFOLIO" in data["details"]

    def test_build_full_portfolio_with_in_progress(self, client, auth_headers):
        """Should include in-progress projects when requested."""
        response = client.get(
            "/api/v2/projects/portfolio/full?include_in_progress=true",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "details" in data

    def test_generate_project_description(self, client, sample_project_execution, auth_headers):
        """Should generate professional project description."""
        response = client.get(
            f"/api/v2/projects/portfolio/projects/{sample_project_execution.id}/description",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "details" in data

    def test_generate_project_description_not_found(self, client, auth_headers):
        """Should return error for non-existent project."""
        response = client.get(
            "/api/v2/projects/portfolio/projects/9999/description",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "not found" in data["details"].lower()

    def test_categorize_projects(self, client, sample_project_execution, auth_headers):
        """Should categorize projects by skill."""
        response = client.get(
            "/api/v2/projects/portfolio/categorized",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "details" in data

    def test_get_portfolio_by_skill(self, client, sample_project_execution, auth_headers):
        """Should filter portfolio by specific skill."""
        response = client.get(
            "/api/v2/projects/portfolio/by-skill/Python",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "details" in data

    def test_get_top_achievements(self, client, sample_project_execution, auth_headers):
        """Should return top achievements."""
        response = client.get(
            "/api/v2/projects/portfolio/achievements?limit=5",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "details" in data
        assert "ACHIEVEMENTS" in data["details"]

    def test_portfolio_without_auth(self, client):
        """Should return 403 without authentication."""
        response = client.get("/api/v2/projects/portfolio/full")
        assert response.status_code == status.HTTP_403_FORBIDDEN
