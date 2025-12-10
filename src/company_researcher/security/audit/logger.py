"""
Audit Logger Implementation.

This module contains the AuditLogger class for security and compliance logging.
"""

import logging
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List

from .models import (
    _utcnow,
    AuditEventType,
    AuditSeverity,
    AuditEntry,
    AuditConfig,
)


class AuditLogger:
    """
    Audit logging for security and compliance.

    Usage:
        audit = AuditLogger(log_file="audit.log")

        # Log authentication
        audit.log_auth(user_id="user123", event=AuditEventType.LOGIN)

        # Log data access
        audit.log_data_access(
            user_id="user123",
            action="read",
            resource="research",
            resource_id="Tesla"
        )

        # Log with decorator
        @audit.audited(event_type=AuditEventType.DATA_READ)
        def get_research(user_id, company):
            ...

        # Query logs
        entries = audit.query(user_id="user123", event_type=AuditEventType.LOGIN)
    """

    def __init__(
        self,
        config: AuditConfig = None,
        log_file: str = None
    ):
        self.config = config or AuditConfig(log_file=log_file)
        self._entries: List[AuditEntry] = []
        self._lock = threading.RLock()
        self._handlers: List[Callable[[AuditEntry], None]] = []
        self._logger = logging.getLogger("audit")

        if self.config.log_file:
            self._setup_file_handler()

        if self.config.log_to_console:
            self._setup_console_handler()

    def _setup_file_handler(self) -> None:
        """Setup file handler for audit logs."""
        log_path = Path(self.config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(str(log_path))
        handler.setFormatter(logging.Formatter('%(message)s'))
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.DEBUG)

    def _setup_console_handler(self) -> None:
        """Setup console handler for audit logs."""
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '[AUDIT] %(message)s'
        ))
        self._logger.addHandler(handler)

    def log(
        self,
        event_type: AuditEventType,
        user_id: str = None,
        action: str = "",
        resource: str = "",
        resource_id: str = None,
        outcome: str = "success",
        severity: AuditSeverity = AuditSeverity.INFO,
        details: Dict[str, Any] = None,
        **kwargs
    ) -> AuditEntry:
        """
        Log an audit event.

        Args:
            event_type: Type of event
            user_id: User who performed the action
            action: Action performed
            resource: Resource type affected
            resource_id: Specific resource identifier
            outcome: success, failure, or error
            severity: Event severity
            details: Additional details
            **kwargs: Additional fields (ip_address, user_agent, etc.)

        Returns:
            Created AuditEntry
        """
        if not self.config.enabled:
            return None

        entry = AuditEntry(
            id=str(uuid.uuid4()),
            timestamp=_utcnow(),
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            outcome=outcome,
            details=details or {},
            **kwargs
        )

        self._store_entry(entry)
        self._notify_handlers(entry)

        return entry

    def _store_entry(self, entry: AuditEntry) -> None:
        """Store entry in memory and file."""
        with self._lock:
            self._entries.append(entry)

            # Enforce max entries
            if len(self._entries) > self.config.max_entries:
                self._entries = self._entries[-self.config.max_entries:]

        # Log to file
        if self.config.log_file:
            self._logger.info(entry.to_json())

    def _notify_handlers(self, entry: AuditEntry) -> None:
        """Notify registered handlers."""
        for handler in self._handlers:
            try:
                handler(entry)
            except Exception as e:
                # Log but don't let handler errors break audit logging
                self._logger.warning(f"Audit handler error: {e}")

    def add_handler(self, handler: Callable[[AuditEntry], None]) -> None:
        """Add a custom audit handler."""
        self._handlers.append(handler)

    # Convenience logging methods

    def log_auth(
        self,
        user_id: str,
        event: AuditEventType,
        outcome: str = "success",
        **kwargs
    ) -> AuditEntry:
        """Log authentication event."""
        severity = AuditSeverity.INFO if outcome == "success" else AuditSeverity.WARNING
        return self.log(
            event_type=event,
            user_id=user_id,
            action=event.value.split(".")[-1],
            resource="auth",
            outcome=outcome,
            severity=severity,
            **kwargs
        )

    def log_data_access(
        self,
        user_id: str,
        action: str,
        resource: str,
        resource_id: str = None,
        outcome: str = "success",
        **kwargs
    ) -> AuditEntry:
        """Log data access event."""
        event_map = {
            "read": AuditEventType.DATA_READ,
            "create": AuditEventType.DATA_CREATE,
            "update": AuditEventType.DATA_UPDATE,
            "delete": AuditEventType.DATA_DELETE,
            "export": AuditEventType.DATA_EXPORT
        }
        event_type = event_map.get(action.lower(), AuditEventType.DATA_READ)

        return self.log(
            event_type=event_type,
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            outcome=outcome,
            **kwargs
        )

    def log_research(
        self,
        user_id: str,
        company: str,
        event: AuditEventType,
        outcome: str = "success",
        **kwargs
    ) -> AuditEntry:
        """Log research operation."""
        return self.log(
            event_type=event,
            user_id=user_id,
            action=event.value.split(".")[-1],
            resource="research",
            resource_id=company,
            outcome=outcome,
            **kwargs
        )

    def log_security(
        self,
        event: AuditEventType,
        severity: AuditSeverity = AuditSeverity.WARNING,
        user_id: str = None,
        **kwargs
    ) -> AuditEntry:
        """Log security event."""
        return self.log(
            event_type=event,
            severity=severity,
            user_id=user_id,
            resource="security",
            **kwargs
        )

    # Query methods

    def query(
        self,
        user_id: str = None,
        event_type: AuditEventType = None,
        resource: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        severity: AuditSeverity = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """
        Query audit logs.

        Args:
            user_id: Filter by user
            event_type: Filter by event type
            resource: Filter by resource
            start_time: Filter by start time
            end_time: Filter by end time
            severity: Filter by minimum severity
            limit: Maximum entries to return

        Returns:
            List of matching AuditEntry objects
        """
        with self._lock:
            results = []
            severity_order = list(AuditSeverity)

            for entry in reversed(self._entries):
                if len(results) >= limit:
                    break

                if user_id and entry.user_id != user_id:
                    continue
                if event_type and entry.event_type != event_type:
                    continue
                if resource and entry.resource != resource:
                    continue
                if start_time and entry.timestamp < start_time:
                    continue
                if end_time and entry.timestamp > end_time:
                    continue
                if severity:
                    if severity_order.index(entry.severity) < severity_order.index(severity):
                        continue

                results.append(entry)

            return results

    def get_user_activity(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[AuditEntry]:
        """Get activity for a specific user."""
        return self.query(user_id=user_id, limit=limit)

    def get_recent(self, limit: int = 100) -> List[AuditEntry]:
        """Get most recent audit entries."""
        with self._lock:
            return list(reversed(self._entries[-limit:]))

    def export(self, filepath: str) -> int:
        """Export audit logs to file."""
        with self._lock:
            with open(filepath, 'w') as f:
                for entry in self._entries:
                    f.write(entry.to_json() + "\n")
            return len(self._entries)

    # Decorator

    def audited(
        self,
        event_type: AuditEventType,
        resource: str = None,
        include_args: bool = False
    ) -> Callable:
        """
        Decorator to automatically audit function calls.

        Usage:
            @audit.audited(event_type=AuditEventType.DATA_READ)
            def get_data(user_id, company):
                ...
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                user_id = kwargs.get('user_id') or (args[0] if args else None)
                details = {}

                if include_args:
                    details['args'] = str(args)
                    details['kwargs'] = str(kwargs)

                try:
                    result = func(*args, **kwargs)
                    self.log(
                        event_type=event_type,
                        user_id=str(user_id) if user_id else None,
                        action=func.__name__,
                        resource=resource or func.__name__,
                        outcome="success",
                        details=details
                    )
                    return result
                except Exception as e:
                    details['error'] = str(e)
                    self.log(
                        event_type=event_type,
                        user_id=str(user_id) if user_id else None,
                        action=func.__name__,
                        resource=resource or func.__name__,
                        outcome="error",
                        severity=AuditSeverity.ERROR,
                        details=details
                    )
                    raise

            return wrapper
        return decorator
