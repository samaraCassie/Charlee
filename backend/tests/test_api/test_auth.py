"""Tests for Authentication API endpoints."""

from fastapi import status


class TestAuthRegistration:
    """Test suite for user registration."""

    def test_register_new_user(self, client):
        """Should successfully register a new user with valid data."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "SecurePass123",
                "full_name": "New User",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "id" in data
        assert "created_at" in data
        assert "hashed_password" not in data  # Should not expose password

    def test_register_duplicate_username(self, client, sample_user):
        """Should return 400 for duplicate username."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": sample_user.username,
                "email": "different@example.com",
                "password": "SecurePass123",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.json()["detail"].lower()

    def test_register_duplicate_email(self, client, sample_user):
        """Should return 400 for duplicate email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "differentuser",
                "email": sample_user.email,
                "password": "SecurePass123",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()["detail"].lower()

    def test_register_weak_password(self, client):
        """Should return 422 for weak password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "weakpass",
                "email": "weak@example.com",
                "password": "weak",  # Too short, no uppercase, no digit
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_invalid_email(self, client):
        """Should return 422 for invalid email format."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "not-an-email",
                "password": "SecurePass123",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_short_username(self, client):
        """Should return 422 for username less than 3 characters."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "ab",
                "email": "test@example.com",
                "password": "SecurePass123",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthLogin:
    """Test suite for user login."""

    def test_login_success(self, client, sample_user):
        """Should successfully login with valid credentials."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "TestPass123",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] == 30 * 60  # 30 minutes in seconds

    def test_login_wrong_password(self, client, sample_user):
        """Should return 401 for incorrect password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "WrongPassword123",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Should return 401 for non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "TestPass123",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, client, db, sample_user):
        """Should return 403 for inactive user."""
        # Deactivate user
        sample_user.is_active = False
        db.commit()

        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "TestPass123",
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "inactive" in response.json()["detail"].lower()


class TestAuthTokens:
    """Test suite for token operations."""

    def test_access_protected_endpoint(self, client, auth_headers):
        """Should access protected endpoint with valid token."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "username" in data
        assert "email" in data

    def test_access_protected_endpoint_without_token(self, client):
        """Should return 403 for protected endpoint without token."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_access_protected_endpoint_invalid_token(self, client):
        """Should return 401 for invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token(self, client, sample_user, db):
        """Should refresh access token with valid refresh token."""
        # First login to get refresh token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "TestPass123",
            },
        )
        assert login_response.status_code == status.HTTP_200_OK
        refresh_token = login_response.json()["refresh_token"]

        # Verify token was saved in database
        from database.models import RefreshToken
        db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
        assert db_token is not None, "Refresh token should be saved in database"
        assert db_token.revoked is False, "Refresh token should not be revoked"

        # Test that we can decode the refresh token
        from api.auth.jwt import decode_refresh_token
        decoded = decode_refresh_token(refresh_token)
        assert decoded is not None, "Failed to decode refresh token. Token might be invalid or using wrong secret."
        assert decoded.user_id == sample_user.id, f"User ID mismatch: {decoded.user_id} != {sample_user.id}"
        assert decoded.token_type == "refresh", f"Token type should be 'refresh', got '{decoded.token_type}'"

        # Refresh the token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}. Response: {response.json()}"
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_refresh_token_invalid(self, client):
        """Should return 401 for invalid refresh token."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_refresh_token"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthLogout:
    """Test suite for logout operations."""

    def test_logout_single_device(self, client, sample_user, auth_headers):
        """Should successfully logout from single device."""
        # Login to get refresh token
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
        assert "logged out" in response.json()["message"].lower()

        # Try to use the revoked refresh token
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_all_devices(self, client, sample_user, auth_headers):
        """Should successfully logout from all devices."""
        # Login multiple times to create multiple refresh tokens
        login_response1 = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "TestPass123",
            },
        )
        refresh_token1 = login_response1.json()["refresh_token"]

        login_response2 = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "TestPass123",
            },
        )
        refresh_token2 = login_response2.json()["refresh_token"]

        # Logout from all devices
        response = client.post(
            "/api/v1/auth/logout-all",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert "all devices" in response.json()["message"].lower()

        # Both refresh tokens should be revoked
        refresh_response1 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token1},
        )
        assert refresh_response1.status_code == status.HTTP_401_UNAUTHORIZED

        refresh_response2 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token2},
        )
        assert refresh_response2.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthPasswordChange:
    """Test suite for password change."""

    def test_change_password_success(self, client, auth_headers, sample_user):
        """Should successfully change password."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "TestPass123",
                "new_password": "NewSecurePass456",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert "success" in response.json()["message"].lower()

        # Login with new password
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user.username,
                "password": "NewSecurePass456",
            },
        )
        assert login_response.status_code == status.HTTP_200_OK

    def test_change_password_wrong_current(self, client, auth_headers):
        """Should return 400 for incorrect current password."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "WrongPassword123",
                "new_password": "NewSecurePass456",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "incorrect" in response.json()["detail"].lower()

    def test_change_password_weak_new(self, client, auth_headers):
        """Should return 422 for weak new password."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "TestPass123",
                "new_password": "weak",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthUserInfo:
    """Test suite for user information."""

    def test_get_current_user_info(self, client, auth_headers, sample_user):
        """Should get current user information."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == sample_user.id
        assert data["username"] == sample_user.username
        assert data["email"] == sample_user.email
        assert data["full_name"] == sample_user.full_name
        assert data["is_active"] is True
        assert "hashed_password" not in data


class TestAuthDataIsolation:
    """Test suite for user data isolation."""

    def test_user_cannot_access_other_users_data(self, client, db):
        """Should ensure users can only access their own data."""
        from api.auth.jwt import create_access_token
        from api.auth.password import hash_password
        from database.models import BigRock, User

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
        db.refresh(user1)
        db.refresh(user2)

        # Create big rock for user1
        big_rock = BigRock(
            name="User1 Big Rock",
            user_id=user1.id,
        )
        db.add(big_rock)
        db.commit()
        db.refresh(big_rock)

        # User2 tries to access user1's big rock
        user2_token = create_access_token(
            {
                "user_id": user2.id,
                "username": user2.username,
                "email": user2.email,
            }
        )
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        response = client.get(
            f"/api/v1/big-rocks/{big_rock.id}",
            headers=user2_headers,
        )

        # Should return 404 (not found) because user2 can't see user1's data
        assert response.status_code == status.HTTP_404_NOT_FOUND
