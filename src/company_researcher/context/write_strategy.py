"""
WRITE Strategy (Phase 12.1).

Scratchpad and working memory for agents:
- Structured note-taking during research
- Intermediate result storage
- Chain-of-thought preservation
- Cross-agent communication via shared scratchpad

The WRITE strategy allows agents to persist working notes
that can be read by subsequent agents in the workflow.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from ..utils import utc_now


# ============================================================================
# Enums and Data Models
# ============================================================================

class NoteType(str, Enum):
    """Types of scratchpad notes."""
    OBSERVATION = "observation"      # Raw observation from research
    HYPOTHESIS = "hypothesis"        # Working hypothesis
    QUESTION = "question"            # Question to investigate
    FINDING = "finding"              # Confirmed finding
    TODO = "todo"                    # Action item
    INSIGHT = "insight"              # Key insight
    CONTRADICTION = "contradiction"  # Contradictory information
    SUMMARY = "summary"              # Summary note


class NotePriority(str, Enum):
    """Priority levels for notes."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ScratchpadNote:
    """A single note in the scratchpad."""
    id: str
    content: str
    note_type: NoteType
    agent_source: str
    priority: NotePriority = NotePriority.MEDIUM
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)
    references: List[str] = field(default_factory=list)  # IDs of related notes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "note_type": self.note_type.value,
            "agent_source": self.agent_source,
            "priority": self.priority.value,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "references": self.references
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScratchpadNote":
        return cls(
            id=data["id"],
            content=data["content"],
            note_type=NoteType(data["note_type"]),
            agent_source=data["agent_source"],
            priority=NotePriority(data.get("priority", "medium")),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else utc_now(),
            references=data.get("references", [])
        )


