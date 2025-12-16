"""
Conversation Memory - Chat history and context management.

Provides:
- Message history storage
- Context window management
- Summarization support
- Multi-turn conversation tracking
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class MessageRole(str, Enum):
    """Message roles in conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


@dataclass
class Message:
    """A message in a conversation."""

    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=_utcnow)
    name: Optional[str] = None  # For function/tool messages
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to LLM-compatible format."""
        result = {"role": self.role.value, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result

    @classmethod
    def user(cls, content: str, **kwargs) -> "Message":
        """Create a user message."""
        return cls(role=MessageRole.USER, content=content, **kwargs)

    @classmethod
    def assistant(cls, content: str, **kwargs) -> "Message":
        """Create an assistant message."""
        return cls(role=MessageRole.ASSISTANT, content=content, **kwargs)

    @classmethod
    def system(cls, content: str, **kwargs) -> "Message":
        """Create a system message."""
        return cls(role=MessageRole.SYSTEM, content=content, **kwargs)


@dataclass
class ConversationSummary:
    """Summary of a conversation segment."""

    content: str
    messages_summarized: int
    tokens_saved: int
    created_at: datetime = field(default_factory=_utcnow)


class ConversationMemory:
    """
    Manages conversation history with context window support.

    Usage:
        memory = ConversationMemory(max_tokens=4000)

        # Add messages
        memory.add_message(Message.user("What is Tesla's revenue?"))
        memory.add_message(Message.assistant("Tesla's Q3 2024 revenue was..."))

        # Get messages for LLM
        messages = memory.get_messages()

        # Get with token limit
        messages = memory.get_messages(max_tokens=2000)

        # Clear conversation
        memory.clear()
    """

    def __init__(
        self,
        max_tokens: int = 4000,
        max_messages: int = 100,
        system_message: str = None,
        summarize_fn: Callable[[List[Message]], str] = None,
    ):
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.summarize_fn = summarize_fn
        self._messages: List[Message] = []
        self._summaries: List[ConversationSummary] = []
        self._total_tokens = 0

        if system_message:
            self.set_system_message(system_message)

    def set_system_message(self, content: str) -> None:
        """Set or update the system message."""
        # Remove existing system message if any
        self._messages = [m for m in self._messages if m.role != MessageRole.SYSTEM]
        # Add new system message at the beginning
        self._messages.insert(0, Message.system(content))

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        # Estimate token count if not provided
        if message.token_count == 0:
            message.token_count = len(message.content) // 4  # Rough estimate

        self._messages.append(message)
        self._total_tokens += message.token_count

        # Check limits
        self._enforce_limits()

    def add_user_message(self, content: str, **kwargs) -> Message:
        """Add a user message."""
        message = Message.user(content, **kwargs)
        self.add_message(message)
        return message

    def add_assistant_message(self, content: str, **kwargs) -> Message:
        """Add an assistant message."""
        message = Message.assistant(content, **kwargs)
        self.add_message(message)
        return message

    def _enforce_limits(self) -> None:
        """Enforce token and message limits."""
        # Summarize if over token limit
        while self._total_tokens > self.max_tokens and len(self._messages) > 2:
            self._summarize_old_messages()

        # Enforce message limit
        while len(self._messages) > self.max_messages:
            removed = self._messages.pop(1)  # Keep system message
            self._total_tokens -= removed.token_count

    def _summarize_old_messages(self) -> None:
        """Summarize older messages to save tokens."""
        if self.summarize_fn is None:
            # Simple truncation if no summarize function
            if len(self._messages) > 1:
                removed = self._messages.pop(1)
                self._total_tokens -= removed.token_count
            return

        # Find messages to summarize (keep system + last few)
        keep_count = 4
        if len(self._messages) <= keep_count:
            return

        to_summarize = self._messages[1 : -keep_count + 1]
        if not to_summarize:
            return

        # Generate summary
        summary_text = self.summarize_fn(to_summarize)
        tokens_saved = sum(m.token_count for m in to_summarize) - len(summary_text) // 4

        # Store summary
        summary = ConversationSummary(
            content=summary_text, messages_summarized=len(to_summarize), tokens_saved=tokens_saved
        )
        self._summaries.append(summary)

        # Replace summarized messages with summary message
        self._messages = (
            self._messages[:1]
            + [Message.system(f"[Previous conversation summary: {summary_text}]")]
            + self._messages[-keep_count + 1 :]
        )
        self._total_tokens = sum(m.token_count for m in self._messages)

    def get_messages(
        self, max_tokens: int = None, include_system: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get messages for LLM, respecting token limits.

        Args:
            max_tokens: Maximum tokens to return
            include_system: Whether to include system message

        Returns:
            List of message dictionaries
        """
        messages = self._messages.copy()

        if not include_system:
            messages = [m for m in messages if m.role != MessageRole.SYSTEM]

        if max_tokens is None:
            return [m.to_dict() for m in messages]

        # Fit within token limit (keep most recent)
        result = []
        current_tokens = 0

        for message in reversed(messages):
            if current_tokens + message.token_count <= max_tokens:
                result.insert(0, message.to_dict())
                current_tokens += message.token_count
            elif message.role == MessageRole.SYSTEM:
                # Always include system message
                result.insert(0, message.to_dict())

        return result

    def get_last_n_messages(self, n: int) -> List[Message]:
        """Get the last n messages."""
        return self._messages[-n:]

    def get_context_string(self) -> str:
        """Get conversation as a single string."""
        lines = []
        for msg in self._messages:
            prefix = msg.role.value.upper()
            lines.append(f"{prefix}: {msg.content}")
        return "\n".join(lines)

    def search_messages(self, query: str, role: MessageRole = None) -> List[Message]:
        """Search messages containing query."""
        results = []
        query_lower = query.lower()

        for message in self._messages:
            if role and message.role != role:
                continue
            if query_lower in message.content.lower():
                results.append(message)

        return results

    def clear(self, keep_system: bool = True) -> None:
        """Clear conversation history."""
        if keep_system:
            self._messages = [m for m in self._messages if m.role == MessageRole.SYSTEM]
        else:
            self._messages = []
        self._total_tokens = sum(m.token_count for m in self._messages)

    @property
    def message_count(self) -> int:
        """Get number of messages."""
        return len(self._messages)

    @property
    def total_tokens(self) -> int:
        """Get total token count."""
        return self._total_tokens


