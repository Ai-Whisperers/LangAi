"""
Base Agent Node - Common functionality for agent node functions.

Provides decorators and base functions to eliminate duplication
across the 19 agent node functions.
"""

from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, List, TypeVar, cast

from ...config import get_config
from ...llm.client_factory import calculate_cost, get_anthropic_client, safe_extract_text
from ...state import OverallState
from .logger import get_agent_logger
from .types import AgentResult, AgentStatus, create_agent_result, create_empty_result

F = TypeVar("F", bound=Callable[..., Dict[str, Any]])


@dataclass
class NodeConfig:
    """Configuration for an agent node."""

    agent_name: str
    max_tokens: int = 1000
    temperature: float = 0.0
    max_sources: int = 15
    content_truncate_length: int = 500
    require_search_results: bool = True


def format_search_results(
    results: List[Dict[str, Any]], max_sources: int = 15, content_length: int = 500
) -> str:
    """
    Format search results for LLM analysis.

    Args:
        results: List of search result dictionaries
        max_sources: Maximum number of sources to include
        content_length: Length to truncate content to

    Returns:
        Formatted string of search results
    """
    formatted = []
    for i, result in enumerate(results[:max_sources]):
        title = result.get("title", "N/A")
        url = result.get("url", "N/A")
        content = result.get("content", "N/A")

        # Safely truncate content
        if isinstance(content, str) and len(content) > content_length:
            content = content[:content_length] + "..."

        formatted.append(f"Source {i+1}: {title}\n" f"URL: {url}\n" f"Content: {content}")

    return "\n\n".join(formatted)


def agent_node(
    agent_name: str,
    max_tokens: int = 1000,
    temperature: float = 0.0,
    max_sources: int = 15,
    content_truncate_length: int = 500,
    require_search_results: bool = True,
):
    """
    Decorator for creating standardized agent node functions.

    Handles common operations:
    - Logging (start/end with separators)
    - Search result validation
    - Cost calculation
    - Token tracking
    - Error handling

    Usage:
        @agent_node("financial", max_tokens=800)
        def financial_agent_node(state, logger, client, config, formatted_results):
            # Only implement the core logic
            prompt = PROMPT.format(...)
            response = client.messages.create(...)
            return response.content[0].text

    Args:
        agent_name: Name of the agent (e.g., "financial")
        max_tokens: Maximum tokens for LLM response
        temperature: LLM temperature
        max_sources: Maximum search results to process
        content_truncate_length: Length to truncate content
        require_search_results: Whether to require search results

    Returns:
        Decorated function
    """

    def decorator(func: F) -> Callable[[OverallState], AgentResult]:
        @wraps(func)
        def wrapper(state: OverallState) -> AgentResult:
            logger = get_agent_logger(agent_name)
            app_config = get_config()
            client = get_anthropic_client()

            company_name = state.get("company_name", "Unknown")
            search_results = state.get("search_results", [])

            with logger.agent_run(company_name):
                # Check for search results if required
                if require_search_results and not search_results:
                    logger.no_data()
                    return create_empty_result(agent_name)

                logger.analyzing(len(search_results))

                # Format search results
                formatted_results = format_search_results(
                    search_results, max_sources=max_sources, content_length=content_truncate_length
                )

                # Create node config
                node_config = NodeConfig(
                    agent_name=agent_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    max_sources=max_sources,
                    content_truncate_length=content_truncate_length,
                )

                try:
                    # Call the actual agent function
                    result = func(
                        state=state,
                        logger=logger,
                        client=client,
                        config=app_config,
                        node_config=node_config,
                        formatted_results=formatted_results,
                        company_name=company_name,
                    )

                    # If result is just a string (analysis text), wrap it
                    if isinstance(result, str):
                        # Need to track tokens - do a simple estimate
                        # In real usage, the func should return full response
                        return create_agent_result(
                            agent_name=agent_name,
                            analysis=result,
                            input_tokens=0,
                            output_tokens=0,
                            cost=0.0,
                            sources_used=len(search_results),
                        )

                    # If result is a response object with usage
                    if hasattr(result, "content") and hasattr(result, "usage"):
                        analysis = result.content[0].text
                        cost = calculate_cost(result.usage.input_tokens, result.usage.output_tokens)
                        logger.complete(cost=cost)

                        return create_agent_result(
                            agent_name=agent_name,
                            analysis=analysis,
                            input_tokens=result.usage.input_tokens,
                            output_tokens=result.usage.output_tokens,
                            cost=cost,
                            sources_used=min(len(search_results), max_sources),
                        )

                    # If result is already an AgentResult dict
                    if isinstance(result, dict) and "agent_outputs" in result:
                        return cast(AgentResult, result)

                    # Fallback
                    logger.warning("Unexpected result type from agent function")
                    return create_empty_result(agent_name, "Unexpected result format")

                except Exception as e:
                    logger.error(f"Agent execution failed: {e}", exc_info=True)
                    return create_empty_result(
                        agent_name, f"Agent error: {str(e)}", status=AgentStatus.ERROR
                    )

        return wrapper

    return decorator


class BaseAgentNode:
    """
    Base class for agent nodes that prefer class-based implementation.

    Usage:
        class FinancialAgentNode(BaseAgentNode):
            agent_name = "financial"
            max_tokens = 800

            def get_prompt(self, company_name, formatted_results):
                return FINANCIAL_PROMPT.format(...)

            def process_response(self, response_text, state):
                return response_text  # or custom processing
    """

    agent_name: str = "base"
    max_tokens: int = 1000
    temperature: float = 0.0
    max_sources: int = 15
    content_truncate_length: int = 500
    require_search_results: bool = True

    def __init__(self):
        self.logger = get_agent_logger(self.agent_name)
        self.config = get_config()
        self.client = get_anthropic_client()

    def get_prompt(self, company_name: str, formatted_results: str, **kwargs) -> str:
        """Override to provide the analysis prompt."""
        raise NotImplementedError("Subclass must implement get_prompt()")

    def process_response(self, response_text: str, state: OverallState) -> str:
        """Override to post-process response. Default returns as-is."""
        return response_text

    def __call__(self, state: OverallState) -> AgentResult:
        """Execute the agent node."""
        company_name = state.get("company_name", "Unknown")
        search_results = state.get("search_results", [])

        with self.logger.agent_run(company_name):
            # Check for search results
            if self.require_search_results and not search_results:
                self.logger.no_data()
                return create_empty_result(self.agent_name)

            self.logger.analyzing(len(search_results))

            # Format search results
            formatted_results = format_search_results(
                search_results,
                max_sources=self.max_sources,
                content_length=self.content_truncate_length,
            )

            try:
                # Get prompt
                prompt = self.get_prompt(company_name, formatted_results, state=state)

                # Call LLM
                response = self.client.messages.create(
                    model=self.config.llm_model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}],
                )

                # Calculate cost
                cost = calculate_cost(response.usage.input_tokens, response.usage.output_tokens)

                # Process response
                response_text = safe_extract_text(response, agent_name=self.agent_name)
                analysis = self.process_response(response_text, state)

                self.logger.complete(cost=cost)

                return create_agent_result(
                    agent_name=self.agent_name,
                    analysis=analysis,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    cost=cost,
                    sources_used=min(len(search_results), self.max_sources),
                )

            except Exception as e:
                self.logger.error(f"Agent execution failed: {e}", exc_info=True)
                return create_empty_result(
                    self.agent_name, f"Agent error: {str(e)}", status=AgentStatus.ERROR
                )
