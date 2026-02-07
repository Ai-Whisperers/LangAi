"""
Research Audit Trail - Complete provenance tracking for claims.

Provides:
- Claim-source linking
- Agent attribution
- Timestamp logging
- Audit report generation
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils import utc_now


class AuditEventType(str, Enum):
    """Types of audit events."""

    RESEARCH_STARTED = "research_started"
    RESEARCH_COMPLETED = "research_completed"
    AGENT_EXECUTED = "agent_executed"
    SOURCE_ACCESSED = "source_accessed"
    CLAIM_EXTRACTED = "claim_extracted"
    CLAIM_VERIFIED = "claim_verified"
    QUALITY_CHECKED = "quality_checked"
    DATA_TRANSFORMED = "data_transformed"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class AuditEvent:
    """An audit trail event."""

    id: str
    event_type: AuditEventType
    timestamp: datetime
    description: str
    actor: str  # Agent or system that triggered event
    data: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None  # For event chains
    research_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "actor": self.actor,
            "data": self.data,
            "parent_id": self.parent_id,
            "research_id": self.research_id,
        }


@dataclass
class SourceReference:
    """Reference to an information source."""

    url: str
    title: str
    accessed_at: datetime
    source_type: str = "web"
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        """Generate unique ID for source."""
        return hashlib.md5(self.url.encode()).hexdigest()[:12]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "accessed_at": self.accessed_at.isoformat(),
            "source_type": self.source_type,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata,
        }


@dataclass
class ClaimProvenance:
    """Provenance record for a claim."""

    claim_id: str
    claim_text: str
    extracted_at: datetime
    extracted_by: str  # Agent that extracted this
    sources: List[SourceReference]
    confidence: float = 1.0
    verified: bool = False
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    verification_notes: str = ""
    context: str = ""  # Section where claim appears
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "claim_id": self.claim_id,
            "claim_text": self.claim_text,
            "extracted_at": self.extracted_at.isoformat(),
            "extracted_by": self.extracted_by,
            "sources": [s.to_dict() for s in self.sources],
            "confidence": self.confidence,
            "verified": self.verified,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "verified_by": self.verified_by,
            "verification_notes": self.verification_notes,
            "context": self.context,
            "metadata": self.metadata,
        }


@dataclass
class AgentExecution:
    """Record of an agent execution."""

    agent_name: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"
    input_summary: str = ""
    output_summary: str = ""
    claims_extracted: int = 0
    sources_used: int = 0
    tokens_used: int = 0
    cost: float = 0.0
    errors: List[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Get execution duration."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_name": self.agent_name,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "duration_seconds": self.duration_seconds,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "claims_extracted": self.claims_extracted,
            "sources_used": self.sources_used,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "errors": self.errors,
        }


class ResearchAuditTrail:
    """
    Complete audit trail for research operations.

    Usage:
        audit = ResearchAuditTrail()

        # Start research
        research_id = audit.start_research("Tesla", "comprehensive")

        # Log agent execution
        audit.log_agent_start(research_id, "financial_agent")
        audit.log_agent_complete(research_id, "financial_agent", output)

        # Track claims
        claim_id = audit.add_claim(
            research_id=research_id,
            claim_text="Tesla's revenue was $25B in Q3 2024",
            extracted_by="financial_agent",
            sources=[source_ref]
        )

        # Verify claim
        audit.verify_claim(claim_id, verified_by="quality_checker")

        # Generate report
        report = audit.get_audit_report(research_id)
    """

    def __init__(self, storage_path: str = None, enable_persistence: bool = True):
        self._events: Dict[str, List[AuditEvent]] = {}
        self._claims: Dict[str, ClaimProvenance] = {}
        self._agent_executions: Dict[str, Dict[str, AgentExecution]] = {}
        self._research_metadata: Dict[str, Dict[str, Any]] = {}
        self._storage_path = Path(storage_path) if storage_path else None
        self._enable_persistence = enable_persistence

        if self._storage_path and enable_persistence:
            self._storage_path.mkdir(parents=True, exist_ok=True)

    def start_research(self, company_name: str, depth: str, metadata: Dict[str, Any] = None) -> str:
        """
        Start tracking a new research session.

        Args:
            company_name: Company being researched
            depth: Research depth level
            metadata: Additional metadata

        Returns:
            Research ID
        """
        research_id = str(uuid.uuid4())[:8]

        self._events[research_id] = []
        self._agent_executions[research_id] = {}
        self._research_metadata[research_id] = {
            "company_name": company_name,
            "depth": depth,
            "started_at": utc_now().isoformat(),
            **(metadata or {}),
        }

        self._log_event(
            research_id=research_id,
            event_type=AuditEventType.RESEARCH_STARTED,
            description=f"Started {depth} research on {company_name}",
            actor="system",
            data={"company_name": company_name, "depth": depth},
        )

        return research_id

    def complete_research(
        self, research_id: str, quality_score: float = 0.0, summary: str = ""
    ) -> None:
        """Mark research as complete."""
        self._research_metadata[research_id]["completed_at"] = utc_now().isoformat()
        self._research_metadata[research_id]["quality_score"] = quality_score

        self._log_event(
            research_id=research_id,
            event_type=AuditEventType.RESEARCH_COMPLETED,
            description=f"Research completed with quality score {quality_score:.2f}",
            actor="system",
            data={"quality_score": quality_score, "summary": summary},
        )

        if self._enable_persistence and self._storage_path:
            self._persist_research(research_id)

    def log_agent_start(self, research_id: str, agent_name: str, input_summary: str = "") -> None:
        """Log agent execution start."""
        execution = AgentExecution(
            agent_name=agent_name, started_at=utc_now(), input_summary=input_summary
        )
        self._agent_executions[research_id][agent_name] = execution

        self._log_event(
            research_id=research_id,
            event_type=AuditEventType.AGENT_EXECUTED,
            description=f"Agent {agent_name} started execution",
            actor=agent_name,
            data={"status": "started", "input_summary": input_summary},
        )

    def log_agent_complete(
        self,
        research_id: str,
        agent_name: str,
        output: Dict[str, Any] = None,
        claims_count: int = 0,
        sources_count: int = 0,
        tokens: int = 0,
        cost: float = 0.0,
    ) -> None:
        """Log agent execution completion."""
        if agent_name in self._agent_executions.get(research_id, {}):
            execution = self._agent_executions[research_id][agent_name]
            execution.completed_at = utc_now()
            execution.status = "completed"
            execution.claims_extracted = claims_count
            execution.sources_used = sources_count
            execution.tokens_used = tokens
            execution.cost = cost
            execution.output_summary = str(output)[:500] if output else ""

        self._log_event(
            research_id=research_id,
            event_type=AuditEventType.AGENT_EXECUTED,
            description=f"Agent {agent_name} completed execution",
            actor=agent_name,
            data={
                "status": "completed",
                "claims_extracted": claims_count,
                "sources_used": sources_count,
                "tokens": tokens,
                "cost": cost,
            },
        )

    def log_agent_error(self, research_id: str, agent_name: str, error: str) -> None:
        """Log agent error."""
        if agent_name in self._agent_executions.get(research_id, {}):
            execution = self._agent_executions[research_id][agent_name]
            execution.completed_at = utc_now()
            execution.status = "error"
            execution.errors.append(error)

        self._log_event(
            research_id=research_id,
            event_type=AuditEventType.ERROR_OCCURRED,
            description=f"Error in agent {agent_name}: {error[:100]}",
            actor=agent_name,
            data={"error": error},
        )

    def log_source_access(
        self, research_id: str, url: str, title: str, agent_name: str
    ) -> SourceReference:
        """Log source access."""
        source = SourceReference(url=url, title=title, accessed_at=utc_now())

        self._log_event(
            research_id=research_id,
            event_type=AuditEventType.SOURCE_ACCESSED,
            description=f"Accessed source: {title[:50]}",
            actor=agent_name,
            data={"url": url, "title": title, "source_id": source.id},
        )

        return source

    def add_claim(
        self,
        research_id: str,
        claim_text: str,
        extracted_by: str,
        sources: List[SourceReference],
        confidence: float = 1.0,
        context: str = "",
    ) -> str:
        """
        Add a claim to the audit trail.

        Returns:
            Claim ID
        """
        claim_id = str(uuid.uuid4())[:8]

        provenance = ClaimProvenance(
            claim_id=claim_id,
            claim_text=claim_text,
            extracted_at=utc_now(),
            extracted_by=extracted_by,
            sources=sources,
            confidence=confidence,
            context=context,
            metadata={"research_id": research_id},
        )

        self._claims[claim_id] = provenance

        self._log_event(
            research_id=research_id,
            event_type=AuditEventType.CLAIM_EXTRACTED,
            description=f"Claim extracted: {claim_text[:50]}...",
            actor=extracted_by,
            data={"claim_id": claim_id, "confidence": confidence, "sources_count": len(sources)},
        )

        return claim_id

    def verify_claim(
        self,
        claim_id: str,
        verified: bool = True,
        verified_by: str = "quality_checker",
        notes: str = "",
    ) -> None:
        """Verify a claim."""
        if claim_id in self._claims:
            claim = self._claims[claim_id]
            claim.verified = verified
            claim.verified_at = utc_now()
            claim.verified_by = verified_by
            claim.verification_notes = notes

            research_id = claim.metadata.get("research_id")
            if research_id:
                self._log_event(
                    research_id=research_id,
                    event_type=AuditEventType.CLAIM_VERIFIED,
                    description=f"Claim {claim_id} verified: {verified}",
                    actor=verified_by,
                    data={"claim_id": claim_id, "verified": verified, "notes": notes},
                )

    def log_quality_check(
        self,
        research_id: str,
        quality_score: float,
        issues: List[str] = None,
        checker: str = "quality_checker",
    ) -> None:
        """Log quality check."""
        self._log_event(
            research_id=research_id,
            event_type=AuditEventType.QUALITY_CHECKED,
            description=f"Quality check: score {quality_score:.2f}",
            actor=checker,
            data={
                "quality_score": quality_score,
                "issues": issues or [],
                "issues_count": len(issues or []),
            },
        )

    def get_claim(self, claim_id: str) -> Optional[ClaimProvenance]:
        """Get claim by ID."""
        return self._claims.get(claim_id)

    def get_claims_for_research(self, research_id: str) -> List[ClaimProvenance]:
        """Get all claims for a research session."""
        return [
            claim
            for claim in self._claims.values()
            if claim.metadata.get("research_id") == research_id
        ]

    def get_events(self, research_id: str) -> List[AuditEvent]:
        """Get all events for a research session."""
        return self._events.get(research_id, [])

    def get_audit_report(self, research_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive audit report.

        Args:
            research_id: Research session ID

        Returns:
            Audit report dictionary
        """
        metadata = self._research_metadata.get(research_id, {})
        events = self._events.get(research_id, [])
        executions = self._agent_executions.get(research_id, {})
        claims = self.get_claims_for_research(research_id)

        # Calculate stats
        total_sources = sum(len(c.sources) for c in claims)
        verified_claims = sum(1 for c in claims if c.verified)
        total_tokens = sum(e.tokens_used for e in executions.values())
        total_cost = sum(e.cost for e in executions.values())

        # Agent summary
        agent_summary = [
            {
                "agent": name,
                "duration_seconds": e.duration_seconds,
                "status": e.status,
                "claims": e.claims_extracted,
                "sources": e.sources_used,
                "tokens": e.tokens_used,
            }
            for name, e in executions.items()
        ]

        return {
            "research_id": research_id,
            "metadata": metadata,
            "summary": {
                "total_events": len(events),
                "total_claims": len(claims),
                "verified_claims": verified_claims,
                "verification_rate": verified_claims / len(claims) if claims else 0,
                "total_sources": total_sources,
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "agents_executed": len(executions),
            },
            "agents": agent_summary,
            "claims": [c.to_dict() for c in claims],
            "events": [e.to_dict() for e in events],
            "generated_at": utc_now().isoformat(),
        }

    def export_audit_trail(self, research_id: str, format: str = "json") -> str:
        """Export audit trail."""
        report = self.get_audit_report(research_id)

        if format == "json":
            return json.dumps(report, indent=2, default=str)
        else:
            # Plain text format
            lines = [
                f"AUDIT TRAIL: {research_id}",
                "=" * 60,
                f"Company: {report['metadata'].get('company_name', 'Unknown')}",
                f"Started: {report['metadata'].get('started_at', 'Unknown')}",
                "",
                "SUMMARY",
                "-" * 40,
                f"Total Events: {report['summary']['total_events']}",
                f"Claims: {report['summary']['total_claims']} ({report['summary']['verified_claims']} verified)",
                f"Sources: {report['summary']['total_sources']}",
                f"Tokens: {report['summary']['total_tokens']}",
                f"Cost: ${report['summary']['total_cost']:.4f}",
                "",
                "AGENTS",
                "-" * 40,
            ]

            for agent in report["agents"]:
                lines.append(
                    f"  {agent['agent']}: {agent['status']} "
                    f"({agent['duration_seconds']:.1f}s, {agent['claims']} claims)"
                )

            lines.extend(
                [
                    "",
                    "CLAIMS",
                    "-" * 40,
                ]
            )

            for claim in report["claims"][:10]:
                lines.append(f"  [{claim['claim_id']}] {claim['claim_text'][:60]}...")
                lines.append(f"    Sources: {len(claim['sources'])}, Verified: {claim['verified']}")

            return "\n".join(lines)

    def _log_event(
        self,
        research_id: str,
        event_type: AuditEventType,
        description: str,
        actor: str,
        data: Dict[str, Any] = None,
        parent_id: str = None,
    ) -> AuditEvent:
        """Log an audit event."""
        event = AuditEvent(
            id=str(uuid.uuid4())[:8],
            event_type=event_type,
            timestamp=utc_now(),
            description=description,
            actor=actor,
            data=data or {},
            parent_id=parent_id,
            research_id=research_id,
        )

        if research_id not in self._events:
            self._events[research_id] = []
        self._events[research_id].append(event)

        return event

    def _persist_research(self, research_id: str) -> None:
        """Persist research audit to file."""
        if not self._storage_path:
            return

        report = self.get_audit_report(research_id)
        filepath = self._storage_path / f"audit_{research_id}.json"

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, default=str)


# Convenience functions


def create_audit_trail(storage_path: str = None) -> ResearchAuditTrail:
    """Create a research audit trail."""
    return ResearchAuditTrail(storage_path=storage_path)
