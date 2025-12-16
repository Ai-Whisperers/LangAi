"""
Parallel Multi-Agent Research Workflow (Phase 4 + Phase 10).

This workflow implements parallel specialized agents with quality assurance:
- Researcher Agent: Finds and gathers sources
- Financial Agent: Extracts financial metrics (PARALLEL)
- Market Agent: Analyzes competitive landscape (PARALLEL)
- Product Agent: Catalogs products and technology (PARALLEL)
- Competitor Scout: Competitive intelligence (PARALLEL) - Phase 9
- Synthesizer Agent: Aggregates all specialist insights
- Logic Critic Agent: Quality assurance and verification - Phase 10
- Quality Check: Validates and triggers iterations

Workflow: Researcher → [Financial, Market, Product, Competitor] → Synthesizer → Logic Critic → Quality → (iterate or finish)

Phase 4 Observability:
- AgentOps session tracking for full workflow replay
- LangSmith tracing for LangChain calls
- Enhanced cost tracking per agent

Phase 10 Quality Assurance:
- Fact extraction and verification
- Contradiction detection (rule-based + LLM)
- Gap identification
- Comprehensive quality scoring
"""

from typing import Any, Dict

from langgraph.graph import END, StateGraph

from ..agents import competitor_scout_agent_node  # Phase 9
from ..agents import (
    financial_agent_node,
    market_agent_node,
    product_agent_node,
    researcher_agent_node,
    synthesizer_agent_node,
)
from ..agents.quality.logic_critic import logic_critic_agent_node  # Phase 10
from ..observability import is_observability_enabled, record_quality_check, track_research_session
from ..prompts import format_sources_for_report
from ..quality import check_research_quality
from ..state import InputState, OutputState, OverallState, create_initial_state, create_output_state
from ..utils import utc_now

# ============================================================================
# Workflow Nodes
# ============================================================================


def check_quality_node(state: OverallState) -> Dict[str, Any]:
    """
    Node: Check research quality (Phase 2 + Phase 10).

    Phase 10: Uses comprehensive quality score from Logic Critic if available,
    otherwise falls back to simple quality check.

    Args:
        state: Current workflow state

    Returns:
        State update with quality assessment
    """
    print("\n[NODE] Checking research quality...")

    # Phase 10: Use quality score from Logic Critic if available
    if "quality_score" in state and state.get("agent_outputs", {}).get("logic_critic"):
        quality_score = state["quality_score"]
        logic_critic_output = state["agent_outputs"]["logic_critic"]

        print(f"[QUALITY] Logic Critic Score: {quality_score:.1f}/100")
        print(f"  - Facts Analyzed: {logic_critic_output.get('facts_analyzed', 0)}")
        print(
            f"  - Contradictions: {logic_critic_output.get('contradictions', {}).get('total', 0)}"
        )
        print(f"  - Gaps: {logic_critic_output.get('gaps', {}).get('total', 0)}")

        missing_info = []
        if quality_score < 85:
            print("[QUALITY] Below threshold (85). Issues identified:")
            # Extract gap information as missing info
            for gap in logic_critic_output.get("gaps", {}).get("items", [])[:3]:
                missing_info.append(f"{gap['section']}: {gap['recommendation']}")
                print(f"  - {gap['section']}: {gap['field']}")

        # Record quality check to observability (Phase 4)
        iteration_count = state.get("iteration_count", 0) + 1
        record_quality_check(
            quality_score=quality_score, missing_info=missing_info, iteration=iteration_count
        )

        return {
            "quality_score": quality_score,
            "missing_info": missing_info,
            "iteration_count": iteration_count,
        }

    else:
        # Fallback: Original simple quality check
        quality_result = check_research_quality(
            company_name=state["company_name"],
            extracted_data=state.get("company_overview", ""),
            sources=state.get("sources", []),
        )

        quality_score = quality_result["quality_score"]
        print(f"[QUALITY] Score: {quality_score:.1f}/100")

        if quality_score < 85:
            print("[QUALITY] Below threshold (85). Missing information:")
            for item in quality_result["missing_information"][:3]:
                print(f"  - {item}")

        # Record quality check to observability (Phase 4)
        iteration_count = state.get("iteration_count", 0) + 1
        record_quality_check(
            quality_score=quality_score,
            missing_info=quality_result["missing_information"],
            iteration=iteration_count,
        )

        return {
            "quality_score": quality_score,
            "missing_info": quality_result["missing_information"],
            "iteration_count": iteration_count,
            "total_cost": state.get("total_cost", 0.0) + quality_result["cost"],
            "total_tokens": {
                "input": state.get("total_tokens", {"input": 0, "output": 0})["input"]
                + quality_result["tokens"]["input"],
                "output": state.get("total_tokens", {"input": 0, "output": 0})["output"]
                + quality_result["tokens"]["output"],
            },
        }


