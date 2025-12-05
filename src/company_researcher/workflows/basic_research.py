"""
Basic Research Workflow - Phase 1

This module implements a single-agent LangGraph workflow for company research.

Workflow:
    Input → Generate Queries → Search → Analyze → Extract Data → Save Report → Output
"""

import json
import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from anthropic import Anthropic
from tavily import TavilyClient
from langgraph.graph import StateGraph, END

from ..state import OverallState, InputState, OutputState, create_initial_state, create_output_state
from ..config import get_config
from ..prompts import (
    GENERATE_QUERIES_PROMPT,
    ANALYZE_RESULTS_PROMPT,
    EXTRACT_DATA_PROMPT,
    GENERATE_REPORT_TEMPLATE,
    format_search_results_for_analysis,
    format_sources_for_extraction,
    format_sources_for_report
)
from ..quality import check_research_quality


# ============================================================================
# Workflow Nodes
# ============================================================================

def generate_queries_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 1: Generate search queries for the company.

    Args:
        state: Current workflow state

    Returns:
        State update with generated queries
    """
    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    print(f"\n[NODE] Generating {config.num_search_queries} search queries...")

    # Create prompt
    prompt = GENERATE_QUERIES_PROMPT.format(
        company_name=state["company_name"],
        num_queries=config.num_search_queries
    )

    # Call Claude
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=500,
        temperature=config.llm_temperature,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse response
    content = response.content[0].text
    try:
        # Extract JSON array from response
        # Claude might wrap it in markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        queries = json.loads(content.strip())
    except json.JSONDecodeError:
        # Fallback: use default queries
        print("[WARN] Failed to parse queries, using defaults")
        queries = [
            f"{state['company_name']} company overview",
            f"{state['company_name']} revenue 2024",
            f"{state['company_name']} products services",
            f"{state['company_name']} competitors",
            f"{state['company_name']} latest news"
        ]

    # Update cost
    cost = config.calculate_llm_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    print(f"[OK] Generated {len(queries)} queries")
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")

    return {
        "search_queries": queries,
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": {
            "input": state.get("total_tokens", {"input": 0, "output": 0})["input"] + response.usage.input_tokens,
            "output": state.get("total_tokens", {"input": 0, "output": 0})["output"] + response.usage.output_tokens
        }
    }


def search_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 2: Execute searches sequentially (parallel in Phase 2).

    Args:
        state: Current workflow state

    Returns:
        State update with search results and sources
    """
    config = get_config()
    client = TavilyClient(api_key=config.tavily_api_key)

    print(f"\n[NODE] Executing {len(state['search_queries'])} searches...")

    # Execute searches sequentially (simpler for Phase 1)
    all_results = []
    for query in state["search_queries"]:
        print(f"  [SEARCH] {query}")
        results = client.search(
            query=query,
            max_results=config.search_results_per_query
        )
        all_results.append(results.get("results", []))

    # Flatten results
    search_results = []
    sources = []

    for results in all_results:
        for result in results:
            search_results.append(result)
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "score": result.get("score", 0.0)
            })

    # Limit to max results
    search_results = search_results[:config.max_search_results]
    sources = sources[:config.max_search_results]

    # Calculate Tavily cost (approximate)
    tavily_cost = len(state["search_queries"]) * 0.001

    print(f"[OK] Found {len(search_results)} total results")

    return {
        "search_results": search_results,
        "sources": sources,
        "total_cost": state.get("total_cost", 0.0) + tavily_cost
    }


def analyze_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 3: Analyze search results with Claude.

    Args:
        state: Current workflow state

    Returns:
        State update with analysis notes
    """
    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    print("\n[NODE] Analyzing search results...")

    # Format search results for prompt
    formatted_results = format_search_results_for_analysis(state["search_results"])

    # Create prompt
    prompt = ANALYZE_RESULTS_PROMPT.format(
        company_name=state["company_name"],
        search_results=formatted_results
    )

    # Call Claude
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=config.llm_max_tokens,
        temperature=config.llm_temperature,
        messages=[{"role": "user", "content": prompt}]
    )

    notes = response.content[0].text

    # Update cost
    cost = config.calculate_llm_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    print("[OK] Analysis complete")

    return {
        "notes": [notes],
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": {
            "input": state.get("total_tokens", {"input": 0, "output": 0})["input"] + response.usage.input_tokens,
            "output": state.get("total_tokens", {"input": 0, "output": 0})["output"] + response.usage.output_tokens
        }
    }


def extract_data_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 4: Extract structured data from notes.

    Args:
        state: Current workflow state

    Returns:
        State update with extracted structured data
    """
    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    print("\n[NODE] Extracting structured data...")

    # Combine all notes
    combined_notes = "\n\n".join(state["notes"])

    # Format sources
    formatted_sources = format_sources_for_extraction(state["sources"])

    # Create prompt
    prompt = EXTRACT_DATA_PROMPT.format(
        company_name=state["company_name"],
        notes=combined_notes,
        sources=formatted_sources
    )

    # Call Claude
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=config.llm_max_tokens,
        temperature=config.llm_temperature,
        messages=[{"role": "user", "content": prompt}]
    )

    extracted_text = response.content[0].text

    # Update cost
    cost = config.calculate_llm_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    print("[OK] Data extraction complete")

    # Store extracted text as-is (it's already formatted markdown)
    # In Phase 1, we keep it simple and don't parse it into structured fields
    return {
        "company_overview": extracted_text,  # Full extraction as overview for now
        "total_cost": state.get("total_cost", 0.0) + cost,
        "total_tokens": {
            "input": state.get("total_tokens", {"input": 0, "output": 0})["input"] + response.usage.input_tokens,
            "output": state.get("total_tokens", {"input": 0, "output": 0})["output"] + response.usage.output_tokens
        }
    }


