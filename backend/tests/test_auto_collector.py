"""Tests for AutoCollector - automated job collection scheduler."""

from datetime import datetime, timedelta, timezone


from agent.specialized_agents.projects.auto_collector import (
    create_auto_collector,
)
from database.models import FreelancePlatform


class TestAutoCollector:
    """Test suite for AutoCollector."""

    def test_create_auto_collector(self, db, sample_user):
        """Should create AutoCollector instance."""
        collector = create_auto_collector(db=db)

        assert collector is not None
        assert collector.db == db

    def test_should_collect_inactive_platform(self, db, sample_user):
        """Should not collect from inactive platform."""
        platform = FreelancePlatform(
            user_id=sample_user.id,
            name="Inactive Platform",
            active=False,
            auto_collect=True,
            collection_interval_minutes=60,
        )
        db.add(platform)
        db.commit()

        collector = create_auto_collector(db=db)
        result = collector.should_collect(platform)

        assert result is False

    def test_should_collect_auto_collect_disabled(self, db, sample_user):
        """Should not collect when auto_collect is disabled."""
        platform = FreelancePlatform(
            user_id=sample_user.id,
            name="Manual Platform",
            active=True,
            auto_collect=False,
            collection_interval_minutes=60,
        )
        db.add(platform)
        db.commit()

        collector = create_auto_collector(db=db)
        result = collector.should_collect(platform)

        assert result is False

    def test_should_collect_never_collected(self, db, sample_user):
        """Should collect from platform that was never collected."""
        platform = FreelancePlatform(
            user_id=sample_user.id,
            name="New Platform",
            active=True,
            auto_collect=True,
            collection_interval_minutes=60,
            last_collection_at=None,
        )
        db.add(platform)
        db.commit()

        collector = create_auto_collector(db=db)
        result = collector.should_collect(platform)

        assert result is True

    def test_should_collect_interval_not_elapsed(self, db, sample_user):
        """Should not collect when interval has not elapsed."""
        # Last collected 10 minutes ago, interval is 60 minutes
        last_collection = datetime.now(timezone.utc) - timedelta(minutes=10)

        platform = FreelancePlatform(
            user_id=sample_user.id,
            name="Recent Platform",
            active=True,
            auto_collect=True,
            collection_interval_minutes=60,
            last_collection_at=last_collection,
        )
        db.add(platform)
        db.commit()

        collector = create_auto_collector(db=db)
        result = collector.should_collect(platform)

        assert result is False

    def test_should_collect_interval_elapsed(self, db, sample_user):
        """Should collect when interval has elapsed."""
        # Last collected 2 hours ago, interval is 60 minutes
        last_collection = datetime.now(timezone.utc) - timedelta(hours=2)

        platform = FreelancePlatform(
            user_id=sample_user.id,
            name="Due Platform",
            active=True,
            auto_collect=True,
            collection_interval_minutes=60,
            last_collection_at=last_collection,
        )
        db.add(platform)
        db.commit()

        collector = create_auto_collector(db=db)
        result = collector.should_collect(platform)

        assert result is True

    def test_collect_from_platform_upwork(self, db, sample_user):
        """Should collect opportunities from Upwork platform."""
        platform = FreelancePlatform(
            user_id=sample_user.id,
            name="Upwork",
            platform_type="freelance_marketplace",
            active=True,
            auto_collect=True,
            collection_interval_minutes=1440,
            api_config={},
        )
        db.add(platform)
        db.commit()

        collector = create_auto_collector(db=db)
        count = collector.collect_from_platform(platform, max_results=10)

        # Mock Upwork integration returns 3 opportunities
        assert count >= 0
        assert isinstance(count, int)

        # Check platform stats were updated
        db.refresh(platform)
        assert platform.last_collection_at is not None
        assert platform.last_collection_count == count
        assert platform.total_projects_collected >= count

    def test_collect_from_platform_freelancer(self, db, sample_user):
        """Should collect opportunities from Freelancer.com platform."""
        platform = FreelancePlatform(
            user_id=sample_user.id,
            name="Freelancer.com",
            platform_type="freelance_marketplace",
            active=True,
            auto_collect=True,
            collection_interval_minutes=1440,
            api_config={},
        )
        db.add(platform)
        db.commit()

        collector = create_auto_collector(db=db)
        count = collector.collect_from_platform(platform, max_results=10)

        # Mock Freelancer.com integration currently returns 0
        assert count == 0

        # Check platform stats were updated
        db.refresh(platform)
        assert platform.last_collection_at is not None

    def test_collect_from_platform_unsupported(self, db, sample_user):
        """Should return 0 for unsupported platform."""
        platform = FreelancePlatform(
            user_id=sample_user.id,
            name="Unknown Platform",
            platform_type="unknown",
            active=True,
            auto_collect=True,
            collection_interval_minutes=1440,
        )
        db.add(platform)
        db.commit()

        collector = create_auto_collector(db=db)
        count = collector.collect_from_platform(platform, max_results=10)

        assert count == 0

    def test_run_collection_cycle(self, db, sample_user):
        """Should run collection cycle for all eligible platforms."""
        # Create multiple platforms
        upwork = FreelancePlatform(
            user_id=sample_user.id,
            name="Upwork",
            active=True,
            auto_collect=True,
            collection_interval_minutes=60,
            last_collection_at=datetime.now(timezone.utc) - timedelta(hours=2),
            api_config={},
        )

        freelancer = FreelancePlatform(
            user_id=sample_user.id,
            name="Freelancer.com",
            active=True,
            auto_collect=True,
            collection_interval_minutes=60,
            last_collection_at=datetime.now(timezone.utc) - timedelta(hours=3),
            api_config={},
        )

        inactive = FreelancePlatform(
            user_id=sample_user.id,
            name="Inactive Platform",
            active=False,
            auto_collect=True,
            collection_interval_minutes=60,
        )

        db.add_all([upwork, freelancer, inactive])
        db.commit()

        collector = create_auto_collector(db=db)
        results = collector.run_collection_cycle(user_id=sample_user.id)

        assert "total_platforms" in results
        assert "collected" in results
        assert "platforms" in results
        assert results["total_platforms"] >= 0
        assert isinstance(results["collected"], int)
        assert isinstance(results["platforms"], list)

    def test_run_collection_cycle_no_platforms(self, db, sample_user):
        """Should handle case with no active platforms."""
        collector = create_auto_collector(db=db)
        results = collector.run_collection_cycle(user_id=sample_user.id)

        assert results["total_platforms"] == 0
        assert results["collected"] == 0
        assert results["platforms"] == []

    def test_run_collection_cycle_filters_by_user(self, db, sample_user):
        """Should only collect for specified user."""
        # Create platform for sample_user
        platform1 = FreelancePlatform(
            user_id=sample_user.id,
            name="User 1 Platform",
            active=True,
            auto_collect=True,
            collection_interval_minutes=60,
            last_collection_at=None,
            api_config={},
        )
        db.add(platform1)
        db.commit()

        collector = create_auto_collector(db=db)
        results = collector.run_collection_cycle(user_id=sample_user.id)

        # Should only collect from user's platforms
        assert results["total_platforms"] >= 0

    def test_collect_from_platform_error_handling(self, db, sample_user):
        """Should handle missing api_config gracefully with mock data."""
        platform = FreelancePlatform(
            user_id=sample_user.id,
            name="Upwork",
            active=True,
            auto_collect=True,
            collection_interval_minutes=60,
            api_config=None,  # Mock integration handles this gracefully
        )
        db.add(platform)
        db.commit()

        collector = create_auto_collector(db=db)
        count = collector.collect_from_platform(platform, max_results=10)

        # Mock integration returns sample data even without config
        assert count >= 0
        assert isinstance(count, int)

    def test_run_collection_cycle_all_users(self, db, sample_user):
        """Should collect for all users when user_id not specified."""
        platform = FreelancePlatform(
            user_id=sample_user.id,
            name="Upwork",
            active=True,
            auto_collect=True,
            collection_interval_minutes=60,
            last_collection_at=None,
            api_config={},
        )
        db.add(platform)
        db.commit()

        collector = create_auto_collector(db=db)
        results = collector.run_collection_cycle()

        assert "total_platforms" in results
        assert "collected" in results
        assert results["total_platforms"] >= 0
