"""Tests for advanced authentication features: lockout, audit log, and OAuth."""

from fastapi import status
from datetime import datetime, timedelta
from database.models import AuditLog


class TestAccountLockout:
    """Test suite for account lockout functionality."""

    def test_account_locks_after_max_attempts(self, client, sample_user):
        """Should lock account after 5 failed login attempts."""
        # Try to login with wrong password 5 times
        for i in range(5):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "username": sample_user.username,
                    "password": "WrongPassword123",
                },
            )

            if i < 4:
                # First 4 attempts should return 401 with remaining attempts
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
                assert "attempts remaining" in response.json()["detail"].lower()
            else:
                # 5th attempt should lock the account
                assert response.status_code == status.HTTP_403_FORBIDDEN
                assert "locked" in response.json()["detail"].lower()

    def test_locked_account_cannot_login(self, client, sample_user, db):
        """Should prevent login when account is locked."""
        # Lock the account manually
        sample_user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.commit()

        # Try to login with correct password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "TestPass123",
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "locked" in response.json()["detail"].lower()

    def test_successful_login_resets_failed_attempts(self, client, sample_user, db):
        """Should reset failed attempts counter on successful login."""
        # Set failed attempts
        sample_user.failed_login_attempts = 3
        db.commit()

        # Successful login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "TestPass123",
            },
        )

        assert response.status_code == status.HTTP_200_OK

        # Check that failed attempts were reset
        db.refresh(sample_user)
        assert sample_user.failed_login_attempts == 0
        assert sample_user.locked_until is None

    def test_failed_attempts_reset_after_24_hours(self, client, sample_user, db):
        """Should reset failed attempts if last failure was > 24 hours ago."""
        # Set old failed attempt
        sample_user.failed_login_attempts = 3
        sample_user.last_failed_login = datetime.utcnow() - timedelta(hours=25)
        db.commit()

        # Try to login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "WrongPassword123",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Check that counter was reset and this is counted as first attempt
        db.refresh(sample_user)
        assert sample_user.failed_login_attempts == 1