def save_report_node(state: OverallState) -> Dict[str, Any]:
    """
    Node: Save markdown report.

    Args:
        state: Current workflow state

    Returns:
        State update with report path
    """
    print("\n[NODE] Generating markdown report...")

    # Generate report content
    timestamp = utc_now().strftime("%Y%m%d_%H%M%S")
    company_name = state["company_name"]

    # Get agent outputs for attribution
    agent_outputs = state.get("agent_outputs", {})
    researcher_metrics = agent_outputs.get("researcher", {})
    financial_metrics = agent_outputs.get("financial", {})
    market_metrics = agent_outputs.get("market", {})
    product_metrics = agent_outputs.get("product", {})
    competitor_metrics = agent_outputs.get("competitor", {})  # Phase 9
    synthesizer_metrics = agent_outputs.get("synthesizer", {})
    logic_critic_metrics = agent_outputs.get("logic_critic", {})  # Phase 10

    # Calculate duration
    duration = (utc_now() - state.get("start_time", utc_now())).total_seconds()

    # Build report
    report_content = f"""# {company_name} - Research Report (Phase 10: Logic Critic QA)

*Generated on {utc_now().strftime("%Y-%m-%d %H:%M:%S")}*

---

{state.get("company_overview", "Not available in research")}

---

## Sources

{format_sources_for_report(state.get("sources", []))}

---

*This report was automatically generated by the Company Researcher System*
*Quality Score: {state.get('quality_score', 0):.1f}/100 | Iterations: {state.get('iteration_count', 0)} | Duration: {duration:.1f}s | Cost: ${state.get('total_cost', 0.0):.4f} | Sources: {len(state.get('sources', []))}*

---

## Phase 10: Quality Assurance Report

### Logic Critic Agent
- **Facts Analyzed**: {logic_critic_metrics.get('facts_analyzed', 0)}
- **Quality Score**: {logic_critic_metrics.get('quality_metrics', {}).get('overall_score', 0):.1f}/100
- **Contradictions Found**: {logic_critic_metrics.get('contradictions', {}).get('total', 0)} (Critical: {logic_critic_metrics.get('contradictions', {}).get('critical', 0)})
- **Gaps Identified**: {logic_critic_metrics.get('gaps', {}).get('total', 0)} (High Severity: {logic_critic_metrics.get('gaps', {}).get('high_severity', 0)})
- **Passed QA**: {'✅ Yes' if logic_critic_metrics.get('passed', False) else '❌ No'}
- **Cost**: ${logic_critic_metrics.get('cost', 0.0):.4f}

---

## Phase 4: Parallel Multi-Agent System Metrics

### Researcher Agent
- Queries Generated: {researcher_metrics.get('queries_generated', 0)}
- Sources Found: {researcher_metrics.get('sources_found', 0)}
- Cost: ${researcher_metrics.get('cost', 0.0):.4f}

### Specialized Agents (Parallel Execution)

#### Financial Agent
- Data Extracted: {financial_metrics.get('data_extracted', False)}
- Cost: ${financial_metrics.get('cost', 0.0):.4f}

#### Market Agent
- Data Extracted: {market_metrics.get('data_extracted', False)}
- Cost: ${market_metrics.get('cost', 0.0):.4f}

#### Product Agent
- Data Extracted: {product_metrics.get('data_extracted', False)}
- Cost: ${product_metrics.get('cost', 0.0):.4f}

#### Competitor Scout Agent (Phase 9)
- Competitors Found: {competitor_metrics.get('competitors_found', 0)}
- Competitive Intensity: {competitor_metrics.get('competitive_intensity', 'N/A')}
- Cost: ${competitor_metrics.get('cost', 0.0):.4f}

### Synthesizer Agent
- Specialists Combined: {synthesizer_metrics.get('specialists_combined', 0)}
- Cost: ${synthesizer_metrics.get('cost', 0.0):.4f}

**Total Specialist Cost**: ${financial_metrics.get('cost', 0.0) + market_metrics.get('cost', 0.0) + product_metrics.get('cost', 0.0) + competitor_metrics.get('cost', 0.0):.4f}

---
"""

    # Save report
    import os

    output_dir = f"outputs/{company_name}"
    os.makedirs(output_dir, exist_ok=True)

    report_path = f"{output_dir}/report_{timestamp}.md"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"[OK] Report saved to: {report_path}")

    return {"report_path": report_path}


