"""
Framework Mappers Module for Company Researcher.

Provides interoperability with different agent frameworks:
- CrewAI Mapper
- LangGraph Mapper
- OpenAI Agents Mapper
- Swarm Mapper
- Pydantic Mapper
- Google ADK Mapper
- MCP (Model Context Protocol) Mapper

Enables analysis, conversion, and unified interface across frameworks.
"""

from .base_mapper import (
    BaseMapper,
    NodeType,
    MappedNode,
    MappedEdge,
    MappedGraph,
    FrameworkType,
)

from .crewai_mapper import (
    CrewAIMapper,
    CrewAIAgent,
    CrewAITask,
    CrewAICrew,
    map_crewai_to_langgraph,
)

from .langgraph_mapper import (
    LangGraphMapper,
    LangGraphNode,
    LangGraphEdge,
    LangGraphState,
    analyze_langgraph,
)

from .openai_agents_mapper import (
    OpenAIAgentsMapper,
    OpenAIAgent,
    OpenAITool,
    map_openai_to_langgraph,
)

from .swarm_mapper import (
    SwarmMapper,
    SwarmAgent,
    SwarmFunction,
    map_swarm_to_langgraph,
)

from .pydantic_mapper import (
    PydanticMapper,
    PydanticAgent,
    map_pydantic_to_langgraph,
)

from .google_adk_mapper import (
    GoogleADKMapper,
    GoogleADKAgent,
    GoogleADKTool,
    map_google_adk_to_langgraph,
)

from .mcp_mapper import (
    MCPMapper,
    MCPServer,
    MCPTool,
    MCPResource,
    MCPPrompt,
    MCPClient,
    map_mcp_to_langgraph,
    get_mcp_tools,
)

from .unified_interface import (
    UnifiedAgent,
    UnifiedWorkflow,
    create_unified_workflow,
    convert_workflow,
)

__all__ = [
    # Base
    "BaseMapper",
    "NodeType",
    "MappedNode",
    "MappedEdge",
    "MappedGraph",
    "FrameworkType",
    # CrewAI
    "CrewAIMapper",
    "CrewAIAgent",
    "CrewAITask",
    "CrewAICrew",
    "map_crewai_to_langgraph",
    # LangGraph
    "LangGraphMapper",
    "LangGraphNode",
    "LangGraphEdge",
    "LangGraphState",
    "analyze_langgraph",
    # OpenAI Agents
    "OpenAIAgentsMapper",
    "OpenAIAgent",
    "OpenAITool",
    "map_openai_to_langgraph",
    # Swarm
    "SwarmMapper",
    "SwarmAgent",
    "SwarmFunction",
    "map_swarm_to_langgraph",
    # Pydantic
    "PydanticMapper",
    "PydanticAgent",
    "map_pydantic_to_langgraph",
    # Google ADK
    "GoogleADKMapper",
    "GoogleADKAgent",
    "GoogleADKTool",
    "map_google_adk_to_langgraph",
    # MCP
    "MCPMapper",
    "MCPServer",
    "MCPTool",
    "MCPResource",
    "MCPPrompt",
    "MCPClient",
    "map_mcp_to_langgraph",
    "get_mcp_tools",
    # Unified
    "UnifiedAgent",
    "UnifiedWorkflow",
    "create_unified_workflow",
    "convert_workflow",
]