class TestAuditLog:
    """Test suite for audit logging."""

    def test_registration_creates_audit_log(self, client, db):
        """Should create audit log entry on user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "audituser",
                "email": "audit@example.com",
                "password": "SecurePass123",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Check audit log
        audit_log = db.query(AuditLog).filter(AuditLog.event_type == "register").first()

        assert audit_log is not None
        assert audit_log.event_status == "success"
        assert "audituser" in audit_log.event_message

    def test_successful_login_creates_audit_log(self, client, sample_user, db):
        """Should create audit log entry on successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "TestPass123",
            },
        )

        assert response.status_code == status.HTTP_200_OK

        # Check audit log
        audit_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.user_id == sample_user.id,
                AuditLog.event_type == "login",
                AuditLog.event_status == "success",
            )
            .first()
        )

        assert audit_log is not None
        assert sample_user.username in audit_log.event_message

    def test_failed_login_creates_audit_log(self, client, sample_user, db):
        """Should create audit log entry on failed login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "WrongPassword123",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Check audit log
        audit_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.event_type == "login",
                AuditLog.event_status == "failure",
            )
            .first()
        )

        assert audit_log is not None
        assert (
            "Invalid credentials" in audit_log.event_message
            or "attempts remaining" in audit_log.event_message
        )

    def test_account_lockout_creates_audit_log(self, client, sample_user, db):
        """Should create audit log entry when account is locked."""
        # Trigger lockout with 5 failed attempts
        for _ in range(5):
            client.post(
                "/api/v1/auth/login",
                json={
                    "username": sample_user.username,
                    "password": "WrongPassword123",
                },
            )

        # Check for lockout audit log
        audit_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.user_id == sample_user.id,
                AuditLog.event_type == "account_locked",
            )
            .first()
        )

        assert audit_log is not None
        assert audit_log.event_status == "blocked"

    def test_logout_creates_audit_log(self, client, sample_user, auth_headers, db):
        """Should create audit log entry on logout."""
        # Login first to get refresh token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "TestPass123",
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Logout
        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK

        # Check audit log
        audit_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.user_id == sample_user.id,
                AuditLog.event_type == "logout",
            )
            .first()
        )

        assert audit_log is not None
        assert audit_log.event_status == "success"

    def test_password_change_creates_audit_log(self, client, auth_headers, sample_user, db):
        """Should create audit log entry on password change."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "TestPass123",
                "new_password": "NewSecurePass456",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK

        # Check audit log
        audit_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.user_id == sample_user.id,
                AuditLog.event_type == "password_change",
            )
            .first()
        )

        assert audit_log is not None
        assert audit_log.event_status == "success"

    def test_audit_log_includes_ip_and_user_agent(self, client, sample_user, db):
        """Should capture IP address and user agent in audit log."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "TestPass123",
            },
            headers={"User-Agent": "TestClient/1.0"},
        )

        assert response.status_code == status.HTTP_200_OK

        # Check audit log
        audit_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.user_id == sample_user.id,
                AuditLog.event_type == "login",
            )
            .first()
        )

        assert audit_log is not None
        assert audit_log.ip_address is not None
        assert audit_log.user_agent == "TestClient/1.0"
        assert audit_log.request_path == "/api/v1/auth/login"


class TestOAuthUser:
    """Test suite for OAuth user management."""

    def test_oauth_user_can_be_created(self, db):
        """Should create user with OAuth provider information."""
        from database.models import User
        from api.auth.password import hash_password

        user = User(
            username="googleuser",
            email="user@gmail.com",
            hashed_password=hash_password("random_password"),
            oauth_provider="google",
            oauth_id="google_12345",
            avatar_url="https://example.com/avatar.jpg",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.oauth_provider == "google"
        assert user.oauth_id == "google_12345"
        assert user.avatar_url is not None

    def test_oauth_user_has_methods(self, db):
        """Should have lockout-related methods available."""
        from database.models import User
        from api.auth.password import hash_password

        user = User(
            username="testuser2",
            email="test2@example.com",
            hashed_password=hash_password("TestPass123"),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Test methods exist
        assert hasattr(user, "is_locked")
        assert hasattr(user, "reset_failed_attempts")

        # Test is_locked returns False initially
        assert user.is_locked() is False

        # Test reset_failed_attempts works
        user.failed_login_attempts = 5
        user.reset_failed_attempts()

        assert user.failed_login_attempts == 0
        assert user.locked_until is None


class TestSecurityEnhancements:
    """Test suite for general security enhancements."""

    def test_registration_with_audit(self, client, db):
        """Should register user and create complete audit trail."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "secureuser",
                "email": "secure@example.com",
                "password": "SecurePass123",
                "full_name": "Secure User",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Verify user was created
        user_data = response.json()
        assert user_data["username"] == "secureuser"
        assert user_data["email"] == "secure@example.com"

        # Verify audit log
        audit_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.event_type == "register",
                AuditLog.event_status == "success",
            )
            .first()
        )

        assert audit_log is not None
        assert audit_log.user_id == user_data["id"]

    def test_multiple_failed_logins_tracked_per_user(self, client, db):
        """Should track failed login attempts independently per user."""
        from database.models import User
        from api.auth.password import hash_password

        # Create two users
        user1 = User(
            username="user1",
            email="user1@example.com",
            hashed_password=hash_password("Pass123"),
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            hashed_password=hash_password("Pass123"),
        )

        db.add_all([user1, user2])
        db.commit()

        # Fail login for user1 3 times
        for _ in range(3):
            client.post(
                "/api/v1/auth/login",
                json={"username": "user1", "password": "wrong"},
            )

        # Fail login for user2 2 times
        for _ in range(2):
            client.post(
                "/api/v1/auth/login",
                json={"username": "user2", "password": "wrong"},
            )

        # Check counters
        db.refresh(user1)
        db.refresh(user2)

        assert user1.failed_login_attempts == 3
        assert user2.failed_login_attempts == 2
