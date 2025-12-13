"""
Pre-built LangFlow Flows for Company Researcher.

This module provides:
- Pre-built flow definitions in LangFlow JSON format
- Export/import utilities for workflows
- Flow templates for common research patterns

Flows can be imported directly into LangFlow's visual builder.
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from ..utils import get_logger, utc_now

logger = get_logger(__name__)


# ============================================================================
# Basic Research Flow Definition
# ============================================================================

BASIC_RESEARCH_FLOW = {
    "name": "Basic Company Research",
    "description": "Simple single-agent company research workflow",
    "version": "1.0.0",
    "created": utc_now().isoformat(),
    "nodes": [
        {
            "id": "researcher-1",
            "type": "ResearcherAgent",
            "position": {"x": 100, "y": 200},
            "data": {
                "label": "Company Researcher",
                "company_name": "",
                "search_depth": 5,
                "max_results": 3,
            },
        },
        {
            "id": "quality-1",
            "type": "QualityChecker",
            "position": {"x": 400, "y": 200},
            "data": {
                "label": "Quality Check",
                "quality_threshold": 85.0,
            },
        },
        {
            "id": "output-1",
            "type": "Output",
            "position": {"x": 700, "y": 200},
            "data": {
                "label": "Research Output",
            },
        },
    ],
    "edges": [
        {
            "id": "e1",
            "source": "researcher-1",
            "target": "quality-1",
            "sourceHandle": "output",
            "targetHandle": "research_data",
        },
        {
            "id": "e2",
            "source": "quality-1",
            "target": "output-1",
            "sourceHandle": "output",
            "targetHandle": "input",
        },
    ],
}


# ============================================================================
# Parallel Research Flow Definition
# ============================================================================

PARALLEL_RESEARCH_FLOW = {
    "name": "Parallel Multi-Agent Research",
    "description": "Full parallel multi-agent company research (Phase 4)",
    "version": "1.0.0",
    "created": utc_now().isoformat(),
    "nodes": [
        # Input
        {
            "id": "input-1",
            "type": "Input",
            "position": {"x": 100, "y": 300},
            "data": {
                "label": "Company Name Input",
                "input_type": "text",
            },
        },
        # Researcher Agent
        {
            "id": "researcher-1",
            "type": "ResearcherAgent",
            "position": {"x": 300, "y": 300},
            "data": {
                "label": "Initial Research",
                "search_depth": 5,
                "max_results": 3,
            },
        },
        # Parallel Specialist Agents
        {
            "id": "financial-1",
            "type": "FinancialAgent",
            "position": {"x": 550, "y": 100},
            "data": {
                "label": "Financial Analysis",
                "use_alpha_vantage": True,
                "use_sec_edgar": True,
            },
        },
        {
            "id": "market-1",
            "type": "MarketAgent",
            "position": {"x": 550, "y": 300},
            "data": {
                "label": "Market Analysis",
                "include_tam_sam_som": True,
                "include_trends": True,
            },
        },
        {
            "id": "product-1",
            "type": "ProductAgent",
            "position": {"x": 550, "y": 500},
            "data": {
                "label": "Product Analysis",
            },
        },
        # Synthesizer
        {
            "id": "synthesizer-1",
            "type": "SynthesizerAgent",
            "position": {"x": 800, "y": 300},
            "data": {
                "label": "Report Synthesis",
            },
        },
        # Quality Check
        {
            "id": "quality-1",
            "type": "QualityChecker",
            "position": {"x": 1050, "y": 300},
            "data": {
                "label": "Quality Validation",
                "quality_threshold": 85.0,
            },
        },
        # Output
        {
            "id": "output-1",
            "type": "Output",
            "position": {"x": 1300, "y": 300},
            "data": {
                "label": "Research Report",
            },
        },
    ],
    "edges": [
        # Input to Researcher
        {
            "id": "e-input",
            "source": "input-1",
            "target": "researcher-1",
            "sourceHandle": "output",
            "targetHandle": "company_name",
        },
        # Researcher to Specialists (parallel)
        {
            "id": "e-r2f",
            "source": "researcher-1",
            "target": "financial-1",
            "sourceHandle": "output",
            "targetHandle": "research_context",
        },
        {
            "id": "e-r2m",
            "source": "researcher-1",
            "target": "market-1",
            "sourceHandle": "output",
            "targetHandle": "research_context",
        },
        {
            "id": "e-r2p",
            "source": "researcher-1",
            "target": "product-1",
            "sourceHandle": "output",
            "targetHandle": "research_context",
        },
        # Specialists to Synthesizer
        {
            "id": "e-f2s",
            "source": "financial-1",
            "target": "synthesizer-1",
            "sourceHandle": "output",
            "targetHandle": "financial_analysis",
        },
        {
            "id": "e-m2s",
            "source": "market-1",
            "target": "synthesizer-1",
            "sourceHandle": "output",
            "targetHandle": "market_analysis",
        },
        {
            "id": "e-p2s",
            "source": "product-1",
            "target": "synthesizer-1",
            "sourceHandle": "output",
            "targetHandle": "product_analysis",
        },
        # Synthesizer to Quality
        {
            "id": "e-s2q",
            "source": "synthesizer-1",
            "target": "quality-1",
            "sourceHandle": "output",
            "targetHandle": "research_data",
        },
        # Quality to Output
        {
            "id": "e-q2o",
            "source": "quality-1",
            "target": "output-1",
            "sourceHandle": "output",
            "targetHandle": "input",
        },
    ],
}


# ============================================================================
# Flow Registry
# ============================================================================

FLOW_REGISTRY = {
    "basic_research": BASIC_RESEARCH_FLOW,
    "parallel_research": PARALLEL_RESEARCH_FLOW,
}


def get_available_flows() -> List[Dict[str, str]]:
    """
    Get list of available pre-built flows.

    Returns:
        List of flow metadata dictionaries
    """
    return [
        {
            "id": flow_id,
            "name": flow["name"],
            "description": flow["description"],
            "version": flow["version"],
        }
        for flow_id, flow in FLOW_REGISTRY.items()
    ]


def export_workflow(
    workflow_id: str,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Export a workflow to LangFlow JSON format.

    Args:
        workflow_id: ID of the workflow to export
        output_path: Optional file path to save JSON

    Returns:
        Flow definition dictionary

    Raises:
        ValueError: If workflow_id not found
    """
    if workflow_id not in FLOW_REGISTRY:
        available = ", ".join(FLOW_REGISTRY.keys())
        raise ValueError(f"Workflow '{workflow_id}' not found. Available: {available}")

    flow = FLOW_REGISTRY[workflow_id].copy()

    # Update timestamp
    flow["exported_at"] = utc_now().isoformat()

    # Save to file if path provided
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(flow, f, indent=2)
        logger.info(f"Flow exported to: {output_path}")

    return flow


