"""Tests for daily tracking endpoints."""

from datetime import date, timedelta
from fastapi import status


class TestDailyTrackingEndpoints:
    """Test suite for daily tracking endpoints."""

    def test_reminder_config_enable(self, client):
        """Test enabling reminder configuration."""
        response = client.post(
            "/api/v2/daily-tracking/reminder/config",
            json={"enabled": True, "preferred_time": "20:30"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "message" in data
        assert "config" in data
        assert data["config"]["enabled"] is True
        assert data["config"]["preferred_time"] == "20:30"
        assert data["config"]["status"] == "active"

    def test_reminder_config_disable(self, client):
        """Test disabling reminder configuration."""
        response = client.post("/api/v2/daily-tracking/reminder/config", json={"enabled": False})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["config"]["enabled"] is False
        assert data["config"]["status"] == "inactive"
        assert data["config"]["preferred_time"] == "20:00"  # Default

    def test_reminder_config_default_time(self, client):
        """Test reminder configuration with default time."""
        response = client.post("/api/v2/daily-tracking/reminder/config", json={"enabled": True})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["config"]["preferred_time"] == "20:00"  # Default value

    def test_reminder_status_no_records(self, client, db):
        """Test reminder status when no records exist."""
        response = client.get("/api/v2/daily-tracking/reminder/status")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "needs_reminder" in data
        assert "recorded_today" in data
        assert "today_date" in data
        assert "missing_days_last_week" in data
        assert "missing_count" in data
        assert "message" in data

        assert data["needs_reminder"] is True
        assert data["recorded_today"] is False
        assert data["today_date"] == str(date.today())

    def test_reminder_status_with_today_record(self, client, db):
        """Test reminder status when today's record exists."""
        from database.models import DailyLog

        # Create today's record
        today_log = DailyLog(date=date.today(), sleep_hours=7.5, sleep_quality=8, morning_energy=7)
        db.add(today_log)
        db.commit()

        response = client.get("/api/v2/daily-tracking/reminder/status")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["needs_reminder"] is False
        assert data["recorded_today"] is True
        assert "Você já registrou hoje!" in data["message"]

    def test_insights_no_data(self, client, db):
        """Test insights endpoint with no data."""
        response = client.get("/api/v2/daily-tracking/insights?days=30")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "message" in data
        assert "days_requested" in data
        assert "records_found" in data
        assert data["records_found"] == 0

    def test_insights_with_data(self, client, db):
        """Test insights endpoint with sample data."""
        from database.models import DailyLog

        # Create sample logs for last 7 days
        for i in range(7):
            log_date = date.today() - timedelta(days=i)
            daily_log = DailyLog(
                date=log_date,
                sleep_hours=7.0 + (i % 2),
                sleep_quality=7 + (i % 3),
                morning_energy=6 + (i % 4),
                afternoon_energy=5 + (i % 3),
                evening_energy=4 + (i % 2),
                deep_work_hours=3.0 + (i % 2),
                completed_tasks=4 + (i % 3),
            )
            db.add(daily_log)
        db.commit()

        response = client.get("/api/v2/daily-tracking/insights?days=7")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify structure
        assert "period" in data
        assert "time_series" in data
        assert "moving_averages" in data
        assert "statistics" in data
        assert "insights" in data
        assert "chart_config" in data

        # Verify period
        assert data["period"]["days_requested"] == 7
        assert data["period"]["records_found"] == 7

        # Verify time_series has correct keys
        assert "dates" in data["time_series"]
        assert "sleep_hours" in data["time_series"]
        assert "sleep_quality" in data["time_series"]
        assert "energy_morning" in data["time_series"]
        assert "deep_work_hours" in data["time_series"]
        assert "tasks_completed" in data["time_series"]

        # Verify data length
        assert len(data["time_series"]["dates"]) == 7
        assert len(data["time_series"]["sleep_hours"]) == 7

        # Verify statistics structure
        assert "sleep_hours" in data["statistics"]
        assert "mean" in data["statistics"]["sleep_hours"]
        assert "min" in data["statistics"]["sleep_hours"]
        assert "max" in data["statistics"]["sleep_hours"]

        # Verify insights
        assert "sleep_energy_correlation" in data["insights"]
        assert "energy_trend" in data["insights"]
        assert "most_productive_phase" in data["insights"]
        assert "consistency_score" in data["insights"]

        # Verify chart config
        assert "recommended_chart_types" in data["chart_config"]
        assert "color_palette" in data["chart_config"]

    def test_insights_exceeds_max_days(self, client, db):
        """Test insights endpoint with days > 90."""
        response = client.get("/api/v2/daily-tracking/insights?days=100")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Maximum 90 days allowed" in data["detail"]

    def test_insights_default_days(self, client, db):
        """Test insights endpoint with default days parameter."""
        response = client.get("/api/v2/daily-tracking/insights")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should default to 30 days (even if no data)
        if "period" in data:
            assert data["period"]["days_requested"] == 30
        else:
            # When no data, check days_requested in response
            assert data["days_requested"] == 30

    def test_insights_moving_averages(self, client, db):
        """Test that moving averages are calculated correctly."""
        from database.models import DailyLog

        # Create 10 days of consistent data
        for i in range(10):
            log_date = date.today() - timedelta(days=i)
            daily_log = DailyLog(
                date=log_date,
                sleep_hours=7.5,
                sleep_quality=8,
                morning_energy=7,
                deep_work_hours=4.0,
                completed_tasks=5,
            )
            db.add(daily_log)
        db.commit()

        response = client.get("/api/v2/daily-tracking/insights?days=10")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify moving averages exist
        assert "sleep_hours_ma" in data["moving_averages"]
        assert "sleep_quality_ma" in data["moving_averages"]
        assert "energy_morning_ma" in data["moving_averages"]
        assert "deep_work_hours_ma" in data["moving_averages"]

        # Verify moving averages have correct length
        assert len(data["moving_averages"]["sleep_hours_ma"]) == 10

        # With consistent data, moving average should equal the value
        assert all(ma == 7.5 for ma in data["moving_averages"]["sleep_hours_ma"] if ma is not None)

    def test_insights_consistency_score(self, client, db):
        """Test that consistency score is calculated correctly."""
        from database.models import DailyLog

        # Create 7 out of 10 days (70% consistency)
        for i in [0, 1, 2, 4, 5, 7, 9]:  # 7 days
            log_date = date.today() - timedelta(days=i)
            daily_log = DailyLog(date=log_date, sleep_hours=7.0, sleep_quality=8, morning_energy=7)
            db.add(daily_log)
        db.commit()

        response = client.get("/api/v2/daily-tracking/insights?days=10")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Consistency should be 70% (7 out of 10 days)
        assert data["insights"]["consistency_score"] == 70.0
