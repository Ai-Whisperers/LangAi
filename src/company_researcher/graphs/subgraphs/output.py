"""
Output Generation Subgraph - Phase 11

Handles report generation in multiple formats:
- Markdown reports (primary)
- PDF reports (optional)
- Excel exports (optional)
- JSON data export (optional)

This subgraph:
1. Formats analysis results
2. Generates section content
3. Creates output files
4. Returns output metadata
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import os
import json
from langgraph.graph import StateGraph, START, END

from ...state.workflow import OverallState
from ...prompts import format_sources_for_report
from ...utils import get_logger, utc_now

logger = get_logger(__name__)


@dataclass
class OutputConfig:
    """Configuration for output generation subgraph."""

    # Output formats
    generate_markdown: bool = True
    generate_pdf: bool = False
    generate_excel: bool = False
    generate_json: bool = False

    # Output directory
    output_dir: str = "outputs"

    # Report customization
    include_metrics: bool = True
    include_sources: bool = True
    include_agent_breakdown: bool = True
    include_quality_report: bool = True

    # Styling
    report_title_prefix: str = ""
    timestamp_format: str = "%Y%m%d_%H%M%S"


# ============================================================================
# Report Generation Nodes
# ============================================================================

def prepare_report_data_node(state: OverallState) -> Dict[str, Any]:
    """
    Prepare data for report generation.

    This node:
    1. Collects all analysis outputs
    2. Calculates final metrics
    3. Prepares data structures for templating

    Args:
        state: Current workflow state

    Returns:
        State update with prepared report data
    """
    logger.info("[NODE] Preparing report data...")

    company_name = state.get("company_name", "Unknown Company")
    agent_outputs = state.get("agent_outputs", {})
    quality_score = state.get("quality_score", 0)
    iteration_count = state.get("iteration_count", 0)
    start_time = state.get("start_time", utc_now())

    # Calculate duration
    duration = (utc_now() - start_time).total_seconds()

    # Aggregate costs
    total_cost = state.get("total_cost", 0.0)
    total_tokens = state.get("total_tokens", {"input": 0, "output": 0})

    # Count sources
    sources = state.get("sources", [])
    search_results = state.get("search_results", [])

    report_data = {
        "company_name": company_name,
        "generated_at": utc_now().isoformat(),
        "duration_seconds": round(duration, 1),
        "quality_score": round(quality_score, 1),
        "iteration_count": iteration_count,
        "total_cost": round(total_cost, 4),
        "total_tokens": total_tokens,
        "sources_count": len(sources),
        "search_results_count": len(search_results),
        "agents_used": list(agent_outputs.keys()),
    }

    logger.info(f"[REPORT] Prepared data for {company_name}")

    return {
        "report_data": report_data,
    }


def generate_markdown_report_node(state: OverallState) -> Dict[str, Any]:
    """
    Generate comprehensive markdown report.

    Args:
        state: Current workflow state

    Returns:
        State update with markdown content
    """
    logger.info("[NODE] Generating markdown report...")

    company_name = state.get("company_name", "Unknown Company")
    report_data = state.get("report_data", {})
    agent_outputs = state.get("agent_outputs", {})
    quality_breakdown = state.get("quality_breakdown", {})
    gaps = state.get("gaps", {})
    contradictions = state.get("contradictions", {})

    # Build report sections
    sections = []

    # Header
    sections.append(f"# {company_name} - Research Report")
    sections.append(f"\n*Generated on {report_data.get('generated_at', 'N/A')}*")
    sections.append("\n---\n")

    # Executive Summary
    sections.append("## Executive Summary\n")
    company_overview = state.get("company_overview", "No overview available.")
    sections.append(company_overview)
    sections.append("\n---\n")

    # Key Metrics
    key_metrics = state.get("key_metrics", {})
    if key_metrics:
        sections.append("## Key Metrics\n")
        for metric, value in key_metrics.items():
            sections.append(f"- **{metric}**: {value}")
        sections.append("\n---\n")

    # Products & Services
    products = state.get("products_services", [])
    if products:
        sections.append("## Products & Services\n")
        for product in products:
            sections.append(f"- {product}")
        sections.append("\n---\n")

    # Competitors
    competitors = state.get("competitors", [])
    if competitors:
        sections.append("## Competitors\n")
        for competitor in competitors:
            sections.append(f"- {competitor}")
        sections.append("\n---\n")

    # Agent Analysis Sections
    sections.append("## Detailed Analysis\n")

    for agent_name, output in agent_outputs.items():
        if agent_name == "logic_critic":
            continue  # Handle separately

        analysis = output.get("analysis", "")
        if analysis:
            sections.append(f"### {agent_name.replace('_', ' ').title()} Analysis\n")
            sections.append(analysis[:2000])  # Truncate if too long
            sections.append("\n")

    sections.append("\n---\n")

    # Quality Report
    sections.append("## Quality Assurance Report\n")
    sections.append(f"**Overall Score**: {report_data.get('quality_score', 0)}/100\n")

    if quality_breakdown:
        sections.append("\n### Score Breakdown\n")
        for component, score in quality_breakdown.items():
            if component not in ("final_score", "weights"):
                sections.append(f"- {component.title()}: {score}/100")
        sections.append("\n")

    if contradictions and contradictions.get("total", 0) > 0:
        sections.append(f"\n### Contradictions\n")
        sections.append(f"- Total: {contradictions.get('total', 0)}")
        sections.append(f"- Critical: {contradictions.get('critical', 0)}")
        sections.append("\n")

    if gaps and gaps.get("total", 0) > 0:
        sections.append(f"\n### Information Gaps\n")
        sections.append(f"- Total: {gaps.get('total', 0)}")
        sections.append(f"- High Severity: {gaps.get('high_severity', 0)}")
        sections.append("\n")

    sections.append("\n---\n")

    # Sources
    sources = state.get("sources", [])
    if sources:
        sections.append("## Sources\n")
        sections.append(format_sources_for_report(sources))
        sections.append("\n---\n")

    # Report Metadata
    sections.append("## Report Metadata\n")
    sections.append(f"- **Duration**: {report_data.get('duration_seconds', 0)}s")
    sections.append(f"- **Cost**: ${report_data.get('total_cost', 0):.4f}")
    sections.append(f"- **Iterations**: {report_data.get('iteration_count', 0)}")
    sections.append(f"- **Sources**: {report_data.get('sources_count', 0)}")

    tokens = report_data.get('total_tokens', {})
    sections.append(f"- **Tokens**: {tokens.get('input', 0):,} in / {tokens.get('output', 0):,} out")

    sections.append("\n\n---\n")
    sections.append("*This report was automatically generated by the Company Researcher System*\n")
    sections.append("*Phase 11: LangGraph Subgraph Architecture*\n")

    markdown_content = "\n".join(sections)

    return {
        "markdown_content": markdown_content,
    }


def save_report_files_node(state: OverallState) -> Dict[str, Any]:
    """
    Save report to output files.

    Args:
        state: Current workflow state

    Returns:
        State update with file paths
    """
    logger.info("[NODE] Saving report files...")

    company_name = state.get("company_name", "Unknown")
    markdown_content = state.get("markdown_content", "")
    report_data = state.get("report_data", {})

    # Create output directory
    output_dir = Path("outputs") / company_name.lower().replace(" ", "_")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = utc_now().strftime("%Y%m%d_%H%M%S")
    output_files = {}

    # Save markdown
    if markdown_content:
        md_path = output_dir / f"report_{timestamp}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        output_files["markdown"] = str(md_path)
        logger.info(f"[SAVE] Markdown report: {md_path}")

    # Save JSON data export
    json_data = {
        "company_name": company_name,
        "report_data": report_data,
        "company_overview": state.get("company_overview", ""),
        "key_metrics": state.get("key_metrics", {}),
        "products_services": state.get("products_services", []),
        "competitors": state.get("competitors", []),
        "quality_score": state.get("quality_score", 0),
        "quality_breakdown": state.get("quality_breakdown", {}),
        "sources_count": len(state.get("sources", [])),
    }

    json_path = output_dir / f"data_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, default=str)
    output_files["json"] = str(json_path)
    logger.info(f"[SAVE] JSON data: {json_path}")

    return {
        "report_path": output_files.get("markdown", ""),
        "output_files": output_files,
    }


# ============================================================================
# Specialized Output Nodes
# ============================================================================

def generate_executive_summary_node(state: OverallState) -> Dict[str, Any]:
    """
    Generate a concise executive summary.

    Args:
        state: Current workflow state

    Returns:
        State update with executive summary
    """
    logger.info("[NODE] Generating executive summary...")

    company_name = state.get("company_name", "Unknown")
    company_overview = state.get("company_overview", "")
    key_metrics = state.get("key_metrics", {})
    quality_score = state.get("quality_score", 0)

    # Create brief summary
    summary_parts = [
        f"**{company_name}** - Research Summary",
        "",
    ]

    if company_overview:
        # Take first 2 sentences
        sentences = company_overview.split(". ")[:2]
        summary_parts.append(". ".join(sentences) + ".")

    if key_metrics:
        summary_parts.append("")
        summary_parts.append("**Key Highlights:**")
        for metric, value in list(key_metrics.items())[:5]:
            summary_parts.append(f"- {metric}: {value}")

    summary_parts.append("")
    summary_parts.append(f"*Quality Score: {quality_score}/100*")

    executive_summary = "\n".join(summary_parts)

    return {
        "executive_summary": executive_summary,
    }


def generate_comparison_output_node(state: OverallState) -> Dict[str, Any]:
    """
    Generate comparison-ready output format.

    Useful when comparing multiple companies.

    Args:
        state: Current workflow state

    Returns:
        State update with comparison data
    """
    logger.info("[NODE] Generating comparison output...")

    company_name = state.get("company_name", "Unknown")
    key_metrics = state.get("key_metrics", {})
    competitors = state.get("competitors", [])
    quality_score = state.get("quality_score", 0)

    comparison_data = {
        "company": company_name,
        "metrics": key_metrics,
        "competitors": competitors,
        "quality_score": quality_score,
        "timestamp": utc_now().isoformat(),
    }

    return {
        "comparison_data": comparison_data,
    }


# ============================================================================
# Subgraph Creation
# ============================================================================

def create_output_subgraph(
    config: Optional[OutputConfig] = None
) -> StateGraph:
    """
    Create the output generation subgraph.

    This subgraph:
    1. Prepares report data
    2. Generates markdown content
    3. Saves output files
    4. Returns file paths

    Args:
        config: Optional configuration

    Returns:
        Compiled StateGraph
    """
    if config is None:
        config = OutputConfig()

    graph = StateGraph(OverallState)

    # ========================================
    # Add Nodes
    # ========================================

    graph.add_node("prepare_data", prepare_report_data_node)
    graph.add_node("generate_summary", generate_executive_summary_node)

    if config.generate_markdown:
        graph.add_node("generate_markdown", generate_markdown_report_node)

    graph.add_node("save_files", save_report_files_node)

    # ========================================
    # Define Edges
    # ========================================

    graph.set_entry_point("prepare_data")
    graph.add_edge("prepare_data", "generate_summary")
    graph.add_edge("generate_summary", "generate_markdown")
    graph.add_edge("generate_markdown", "save_files")
    graph.add_edge("save_files", END)

    return graph.compile()


def create_minimal_output_subgraph() -> StateGraph:
    """
    Create a minimal output subgraph for testing.

    Only generates markdown and saves it.

    Returns:
        Compiled StateGraph
    """
    graph = StateGraph(OverallState)

    graph.add_node("prepare_data", prepare_report_data_node)
    graph.add_node("generate_markdown", generate_markdown_report_node)
    graph.add_node("save_files", save_report_files_node)

    graph.set_entry_point("prepare_data")
    graph.add_edge("prepare_data", "generate_markdown")
    graph.add_edge("generate_markdown", "save_files")
    graph.add_edge("save_files", END)

    return graph.compile()
