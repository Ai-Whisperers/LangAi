"""
Test Fixtures - Mock objects and test data generators.

Provides:
- Mock LLM responses
- Mock tool results
- Mock research state
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union


@dataclass
class MockLLMConfig:
    """Configuration for mock LLM."""
    default_response: str = "This is a mock response."
    response_delay: float = 0.0  # seconds
    fail_rate: float = 0.0  # 0-1, rate of simulated failures
    token_count: int = 100


class MockLLM:
    """
    Mock LLM for testing without API calls.

    Usage:
        llm = MockLLM()

        # Set specific responses
        llm.set_response("What is Tesla?", "Tesla is an EV company.")

        # Use in tests
        response = llm.invoke("What is Tesla?")
    """

    def __init__(self, config: Optional[MockLLMConfig] = None):
        self.config = config or MockLLMConfig()
        self._responses: Dict[str, str] = {}
        self._response_queue: List[str] = []
        self._call_history: List[Dict[str, Any]] = []
        self._call_count = 0

    def set_response(self, prompt_contains: str, response: str) -> None:
        """Set response for prompts containing a specific string."""
        self._responses[prompt_contains] = response

    def queue_response(self, response: str) -> None:
        """Queue a response to be returned in order."""
        self._response_queue.append(response)

    def queue_responses(self, responses: List[str]) -> None:
        """Queue multiple responses."""
        self._response_queue.extend(responses)

    def invoke(self, prompt: str, **kwargs) -> str:
        """Invoke the mock LLM."""
        import random
        import time

        self._call_count += 1
        self._call_history.append({
            "prompt": prompt,
            "kwargs": kwargs,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Simulate delay
        if self.config.response_delay > 0:
            time.sleep(self.config.response_delay)

        # Simulate failures
        if random.random() < self.config.fail_rate:
            raise Exception("Simulated LLM failure")

        # Check queued responses
        if self._response_queue:
            return self._response_queue.pop(0)

        # Check pattern-matched responses
        for pattern, response in self._responses.items():
            if pattern.lower() in prompt.lower():
                return response

        return self.config.default_response

    async def ainvoke(self, prompt: str, **kwargs) -> str:
        """Async invoke."""
        import asyncio

        if self.config.response_delay > 0:
            await asyncio.sleep(self.config.response_delay)

        return self.invoke(prompt, **kwargs)

    def get_call_count(self) -> int:
        """Get number of times LLM was called."""
        return self._call_count

    def get_call_history(self) -> List[Dict[str, Any]]:
        """Get history of all calls."""
        return self._call_history.copy()

    def reset(self) -> None:
        """Reset mock state."""
        self._responses.clear()
        self._response_queue.clear()
        self._call_history.clear()
        self._call_count = 0


class MockTool:
    """
    Mock tool for testing.

    Usage:
        tool = MockTool("search")
        tool.set_response({"results": ["result1", "result2"]})

        result = tool.invoke("query")
    """

    def __init__(
        self,
        name: str,
        default_response: Optional[Any] = None
    ):
        self.name = name
        self.description = f"Mock {name} tool"
        self._default_response = default_response or {"status": "success"}
        self._responses: Dict[str, Any] = {}
        self._response_queue: List[Any] = []
        self._call_history: List[Dict[str, Any]] = []

    def set_response(self, response: Any, input_contains: Optional[str] = None) -> None:
        """Set response, optionally for specific input patterns."""
        if input_contains:
            self._responses[input_contains] = response
        else:
            self._default_response = response

    def queue_response(self, response: Any) -> None:
        """Queue a response."""
        self._response_queue.append(response)

    def invoke(self, input: Any, **kwargs) -> Any:
        """Invoke the mock tool."""
        self._call_history.append({
            "input": input,
            "kwargs": kwargs,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Check queue
        if self._response_queue:
            return self._response_queue.pop(0)

        # Check patterns
        input_str = str(input)
        for pattern, response in self._responses.items():
            if pattern.lower() in input_str.lower():
                return response

        return self._default_response

    async def ainvoke(self, input: Any, **kwargs) -> Any:
        """Async invoke."""
        return self.invoke(input, **kwargs)

    def get_call_history(self) -> List[Dict[str, Any]]:
        """Get call history."""
        return self._call_history.copy()

    def reset(self) -> None:
        """Reset mock state."""
        self._responses.clear()
        self._response_queue.clear()
        self._call_history.clear()


def mock_llm_response(
    content: str = "Mock response",
    model: str = "mock-model",
    usage: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Create a mock LLM response structure.

    Args:
        content: Response content
        model: Model name
        usage: Token usage info

    Returns:
        Mock response dictionary
    """
    return {
        "id": f"mock-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(datetime.utcnow().timestamp()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }
        ],
        "usage": usage or {
            "prompt_tokens": 50,
            "completion_tokens": 100,
            "total_tokens": 150
        }
    }


def mock_tool_result(
    tool_name: str,
    result: Any,
    success: bool = True
) -> Dict[str, Any]:
    """
    Create a mock tool result structure.

    Args:
        tool_name: Name of the tool
        result: Tool result
        success: Whether tool succeeded

    Returns:
        Mock tool result dictionary
    """
    return {
        "tool_name": tool_name,
        "tool_call_id": f"call_{uuid.uuid4()}",
        "result": result,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }


def mock_research_state(
    company_name: str = "TestCorp",
    include_financials: bool = True,
    include_competitors: bool = True,
    include_news: bool = True
) -> Dict[str, Any]:
    """
    Create a mock research state for testing.

    Args:
        company_name: Company name
        include_financials: Include financial data
        include_competitors: Include competitor data
        include_news: Include news data

    Returns:
        Mock research state dictionary
    """
    state = {
        "company_name": company_name,
        "messages": [],
        "research_data": {
            "overview": {
                "name": company_name,
                "description": f"Mock description for {company_name}",
                "industry": "Technology",
                "founded": "2020",
                "headquarters": "San Francisco, CA"
            }
        },
        "quality_score": 0.85,
        "confidence": 0.9,
        "sources": [
            {
                "url": f"https://example.com/{company_name.lower()}",
                "title": f"{company_name} Overview",
                "quality": "high"
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

    if include_financials:
        state["research_data"]["financials"] = {
            "revenue": "$1B",
            "profit": "$100M",
            "growth_rate": "15%",
            "market_cap": "$10B"
        }

    if include_competitors:
        state["research_data"]["competitors"] = [
            {"name": "Competitor A", "market_share": "30%"},
            {"name": "Competitor B", "market_share": "25%"},
            {"name": "Competitor C", "market_share": "20%"}
        ]

    if include_news:
        state["research_data"]["news"] = [
            {
                "title": f"{company_name} announces new product",
                "date": "2024-01-15",
                "sentiment": "positive"
            },
            {
                "title": f"{company_name} Q4 earnings beat expectations",
                "date": "2024-01-10",
                "sentiment": "positive"
            }
        ]

    return state