# ============================================================================
# Decision Functions
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
        print(
            f"[DECISION] Max iterations reached ({iteration_count}/{max_iterations}). Proceeding to report."
        )
        return "finish"
    else:
        print(
            f"[DECISION] Quality low ({quality_score:.1f} < 85), iteration {iteration_count}/{max_iterations}. Re-researching."
        )
        return "iterate"


# ============================================================================
# Workflow Creation
# ============================================================================


def create_parallel_agent_workflow() -> StateGraph:
    """
    Create the parallel multi-agent research workflow (Phase 4 + Phase 9 + Phase 10).

    Workflow:
        researcher → [financial, market, product, competitor] → synthesizer → logic_critic → check_quality → (iterate or finish)

    LangGraph automatically executes financial, market, product, and competitor in parallel
    since they all depend on researcher and don't depend on each other.

    Phase 9: Added Competitor Scout agent for competitive intelligence.
    Phase 10: Added Logic Critic agent for quality assurance (fact verification, contradiction detection, gap analysis).

    Returns:
        Compiled StateGraph workflow
    """
    # Create graph
    workflow = StateGraph(OverallState, input=InputState, output=OutputState)

    # Add nodes
    workflow.add_node("researcher", researcher_agent_node)
    workflow.add_node("financial", financial_agent_node)
    workflow.add_node("market", market_agent_node)
    workflow.add_node("product", product_agent_node)
    workflow.add_node("competitor", competitor_scout_agent_node)  # Phase 9
    workflow.add_node("synthesizer", synthesizer_agent_node)
    workflow.add_node("logic_critic", logic_critic_agent_node)  # Phase 10
    workflow.add_node("check_quality", check_quality_node)
    workflow.add_node("save_report", save_report_node)

    # Define edges
    workflow.set_entry_point("researcher")

    # Fan out to specialists (PARALLEL EXECUTION)
    workflow.add_edge("researcher", "financial")
    workflow.add_edge("researcher", "market")
    workflow.add_edge("researcher", "product")
    workflow.add_edge("researcher", "competitor")  # Phase 9

    # Fan in to synthesizer (waits for all specialists)
    workflow.add_edge("financial", "synthesizer")
    workflow.add_edge("market", "synthesizer")
    workflow.add_edge("product", "synthesizer")
    workflow.add_edge("competitor", "synthesizer")  # Phase 9

    # Quality assurance pipeline (Phase 10)
    workflow.add_edge("synthesizer", "logic_critic")
    workflow.add_edge("logic_critic", "check_quality")

    # Conditional edge from check_quality
    workflow.add_conditional_edges(
        "check_quality",
        should_continue_research,
        {
            "iterate": "researcher",  # Loop back to improve
            "finish": "save_report",  # Quality is good, save report
        },
    )

    workflow.add_edge("save_report", END)

    return workflow.compile()


# ============================================================================
# Main Research Function
# ============================================================================


def research_company(company_name: str) -> OutputState:
    """
    Research a company using the parallel multi-agent workflow.

    Phase 4: Includes observability tracking with AgentOps and LangSmith.

    Args:
        company_name: Name of company to research

    Returns:
        OutputState with results and metrics
    """
    print(f"\n{'='*60}")
    print(f"[WORKFLOW] Parallel Multi-Agent Research: {company_name}")
    if is_observability_enabled():
        print("[OBSERVABILITY] Tracking enabled (AgentOps/LangSmith)")
    print(f"{'='*60}")

    # Track research session with observability (Phase 4)
    with track_research_session(company_name=company_name, tags=["phase-4", "parallel"]):
        # Create workflow
        workflow = create_parallel_agent_workflow()

        # Create initial state
        initial_state = create_initial_state(company_name)

        # Run workflow (automatically traced by LangSmith if enabled)
        final_state = workflow.invoke(initial_state)

        # Convert to output state
        output = create_output_state(final_state)

        # Print summary
        print(f"\n{'='*60}")
        print("[RESULTS] Parallel Multi-Agent Research Complete")
        print(f"{'='*60}")
        print(f"Report: {output['report_path']}")
        print(f"Duration: {output['metrics']['duration_seconds']:.1f}s")
        print(f"Cost: ${output['metrics']['cost_usd']:.4f}")
        print(
            f"Tokens: {output['metrics']['tokens']['input']:,} in, {output['metrics']['tokens']['output']:,} out"
        )
        print(f"Sources: {output['metrics']['sources_count']}")
        print(f"Quality: {output['metrics']['quality_score']:.1f}/100")
        print(f"Iterations: {output['metrics']['iterations']}")
        print(f"{'='*60}\n")

        return output
