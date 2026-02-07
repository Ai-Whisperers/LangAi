"""
Batch Processing for Anthropic API.

Provides batch API support for cost-effective processing of multiple
requests. Batch requests cost 50% less than real-time requests but
have higher latency.

Usage:
    from company_researcher.llm.batch_processor import get_batch_processor

    processor = get_batch_processor()

    # Create batch request
    batch_id = processor.create_batch([
        BatchRequest(
            custom_id="company_1",
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": "Analyze Tesla"}]
        ),
        BatchRequest(
            custom_id="company_2",
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": "Analyze Apple"}]
        )
    ])

    # Wait for completion
    results = processor.wait_for_batch(batch_id)
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Any, Callable, Dict, List, Optional

from anthropic import Anthropic

from ..utils import utc_now
from .client_factory import get_anthropic_client


@dataclass
class BatchRequest:
    """Single request in a batch."""

    custom_id: str
    model: str
    max_tokens: int
    messages: List[Dict[str, Any]]
    system: Optional[str] = None
    temperature: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchResult:
    """Result from a single batch request."""

    custom_id: str
    status: str  # success, error
    content: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "custom_id": self.custom_id,
            "status": self.status,
            "content": self.content,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class BatchStatus:
    """Status of a batch job."""

    batch_id: str
    status: str  # created, in_progress, ended, canceling, canceled
    total_requests: int = 0
    completed_requests: int = 0
    failed_requests: int = 0
    created_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    @property
    def is_complete(self) -> bool:
        return self.status in ("ended", "canceled")

    @property
    def progress_percent(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.completed_requests + self.failed_requests) / self.total_requests * 100


class BatchProcessor:
    """
    Handles batch API requests for cost optimization.

    Batch requests are processed asynchronously and cost 50% less
    than real-time API calls.
    """

    def __init__(self, client: Optional[Anthropic] = None):
        """
        Initialize the batch processor.

        Args:
            client: Optional Anthropic client
        """
        self.client = client or get_anthropic_client()
        self._active_batches: Dict[str, BatchStatus] = {}
        self._lock = Lock()

    def create_batch(
        self, requests: List[BatchRequest], metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a batch of requests.

        Args:
            requests: List of BatchRequest objects
            metadata: Optional batch-level metadata

        Returns:
            Batch ID for tracking

        Note:
            Batch processing has minimum and maximum limits.
            Check Anthropic documentation for current limits.
        """
        # Format requests for batch API
        batch_requests = []
        for req in requests:
            params = {
                "model": req.model,
                "max_tokens": req.max_tokens,
                "temperature": req.temperature,
                "messages": req.messages,
            }
            if req.system:
                params["system"] = req.system

            batch_requests.append({"custom_id": req.custom_id, "params": params})

        # Create batch
        batch = self.client.messages.batches.create(requests=batch_requests)

        # Track batch
        with self._lock:
            self._active_batches[batch.id] = BatchStatus(
                batch_id=batch.id,
                status="created",
                total_requests=len(requests),
                created_at=utc_now(),
            )

        return batch.id

    def get_batch_status(self, batch_id: str) -> BatchStatus:
        """
        Get current status of a batch.

        Args:
            batch_id: Batch identifier

        Returns:
            BatchStatus object
        """
        batch = self.client.messages.batches.retrieve(batch_id)

        status = BatchStatus(
            batch_id=batch.id,
            status=batch.processing_status,
            total_requests=batch.request_counts.total if hasattr(batch, "request_counts") else 0,
            completed_requests=(
                batch.request_counts.succeeded if hasattr(batch, "request_counts") else 0
            ),
            failed_requests=batch.request_counts.errored if hasattr(batch, "request_counts") else 0,
            created_at=batch.created_at if hasattr(batch, "created_at") else None,
            ended_at=batch.ended_at if hasattr(batch, "ended_at") else None,
        )

        # Update tracking
        with self._lock:
            self._active_batches[batch_id] = status

        return status

    def wait_for_batch(
        self,
        batch_id: str,
        poll_interval: int = 30,
        timeout: int = 3600,
        on_progress: Optional[Callable[[BatchStatus], None]] = None,
    ) -> Dict[str, BatchResult]:
        """
        Wait for batch to complete and return results.

        Args:
            batch_id: Batch identifier
            poll_interval: Seconds between status checks
            timeout: Maximum wait time in seconds
            on_progress: Optional callback for progress updates

        Returns:
            Dictionary mapping custom_id to BatchResult

        Raises:
            TimeoutError: If batch doesn't complete within timeout
        """
        start_time = time.time()

        while True:
            status = self.get_batch_status(batch_id)

            if on_progress:
                on_progress(status)

            if status.is_complete:
                return self._get_batch_results(batch_id)

            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Batch {batch_id} did not complete within {timeout}s. "
                    f"Status: {status.status}, Progress: {status.progress_percent:.1f}%"
                )

            time.sleep(poll_interval)

    def _get_batch_results(self, batch_id: str) -> Dict[str, BatchResult]:
        """
        Retrieve results from completed batch.

        Args:
            batch_id: Batch identifier

        Returns:
            Dictionary mapping custom_id to BatchResult
        """
        results = {}

        # Stream results from batch
        for result in self.client.messages.batches.results(batch_id):
            custom_id = result.custom_id

            if result.result.type == "succeeded":
                message = result.result.message
                results[custom_id] = BatchResult(
                    custom_id=custom_id,
                    status="success",
                    content=message.content[0].text if message.content else None,
                    input_tokens=message.usage.input_tokens,
                    output_tokens=message.usage.output_tokens,
                )
            else:
                results[custom_id] = BatchResult(
                    custom_id=custom_id,
                    status="error",
                    error=(
                        str(result.result.error)
                        if hasattr(result.result, "error")
                        else "Unknown error"
                    ),
                )

        return results

    def cancel_batch(self, batch_id: str) -> bool:
        """
        Cancel a running batch.

        Args:
            batch_id: Batch identifier

        Returns:
            True if cancellation initiated
        """
        try:
            self.client.messages.batches.cancel(batch_id)
            return True
        except Exception:
            return False

    def list_active_batches(self) -> List[BatchStatus]:
        """
        List all tracked active batches.

        Returns:
            List of BatchStatus objects
        """
        with self._lock:
            return list(self._active_batches.values())

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def process_companies_batch(
        self,
        companies: List[str],
        prompt_template: str,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        wait: bool = True,
        on_progress: Optional[Callable[[BatchStatus], None]] = None,
    ) -> Dict[str, BatchResult]:
        """
        Process multiple companies in a single batch.

        Args:
            companies: List of company names
            prompt_template: Prompt template with {company_name} placeholder
            model: Model to use
            max_tokens: Maximum tokens per response
            system_prompt: Optional system prompt
            wait: Whether to wait for completion
            on_progress: Progress callback

        Returns:
            Results dictionary (if wait=True) or batch_id (if wait=False)
        """
        requests = []
        for i, company in enumerate(companies):
            requests.append(
                BatchRequest(
                    custom_id=f"company_{i}_{company.replace(' ', '_').lower()}",
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt_template.format(company_name=company)}
                    ],
                    metadata={"company": company},
                )
            )

        batch_id = self.create_batch(requests)
        print(f"[Batch] Created batch {batch_id} with {len(requests)} requests")

        if wait:
            return self.wait_for_batch(batch_id, on_progress=on_progress)
        else:
            return {"batch_id": batch_id}

    def batch_financial_analysis(
        self,
        companies: List[str],
        search_results_map: Dict[str, str],
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 1200,
    ) -> Dict[str, BatchResult]:
        """
        Batch financial analysis for multiple companies.

        Args:
            companies: List of company names
            search_results_map: Map of company name to search results
            model: Model to use
            max_tokens: Maximum tokens per response

        Returns:
            Results dictionary
        """
        system_prompt = """You are a financial analyst extracting financial data.

Focus on:
1. Revenue (annual, quarterly, growth rates)
2. Profitability (margins, net income)
3. Funding/Valuation
4. Key financial metrics

Be specific with numbers and dates. Cite sources."""

        requests = []
        for company in companies:
            search_results = search_results_map.get(company, "No search results available")

            requests.append(
                BatchRequest(
                    custom_id=f"financial_{company.replace(' ', '_').lower()}",
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Company: {company}\n\nSearch Results:\n{search_results}\n\nExtract financial data:",
                        }
                    ],
                    metadata={"company": company, "analysis_type": "financial"},
                )
            )

        batch_id = self.create_batch(requests)
        print(f"[Batch Financial] Created batch {batch_id}")

        return self.wait_for_batch(batch_id)

    def calculate_batch_cost_savings(
        self, results: Dict[str, BatchResult], model: str = "claude-sonnet-4-20250514"
    ) -> Dict[str, float]:
        """
        Calculate cost savings from using batch API.

        Args:
            results: Batch results
            model: Model used

        Returns:
            Cost comparison dictionary
        """
        from .cost_tracker import CostTracker

        pricing = CostTracker.PRICING.get(model, CostTracker.DEFAULT_PRICING)

        total_input = sum(r.input_tokens for r in results.values() if r.status == "success")
        total_output = sum(r.output_tokens for r in results.values() if r.status == "success")

        # Regular pricing
        regular_cost = (total_input / 1_000_000) * pricing["input"]
        regular_cost += (total_output / 1_000_000) * pricing["output"]

        # Batch pricing (50% off)
        batch_cost = (total_input / 1_000_000) * pricing["batch_input"]
        batch_cost += (total_output / 1_000_000) * pricing["batch_output"]

        return {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "regular_cost": regular_cost,
            "batch_cost": batch_cost,
            "savings": regular_cost - batch_cost,
            "savings_percent": (
                ((regular_cost - batch_cost) / regular_cost * 100) if regular_cost > 0 else 0
            ),
        }


# Singleton instance
_batch_processor: Optional[BatchProcessor] = None
_processor_lock = Lock()


def get_batch_processor() -> BatchProcessor:
    """
    Get singleton batch processor instance.

    Returns:
        BatchProcessor instance
    """
    global _batch_processor
    if _batch_processor is None:
        with _processor_lock:
            if _batch_processor is None:
                _batch_processor = BatchProcessor()
    return _batch_processor


def reset_batch_processor() -> None:
    """Reset batch processor instance (for testing)."""
    global _batch_processor
    _batch_processor = None
