"""Role-Based Access Control (RBAC) utilities."""

from enum import Enum
from functools import wraps
from typing import Callable, List, Union

from fastapi import HTTPException, status

from database.models import User


class Role(str, Enum):
    """User roles for RBAC."""

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


# Role hierarchy: admin > moderator > user
ROLE_HIERARCHY = {
    Role.ADMIN: 3,
    Role.MODERATOR: 2,
    Role.USER: 1,
}


def has_permission(user: User, required_role: Union[Role, str]) -> bool:
    """
    Check if user has permission based on role hierarchy.

    Args:
        user: The user to check
        required_role: The minimum required role

    Returns:
        True if user has sufficient permission, False otherwise

    Examples:
        >>> admin_user = User(role="admin")
        >>> has_permission(admin_user, Role.USER)
        True
        >>> has_permission(admin_user, Role.ADMIN)
        True
        >>> user = User(role="user")
        >>> has_permission(user, Role.ADMIN)
        False
    """
    if isinstance(required_role, str):
        required_role = Role(required_role)

    # Get user role (fallback to USER if not set)
    user_role_str = getattr(user, "role", "user")
    user_role = Role(user_role_str)

    # Check hierarchy
    user_level = ROLE_HIERARCHY.get(user_role, 1)
    required_level = ROLE_HIERARCHY.get(required_role, 1)

    return user_level >= required_level


def require_role(
    *roles: Union[Role, str],
    allow_self: bool = False
) -> Callable:
    """
    Decorator to require specific role(s) for a route.

    Args:
        *roles: One or more roles that can access the route
        allow_self: If True, user can access their own resources regardless of role

    Returns:
        Decorator function

    Examples:
        @router.get("/admin/dashboard")
        @require_role(Role.ADMIN)
        async def admin_dashboard(current_user: User = Depends(get_current_user)):
            ...

        @router.get("/users/{user_id}")
        @require_role(Role.MODERATOR, allow_self=True)
        async def get_user(user_id: int, current_user: User = Depends(get_current_user)):
            # Moderators can see any user, users can see themselves
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get("current_user")

            if current_user is None:
                # Try to find in args (less common)
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break

            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check if user has any of the required roles
            has_required_role = any(
                has_permission(current_user, role) for role in roles
            )

            if not has_required_role:
                # Check allow_self exception
                if allow_self:
                    # Try to extract resource user_id from kwargs or path params
                    resource_user_id = kwargs.get("user_id")

                    if resource_user_id and int(resource_user_id) == current_user.id:
                        # User is accessing their own resource
                        return await func(*args, **kwargs)

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of the following roles: {', '.join(str(r) for r in roles)}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def is_admin(user: User) -> bool:
    """
    Check if user is an admin.

    Args:
        user: The user to check

    Returns:
        True if user is admin, False otherwise
    """
    return has_permission(user, Role.ADMIN)


def is_moderator_or_above(user: User) -> bool:
    """
    Check if user is a moderator or admin.

    Args:
        user: The user to check

    Returns:
        True if user is moderator or admin, False otherwise
    """
    return has_permission(user, Role.MODERATOR)


def check_permission_or_raise(
    user: User,
    required_role: Union[Role, str],
    custom_message: str = None
) -> None:
    """
    Check permission and raise HTTPException if insufficient.

    Args:
        user: The user to check
        required_role: The minimum required role
        custom_message: Optional custom error message

    Raises:
        HTTPException: If user doesn't have permission
    """
    if not has_permission(user, required_role):
        message = custom_message or f"Requires {required_role} role or higher"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )


def filter_by_role(
    user: User,
    *,
    admin_action: Callable = None,
    moderator_action: Callable = None,
    user_action: Callable = None,
) -> any:
    """
    Execute different actions based on user role.

    Args:
        user: The user to check
        admin_action: Action for admin users
        moderator_action: Action for moderator users
        user_action: Action for regular users

    Returns:
        Result of the appropriate action

    Example:
        result = filter_by_role(
            current_user,
            admin_action=lambda: get_all_users(),
            moderator_action=lambda: get_active_users(),
            user_action=lambda: get_user(current_user.id),
        )
    """
    user_role = Role(getattr(user, "role", "user"))

    if user_role == Role.ADMIN and admin_action:
        return admin_action()
    elif user_role == Role.MODERATOR and moderator_action:
        return moderator_action()
    elif user_action:
        return user_action()

    return None
