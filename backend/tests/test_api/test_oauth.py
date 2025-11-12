"""Tests for OAuth authentication utilities and helper functions."""

import pytest


class TestOAuthHelpers:
    """Test suite for OAuth helper functions."""

    def test_generate_unique_username(self, db):
        """Should generate unique username when collision exists."""
        from api.auth.oauth import generate_unique_username
        from database.models import User

        # Create user with desired username
        existing_user = User(
            username="testuser",
            email="existing@example.com",
            hashed_password="dummy",
            is_active=True,
        )
        db.add(existing_user)
        db.commit()

        # Generate unique username
        unique_username = generate_unique_username(db, "testuser")

        assert unique_username != "testuser"
        assert unique_username.startswith("testuser")

    def test_extract_google_user_info(self):
        """Should extract user info from Google token."""
        from api.auth.oauth import extract_google_user_info

        token = {
            "userinfo": {
                "sub": "google_123",
                "email": "user@gmail.com",
                "name": "Test User",
                "picture": "https://example.com/pic.jpg",
                "given_name": "Test",
            }
        }

        user_info = extract_google_user_info(token)

        assert user_info["oauth_id"] == "google_123"
        assert user_info["email"] == "user@gmail.com"
        assert user_info["username"] == "user"  # Username from email prefix
        assert user_info["full_name"] == "Test User"
        assert user_info["avatar_url"] == "https://example.com/pic.jpg"

    def test_extract_github_user_info(self):
        """Should extract user info from GitHub user data and emails."""
        from api.auth.oauth import extract_github_user_info

        user_data = {
            "id": 12345,
            "login": "octocat",
            "email": "octocat@github.com",
            "name": "The Octocat",
            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
        }

        email_data = [
            {"email": "octocat@github.com", "primary": True, "verified": True},
        ]

        user_info = extract_github_user_info(user_data, email_data)

        assert user_info["oauth_id"] == "12345"
        assert user_info["email"] == "octocat@github.com"
        assert user_info["username"] == "octocat"
        assert user_info["full_name"] == "The Octocat"

    def test_extract_github_user_info_no_primary_email(self):
        """Should use first email when no primary email exists."""
        from api.auth.oauth import extract_github_user_info

        user_data = {
            "id": 12345,
            "login": "octocat",
            "name": "The Octocat",
        }

        email_data = [
            {"email": "first@github.com", "primary": False, "verified": True},
            {"email": "second@github.com", "primary": False, "verified": False},
        ]

        user_info = extract_github_user_info(user_data, email_data)

        assert user_info["email"] == "first@github.com"

    def test_create_or_update_oauth_user_new(self, db):
        """Should create new OAuth user."""
        from api.auth.oauth import create_or_update_oauth_user

        user = create_or_update_oauth_user(
            db=db,
            provider="google",
            oauth_id="new_oauth_123",
            email="newuser@gmail.com",
            username="newuser",
            full_name="New User",
            avatar_url="https://example.com/avatar.jpg",
        )

        assert user.id is not None
        assert user.email == "newuser@gmail.com"
        assert user.username == "newuser"
        assert user.full_name == "New User"
        assert user.oauth_provider == "google"
        assert user.oauth_id == "new_oauth_123"
        assert user.is_active is True

    def test_create_or_update_oauth_user_existing(self, db, sample_user):
        """Should update existing OAuth user."""
        from api.auth.oauth import create_or_update_oauth_user

        # Set OAuth info on existing user
        sample_user.oauth_provider = "google"
        sample_user.oauth_id = "existing_oauth_123"
        db.commit()

        # Update user via OAuth
        updated_user = create_or_update_oauth_user(
            db=db,
            provider="google",
            oauth_id="existing_oauth_123",
            email=sample_user.email,
            username=sample_user.username,
            full_name="Updated Name",
            avatar_url="https://example.com/new_avatar.jpg",
        )

        assert updated_user.id == sample_user.id
        assert updated_user.full_name == "Updated Name"
        assert updated_user.is_active is True

    def test_create_or_update_oauth_user_link_to_local_account(self, db, sample_user):
        """Should link OAuth to existing local account by email."""
        from api.auth.oauth import create_or_update_oauth_user

        # sample_user exists without OAuth info
        assert sample_user.oauth_provider is None
        assert sample_user.oauth_id is None

        # Link OAuth to existing local account
        linked_user = create_or_update_oauth_user(
            db=db,
            provider="github",
            oauth_id="github_999",
            email=sample_user.email,  # Same email as existing user
            username="different_username",
            full_name="Updated via OAuth",
            avatar_url="https://example.com/oauth_avatar.jpg",
        )

        assert linked_user.id == sample_user.id
        assert linked_user.oauth_provider == "github"
        assert linked_user.oauth_id == "github_999"
        assert linked_user.avatar_url == "https://example.com/oauth_avatar.jpg"

    def test_extract_google_user_info_with_given_name(self):
        """Should extract username from email prefix."""
        from api.auth.oauth import extract_google_user_info

        token = {
            "userinfo": {
                "sub": "google_456",
                "email": "jane.doe@gmail.com",
                "name": "Jane Doe",
                "given_name": "Jane",
                "picture": None,
            }
        }

        user_info = extract_google_user_info(token)

        assert user_info["oauth_id"] == "google_456"
        assert user_info["username"] == "jane.doe"  # Username from email prefix
        assert user_info["avatar_url"] is None

    def test_generate_unique_username_no_collision(self, db):
        """Should return base username when no collision exists."""
        from api.auth.oauth import generate_unique_username

        unique_username = generate_unique_username(db, "brandnewuser")

        assert unique_username == "brandnewuser"

    def test_generate_unique_username_multiple_collisions(self, db):
        """Should handle multiple username collisions."""
        from api.auth.oauth import generate_unique_username
        from api.auth.password import hash_password
        from database.models import User

        # Create users with colliding usernames
        for i in range(3):
            username = "popular" if i == 0 else f"popular{i}"
            user = User(
                username=username,
                email=f"user{i}@example.com",
                hashed_password=hash_password("pass123"),
                is_active=True,
            )
            db.add(user)
        db.commit()

        # Should generate "popular3"
        unique_username = generate_unique_username(db, "popular")

        assert unique_username == "popular3"

    def test_extract_google_user_info_minimal(self):
        """Should handle minimal Google user info."""
        from api.auth.oauth import extract_google_user_info

        token = {
            "userinfo": {
                "sub": "google_minimal",
                "email": "minimal@gmail.com",
            }
        }

        user_info = extract_google_user_info(token)

        assert user_info["oauth_id"] == "google_minimal"
        assert user_info["email"] == "minimal@gmail.com"
        assert user_info["username"] == "minimal"

    def test_extract_github_user_info_fallback_email(self):
        """Should fallback to user_data email when email_data is empty."""
        from api.auth.oauth import extract_github_user_info

        user_data = {
            "id": 99999,
            "login": "testuser",
            "email": "fallback@github.com",
            "name": "Test User",
        }

        user_info = extract_github_user_info(user_data, [])

        assert user_info["oauth_id"] == "99999"
        assert user_info["email"] == "fallback@github.com"
        assert user_info["username"] == "testuser"
