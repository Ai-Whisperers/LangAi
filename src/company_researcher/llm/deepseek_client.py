"""
DeepSeek API integration for ultra-low-cost bulk processing.

DeepSeek-V3 provides frontier model performance at 99% lower cost than Claude/GPT-4.

Pricing (per 1M tokens):
- Input: $0.14 (cache hit: $0.014)
- Output: $0.27

Off-peak discount: 50-75% additional savings

Usage:
    from company_researcher.llm.deepseek_client import get_deepseek_client

    client = get_deepseek_client()

    # Simple completion
    result = client.create_message("Analyze Tesla's market position")

    # Bulk extraction
    data = client.extract_company_data(
        company_name="Apple",
        search_results="...",
        fields=["revenue", "employees", "market_cap"]
    )
"""

from openai import OpenAI  # DeepSeek uses OpenAI-compatible API
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from threading import Lock
from datetime import datetime
import logging
import json
import os

logger = logging.getLogger(__name__)


# Pricing per 1M tokens
DEEPSEEK_PRICING = {
    "deepseek-chat": {  # V3
        "input": 0.14,
        "output": 0.27,
        "cache_hit": 0.014,  # 90% discount for cached
        "context_window": 128000,
        "max_output": 8000
    },
    "deepseek-reasoner": {  # R1 - reasoning model
        "input": 0.55,
        "output": 2.19,
        "cache_hit": 0.14,
        "context_window": 128000,
        "max_output": 8000
    }
}


@dataclass
class DeepSeekResponse:
    """Response from DeepSeek API."""
    content: str
    input_tokens: int
    output_tokens: int
    model: str
    cost: float
    cached_tokens: int = 0
    reasoning_tokens: int = 0  # For R1 model

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "model": self.model,
            "cost": self.cost,
            "cached_tokens": self.cached_tokens,
            "reasoning_tokens": self.reasoning_tokens
        }


class DeepSeekClient:
    """
    DeepSeek API client for cost-effective bulk processing.

    Uses OpenAI-compatible API format.
    99% cheaper than Claude/GPT-4 with comparable quality.

    Models:
    - deepseek-chat (V3): General purpose, best value
    - deepseek-reasoner (R1): Complex reasoning tasks
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        default_model: str = "deepseek-chat"
    ):
        """
        Initialize DeepSeek client.

        Args:
            api_key: DeepSeek API key (or DEEPSEEK_API_KEY env var)
            base_url: API base URL
            default_model: Default model to use
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            logger.warning("DeepSeek API key not found. Set DEEPSEEK_API_KEY env var.")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        ) if self.api_key else None

        self.default_model = default_model
        self._total_cost = 0.0
        self._total_calls = 0
        self._lock = Lock()

    def create_message(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.0,
        json_mode: bool = False
    ) -> DeepSeekResponse:
        """
        Create a completion with DeepSeek.

        Args:
            prompt: User prompt
            system: System prompt
            model: Model to use (default: deepseek-chat)
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            json_mode: Enable JSON output mode

        Returns:
            DeepSeekResponse with content and usage
        """
        if not self.client:
            raise ValueError("DeepSeek client not initialized. Set DEEPSEEK_API_KEY.")

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

        response = self.client.chat.completions.create(**kwargs)

        # Calculate cost
        pricing = DEEPSEEK_PRICING.get(model, DEEPSEEK_PRICING["deepseek-chat"])
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cached_tokens = getattr(response.usage, 'prompt_cache_hit_tokens', 0)

        # Cost calculation
        uncached_input = input_tokens - cached_tokens
        cost = (uncached_input / 1_000_000) * pricing["input"]
        cost += (cached_tokens / 1_000_000) * pricing["cache_hit"]
        cost += (output_tokens / 1_000_000) * pricing["output"]

        # Track totals
        with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return DeepSeekResponse(
            content=response.choices[0].message.content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=response.model,
            cost=cost,
            cached_tokens=cached_tokens
        )

    def extract_company_data(
        self,
        company_name: str,
        search_results: str,
        fields: List[str],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured company data.

        Cost-effective for bulk extraction tasks.

        Args:
            company_name: Company to extract data for
            search_results: Raw search results text
            fields: List of fields to extract

        Returns:
            Dict with extracted fields
        """
        fields_list = "\n".join(f"- {field}" for field in fields)

        prompt = f"""Extract the following fields for {company_name}:
{fields_list}

Search Results:
{search_results}

Return valid JSON with the extracted fields. Use null for missing data.
Include a "confidence" field (0-1) for each extracted value."""

        response = self.create_message(
            prompt=prompt,
            system="You are a data extraction specialist. Return valid JSON only.",
            model=model,
            max_tokens=2000,
            json_mode=True
        )

        try:
            data = json.loads(response.content)
            data["_meta"] = {
                "model": response.model,
                "cost": response.cost,
                "tokens": response.input_tokens + response.output_tokens
            }
            return data
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse JSON",
                "raw_content": response.content,
                "_meta": {"model": response.model, "cost": response.cost}
            }

    def analyze_financials(
        self,
        company_name: str,
        financial_data: str,
        model: Optional[str] = None
    ) -> DeepSeekResponse:
        """
        Analyze company financials.

        Args:
            company_name: Company name
            financial_data: Raw financial data/text

        Returns:
            DeepSeekResponse with analysis
        """
        prompt = f"""Analyze the financial data for {company_name}:

{financial_data}

Provide:
1. Revenue analysis (trends, growth rates)
2. Profitability assessment (margins, efficiency)
3. Key financial metrics
4. Notable concerns or highlights
5. Comparison to industry if data available

Be specific with numbers and cite sources."""

        return self.create_message(
            prompt=prompt,
            system="You are a senior financial analyst. Provide objective, data-driven analysis.",
            model=model,
            max_tokens=3000
        )

    def batch_extract(
        self,
        items: List[Dict[str, Any]],
        extraction_prompt: str,
        model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract data from multiple items.

        Args:
            items: List of items with 'id' and 'content' keys
            extraction_prompt: Prompt template with {content} placeholder
            model: Model to use

        Returns:
            List of extraction results
        """
        results = []

        for item in items:
            prompt = extraction_prompt.format(content=item.get("content", ""))

            response = self.create_message(
                prompt=prompt,
                model=model,
                max_tokens=1500,
                json_mode=True
            )

            try:
                data = json.loads(response.content)
            except json.JSONDecodeError:
                data = {"raw": response.content}

            results.append({
                "id": item.get("id"),
                "data": data,
                "cost": response.cost,
                "tokens": response.input_tokens + response.output_tokens
            })

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with self._lock:
            return {
                "total_calls": self._total_calls,
                "total_cost": self._total_cost,
                "avg_cost_per_call": self._total_cost / self._total_calls if self._total_calls > 0 else 0
            }

    def reset_stats(self) -> None:
        """Reset usage statistics."""
        with self._lock:
            self._total_cost = 0.0
            self._total_calls = 0


# Singleton instance
_deepseek_client: Optional[DeepSeekClient] = None
_client_lock = Lock()


def get_deepseek_client() -> DeepSeekClient:
    """Get singleton DeepSeek client instance."""
    global _deepseek_client
    if _deepseek_client is None:
        with _client_lock:
            if _deepseek_client is None:
                _deepseek_client = DeepSeekClient()
    return _deepseek_client


def reset_deepseek_client() -> None:
    """Reset DeepSeek client instance (for testing)."""
    global _deepseek_client
    _deepseek_client = None
