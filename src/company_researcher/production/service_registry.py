"""
Service Registry - Service discovery and registration.

Provides:
- Service registration
- Service discovery
- Health-aware routing
- Load balancing
"""

import asyncio
import random
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class ServiceStatus(str, Enum):
    """Status of a service instance."""
    UP = "up"
    DOWN = "down"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class LoadBalanceStrategy(str, Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"


@dataclass
class ServiceInstance:
    """A registered service instance."""
    id: str
    service_name: str
    host: str
    port: int
    status: ServiceStatus = ServiceStatus.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    registered_at: datetime = field(default_factory=_utcnow)
    last_heartbeat: datetime = field(default_factory=_utcnow)
    connections: int = 0

    @property
    def address(self) -> str:
        """Get service address."""
        return f"{self.host}:{self.port}"

    @property
    def url(self) -> str:
        """Get service URL."""
        protocol = self.metadata.get("protocol", "http")
        return f"{protocol}://{self.host}:{self.port}"

    def is_healthy(self, timeout_seconds: float = 30) -> bool:
        """Check if instance is healthy based on heartbeat."""
        if self.status != ServiceStatus.UP:
            return False
        age = (_utcnow() - self.last_heartbeat).total_seconds()
        return age < timeout_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "service_name": self.service_name,
            "host": self.host,
            "port": self.port,
            "status": self.status.value,
            "metadata": self.metadata,
            "weight": self.weight,
            "registered_at": self.registered_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "connections": self.connections
        }


