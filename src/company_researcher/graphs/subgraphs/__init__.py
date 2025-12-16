"""
Subgraphs Package - Phase 11: Modular Graph Architecture

This package contains reusable LangGraph subgraphs that can be composed
into larger workflows. Each subgraph handles a specific phase of research.

Subgraphs:
    - data_collection: Query generation, search, SEC data, website scraping
    - analysis: Parallel specialist agents (financial, market, product, etc.)
    - quality: Fact extraction, contradiction detection, gap analysis
    - output: Report generation in multiple formats

Usage:
    from company_researcher.graphs.subgraphs import (
        create_data_collection_subgraph,
        create_analysis_subgraph,
        create_quality_subgraph,
        create_output_subgraph,
    )

    # Use as nodes in main graph
    main_graph.add_node("data_collection", create_data_collection_subgraph())
"""

from .analysis import AnalysisConfig, create_analysis_subgraph, create_parallel_analysis_subgraph
from .data_collection import DataCollectionConfig, create_data_collection_subgraph
from .output import OutputConfig, create_output_subgraph
from .quality import QualityConfig, create_quality_subgraph

__all__ = [
    # Data Collection
    "create_data_collection_subgraph",
    "DataCollectionConfig",
    # Analysis
    "create_analysis_subgraph",
    "create_parallel_analysis_subgraph",
    "AnalysisConfig",
    # Quality
    "create_quality_subgraph",
    "QualityConfig",
    # Output
    "create_output_subgraph",
    "OutputConfig",
]
