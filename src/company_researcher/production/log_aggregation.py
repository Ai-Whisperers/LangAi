"""
Log Aggregation - Centralized logging and analysis.

Provides:
- Structured logging
- Log aggregation
- Log shipping
- Log analysis
"""

import json
import logging
import queue
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """A structured log entry."""
    timestamp: datetime
    level: LogLevel
    message: str
    logger_name: str
    service: str = "company-researcher"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "@timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "logger": self.logger_name,
            "service": self.service,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            **self.extra
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_record(cls, record: logging.LogRecord, service: str = "company-researcher") -> "LogEntry":
        """Create from logging.LogRecord."""
        level_map = {
            logging.DEBUG: LogLevel.DEBUG,
            logging.INFO: LogLevel.INFO,
            logging.WARNING: LogLevel.WARNING,
            logging.ERROR: LogLevel.ERROR,
            logging.CRITICAL: LogLevel.CRITICAL,
        }

        extra = {}
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'created', 'levelname', 'levelno',
                          'pathname', 'filename', 'module', 'lineno', 'funcName',
                          'exc_info', 'exc_text', 'stack_info', 'message'):
                extra[key] = value

        return cls(
            timestamp=datetime.fromtimestamp(record.created),
            level=level_map.get(record.levelno, LogLevel.INFO),
            message=record.getMessage(),
            logger_name=record.name,
            service=service,
            trace_id=getattr(record, 'trace_id', None),
            span_id=getattr(record, 'span_id', None),
            extra=extra
        )


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, service: str = "company-researcher"):
        super().__init__()
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        """Format record as JSON."""
        entry = LogEntry.from_record(record, self.service)
        return entry.to_json()