def check_quality_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 5: Check research quality (Phase 2).

    Args:
        state: Current workflow state

    Returns:
        State update with quality assessment
    """
    print("\n[NODE] Checking research quality...")

    # Check quality
    quality_result = check_research_quality(
        company_name=state["company_name"],
        extracted_data=state.get("company_overview", ""),
        sources=state.get("sources", [])
    )

    quality_score = quality_result["quality_score"]
    print(f"[QUALITY] Score: {quality_score:.1f}/100")

    if quality_score < 85:
        print("[QUALITY] Below threshold (85). Missing information:")
        for item in quality_result["missing_information"][:3]:
            print(f"  - {item}")

    return {
        "quality_score": quality_score,
        "missing_info": quality_result["missing_information"],
        "iteration_count": state.get("iteration_count", 0) + 1,
        "total_cost": state.get("total_cost", 0.0) + quality_result["cost"],
        "total_tokens": {
            "input": state.get("total_tokens", {"input": 0, "output": 0})["input"] + quality_result["tokens"]["input"],
            "output": state.get("total_tokens", {"input": 0, "output": 0})["output"] + quality_result["tokens"]["output"]
        }
    }


def save_report_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 5: Generate and save markdown report.

    Args:
        state: Current workflow state

    Returns:
        State update with report path
    """
    config = get_config()

    print("\n[NODE] Generating markdown report...")

    # Calculate duration
    duration = (datetime.now() - state.get("start_time", datetime.now())).total_seconds()

    # Create output directory
    output_dir = Path(config.output_dir) / state["company_name"].replace(" ", "_")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate report filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"report_{timestamp}.md"

    # Format sources for report
    formatted_sources = format_sources_for_report(state["sources"])

    # Generate report content
    # For Phase 1, we use the extracted text directly since it's already well-formatted
    report_content = f"""# {state['company_name']} - Research Report

*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

---

{state['company_overview']}

---

## Sources

{formatted_sources}

---

*This report was automatically generated by the Company Researcher System*
*Quality Score: {state.get('quality_score', 0):.1f}/100 | Iterations: {state.get('iteration_count', 0)} | Duration: {duration:.1f}s | Cost: ${state.get('total_cost', 0.0):.4f} | Sources: {len(state.get('sources', []))}*
"""

    # Save report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"[OK] Report saved to: {report_path}")

    return {
        "report_path": str(report_path)
    }


# ============================================================================
# Workflow Graph Construction
# ============================================================================

def should_continue_research(state: OverallState) -> str:
    """
    Decision function: Should we iterate or finish?

    Args:
        state: Current workflow state

    Returns:
        "iterate" to continue research, "finish" to complete
    """
    quality_score = state.get("quality_score", 0)
    iteration_count = state.get("iteration_count", 0)
    max_iterations = 2  # Maximum 2 iterations

    # Finish if quality is good enough OR max iterations reached
    if quality_score >= 85:
        print(f"[DECISION] Quality sufficient ({quality_score:.1f} >= 85). Proceeding to report.")
        return "finish"
    elif iteration_count >= max_iterations:
        print(f"[DECISION] Max iterations reached ({iteration_count}/{max_iterations}). Proceeding to report.")
        return "finish"
    else:
        print(f"[DECISION] Quality low ({quality_score:.1f} < 85), iteration {iteration_count}/{max_iterations}. Re-searching.")
        return "iterate"


def create_research_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for basic research.

    Returns:
        Compiled StateGraph workflow
    """
    # Create graph
    workflow = StateGraph(OverallState, input=InputState, output=OutputState)

    # Add nodes
    workflow.add_node("generate_queries", generate_queries_node)
    workflow.add_node("search", search_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("extract_data", extract_data_node)
    workflow.add_node("check_quality", check_quality_node)
    workflow.add_node("save_report", save_report_node)

    # Define edges
    workflow.set_entry_point("generate_queries")
    workflow.add_edge("generate_queries", "search")
    workflow.add_edge("search", "analyze")
    workflow.add_edge("analyze", "extract_data")
    workflow.add_edge("extract_data", "check_quality")

    # Conditional edge from check_quality
    workflow.add_conditional_edges(
        "check_quality",
        should_continue_research,
        {
            "iterate": "generate_queries",  # Loop back to improve
            "finish": "save_report"  # Quality is good, save report
        }
    )

    workflow.add_edge("save_report", END)

    return workflow.compile()


# ============================================================================
# Main Research Function
# ============================================================================

def research_company(company_name: str) -> OutputState:
    """
    Research a company using the basic workflow.

    Args:
        company_name: Name of company to research

    Returns:
        OutputState with results and metrics
    """
    print(f"\n{'='*60}")
    print(f"[WORKFLOW] Researching: {company_name}")
    print(f"{'='*60}")

    # Create workflow
    workflow = create_research_workflow()

    # Create initial state
    initial_state = create_initial_state(company_name)

    # Run workflow
    final_state = workflow.invoke(initial_state)

    # Convert to output state
    output = create_output_state(final_state)

    # Print summary
    print(f"\n{'='*60}")
    print("[RESULTS] Research Complete")
    print(f"{'='*60}")
    print(f"Report: {output['report_path']}")
    print(f"Duration: {output['metrics']['duration_seconds']:.1f}s")
    print(f"Cost: ${output['metrics']['cost_usd']:.4f}")
    print(f"Tokens: {output['metrics']['tokens']['input']:,} in, {output['metrics']['tokens']['output']:,} out")
    print(f"Sources: {output['metrics']['sources_count']}")
    print(f"{'='*60}\n")

    return output