def import_workflow(
    flow_path: str,
) -> Dict[str, Any]:
    """
    Import a workflow from LangFlow JSON file.

    Args:
        flow_path: Path to the flow JSON file

    Returns:
        Flow definition dictionary

    Raises:
        FileNotFoundError: If file not found
        json.JSONDecodeError: If invalid JSON
    """
    flow_file = Path(flow_path)

    if not flow_file.exists():
        raise FileNotFoundError(f"Flow file not found: {flow_path}")

    with open(flow_file, "r") as f:
        flow = json.load(f)

    logger.info(f"Flow imported: {flow.get('name', 'Unknown')}")
    return flow


def save_flow_to_langflow_format(
    flow: Dict[str, Any],
    output_path: str,
) -> str:
    """
    Save a flow in LangFlow-compatible format.

    This ensures the flow can be directly imported into LangFlow.

    Args:
        flow: Flow definition dictionary
        output_path: Output file path

    Returns:
        Path to saved file
    """
    # Ensure LangFlow-compatible structure
    langflow_flow = {
        "data": {
            "nodes": flow.get("nodes", []),
            "edges": flow.get("edges", []),
            "viewport": {"x": 0, "y": 0, "zoom": 1},
        },
        "name": flow.get("name", "Unnamed Flow"),
        "description": flow.get("description", ""),
        "is_component": False,
    }

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(langflow_flow, f, indent=2)

    logger.info(f"LangFlow-compatible flow saved to: {output_path}")
    return str(output_file)


def create_flow_from_workflow(
    workflow_name: str,
) -> Dict[str, Any]:
    """
    Create a LangFlow flow from an existing Company Researcher workflow.

    This converts the Python-defined workflows to LangFlow format.

    Args:
        workflow_name: Name of workflow ("basic", "parallel", "multi_agent")

    Returns:
        LangFlow-compatible flow definition
    """
    workflow_map = {
        "basic": "basic_research",
        "parallel": "parallel_research",
        "multi_agent": "parallel_research",
    }

    flow_id = workflow_map.get(workflow_name, workflow_name)

    if flow_id not in FLOW_REGISTRY:
        raise ValueError(f"Unknown workflow: {workflow_name}")

    return export_workflow(flow_id)


# ============================================================================
# CLI Helper
# ============================================================================

def print_available_flows():
    """Print available flows to console."""
    print("\n" + "=" * 60)
    print("Available LangFlow Flows")
    print("=" * 60)

    for flow_info in get_available_flows():
        print(f"\n  {flow_info['id']}:")
        print(f"    Name: {flow_info['name']}")
        print(f"    Description: {flow_info['description']}")
        print(f"    Version: {flow_info['version']}")

    print("\n  Export a flow with:")
    print('    export_workflow("parallel_research", "my_flow.json")')
    print("=" * 60 + "\n")