@dataclass
class WorkingMemory:
    """Working memory state for an agent."""
    agent_name: str
    current_focus: str = ""
    context_window: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    chain_of_thought: List[str] = field(default_factory=list)

    def add_thought(self, thought: str) -> None:
        """Add a thought to the chain."""
        self.chain_of_thought.append(f"[{utc_now().strftime('%H:%M:%S')}] {thought}")

    def set_variable(self, name: str, value: Any) -> None:
        """Set a working variable."""
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a working variable."""
        return self.variables.get(name, default)

    def update_focus(self, focus: str) -> None:
        """Update current focus."""
        self.current_focus = focus

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "current_focus": self.current_focus,
            "context_window": self.context_window,
            "variables": self.variables,
            "chain_of_thought": self.chain_of_thought
        }


# ============================================================================
# Scratchpad
# ============================================================================

class Scratchpad:
    """
    Shared scratchpad for multi-agent workflows.

    Allows agents to write and read notes, maintaining
    a structured working memory across the research process.

    Usage:
        scratchpad = Scratchpad(company_name="Tesla")

        # Agent writes notes
        scratchpad.write(
            content="Tesla's automotive revenue grew 6% YoY",
            note_type=NoteType.FINDING,
            agent_source="financial_agent",
            priority=NotePriority.HIGH,
            tags=["revenue", "growth"]
        )

        # Later agent reads notes
        findings = scratchpad.read(note_type=NoteType.FINDING)
        contradictions = scratchpad.read(note_type=NoteType.CONTRADICTION)
    """

    def __init__(self, company_name: str, max_notes: int = 500):
        """
        Initialize scratchpad.

        Args:
            company_name: Company being researched
            max_notes: Maximum notes to keep
        """
        self.company_name = company_name
        self._max_notes = max_notes
        self._notes: Dict[str, ScratchpadNote] = {}
        self._note_counter = 0
        self._working_memories: Dict[str, WorkingMemory] = {}
        self._created_at = utc_now()

    @property
    def note_count(self) -> int:
        return len(self._notes)

    def _generate_id(self) -> str:
        """Generate unique note ID."""
        self._note_counter += 1
        return f"note_{self._note_counter:04d}"

    # ==========================================================================
    # Write Operations
    # ==========================================================================

    def write(
        self,
        content: str,
        note_type: NoteType,
        agent_source: str,
        priority: NotePriority = NotePriority.MEDIUM,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        references: Optional[List[str]] = None
    ) -> str:
        """
        Write a note to the scratchpad.

        Args:
            content: Note content
            note_type: Type of note
            agent_source: Agent that created the note
            priority: Note priority
            tags: Tags for categorization
            metadata: Additional metadata
            references: IDs of related notes

        Returns:
            Note ID
        """
        note_id = self._generate_id()

        note = ScratchpadNote(
            id=note_id,
            content=content,
            note_type=note_type,
            agent_source=agent_source,
            priority=priority,
            tags=tags or [],
            metadata=metadata or {},
            references=references or []
        )

        self._notes[note_id] = note

        # Evict old notes if over limit
        if len(self._notes) > self._max_notes:
            self._evict_oldest()

        return note_id

    def write_observation(
        self,
        content: str,
        agent_source: str,
        tags: Optional[List[str]] = None
    ) -> str:
        """Write an observation note."""
        return self.write(
            content=content,
            note_type=NoteType.OBSERVATION,
            agent_source=agent_source,
            tags=tags
        )

    def write_finding(
        self,
        content: str,
        agent_source: str,
        priority: NotePriority = NotePriority.HIGH,
        tags: Optional[List[str]] = None
    ) -> str:
        """Write a confirmed finding."""
        return self.write(
            content=content,
            note_type=NoteType.FINDING,
            agent_source=agent_source,
            priority=priority,
            tags=tags
        )

    def write_hypothesis(
        self,
        content: str,
        agent_source: str,
        confidence: float = 0.5
    ) -> str:
        """Write a hypothesis with confidence level."""
        return self.write(
            content=content,
            note_type=NoteType.HYPOTHESIS,
            agent_source=agent_source,
            metadata={"confidence": confidence}
        )

    def write_contradiction(
        self,
        content: str,
        agent_source: str,
        conflicting_note_ids: Optional[List[str]] = None
    ) -> str:
        """Write a contradiction note."""
        return self.write(
            content=content,
            note_type=NoteType.CONTRADICTION,
            agent_source=agent_source,
            priority=NotePriority.HIGH,
            references=conflicting_note_ids
        )

    def write_question(
        self,
        content: str,
        agent_source: str,
        priority: NotePriority = NotePriority.MEDIUM
    ) -> str:
        """Write a question to investigate."""
        return self.write(
            content=content,
            note_type=NoteType.QUESTION,
            agent_source=agent_source,
            priority=priority
        )

    def write_summary(
        self,
        content: str,
        agent_source: str,
        summarized_note_ids: Optional[List[str]] = None
    ) -> str:
        """Write a summary note."""
        return self.write(
            content=content,
            note_type=NoteType.SUMMARY,
            agent_source=agent_source,
            priority=NotePriority.HIGH,
            references=summarized_note_ids
        )

    # ==========================================================================
    # Read Operations
    # ==========================================================================

    def read(
        self,
        note_type: Optional[NoteType] = None,
        agent_source: Optional[str] = None,
        priority: Optional[NotePriority] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[ScratchpadNote]:
        """
        Read notes matching criteria.

        Args:
            note_type: Filter by note type
            agent_source: Filter by source agent
            priority: Filter by priority
            tags: Filter by tags (any match)
            limit: Maximum notes to return

        Returns:
            List of matching notes
        """
        results = []

        for note in self._notes.values():
            # Apply filters
            if note_type and note.note_type != note_type:
                continue
            if agent_source and note.agent_source != agent_source:
                continue
            if priority and note.priority != priority:
                continue
            if tags and not any(t in note.tags for t in tags):
                continue

            results.append(note)

        # Sort by priority and recency
        priority_order = {
            NotePriority.CRITICAL: 0,
            NotePriority.HIGH: 1,
            NotePriority.MEDIUM: 2,
            NotePriority.LOW: 3
        }

        results.sort(
            key=lambda n: (priority_order[n.priority], -n.created_at.timestamp())
        )

        return results[:limit]

    def read_all(self) -> List[ScratchpadNote]:
        """Read all notes."""
        return list(self._notes.values())

    def read_by_id(self, note_id: str) -> Optional[ScratchpadNote]:
        """Read specific note by ID."""
        return self._notes.get(note_id)

    def read_findings(self, limit: int = 20) -> List[ScratchpadNote]:
        """Read all findings."""
        return self.read(note_type=NoteType.FINDING, limit=limit)

    def read_contradictions(self) -> List[ScratchpadNote]:
        """Read all contradictions."""
        return self.read(note_type=NoteType.CONTRADICTION, limit=100)

    def read_questions(self) -> List[ScratchpadNote]:
        """Read unanswered questions."""
        return self.read(note_type=NoteType.QUESTION)

    def read_by_agent(self, agent_name: str) -> List[ScratchpadNote]:
        """Read all notes from a specific agent."""
        return self.read(agent_source=agent_name, limit=100)

    def read_critical(self) -> List[ScratchpadNote]:
        """Read all critical priority notes."""
        return self.read(priority=NotePriority.CRITICAL, limit=100)

    # ==========================================================================
    # Working Memory Management
    # ==========================================================================

    def get_working_memory(self, agent_name: str) -> WorkingMemory:
        """
        Get or create working memory for an agent.

        Args:
            agent_name: Agent name

        Returns:
            WorkingMemory instance
        """
        if agent_name not in self._working_memories:
            self._working_memories[agent_name] = WorkingMemory(agent_name=agent_name)
        return self._working_memories[agent_name]

    def update_working_memory(
        self,
        agent_name: str,
        focus: Optional[str] = None,
        thought: Optional[str] = None,
        variable: Optional[tuple] = None
    ) -> WorkingMemory:
        """
        Update agent's working memory.

        Args:
            agent_name: Agent name
            focus: New focus (optional)
            thought: Thought to add (optional)
            variable: (name, value) tuple to set (optional)

        Returns:
            Updated WorkingMemory
        """
        memory = self.get_working_memory(agent_name)

        if focus:
            memory.update_focus(focus)
        if thought:
            memory.add_thought(thought)
        if variable:
            memory.set_variable(variable[0], variable[1])

        return memory

    # ==========================================================================
    # Utility Operations
    # ==========================================================================

    def _evict_oldest(self) -> None:
        """Evict oldest low-priority notes."""
        # Sort by priority (keep critical/high) then by age
        notes_list = list(self._notes.values())
        notes_list.sort(
            key=lambda n: (
                0 if n.priority in (NotePriority.CRITICAL, NotePriority.HIGH) else 1,
                n.created_at.timestamp()
            )
        )

        # Remove oldest 10% of low-priority notes
        to_remove = int(self._max_notes * 0.1)
        for note in notes_list[-to_remove:]:
            if note.priority not in (NotePriority.CRITICAL, NotePriority.HIGH):
                del self._notes[note.id]

    def clear(self, note_type: Optional[NoteType] = None) -> int:
        """
        Clear notes from scratchpad.

        Args:
            note_type: If specified, only clear this type

        Returns:
            Number of notes cleared
        """
        if note_type is None:
            count = len(self._notes)
            self._notes.clear()
            return count

        to_remove = [
            note_id for note_id, note in self._notes.items()
            if note.note_type == note_type
        ]

        for note_id in to_remove:
            del self._notes[note_id]

        return len(to_remove)

    def export(self) -> Dict[str, Any]:
        """Export scratchpad state."""
        return {
            "company_name": self.company_name,
            "created_at": self._created_at.isoformat(),
            "note_count": len(self._notes),
            "notes": [note.to_dict() for note in self._notes.values()],
            "working_memories": {
                name: memory.to_dict()
                for name, memory in self._working_memories.items()
            }
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        by_type = {}
        by_agent = {}
        by_priority = {}

        for note in self._notes.values():
            by_type[note.note_type.value] = by_type.get(note.note_type.value, 0) + 1
            by_agent[note.agent_source] = by_agent.get(note.agent_source, 0) + 1
            by_priority[note.priority.value] = by_priority.get(note.priority.value, 0) + 1

        return {
            "total_notes": len(self._notes),
            "by_type": by_type,
            "by_agent": by_agent,
            "by_priority": by_priority,
            "working_memories": list(self._working_memories.keys())
        }

    def format_for_context(
        self,
        note_types: Optional[List[NoteType]] = None,
        max_length: int = 4000
    ) -> str:
        """
        Format scratchpad notes for inclusion in LLM context.

        Args:
            note_types: Types to include (all if None)
            max_length: Maximum character length

        Returns:
            Formatted string for LLM context
        """
        lines = [f"## Scratchpad Notes for {self.company_name}\n"]

        types_to_include = note_types or list(NoteType)
        current_length = len(lines[0])

        for note_type in types_to_include:
            notes = self.read(note_type=note_type, limit=10)
            if not notes:
                continue

            section = f"\n### {note_type.value.upper()}S:\n"
            current_length += len(section)

            if current_length > max_length:
                break

            lines.append(section)

            for note in notes:
                note_line = f"- [{note.priority.value}] {note.content}\n"
                if current_length + len(note_line) > max_length:
                    lines.append("... (truncated)\n")
                    break
                lines.append(note_line)
                current_length += len(note_line)

        return "".join(lines)


# ============================================================================
# Factory Functions
# ============================================================================

def create_scratchpad(company_name: str) -> Scratchpad:
    """Create a new scratchpad for a company."""
    return Scratchpad(company_name=company_name)


def scratchpad_from_state(state: Dict[str, Any]) -> Scratchpad:
    """
    Create or retrieve scratchpad from workflow state.

    Args:
        state: Workflow state dictionary

    Returns:
        Scratchpad instance
    """
    company_name = state.get("company_name", "Unknown")

    # Check if scratchpad exists in state
    if "scratchpad" in state and isinstance(state["scratchpad"], Scratchpad):
        return state["scratchpad"]

    # Create new scratchpad
    return Scratchpad(company_name=company_name)
