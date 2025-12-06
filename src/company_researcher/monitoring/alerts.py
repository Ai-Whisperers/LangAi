"""
Alert Manager (Phase 19.5).

Alert management system:
- Alert rules
- Alert triggering
- Notification channels
- Alert history
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import logging


# ============================================================================
# Enums and Data Models
# ============================================================================

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"


class AlertCondition(str, Enum):
    """Alert condition types."""
    THRESHOLD = "threshold"        # Value exceeds threshold
    RATE = "rate"                  # Rate of change
    ABSENCE = "absence"            # No data received
    PATTERN = "pattern"            # Pattern detected


@dataclass
class AlertRule:
    """Definition of an alert rule."""
    rule_id: str
    name: str
    metric: str
    condition: AlertCondition
    threshold: float
    severity: AlertSeverity = AlertSeverity.WARNING
    duration_seconds: int = 60  # How long condition must persist
    cooldown_seconds: int = 300  # Minimum time between alerts
    description: str = ""
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "metric": self.metric,
            "condition": self.condition.value,
            "threshold": self.threshold,
            "severity": self.severity.value,
            "duration_seconds": self.duration_seconds,
            "enabled": self.enabled
        }


@dataclass
class Alert:
    """An active or historical alert."""
    alert_id: str
    rule_id: str
    name: str
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.ACTIVE
    message: str = ""
    value: float = 0.0
    threshold: float = 0.0
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "rule_id": self.rule_id,
            "name": self.name,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "value": round(self.value, 4),
            "threshold": self.threshold,
            "triggered_at": self.triggered_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }


# ============================================================================
# Alert Manager
# ============================================================================

class AlertManager:
    """
    Manage alerts and notifications.

    Features:
    - Rule-based alert triggering
    - Multiple notification channels
    - Alert acknowledgment and resolution
    - Alert history

    Usage:
        manager = AlertManager()

        # Define alert rules
        manager.add_rule(AlertRule(
            rule_id="high_cost",
            name="High Cost Alert",
            metric="cost.daily",
            condition=AlertCondition.THRESHOLD,
            threshold=10.0,
            severity=AlertSeverity.WARNING
        ))

        # Check metric values
        manager.check_metric("cost.daily", 15.0)

        # Get active alerts
        alerts = manager.get_active_alerts()
    """

    def __init__(self):
        """Initialize alert manager."""
        self._rules: Dict[str, AlertRule] = {}
        self._alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []

        # Track last alert time per rule (for cooldown)
        self._last_alert_time: Dict[str, datetime] = {}

        # Track metric values for duration checking
        self._metric_values: Dict[str, List[tuple]] = {}

        # Notification handlers
        self._notification_handlers: List[Callable[[Alert], None]] = []

        # Thread safety
        self._lock = threading.RLock()

        # Logger
        self._logger = logging.getLogger("alerts")

        # Alert counter
        self._alert_counter = 0

        # Initialize default rules
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """Initialize default alert rules."""
        default_rules = [
            AlertRule(
                rule_id="high_failure_rate",
                name="High Failure Rate",
                metric="research.failure_rate",
                condition=AlertCondition.THRESHOLD,
                threshold=0.2,  # 20% failure rate
                severity=AlertSeverity.ERROR,
                description="Research failure rate exceeds 20%"
            ),
            AlertRule(
                rule_id="high_daily_cost",
                name="High Daily Cost",
                metric="cost.daily",
                condition=AlertCondition.THRESHOLD,
                threshold=10.0,  # $10/day
                severity=AlertSeverity.WARNING,
                description="Daily cost exceeds $10"
            ),
            AlertRule(
                rule_id="slow_response",
                name="Slow Response Time",
                metric="latency.p95",
                condition=AlertCondition.THRESHOLD,
                threshold=30.0,  # 30 seconds
                severity=AlertSeverity.WARNING,
                description="P95 latency exceeds 30 seconds"
            ),
            AlertRule(
                rule_id="api_errors",
                name="API Error Rate",
                metric="api.error_rate",
                condition=AlertCondition.THRESHOLD,
                threshold=0.05,  # 5% error rate
                severity=AlertSeverity.ERROR,
                description="API error rate exceeds 5%"
            )
        ]

        for rule in default_rules:
            self._rules[rule.rule_id] = rule

    # ==========================================================================
    # Rule Management
    # ==========================================================================

    def add_rule(self, rule: AlertRule):
        """Add or update an alert rule."""
        with self._lock:
            self._rules[rule.rule_id] = rule
            self._logger.info(f"Added alert rule: {rule.name}")

    def remove_rule(self, rule_id: str):
        """Remove an alert rule."""
        with self._lock:
            if rule_id in self._rules:
                del self._rules[rule_id]
                self._logger.info(f"Removed alert rule: {rule_id}")

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get an alert rule by ID."""
        return self._rules.get(rule_id)

    def get_all_rules(self) -> List[AlertRule]:
        """Get all alert rules."""
        return list(self._rules.values())

    def enable_rule(self, rule_id: str):
        """Enable an alert rule."""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = True

    def disable_rule(self, rule_id: str):
        """Disable an alert rule."""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = False

    # ==========================================================================
    # Metric Checking
    # ==========================================================================

    def check_metric(
        self,
        metric: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Check a metric value against all applicable rules.

        Args:
            metric: Metric name
            value: Current metric value
            metadata: Additional context
        """
        with self._lock:
            # Store value
            now = datetime.now()
            if metric not in self._metric_values:
                self._metric_values[metric] = []
            self._metric_values[metric].append((now, value))

            # Trim old values (keep last hour)
            cutoff = now - timedelta(hours=1)
            self._metric_values[metric] = [
                (ts, v) for ts, v in self._metric_values[metric]
                if ts > cutoff
            ]

            # Check rules
            for rule in self._rules.values():
                if rule.metric == metric and rule.enabled:
                    self._evaluate_rule(rule, value, metadata)

    def _evaluate_rule(
        self,
        rule: AlertRule,
        value: float,
        metadata: Optional[Dict[str, Any]]
    ):
        """Evaluate a rule against a value."""
        triggered = False

        if rule.condition == AlertCondition.THRESHOLD:
            triggered = value > rule.threshold

        elif rule.condition == AlertCondition.RATE:
            # Check rate of change
            values = self._metric_values.get(rule.metric, [])
            if len(values) >= 2:
                old_value = values[0][1]
                rate = (value - old_value) / old_value if old_value else 0
                triggered = abs(rate) > rule.threshold

        if triggered:
            self._maybe_trigger_alert(rule, value, metadata)
        else:
            # Auto-resolve if condition no longer met
            self._maybe_resolve_alert(rule.rule_id)

    def _maybe_trigger_alert(
        self,
        rule: AlertRule,
        value: float,
        metadata: Optional[Dict[str, Any]]
    ):
        """Trigger alert if cooldown allows."""
        now = datetime.now()

        # Check cooldown
        last_time = self._last_alert_time.get(rule.rule_id)
        if last_time:
            cooldown = timedelta(seconds=rule.cooldown_seconds)
            if now - last_time < cooldown:
                return

        # Check if already active
        active_alert = self._get_active_alert_for_rule(rule.rule_id)
        if active_alert:
            return

        # Create alert
        self._alert_counter += 1
        alert_id = f"alert_{int(now.timestamp())}_{self._alert_counter}"

        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            name=rule.name,
            severity=rule.severity,
            message=f"{rule.name}: {value:.4f} exceeds threshold {rule.threshold}",
            value=value,
            threshold=rule.threshold,
            metadata=metadata or {}
        )

        self._alerts[alert_id] = alert
        self._last_alert_time[rule.rule_id] = now

        self._logger.warning(f"Alert triggered: {alert.message}")

        # Notify handlers
        self._notify(alert)

    def _maybe_resolve_alert(self, rule_id: str):
        """Auto-resolve alert if condition no longer met."""
        alert = self._get_active_alert_for_rule(rule_id)
        if alert:
            self.resolve_alert(alert.alert_id, auto=True)

    def _get_active_alert_for_rule(self, rule_id: str) -> Optional[Alert]:
        """Get active alert for a rule."""
        for alert in self._alerts.values():
            if alert.rule_id == rule_id and alert.status == AlertStatus.ACTIVE:
                return alert
        return None

    # ==========================================================================
    # Alert Management
    # ==========================================================================

    def acknowledge_alert(self, alert_id: str, by: str = "system"):
        """Acknowledge an alert."""
        with self._lock:
            alert = self._alerts.get(alert_id)
            if alert and alert.status == AlertStatus.ACTIVE:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now()
                alert.acknowledged_by = by
                self._logger.info(f"Alert acknowledged: {alert_id} by {by}")

    def resolve_alert(self, alert_id: str, auto: bool = False):
        """Resolve an alert."""
        with self._lock:
            alert = self._alerts.get(alert_id)
            if alert and alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]:
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()

                # Move to history
                self._alert_history.append(alert)
                del self._alerts[alert_id]

                msg = "auto-resolved" if auto else "resolved"
                self._logger.info(f"Alert {msg}: {alert_id}")

    def silence_alert(self, alert_id: str, duration_minutes: int = 60):
        """Silence an alert temporarily."""
        with self._lock:
            alert = self._alerts.get(alert_id)
            if alert:
                alert.status = AlertStatus.SILENCED
                self._logger.info(f"Alert silenced: {alert_id} for {duration_minutes}m")

    def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Get all active alerts."""
        with self._lock:
            alerts = [
                a for a in self._alerts.values()
                if a.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]
            ]

            if severity:
                alerts = [a for a in alerts if a.severity == severity]

            # Sort by severity then time
            severity_order = {
                AlertSeverity.CRITICAL: 0,
                AlertSeverity.ERROR: 1,
                AlertSeverity.WARNING: 2,
                AlertSeverity.INFO: 3
            }
            alerts.sort(key=lambda a: (severity_order.get(a.severity, 4), a.triggered_at))

            return alerts

    def get_alert_history(
        self,
        limit: int = 100,
        since: Optional[datetime] = None
    ) -> List[Alert]:
        """Get alert history."""
        with self._lock:
            history = self._alert_history

            if since:
                history = [a for a in history if a.triggered_at >= since]

            return sorted(history, key=lambda a: a.triggered_at, reverse=True)[:limit]

    def get_alert_count_by_severity(self) -> Dict[str, int]:
        """Get count of active alerts by severity."""
        counts = {s.value: 0 for s in AlertSeverity}

        for alert in self._alerts.values():
            if alert.status == AlertStatus.ACTIVE:
                counts[alert.severity.value] += 1

        return counts

    # ==========================================================================
    # Notifications
    # ==========================================================================

    def add_notification_handler(self, handler: Callable[[Alert], None]):
        """Add a notification handler."""
        self._notification_handlers.append(handler)

    def _notify(self, alert: Alert):
        """Send notifications for an alert."""
        for handler in self._notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                self._logger.error(f"Notification handler error: {e}")

    # ==========================================================================
    # Export
    # ==========================================================================

    def export_json(self) -> Dict[str, Any]:
        """Export alert data as JSON."""
        return {
            "active_alerts": [a.to_dict() for a in self.get_active_alerts()],
            "alert_counts": self.get_alert_count_by_severity(),
            "rules": [r.to_dict() for r in self._rules.values()],
            "history_count": len(self._alert_history)
        }


# ============================================================================
# Factory Function
# ============================================================================

def create_alert_manager() -> AlertManager:
    """Create an alert manager instance."""
    return AlertManager()


# Global instance
_global_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Get global alert manager."""
    global _global_alert_manager
    if _global_alert_manager is None:
        _global_alert_manager = AlertManager()
    return _global_alert_manager
