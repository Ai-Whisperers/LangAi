"""
Role-Based Access Control (RBAC) - Authorization management.

Provides:
- Role definitions and hierarchy
- Permission management
- User-role assignments
- Access control checks
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set


class PermissionAction(str, Enum):
    """Standard permission actions."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class Permission:
    """
    A permission definition.

    Format: action:resource (e.g., "read:research", "write:notes")
    """
    name: str
    description: str = ""
    resource: str = "*"
    action: str = "read"
    conditions: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_string(cls, permission_str: str) -> "Permission":
        """Parse permission from string format."""
        parts = permission_str.split(":")
        if len(parts) == 2:
            return cls(
                name=permission_str,
                action=parts[0],
                resource=parts[1]
            )
        return cls(name=permission_str)

    def matches(self, required: "Permission") -> bool:
        """Check if this permission matches the required permission."""
        # Wildcard matches everything
        if self.name == "*" or self.resource == "*":
            return True

        # Exact match
        if self.name == required.name:
            return True

        # Action:resource match
        if self.action == required.action and self.resource == required.resource:
            return True

        # Resource wildcard (e.g., "read:*" matches "read:anything")
        if self.action == required.action and self.resource == "*":
            return True

        return False


@dataclass
class Role:
    """
    A role with associated permissions.

    Roles can inherit from parent roles.
    """
    name: str
    description: str = ""
    permissions: Set[str] = field(default_factory=set)
    parent_roles: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_permission(self, permission: str) -> None:
        """Add a permission to this role."""
        self.permissions.add(permission)

    def remove_permission(self, permission: str) -> None:
        """Remove a permission from this role."""
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        """Check if role has permission (direct only)."""
        return permission in self.permissions or "*" in self.permissions


@dataclass
class User:
    """
    A user with assigned roles.
    """
    id: str
    username: str
    roles: Set[str] = field(default_factory=set)
    direct_permissions: Set[str] = field(default_factory=set)
    attributes: Dict[str, Any] = field(default_factory=dict)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_role(self, role: str) -> None:
        """Assign a role to user."""
        self.roles.add(role)

    def remove_role(self, role: str) -> None:
        """Remove a role from user."""
        self.roles.discard(role)

    def add_permission(self, permission: str) -> None:
        """Add direct permission to user."""
        self.direct_permissions.add(permission)


