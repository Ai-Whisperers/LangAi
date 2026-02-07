"""
Custom Agent Example

Demonstrates how to create a custom agent and integrate it into the
Phase 4 parallel multi-agent workflow.

This example creates a "News Agent" that specializes in finding recent
news and press releases about a company.

Usage:
    python examples/custom_agent.py
"""

from typing import Any, Dict, List

from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, StateGraph

from src.company_researcher.config import config
from src.company_researcher.prompts import NEWS_AGENT_PROMPT
from src.company_researcher.state import InputState, OutputState, OverallState

# ==============================================================================
# Custom Agent: News Agent
# ==============================================================================


def news_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    News Agent: Finds recent news and press releases.

    This agent specializes in:
    - Recent news articles (last 6 months)
    - Press releases
    - Major announcements
    - Media coverage

    Args:
        state: Current workflow state

    Returns:
        State updates with news analysis
    """
    print("[NEWS AGENT] Analyzing recent news and press releases...")

    # 1. Extract inputs from state
    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    # Filter for news-related sources
    news_sources = [
        r
        for r in search_results
        if any(
            keyword in r.get("url", "").lower()
            for keyword in ["news", "press", "announcement", "blog"]
        )
    ]

    # 2. Create prompt
    prompt = f"""You are a News Analysis specialist.

Company: {company_name}

Search Results:
{format_search_results(news_sources[:10])}

Analyze recent news and press releases. Focus on:
1. Major announcements (last 6 months)
2. Product launches
3. Funding/acquisition news
4. Leadership changes
5. Partnerships and collaborations

Format your analysis as a structured summary with dates and sources.
"""

    # 3. Call LLM
    llm = ChatAnthropic(
        model=config.llm_model,
        temperature=config.llm_temperature,
        max_tokens=config.llm_max_tokens,
        api_key=config.anthropic_api_key,
    )

    response = llm.invoke(prompt)

    # 4. Track costs
    input_tokens = response.usage_metadata.get("input_tokens", 0)
    output_tokens = response.usage_metadata.get("output_tokens", 0)
    cost = config.calculate_llm_cost(input_tokens, output_tokens)

    # 5. Return state updates
    return {
        "agent_outputs": {"news": response.content},
        "total_cost": cost,
        "total_tokens": {"input": input_tokens, "output": output_tokens},
    }


def format_search_results(results: List[Dict]) -> str:
    """Format search results for prompt."""
    formatted = []
    for i, result in enumerate(results, 1):
        formatted.append(
            f"{i}. {result.get('title', 'No title')}\n"
            f"   URL: {result.get('url', 'No URL')}\n"
            f"   {result.get('content', 'No content')[:200]}..."
        )
    return "\n\n".join(formatted)


# ==============================================================================
# Custom Workflow with News Agent
# ==============================================================================


def create_custom_workflow() -> StateGraph:
    """
    Create a workflow that includes the custom News Agent.

    This workflow adds the News Agent in parallel with the standard
    Financial, Market, and Product agents.
    """
    from src.company_researcher.agents.financial import financial_agent_node
    from src.company_researcher.agents.market import market_agent_node
    from src.company_researcher.agents.product import product_agent_node
    from src.company_researcher.agents.researcher import researcher_node
    from src.company_researcher.agents.synthesizer import synthesizer_node
    from src.company_researcher.quality.checker import check_quality_node
    from src.company_researcher.workflows.parallel_agent_research import (
        create_initial_state,
        save_report_node,
        should_continue_research,
    )

    # Create workflow
    workflow = StateGraph(OverallState, input=InputState, output=OutputState)

    # Add nodes
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("financial", financial_agent_node)
    workflow.add_node("market", market_agent_node)
    workflow.add_node("product", product_agent_node)
    workflow.add_node("news", news_agent_node)  # Custom agent
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("check_quality", check_quality_node)
    workflow.add_node("save_report", save_report_node)

    # Set entry point
    workflow.set_entry_point("researcher")

    # Fan-out to parallel agents (now includes news)
    workflow.add_edge("researcher", "financial")
    workflow.add_edge("researcher", "market")
    workflow.add_edge("researcher", "product")
    workflow.add_edge("researcher", "news")  # Custom agent

    # Fan-in to synthesizer
    workflow.add_edge("financial", "synthesizer")
    workflow.add_edge("market", "synthesizer")
    workflow.add_edge("product", "synthesizer")
    workflow.add_edge("news", "synthesizer")  # Custom agent

    # Continue workflow
    workflow.add_edge("synthesizer", "check_quality")

    # Conditional routing
    workflow.add_conditional_edges(
        "check_quality",
        should_continue_research,
        {"iterate": "researcher", "finish": "save_report"},
    )

    workflow.add_edge("save_report", END)

    return workflow.compile()


def research_with_news_agent(company_name: str) -> OutputState:
    """
    Research a company using the custom workflow with News Agent.

    Args:
        company_name: Name of company to research

    Returns:
        Research output with news analysis
    """
    print(f"=== Custom Workflow with News Agent ===")
    print(f"Company: {company_name}\n")

    # Create custom workflow
    workflow = create_custom_workflow()

    # Create initial state
    from src.company_researcher.workflows.parallel_agent_research import (
        create_initial_state,
        create_output_state,
    )

    initial_state = create_initial_state(company_name)

    # Execute workflow
    final_state = workflow.invoke(initial_state)

    # Create output
    output = create_output_state(final_state)

    # Display news analysis
    print("\n=== News Analysis ===")
    news_output = final_state.get("agent_outputs", {}).get("news", "No news analysis")
    print(news_output[:500] + "...")

    return output


def main():
    """Run custom agent example."""
    company_name = "OpenAI"

    # Research with custom News Agent
    result = research_with_news_agent(company_name)

    # Display results
    print(f"\n=== Research Complete ===")
    print(f"Quality Score: {result['quality_score']:.1f}/100")
    print(f"Total Cost: ${result['total_cost']:.4f}")
    print(f"Report saved: {result['report_path']}")

    return result


if __name__ == "__main__":
    result = main()