class ServiceRegistry:
    """
    Service registry for service discovery.

    Usage:
        registry = ServiceRegistry()

        # Register service
        registry.register(
            service_name="research-api",
            host="localhost",
            port=8000,
            metadata={"version": "1.0.0"}
        )

        # Discover services
        instances = registry.get_instances("research-api")

        # Get instance with load balancing
        instance = registry.get_instance("research-api")

        # Deregister
        registry.deregister(instance_id)
    """

    def __init__(
        self,
        heartbeat_timeout: float = 30,
        cleanup_interval: float = 60,
        load_balance_strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN
    ):
        self.heartbeat_timeout = heartbeat_timeout
        self.cleanup_interval = cleanup_interval
        self.load_balance_strategy = load_balance_strategy
        self._instances: Dict[str, ServiceInstance] = {}
        self._services: Dict[str, List[str]] = {}  # service_name -> instance_ids
        self._round_robin_index: Dict[str, int] = {}
        self._lock = threading.RLock()
        self._running = False
        self._cleanup_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the registry (cleanup thread)."""
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def stop(self) -> None:
        """Stop the registry."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)

    def _cleanup_loop(self) -> None:
        """Background cleanup of unhealthy instances."""
        while self._running:
            time.sleep(self.cleanup_interval)
            self._cleanup_unhealthy()

    def _cleanup_unhealthy(self) -> None:
        """Remove unhealthy instances."""
        with self._lock:
            unhealthy = [
                instance_id for instance_id, instance in self._instances.items()
                if not instance.is_healthy(self.heartbeat_timeout)
            ]
            for instance_id in unhealthy:
                self._deregister_internal(instance_id)

    def register(
        self,
        service_name: str,
        host: str,
        port: int,
        instance_id: str = None,
        metadata: Dict[str, Any] = None,
        weight: float = 1.0
    ) -> ServiceInstance:
        """
        Register a service instance.

        Args:
            service_name: Name of the service
            host: Host address
            port: Port number
            instance_id: Custom instance ID (auto-generated if not provided)
            metadata: Instance metadata
            weight: Weight for load balancing

        Returns:
            Registered ServiceInstance
        """
        import uuid

        with self._lock:
            iid = instance_id or str(uuid.uuid4())[:8]

            instance = ServiceInstance(
                id=iid,
                service_name=service_name,
                host=host,
                port=port,
                status=ServiceStatus.UP,
                metadata=metadata or {},
                weight=weight
            )

            self._instances[iid] = instance

            if service_name not in self._services:
                self._services[service_name] = []
            if iid not in self._services[service_name]:
                self._services[service_name].append(iid)

            return instance

    def deregister(self, instance_id: str) -> bool:
        """Deregister a service instance."""
        with self._lock:
            return self._deregister_internal(instance_id)

    def _deregister_internal(self, instance_id: str) -> bool:
        """Internal deregistration (no lock)."""
        if instance_id not in self._instances:
            return False

        instance = self._instances[instance_id]
        service_name = instance.service_name

        del self._instances[instance_id]

        if service_name in self._services:
            if instance_id in self._services[service_name]:
                self._services[service_name].remove(instance_id)

        return True

    def heartbeat(self, instance_id: str) -> bool:
        """Send heartbeat for an instance."""
        with self._lock:
            if instance_id in self._instances:
                self._instances[instance_id].last_heartbeat = _utcnow()
                return True
            return False

    def update_status(self, instance_id: str, status: ServiceStatus) -> bool:
        """Update instance status."""
        with self._lock:
            if instance_id in self._instances:
                self._instances[instance_id].status = status
                return True
            return False

    def get_instances(
        self,
        service_name: str,
        healthy_only: bool = True
    ) -> List[ServiceInstance]:
        """
        Get all instances of a service.

        Args:
            service_name: Name of the service
            healthy_only: Only return healthy instances

        Returns:
            List of ServiceInstance objects
        """
        with self._lock:
            instance_ids = self._services.get(service_name, [])
            instances = [self._instances[iid] for iid in instance_ids if iid in self._instances]

            if healthy_only:
                instances = [i for i in instances if i.is_healthy(self.heartbeat_timeout)]

            return instances

    def get_instance(
        self,
        service_name: str,
        strategy: LoadBalanceStrategy = None
    ) -> Optional[ServiceInstance]:
        """
        Get a single instance using load balancing.

        Args:
            service_name: Name of the service
            strategy: Load balancing strategy (uses default if not specified)

        Returns:
            Selected ServiceInstance or None
        """
        instances = self.get_instances(service_name, healthy_only=True)
        if not instances:
            return None

        strategy = strategy or self.load_balance_strategy

        if strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin_select(service_name, instances)
        elif strategy == LoadBalanceStrategy.RANDOM:
            return random.choice(instances)
        elif strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return min(instances, key=lambda i: i.connections)
        elif strategy == LoadBalanceStrategy.WEIGHTED:
            return self._weighted_select(instances)

        return instances[0]

    def _round_robin_select(
        self,
        service_name: str,
        instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """Round-robin selection."""
        with self._lock:
            index = self._round_robin_index.get(service_name, 0)
            instance = instances[index % len(instances)]
            self._round_robin_index[service_name] = index + 1
            return instance

    def _weighted_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted random selection."""
        total_weight = sum(i.weight for i in instances)
        r = random.uniform(0, total_weight)

        cumulative = 0
        for instance in instances:
            cumulative += instance.weight
            if r <= cumulative:
                return instance

        return instances[-1]

    def get_service_names(self) -> List[str]:
        """Get all registered service names."""
        with self._lock:
            return list(self._services.keys())

    def get_all_instances(self) -> Dict[str, List[ServiceInstance]]:
        """Get all instances grouped by service."""
        with self._lock:
            result = {}
            for service_name, instance_ids in self._services.items():
                result[service_name] = [
                    self._instances[iid] for iid in instance_ids
                    if iid in self._instances
                ]
            return result

    def to_dict(self) -> Dict[str, Any]:
        """Export registry state."""
        with self._lock:
            return {
                "services": {
                    name: [self._instances[iid].to_dict() for iid in ids if iid in self._instances]
                    for name, ids in self._services.items()
                }
            }


class ServiceClient:
    """
    Client for interacting with registered services.

    Usage:
        client = ServiceClient(registry)

        # Get service URL
        url = client.get_url("research-api")

        # Call with automatic discovery
        result = await client.call("research-api", "/health")
    """

    def __init__(
        self,
        registry: ServiceRegistry,
        timeout: float = 30.0
    ):
        self.registry = registry
        self.timeout = timeout

    def get_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """Get an instance for a service."""
        return self.registry.get_instance(service_name)

    def get_url(self, service_name: str) -> Optional[str]:
        """Get URL for a service instance."""
        instance = self.get_instance(service_name)
        return instance.url if instance else None

    async def call(
        self,
        service_name: str,
        path: str,
        method: str = "GET",
        **kwargs
    ) -> Any:
        """
        Call a service endpoint.

        Args:
            service_name: Service to call
            path: Endpoint path
            method: HTTP method
            **kwargs: Request arguments

        Returns:
            Response data
        """
        import urllib.request
        import json

        instance = self.get_instance(service_name)
        if not instance:
            raise ValueError(f"No healthy instance found for {service_name}")

        url = f"{instance.url}{path}"

        def _blocking_request():
            """Blocking HTTP request to run in executor."""
            request = urllib.request.Request(url, method=method)
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read())

        try:
            instance.connections += 1

            # Run blocking I/O in thread pool to avoid blocking event loop
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _blocking_request)

        finally:
            instance.connections -= 1


# Convenience functions


def create_service_registry(
    heartbeat_timeout: float = 30,
    strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN
) -> ServiceRegistry:
    """Create a service registry."""
    registry = ServiceRegistry(
        heartbeat_timeout=heartbeat_timeout,
        load_balance_strategy=strategy
    )
    registry.start()
    return registry
