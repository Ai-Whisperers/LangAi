"""
Groq API integration for ultra-fast inference.

Groq's LPU (Language Processing Unit) provides 10-100x faster inference
than GPU-based solutions, making it ideal for real-time applications.

Speed: 1,300+ tokens/second (Llama 3.1 8B)
Pricing (per 1M tokens):
- Llama 3.1 8B: $0.05 input, $0.08 output
- Llama 3.1 70B: $0.59 input, $0.79 output
- Llama 3.1 405B: $3.00 input, $3.00 output

Usage:
    from company_researcher.llm.groq_client import get_groq_client

    client = get_groq_client()

    # Ultra-fast query (1,300 tok/sec)
    result = client.fast_query("What is Tesla's market cap?")

    # Real-time company lookup
    info = client.quick_company_info("NVIDIA")
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from threading import Lock
from datetime import datetime
import logging
import json
import os

logger = logging.getLogger(__name__)

# Try to import groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("groq not installed. Run: pip install groq")


# Pricing per 1M tokens
GROQ_PRICING = {
    "llama-3.1-8b-instant": {
        "input": 0.05,
        "output": 0.08,
        "speed": 1300,  # tokens/sec
        "context_window": 128000
    },
    "llama-3.1-70b-versatile": {
        "input": 0.59,
        "output": 0.79,
        "speed": 814,
        "context_window": 128000
    },
    "llama-3.1-405b-reasoning": {
        "input": 3.00,
        "output": 3.00,
        "speed": 200,  # approximate
        "context_window": 8192
    },
    "llama-3.2-1b-preview": {
        "input": 0.04,
        "output": 0.04,
        "speed": 2000,  # fastest
        "context_window": 128000
    },
    "llama-3.2-3b-preview": {
        "input": 0.06,
        "output": 0.06,
        "speed": 1800,
        "context_window": 128000
    },
    "mixtral-8x7b-32768": {
        "input": 0.24,
        "output": 0.24,
        "speed": 500,
        "context_window": 32768
    },
    "gemma2-9b-it": {
        "input": 0.20,
        "output": 0.20,
        "speed": 600,
        "context_window": 8192
    }
}


@dataclass
class GroqResponse:
    """Response from Groq API."""
    content: str
    input_tokens: int
    output_tokens: int
    model: str
    cost: float
    latency_ms: Optional[float] = None
    tokens_per_second: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "model": self.model,
            "cost": self.cost,
            "latency_ms": self.latency_ms,
            "tokens_per_second": self.tokens_per_second
        }


class GroqClient:
    """
    Groq API client for ultra-fast inference.

    Groq's LPU technology provides deterministic, ultra-low latency
    inference. Ideal for real-time applications and interactive features.

    Speed comparison:
    - Groq Llama 8B: 1,300 tokens/sec
    - GPU-based: 50-100 tokens/sec
    - 10-100x faster inference
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "llama-3.1-70b-versatile"
    ):
        """
        Initialize Groq client.

        Args:
            api_key: Groq API key (or GROQ_API_KEY env var)
            default_model: Default model to use
        """
        if not GROQ_AVAILABLE:
            raise ImportError("groq not installed. Run: pip install groq")

        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("Groq API key not found. Set GROQ_API_KEY env var.")

        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.default_model = default_model
        self._total_cost = 0.0
        self._total_calls = 0
        self._total_latency_ms = 0.0
        self._lock = Lock()

    def fast_query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.0,
        json_mode: bool = False
    ) -> GroqResponse:
        """
        Ultra-fast completion (1,300+ tok/sec).

        Ideal for real-time company lookups and interactive features.

        Args:
            prompt: User prompt
            system: System prompt
            model: Model to use
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            json_mode: Enable JSON output mode

        Returns:
            GroqResponse with content and performance metrics
        """
        if not self.client:
            raise ValueError("Groq client not initialized. Set GROQ_API_KEY.")

        model = model or self.default_model
        messages = []

        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        import time
        start_time = time.time()

        response = self.client.chat.completions.create(**kwargs)

        latency_ms = (time.time() - start_time) * 1000

        # Calculate cost
        pricing = GROQ_PRICING.get(model, GROQ_PRICING["llama-3.1-70b-versatile"])
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        cost = (input_tokens / 1_000_000) * pricing["input"]
        cost += (output_tokens / 1_000_000) * pricing["output"]

        # Calculate tokens per second
        total_tokens = input_tokens + output_tokens
        tokens_per_second = (total_tokens / latency_ms) * 1000 if latency_ms > 0 else 0

        # Track totals
        with self._lock:
            self._total_cost += cost
            self._total_calls += 1
            self._total_latency_ms += latency_ms

        return GroqResponse(
            content=response.choices[0].message.content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost=cost,
            latency_ms=latency_ms,
            tokens_per_second=tokens_per_second
        )

    def quick_company_info(
        self,
        company_name: str,
        fields: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Quick company information lookup.

        Ultra-fast for real-time UI updates.

        Args:
            company_name: Company to look up
            fields: Specific fields to return

        Returns:
            Dict with company info
        """
        default_fields = [
            "full_name", "industry", "founded", "headquarters",
            "ceo", "employees", "description"
        ]
        fields = fields or default_fields

        prompt = f"""Provide brief information about {company_name}:
Return JSON with these fields: {', '.join(fields)}
Use null for unknown fields. Be concise."""

        response = self.fast_query(
            prompt=prompt,
            system="You are a company database. Return valid JSON only.",
            model=model or "llama-3.1-8b-instant",  # Use fastest model
            max_tokens=500,
            json_mode=True
        )

        try:
            data = json.loads(response.content)
            data["_meta"] = {
                "latency_ms": response.latency_ms,
                "tokens_per_second": response.tokens_per_second,
                "cost": response.cost
            }
            return data
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse JSON",
                "raw_content": response.content,
                "_meta": {"latency_ms": response.latency_ms}
            }

    def fast_extract(
        self,
        text: str,
        extraction_prompt: str,
        model: Optional[str] = None
    ) -> GroqResponse:
        """
        Fast structured extraction.

        Args:
            text: Text to extract from
            extraction_prompt: What to extract

        Returns:
            GroqResponse
        """
        return self.fast_query(
            prompt=f"{extraction_prompt}\n\nText:\n{text}",
            system="Extract the requested information. Be precise and concise.",
            model=model or "llama-3.1-8b-instant",
            max_tokens=1000
        )

    def fast_classify(
        self,
        text: str,
        categories: List[str],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ultra-fast text classification.

        Args:
            text: Text to classify
            categories: List of possible categories

        Returns:
            Dict with category and confidence
        """
        categories_str = ", ".join(categories)

        prompt = f"""Classify this text into one of these categories: {categories_str}

Text: {text}

Return JSON with:
- category: one of the categories above
- confidence: 0-1 score
- reasoning: brief explanation"""

        response = self.fast_query(
            prompt=prompt,
            model=model or "llama-3.1-8b-instant",
            max_tokens=200,
            json_mode=True
        )

        try:
            result = json.loads(response.content)
            result["_meta"] = {
                "latency_ms": response.latency_ms,
                "cost": response.cost
            }
            return result
        except json.JSONDecodeError:
            return {
                "category": "unknown",
                "confidence": 0,
                "error": "Failed to parse response",
                "_meta": {"latency_ms": response.latency_ms}
            }

    def batch_fast_queries(
        self,
        prompts: List[str],
        system: Optional[str] = None,
        model: Optional[str] = None
    ) -> List[GroqResponse]:
        """
        Process multiple queries quickly.

        Args:
            prompts: List of prompts to process
            system: Shared system prompt
            model: Model to use

        Returns:
            List of GroqResponse objects
        """
        results = []
        for prompt in prompts:
            result = self.fast_query(
                prompt=prompt,
                system=system,
                model=model or "llama-3.1-8b-instant",
                max_tokens=1000
            )
            results.append(result)
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get usage and performance statistics."""
        with self._lock:
            avg_latency = self._total_latency_ms / self._total_calls if self._total_calls > 0 else 0
            return {
                "total_calls": self._total_calls,
                "total_cost": self._total_cost,
                "total_latency_ms": self._total_latency_ms,
                "avg_latency_ms": avg_latency,
                "avg_cost_per_call": self._total_cost / self._total_calls if self._total_calls > 0 else 0
            }

    def reset_stats(self) -> None:
        """Reset usage statistics."""
        with self._lock:
            self._total_cost = 0.0
            self._total_calls = 0
            self._total_latency_ms = 0.0


# Singleton instance
_groq_client: Optional[GroqClient] = None
_client_lock = Lock()


def get_groq_client() -> GroqClient:
    """Get singleton Groq client instance."""
    global _groq_client
    if _groq_client is None:
        with _client_lock:
            if _groq_client is None:
                _groq_client = GroqClient()
    return _groq_client


def reset_groq_client() -> None:
    """Reset Groq client instance (for testing)."""
    global _groq_client
    _groq_client = None