class WindowedConversationMemory(ConversationMemory):
    """
    Conversation memory with a sliding window approach.

    Keeps only the most recent messages within a window.
    """

    def __init__(self, window_size: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.window_size = window_size

    def _enforce_limits(self) -> None:
        """Enforce window size limit."""
        while len(self._messages) > self.window_size:
            # Keep system message
            if self._messages[1].role != MessageRole.SYSTEM:
                removed = self._messages.pop(1)
                self._total_tokens -= removed.token_count
            else:
                if len(self._messages) > 2:
                    removed = self._messages.pop(2)
                    self._total_tokens -= removed.token_count


class BufferedConversationMemory:
    """
    Conversation memory with separate buffer for working messages.

    Useful for multi-turn interactions before committing to history.
    """

    def __init__(self, main_memory: ConversationMemory = None):
        self.main_memory = main_memory or ConversationMemory()
        self._buffer: List[Message] = []

    def add_to_buffer(self, message: Message) -> None:
        """Add message to buffer."""
        self._buffer.append(message)

    def commit_buffer(self) -> None:
        """Commit buffered messages to main memory."""
        for message in self._buffer:
            self.main_memory.add_message(message)
        self._buffer.clear()

    def clear_buffer(self) -> None:
        """Clear buffer without committing."""
        self._buffer.clear()

    def get_all_messages(self) -> List[Dict[str, Any]]:
        """Get main + buffered messages."""
        main_msgs = self.main_memory.get_messages()
        buffer_msgs = [m.to_dict() for m in self._buffer]
        return main_msgs + buffer_msgs


# Convenience functions


def create_conversation_memory(
    max_tokens: int = 4000, system_message: str = None
) -> ConversationMemory:
    """Create a conversation memory."""
    return ConversationMemory(max_tokens=max_tokens, system_message=system_message)