class RBACManager:
    """
    Role-Based Access Control manager.

    Usage:
        rbac = RBACManager()

        # Define roles
        rbac.add_role("viewer", permissions=["read:research"])
        rbac.add_role("analyst", permissions=["read:research", "write:notes"], parent_roles=["viewer"])
        rbac.add_role("admin", permissions=["*"])

        # Create user
        user = rbac.create_user("user123", "john", roles=["analyst"])

        # Check permissions
        if rbac.has_permission(user, "read:research"):
            # allow access

        # Use decorator
        @rbac.require_permission("write:notes")
        def save_notes(user, notes):
            ...
    """

    def __init__(self):
        self._roles: Dict[str, Role] = {}
        self._users: Dict[str, User] = {}
        self._permission_cache: Dict[str, Set[str]] = {}

    def add_role(
        self,
        name: str,
        permissions: List[str] = None,
        parent_roles: List[str] = None,
        description: str = ""
    ) -> Role:
        """
        Add a role definition.

        Args:
            name: Role name
            permissions: List of permission strings
            parent_roles: Roles to inherit from
            description: Role description

        Returns:
            Created Role
        """
        role = Role(
            name=name,
            description=description,
            permissions=set(permissions or []),
            parent_roles=parent_roles or []
        )
        self._roles[name] = role
        self._invalidate_cache()
        return role

    def get_role(self, name: str) -> Optional[Role]:
        """Get role by name."""
        return self._roles.get(name)

    def remove_role(self, name: str) -> bool:
        """Remove a role."""
        if name in self._roles:
            del self._roles[name]
            self._invalidate_cache()
            return True
        return False

    def create_user(
        self,
        user_id: str,
        username: str,
        roles: List[str] = None,
        permissions: List[str] = None
    ) -> User:
        """
        Create a user.

        Args:
            user_id: User identifier
            username: Username
            roles: List of role names
            permissions: Direct permissions

        Returns:
            Created User
        """
        user = User(
            id=user_id,
            username=username,
            roles=set(roles or []),
            direct_permissions=set(permissions or [])
        )
        self._users[user_id] = user
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(user_id)

    def assign_role(self, user_id: str, role: str) -> bool:
        """Assign a role to a user."""
        user = self._users.get(user_id)
        if user and role in self._roles:
            user.add_role(role)
            return True
        return False

    def revoke_role(self, user_id: str, role: str) -> bool:
        """Revoke a role from a user."""
        user = self._users.get(user_id)
        if user:
            user.remove_role(role)
            return True
        return False

    def get_user_permissions(self, user: User) -> Set[str]:
        """
        Get all permissions for a user (including inherited).

        Args:
            user: User object

        Returns:
            Set of permission strings
        """
        cache_key = f"{user.id}:{','.join(sorted(user.roles))}"
        if cache_key in self._permission_cache:
            return self._permission_cache[cache_key].copy()

        permissions = user.direct_permissions.copy()

        # Collect permissions from all roles
        for role_name in user.roles:
            permissions.update(self._get_role_permissions(role_name))

        self._permission_cache[cache_key] = permissions
        return permissions.copy()

    def _get_role_permissions(self, role_name: str, visited: Set[str] = None) -> Set[str]:
        """Get all permissions for a role including inherited."""
        if visited is None:
            visited = set()

        if role_name in visited:
            return set()  # Prevent circular inheritance

        visited.add(role_name)

        role = self._roles.get(role_name)
        if not role:
            return set()

        permissions = role.permissions.copy()

        # Inherit from parent roles
        for parent_name in role.parent_roles:
            permissions.update(self._get_role_permissions(parent_name, visited))

        return permissions

    def has_permission(
        self,
        user: User,
        permission: str,
        resource: Any = None
    ) -> bool:
        """
        Check if user has a specific permission.

        Args:
            user: User to check
            permission: Permission string (e.g., "read:research")
            resource: Optional resource for condition checking

        Returns:
            True if user has permission
        """
        if not user.active:
            return False

        user_permissions = self.get_user_permissions(user)

        # Check for wildcard
        if "*" in user_permissions:
            return True

        # Direct match
        if permission in user_permissions:
            return True

        # Parse permission and check wildcards
        required = Permission.from_string(permission)
        for perm_str in user_permissions:
            user_perm = Permission.from_string(perm_str)
            if user_perm.matches(required):
                return True

        return False

    def has_role(self, user: User, role: str) -> bool:
        """Check if user has a specific role."""
        return role in user.roles

    def has_any_role(self, user: User, roles: List[str]) -> bool:
        """Check if user has any of the specified roles."""
        return bool(user.roles.intersection(roles))

    def has_all_roles(self, user: User, roles: List[str]) -> bool:
        """Check if user has all of the specified roles."""
        return set(roles).issubset(user.roles)

    def require_permission(
        self,
        permission: str
    ) -> Callable:
        """
        Decorator to require a permission for a function.

        The decorated function must receive a 'user' argument.

        Usage:
            @rbac.require_permission("write:notes")
            def save_notes(user: User, notes: str):
                ...
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                # Find user in args or kwargs
                user = kwargs.get('user')
                if user is None and args:
                    for arg in args:
                        if isinstance(arg, User):
                            user = arg
                            break

                if user is None:
                    raise ValueError("User not provided to permission-protected function")

                if not self.has_permission(user, permission):
                    raise PermissionError(f"Permission denied: {permission}")

                return func(*args, **kwargs)
            return wrapper
        return decorator

    def require_role(
        self,
        role: str
    ) -> Callable:
        """
        Decorator to require a role for a function.

        Usage:
            @rbac.require_role("admin")
            def admin_action(user: User):
                ...
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                user = kwargs.get('user')
                if user is None and args:
                    for arg in args:
                        if isinstance(arg, User):
                            user = arg
                            break

                if user is None:
                    raise ValueError("User not provided to role-protected function")

                if not self.has_role(user, role):
                    raise PermissionError(f"Role required: {role}")

                return func(*args, **kwargs)
            return wrapper
        return decorator

    def _invalidate_cache(self) -> None:
        """Invalidate permission cache."""
        self._permission_cache.clear()


# Predefined roles for company research


def create_default_roles(rbac: RBACManager) -> None:
    """Create default roles for company research."""
    rbac.add_role(
        "viewer",
        permissions=["read:research", "read:reports"],
        description="Can view research and reports"
    )

    rbac.add_role(
        "analyst",
        permissions=["write:notes", "write:reports", "execute:research"],
        parent_roles=["viewer"],
        description="Can conduct research and create reports"
    )

    rbac.add_role(
        "editor",
        permissions=["update:research", "update:reports", "delete:notes"],
        parent_roles=["analyst"],
        description="Can edit and manage research"
    )

    rbac.add_role(
        "admin",
        permissions=["*"],
        description="Full access to all resources"
    )


# Convenience functions


def create_rbac_manager(with_defaults: bool = True) -> RBACManager:
    """Create an RBAC manager with optional default roles."""
    rbac = RBACManager()
    if with_defaults:
        create_default_roles(rbac)
    return rbac


def check_permission(
    user: User,
    permission: str,
    rbac: RBACManager
) -> bool:
    """Quick permission check."""
    return rbac.has_permission(user, permission)