class LogAggregator:
    """
    Aggregates logs from multiple sources.

    Usage:
        aggregator = LogAggregator()

        # Add handlers
        aggregator.add_file_handler("logs/app.log")
        aggregator.add_console_handler()

        # Ship to external service
        aggregator.add_shipper(ElasticsearchShipper(url="http://localhost:9200"))

        # Get logger
        logger = aggregator.get_logger("research")
        logger.info("Starting research", extra={"company": "Tesla"})

        # Query logs
        logs = aggregator.query(level=LogLevel.ERROR, limit=100)
    """

    def __init__(
        self,
        service_name: str = "company-researcher",
        buffer_size: int = 1000
    ):
        self.service_name = service_name
        self._buffer: List[LogEntry] = []
        self._buffer_size = buffer_size
        self._lock = threading.RLock()
        self._shippers: List["LogShipper"] = []
        self._loggers: Dict[str, logging.Logger] = {}
        self._handlers: List[logging.Handler] = []

        # Create root logger
        self._root_logger = logging.getLogger(service_name)
        self._root_logger.setLevel(logging.DEBUG)

        # In-memory handler for buffering
        self._memory_handler = _MemoryHandler(self)
        self._root_logger.addHandler(self._memory_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """Get a named logger."""
        full_name = f"{self.service_name}.{name}"
        if full_name not in self._loggers:
            logger = logging.getLogger(full_name)
            logger.setLevel(logging.DEBUG)
            self._loggers[full_name] = logger
        return self._loggers[full_name]

    def add_console_handler(self, level: LogLevel = LogLevel.INFO) -> None:
        """Add console output handler."""
        handler = logging.StreamHandler()
        handler.setLevel(getattr(logging, level.value.upper()))
        handler.setFormatter(StructuredFormatter(self.service_name))
        self._root_logger.addHandler(handler)
        self._handlers.append(handler)

    def add_file_handler(
        self,
        filepath: str,
        level: LogLevel = LogLevel.DEBUG,
        max_bytes: int = 10_000_000,
        backup_count: int = 5
    ) -> None:
        """Add file output handler with rotation."""
        from logging.handlers import RotatingFileHandler

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        handler = RotatingFileHandler(
            filepath,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        handler.setLevel(getattr(logging, level.value.upper()))
        handler.setFormatter(StructuredFormatter(self.service_name))
        self._root_logger.addHandler(handler)
        self._handlers.append(handler)

    def add_shipper(self, shipper: "LogShipper") -> None:
        """Add a log shipper."""
        shipper.start()
        self._shippers.append(shipper)

    def _handle_entry(self, entry: LogEntry) -> None:
        """Handle a new log entry."""
        with self._lock:
            self._buffer.append(entry)
            if len(self._buffer) > self._buffer_size:
                self._buffer = self._buffer[-self._buffer_size:]

        # Send to shippers
        for shipper in self._shippers:
            shipper.ship(entry)

    def query(
        self,
        level: LogLevel = None,
        logger_name: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        trace_id: str = None,
        search: str = None,
        limit: int = 100
    ) -> List[LogEntry]:
        """
        Query buffered logs.

        Args:
            level: Filter by minimum level
            logger_name: Filter by logger
            start_time: Filter by start time
            end_time: Filter by end time
            trace_id: Filter by trace ID
            search: Search in message
            limit: Maximum results

        Returns:
            List of matching LogEntry objects
        """
        level_order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]

        with self._lock:
            results = []
            for entry in reversed(self._buffer):
                if len(results) >= limit:
                    break

                if level and level_order.index(entry.level) < level_order.index(level):
                    continue
                if logger_name and entry.logger_name != logger_name:
                    continue
                if start_time and entry.timestamp < start_time:
                    continue
                if end_time and entry.timestamp > end_time:
                    continue
                if trace_id and entry.trace_id != trace_id:
                    continue
                if search and search.lower() not in entry.message.lower():
                    continue

                results.append(entry)

            return results

    def get_recent(self, limit: int = 50) -> List[LogEntry]:
        """Get most recent logs."""
        with self._lock:
            return list(reversed(self._buffer[-limit:]))

    def get_errors(self, limit: int = 50) -> List[LogEntry]:
        """Get recent errors."""
        return self.query(level=LogLevel.ERROR, limit=limit)

    def clear_buffer(self) -> None:
        """Clear the log buffer."""
        with self._lock:
            self._buffer.clear()

    def shutdown(self) -> None:
        """Shutdown aggregator and shippers."""
        for shipper in self._shippers:
            shipper.stop()
        for handler in self._handlers:
            handler.close()


class _MemoryHandler(logging.Handler):
    """Internal handler for buffering logs."""

    def __init__(self, aggregator: LogAggregator):
        super().__init__()
        self.aggregator = aggregator

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        try:
            entry = LogEntry.from_record(record, self.aggregator.service_name)
            self.aggregator._handle_entry(entry)
        except Exception:
            pass  # Don't let logging errors propagate


class LogShipper:
    """Base class for log shippers."""

    def start(self) -> None:
        """Start the shipper."""
        pass

    def stop(self) -> None:
        """Stop the shipper."""
        pass

    def ship(self, entry: LogEntry) -> None:
        """Ship a log entry."""
        raise NotImplementedError


class AsyncLogShipper(LogShipper):
    """Async log shipper with batching."""

    def __init__(
        self,
        batch_size: int = 100,
        flush_interval: float = 5.0
    ):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._queue: queue.Queue = queue.Queue()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the shipper thread."""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the shipper thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)

    def ship(self, entry: LogEntry) -> None:
        """Queue entry for shipping."""
        self._queue.put(entry)

    def _run(self) -> None:
        """Background shipping loop."""
        batch = []
        last_flush = time.time()

        while self._running:
            try:
                entry = self._queue.get(timeout=1)
                batch.append(entry)
            except queue.Empty:
                pass

            # Flush if batch is full or interval elapsed
            if len(batch) >= self.batch_size or (time.time() - last_flush) >= self.flush_interval:
                if batch:
                    self._send_batch(batch)
                    batch = []
                    last_flush = time.time()

        # Final flush
        if batch:
            self._send_batch(batch)

    def _send_batch(self, batch: List[LogEntry]) -> None:
        """Send a batch of entries. Override in subclass."""
        pass


class FileShipper(AsyncLogShipper):
    """Ships logs to a file."""

    def __init__(self, filepath: str, **kwargs):
        super().__init__(**kwargs)
        self.filepath = filepath
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    def _send_batch(self, batch: List[LogEntry]) -> None:
        """Write batch to file."""
        with open(self.filepath, 'a') as f:
            for entry in batch:
                f.write(entry.to_json() + "\n")


class HTTPShipper(AsyncLogShipper):
    """Ships logs to an HTTP endpoint."""

    def __init__(
        self,
        url: str,
        headers: Dict[str, str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.url = url
        self.headers = headers or {}

    def _send_batch(self, batch: List[LogEntry]) -> None:
        """Send batch to HTTP endpoint."""
        import urllib.request

        payload = json.dumps([e.to_dict() for e in batch]).encode('utf-8')

        request = urllib.request.Request(
            self.url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                **self.headers
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                pass  # Log success if needed
        except Exception:
            pass  # Handle error silently


class ElasticsearchShipper(AsyncLogShipper):
    """Ships logs to Elasticsearch."""

    def __init__(
        self,
        url: str,
        index: str = "logs",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.url = url.rstrip('/')
        self.index = index

    def _send_batch(self, batch: List[LogEntry]) -> None:
        """Send batch to Elasticsearch using bulk API."""
        import urllib.request

        # Build bulk request body
        lines = []
        for entry in batch:
            index_line = json.dumps({"index": {"_index": self.index}})
            doc_line = json.dumps(entry.to_dict())
            lines.append(index_line)
            lines.append(doc_line)

        body = "\n".join(lines) + "\n"

        request = urllib.request.Request(
            f"{self.url}/_bulk",
            data=body.encode('utf-8'),
            headers={"Content-Type": "application/x-ndjson"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                pass
        except Exception:
            pass


# Convenience functions


def create_log_aggregator(
    service_name: str = "company-researcher",
    log_file: str = None,
    console: bool = True
) -> LogAggregator:
    """Create a configured log aggregator."""
    aggregator = LogAggregator(service_name=service_name)

    if console:
        aggregator.add_console_handler()

    if log_file:
        aggregator.add_file_handler(log_file)

    return aggregator


def setup_structured_logging(
    service_name: str = "company-researcher",
    level: str = "INFO"
) -> logging.Logger:
    """Setup structured logging for the application."""
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper()))

    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter(service_name))
    logger.addHandler(handler)

    return logger
