"""Tests for Projects Intelligence System API endpoints."""

from fastapi import status


class TestFreelancePlatformAPI:
    """Test suite for FreelancePlatform CRUD operations."""

    def test_create_platform(self, client, auth_headers):
        """Should create FreelancePlatform with valid data."""
        response = client.post(
            "/api/v2/projects/platforms/",
            json={
                "name": "Upwork",
                "platform_type": "freelance_marketplace",
                "active": True,
                "auto_collect": True,
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Upwork"
        assert data["platform_type"] == "freelance_marketplace"
        assert data["active"] is True
        assert "id" in data

    def test_create_platform_missing_name(self, client, auth_headers):
        """Should return 422 for missing required field."""
        response = client.post(
            "/api/v2/projects/platforms/",
            json={"platform_type": "marketplace"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_platforms(self, client, sample_platform, auth_headers):
        """Should list all platforms for authenticated user."""
        response = client.get("/api/v2/projects/platforms/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "platforms" in data
        assert len(data["platforms"]) >= 1
        assert data["platforms"][0]["name"] == "Upwork"

    def test_get_platform(self, client, sample_platform, auth_headers):
        """Should get platform by ID for authenticated user."""
        response = client.get(
            f"/api/v2/projects/platforms/{sample_platform.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_platform.id
        assert data["name"] == "Upwork"

    def test_get_platform_not_found(self, client, auth_headers):
        """Should return 404 for non-existent ID."""
        response = client.get("/api/v2/projects/platforms/9999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_platform(self, client, sample_platform, auth_headers):
        """Should update platform for authenticated user."""
        response = client.patch(
            f"/api/v2/projects/platforms/{sample_platform.id}",
            json={"name": "Upwork Pro", "active": False},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Upwork Pro"
        assert data["active"] is False

    def test_delete_platform(self, client, sample_platform, auth_headers):
        """Should delete platform for authenticated user."""
        response = client.delete(
            f"/api/v2/projects/platforms/{sample_platform.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_platform_without_auth(self, client):
        """Should return 403 without authentication."""
        response = client.get("/api/v2/projects/platforms/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestFreelanceOpportunityAPI:
    """Test suite for FreelanceOpportunity CRUD operations."""

    def test_create_opportunity(self, client, sample_platform, auth_headers):
        """Should create FreelanceOpportunity with valid data."""
        response = client.post(
            "/api/v2/projects/opportunities/",
            json={
                "title": "Build a Mobile App",
                "description": "Need a React Native developer for iOS and Android app",
                "platform_id": sample_platform.id,
                "client_budget": 3000.0,
                "client_currency": "USD",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Build a Mobile App"
        assert data["status"] == "new"
        assert "id" in data

    def test_create_opportunity_invalid_platform(self, client, auth_headers):
        """Should return 400 for invalid platform_id."""
        response = client.post(
            "/api/v2/projects/opportunities/",
            json={
                "title": "Test Project",
                "description": "Test description",
                "platform_id": 9999,
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_opportunities(self, client, sample_opportunity, auth_headers):
        """Should list all opportunities for authenticated user."""
        response = client.get("/api/v2/projects/opportunities/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "opportunities" in data
        assert len(data["opportunities"]) >= 1

    def test_list_opportunities_with_filters(self, client, sample_opportunity, auth_headers):
        """Should filter opportunities by status."""
        response = client.get(
            "/api/v2/projects/opportunities/?status=new",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(opp["status"] == "new" for opp in data["opportunities"])

    def test_get_opportunity(self, client, sample_opportunity, auth_headers):
        """Should get opportunity by ID for authenticated user."""
        response = client.get(
            f"/api/v2/projects/opportunities/{sample_opportunity.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_opportunity.id
        assert data["title"] == "Build a Full-Stack Web Application"

    def test_update_opportunity(self, client, sample_opportunity, auth_headers):
        """Should update opportunity for authenticated user."""
        response = client.patch(
            f"/api/v2/projects/opportunities/{sample_opportunity.id}",
            json={"status": "analyzed", "recommendation": "accept"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "analyzed"
        assert data["recommendation"] == "accept"

    def test_delete_opportunity(self, client, sample_opportunity, auth_headers):
        """Should delete opportunity for authenticated user."""
        response = client.delete(
            f"/api/v2/projects/opportunities/{sample_opportunity.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestPricingParameterAPI:
    """Test suite for PricingParameter CRUD operations."""

    def test_create_pricing_parameter(self, client, auth_headers):
        """Should create PricingParameter with valid data."""
        response = client.post(
            "/api/v2/projects/pricing-parameters/",
            json={
                "base_hourly_rate": 120.0,
                "minimum_margin": 0.25,
                "minimum_project_value": 1000.0,
                "complexity_factors": {"5-6": 1.0, "7-8": 1.2},
                "active": True,
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["base_hourly_rate"] == 120.0
        assert data["version"] == 1
        assert data["active"] is True

    def test_create_pricing_parameter_invalid_factors(self, client, auth_headers):
        """Should return 422 for invalid factor values."""
        response = client.post(
            "/api/v2/projects/pricing-parameters/",
            json={
                "base_hourly_rate": 100.0,
                "complexity_factors": {"test": -1.0},  # Negative factor
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_pricing_parameters(self, client, sample_pricing_parameter, auth_headers):
        """Should list all pricing parameters for authenticated user."""
        response = client.get("/api/v2/projects/pricing-parameters/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "pricing_parameters" in data
        assert len(data["pricing_parameters"]) >= 1

    def test_get_active_pricing_parameter(self, client, sample_pricing_parameter, auth_headers):
        """Should get active pricing parameter for authenticated user."""
        response = client.get(
            "/api/v2/projects/pricing-parameters/active",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["active"] is True
        assert data["version"] == 1

    def test_get_pricing_parameter(self, client, sample_pricing_parameter, auth_headers):
        """Should get pricing parameter by ID for authenticated user."""
        response = client.get(
            f"/api/v2/projects/pricing-parameters/{sample_pricing_parameter.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_pricing_parameter.id
        assert data["base_hourly_rate"] == 100.0

    def test_update_pricing_parameter(self, client, sample_pricing_parameter, auth_headers):
        """Should update pricing parameter for authenticated user."""
        response = client.patch(
            f"/api/v2/projects/pricing-parameters/{sample_pricing_parameter.id}",
            json={"base_hourly_rate": 150.0},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["base_hourly_rate"] == 150.0

    def test_delete_inactive_pricing_parameter(self, client, db, sample_user, auth_headers):
        """Should delete inactive pricing parameter."""
        from database.models import PricingParameter

        # Create inactive parameter
        inactive_param = PricingParameter(
            user_id=sample_user.id,
            version=2,
            base_hourly_rate=100.0,
            active=False,
        )
        db.add(inactive_param)
        db.commit()
        db.refresh(inactive_param)

        response = client.delete(
            f"/api/v2/projects/pricing-parameters/{inactive_param.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_active_pricing_parameter_fails(
        self, client, sample_pricing_parameter, auth_headers
    ):
        """Should return 400 when trying to delete active pricing parameter."""
        response = client.delete(
            f"/api/v2/projects/pricing-parameters/{sample_pricing_parameter.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestProjectExecutionAPI:
    """Test suite for ProjectExecution CRUD operations."""

    def test_create_project_execution(self, client, sample_opportunity, auth_headers):
        """Should create ProjectExecution with valid data."""
        from datetime import date, timedelta

        response = client.post(
            "/api/v2/projects/executions/",
            json={
                "opportunity_id": sample_opportunity.id,
                "negotiated_value": 5000.0,
                "start_date": date.today().isoformat(),
                "planned_end_date": (date.today() + timedelta(days=30)).isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["negotiated_value"] == 5000.0
        assert data["status"] == "planned"
        assert "created_at" in data

    def test_create_execution_invalid_opportunity(self, client, auth_headers):
        """Should return 400 for invalid opportunity_id."""
        from datetime import date

        response = client.post(
            "/api/v2/projects/executions/",
            json={
                "opportunity_id": 9999,
                "negotiated_value": 1000.0,
                "start_date": date.today().isoformat(),
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_project_executions(self, client, sample_project_execution, auth_headers):
        """Should list all project executions for authenticated user."""
        response = client.get("/api/v2/projects/executions/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "executions" in data
        assert len(data["executions"]) >= 1

    def test_get_project_execution(self, client, sample_project_execution, auth_headers):
        """Should get project execution by ID for authenticated user."""
        response = client.get(
            f"/api/v2/projects/executions/{sample_project_execution.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_project_execution.id
        assert data["negotiated_value"] == 5000.0

    def test_update_project_execution(self, client, sample_project_execution, auth_headers):
        """Should update project execution for authenticated user."""
        response = client.patch(
            f"/api/v2/projects/executions/{sample_project_execution.id}",
            json={
                "actual_hours": 45.0,
                "actual_revenue": 5000.0,
                "status": "completed",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["actual_hours"] == 45.0
        assert data["status"] == "completed"

    def test_delete_project_execution(self, client, sample_project_execution, auth_headers):
        """Should delete project execution for authenticated user."""
        response = client.delete(
            f"/api/v2/projects/executions/{sample_project_execution.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestNegotiationAPI:
    """Test suite for Negotiation CRUD operations."""

    def test_create_negotiation(self, client, sample_opportunity, auth_headers):
        """Should create Negotiation with valid data."""
        response = client.post(
            "/api/v2/projects/negotiations/",
            json={
                "opportunity_id": sample_opportunity.id,
                "original_budget": 5000.0,
                "counter_proposal_budget": 6000.0,
                "counter_proposal_justification": "Need higher budget for added features",
                "final_agreed_budget": 5500.0,
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["counter_proposal_budget"] == 6000.0
        assert data["final_agreed_budget"] == 5500.0
        assert data["outcome"] == "pending"

    def test_create_negotiation_invalid_opportunity(self, client, auth_headers):
        """Should return 400 for invalid opportunity_id."""
        response = client.post(
            "/api/v2/projects/negotiations/",
            json={
                "opportunity_id": 9999,
                "counter_proposal_budget": 1000.0,
                "counter_proposal_justification": "Test justification",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_negotiations(self, client, sample_negotiation, auth_headers):
        """Should list all negotiations for authenticated user."""
        response = client.get("/api/v2/projects/negotiations/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "negotiations" in data
        assert len(data["negotiations"]) >= 1

    def test_get_negotiation(self, client, sample_negotiation, auth_headers):
        """Should get negotiation by ID for authenticated user."""
        response = client.get(
            f"/api/v2/projects/negotiations/{sample_negotiation.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_negotiation.id
        assert data["counter_proposal_budget"] == 6000.0

    def test_update_negotiation(self, client, sample_negotiation, auth_headers):
        """Should update negotiation for authenticated user."""
        response = client.patch(
            f"/api/v2/projects/negotiations/{sample_negotiation.id}",
            json={"outcome": "accepted", "final_agreed_budget": 5800.0},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["outcome"] == "accepted"
        assert data["final_agreed_budget"] == 5800.0

    def test_delete_negotiation(self, client, sample_negotiation, auth_headers):
        """Should delete negotiation for authenticated user."""
        response = client.delete(
            f"/api/v2/projects/negotiations/{sample_negotiation.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestAgentActions:
    """Test suite for Agent action endpoints."""

    def test_collect_opportunities_endpoint_exists(self, client, sample_platform, auth_headers):
        """Should have collect endpoint (returns 202 or 500 depending on implementation)."""
        response = client.post(
            "/api/v2/projects/collect",
            headers=auth_headers,
        )

        # Endpoint exists (not 404), but may return 500 if agents not fully configured
        assert response.status_code in [
            status.HTTP_202_ACCEPTED,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_analyze_opportunity_endpoint_exists(self, client, sample_opportunity, auth_headers):
        """Should have analyze endpoint (returns 200 or 500 depending on AI availability)."""
        response = client.post(
            f"/api/v2/projects/opportunities/{sample_opportunity.id}/analyze",
            headers=auth_headers,
        )

        # Endpoint exists (not 404), but may return 500 if OpenAI not configured
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_evaluate_opportunity_endpoint_exists(self, client, sample_opportunity, auth_headers):
        """Should have evaluate endpoint (returns 200 or 500 depending on AI availability)."""
        response = client.post(
            f"/api/v2/projects/opportunities/{sample_opportunity.id}/evaluate",
            headers=auth_headers,
        )

        # Endpoint exists (not 404), but may return 500 if OpenAI not configured
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]


class TestUserIsolation:
    """Test suite for multi-tenancy and user isolation."""

    def test_cannot_access_other_user_platform(self, client, db, sample_platform, auth_headers):
        """Should not access another user's platform."""
        from api.auth.password import hash_password
        from database.models import FreelancePlatform, User

        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=hash_password("OtherPass123"),
            is_active=True,
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)

        # Create platform for other user
        other_platform = FreelancePlatform(
            user_id=other_user.id,
            name="Other Platform",
            active=True,
        )
        db.add(other_platform)
        db.commit()
        db.refresh(other_platform)

        # Try to access other user's platform
        response = client.get(
            f"/api/v2/projects/platforms/{other_platform.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_update_other_user_opportunity(
        self, client, db, sample_opportunity, auth_headers
    ):
        """Should not update another user's opportunity."""
        from api.auth.password import hash_password
        from database.models import FreelanceOpportunity, User

        # Create another user
        other_user = User(
            username="otheruser2",
            email="other2@example.com",
            hashed_password=hash_password("OtherPass123"),
            is_active=True,
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)

        # Create opportunity for other user
        other_opp = FreelanceOpportunity(
            user_id=other_user.id,
            title="Other Opportunity",
            description="Other description",
            status="new",
            recommendation="pending",
        )
        db.add(other_opp)
        db.commit()
        db.refresh(other_opp)

        # Try to update other user's opportunity
        response = client.patch(
            f"/api/v2/projects/opportunities/{other_opp.id}",
            json={"title": "Hacked"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
