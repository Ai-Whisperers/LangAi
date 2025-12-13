"""
State Versioning - Schema migrations and version management.

Provides:
- State versioning
- Migration definitions
- Version upgrades
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from ..utils import utc_now


@dataclass
class StateVersion:
    """Version information for state schema."""
    version: str
    created_at: datetime = field(default_factory=utc_now)
    description: str = ""
    schema_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "description": self.description,
            "schema_hash": self.schema_hash
        }


@dataclass
class Migration:
    """
    A migration from one version to another.

    Attributes:
        from_version: Source version
        to_version: Target version
        migrate_fn: Function to transform state
        description: Migration description
    """
    from_version: str
    to_version: str
    migrate_fn: Callable[[Dict[str, Any]], Dict[str, Any]]
    description: str = ""
    reversible: bool = False
    reverse_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None

    def apply(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Apply migration to state."""
        return self.migrate_fn(state)

    def reverse(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse migration (if reversible)."""
        if not self.reversible or not self.reverse_fn:
            raise ValueError("Migration is not reversible")
        return self.reverse_fn(state)


class VersionManager:
    """
    Manage state versions and migrations.

    Usage:
        manager = VersionManager()

        # Define migrations
        manager.add_migration(Migration(
            from_version="1.0",
            to_version="1.1",
            migrate_fn=lambda s: {**s, "new_field": "default"}
        ))

        # Migrate state
        new_state = manager.migrate(old_state, from_version="1.0", to_version="1.1")
    """

    def __init__(self, current_version: str = "1.0"):
        self.current_version = current_version
        self._migrations: Dict[str, Dict[str, Migration]] = {}  # from -> to -> migration
        self._versions: List[StateVersion] = []

    def add_version(self, version: StateVersion) -> None:
        """Add a version definition."""
        self._versions.append(version)
        self._versions.sort(key=lambda v: v.version)

    def add_migration(self, migration: Migration) -> None:
        """Add a migration."""
        if migration.from_version not in self._migrations:
            self._migrations[migration.from_version] = {}
        self._migrations[migration.from_version][migration.to_version] = migration

    def get_migration(self, from_version: str, to_version: str) -> Optional[Migration]:
        """Get a specific migration."""
        return self._migrations.get(from_version, {}).get(to_version)

    def get_migration_path(
        self,
        from_version: str,
        to_version: str
    ) -> Optional[List[Migration]]:
        """
        Find migration path between versions.

        Returns:
            List of migrations to apply, or None if no path exists
        """
        if from_version == to_version:
            return []

        # BFS to find path
        visited = {from_version}
        queue = [(from_version, [])]

        while queue:
            current, path = queue.pop(0)

            if current not in self._migrations:
                continue

            for next_version, migration in self._migrations[current].items():
                if next_version == to_version:
                    return path + [migration]

                if next_version not in visited:
                    visited.add(next_version)
                    queue.append((next_version, path + [migration]))

        return None

    def migrate(
        self,
        state: Dict[str, Any],
        from_version: str,
        to_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Migrate state from one version to another.

        Args:
            state: State to migrate
            from_version: Current state version
            to_version: Target version (defaults to current_version)

        Returns:
            Migrated state

        Raises:
            ValueError if no migration path exists
        """
        target = to_version or self.current_version

        if from_version == target:
            return state.copy()

        path = self.get_migration_path(from_version, target)
        if path is None:
            raise ValueError(f"No migration path from {from_version} to {target}")

        result = state.copy()
        for migration in path:
            result = migration.apply(result)

        # Add version metadata
        result["_version"] = target
        result["_migrated_at"] = utc_now().isoformat()

        return result

    def can_migrate(self, from_version: str, to_version: str) -> bool:
        """Check if migration is possible."""
        return self.get_migration_path(from_version, to_version) is not None

    def get_state_version(self, state: Dict[str, Any]) -> str:
        """Extract version from state."""
        return state.get("_version", "1.0")

    def ensure_current(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure state is at current version."""
        current = self.get_state_version(state)
        if current != self.current_version:
            return self.migrate(state, current, self.current_version)
        return state


# Convenience functions
def migrate_state(
    state: Dict[str, Any],
    migrations: List[Migration],
    from_version: str,
    to_version: str
) -> Dict[str, Any]:
    """
    Apply migrations to state.

    Args:
        state: State to migrate
        migrations: Available migrations
        from_version: Current version
        to_version: Target version

    Returns:
        Migrated state
    """
    manager = VersionManager(to_version)
    for migration in migrations:
        manager.add_migration(migration)

    return manager.migrate(state, from_version, to_version)


# Common migrations
def add_field_migration(
    from_version: str,
    to_version: str,
    field_name: str,
    default_value: Any,
    description: str = ""
) -> Migration:
    """Create migration that adds a field."""
    return Migration(
        from_version=from_version,
        to_version=to_version,
        migrate_fn=lambda s: {**s, field_name: default_value},
        description=description or f"Add field {field_name}",
        reversible=True,
        reverse_fn=lambda s: {k: v for k, v in s.items() if k != field_name}
    )


def rename_field_migration(
    from_version: str,
    to_version: str,
    old_name: str,
    new_name: str,
    description: str = ""
) -> Migration:
    """Create migration that renames a field."""
    def migrate(state):
        result = state.copy()
        if old_name in result:
            result[new_name] = result.pop(old_name)
        return result

    def reverse(state):
        result = state.copy()
        if new_name in result:
            result[old_name] = result.pop(new_name)
        return result

    return Migration(
        from_version=from_version,
        to_version=to_version,
        migrate_fn=migrate,
        description=description or f"Rename {old_name} to {new_name}",
        reversible=True,
        reverse_fn=reverse
    )


def remove_field_migration(
    from_version: str,
    to_version: str,
    field_name: str,
    description: str = ""
) -> Migration:
    """Create migration that removes a field."""
    return Migration(
        from_version=from_version,
        to_version=to_version,
        migrate_fn=lambda s: {k: v for k, v in s.items() if k != field_name},
        description=description or f"Remove field {field_name}",
        reversible=False
    )
