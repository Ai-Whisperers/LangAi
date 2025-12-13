"""
MCP (Model Context Protocol) Mapper - Integration with MCP servers.

Supports:
- MCP server discovery and connection
- Tool extraction from MCP servers
- Resource access
- Conversion to LangGraph tools
"""

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from .base_mapper import (
    BaseMapper,
    FrameworkType,
    MappedEdge,
    MappedGraph,
    MappedNode,
    NodeType,
)


@dataclass
class MCPTool:
    """Representation of an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    annotations: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPResource:
    """Representation of an MCP resource."""
    uri: str
    name: str
    description: str = ""
    mime_type: str = "text/plain"
    annotations: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPPrompt:
    """Representation of an MCP prompt template."""
    name: str
    description: str = ""
    arguments: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MCPServer:
    """Representation of an MCP server configuration."""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    tools: List[MCPTool] = field(default_factory=list)
    resources: List[MCPResource] = field(default_factory=list)
    prompts: List[MCPPrompt] = field(default_factory=list)


class MCPMapper(BaseMapper):
    """
    Mapper for Model Context Protocol servers.

    Usage:
        mapper = MCPMapper()
        graph = mapper.analyze(mcp_config)
        tools = mapper.to_langchain_tools(graph)
    """

    def __init__(self):
        super().__init__(FrameworkType.MCP)

    def analyze(self, source: Any) -> MappedGraph:
        """
        Analyze MCP configuration or server.

        Args:
            source: MCP server config dict or MCPServer instance

        Returns:
            MappedGraph representation
        """
        if isinstance(source, dict):
            servers = self._parse_config(source)
        elif isinstance(source, MCPServer):
            servers = [source]
        elif isinstance(source, list):
            servers = [self._parse_server_config(s) if isinstance(s, dict) else s for s in source]
        else:
            servers = [self._extract_server(source)]

        return self._build_graph(servers)

    def _parse_config(self, config: Dict[str, Any]) -> List[MCPServer]:
        """Parse MCP configuration file format."""
        servers = []

        # Handle mcpServers format (Claude Desktop style)
        mcp_servers = config.get("mcpServers", config.get("servers", {}))

        for name, server_config in mcp_servers.items():
            servers.append(self._parse_server_config(server_config, name))

        return servers

    def _parse_server_config(self, config: Dict[str, Any], name: str = "") -> MCPServer:
        """Parse individual server configuration."""
        return MCPServer(
            name=name or config.get("name", "mcp_server"),
            command=config.get("command", ""),
            args=config.get("args", []),
            env=config.get("env", {}),
            tools=[self._parse_tool(t) for t in config.get("tools", [])],
            resources=[self._parse_resource(r) for r in config.get("resources", [])],
            prompts=[self._parse_prompt(p) for p in config.get("prompts", [])]
        )

    def _parse_tool(self, tool_config: Dict[str, Any]) -> MCPTool:
        """Parse tool configuration."""
        return MCPTool(
            name=tool_config.get("name", ""),
            description=tool_config.get("description", ""),
            input_schema=tool_config.get("inputSchema", tool_config.get("input_schema", {})),
            annotations=tool_config.get("annotations", {})
        )

    def _parse_resource(self, resource_config: Dict[str, Any]) -> MCPResource:
        """Parse resource configuration."""
        return MCPResource(
            uri=resource_config.get("uri", ""),
            name=resource_config.get("name", ""),
            description=resource_config.get("description", ""),
            mime_type=resource_config.get("mimeType", "text/plain"),
            annotations=resource_config.get("annotations", {})
        )

    def _parse_prompt(self, prompt_config: Dict[str, Any]) -> MCPPrompt:
        """Parse prompt configuration."""
        return MCPPrompt(
            name=prompt_config.get("name", ""),
            description=prompt_config.get("description", ""),
            arguments=prompt_config.get("arguments", [])
        )

    def _extract_server(self, server: Any) -> MCPServer:
        """Extract server information from MCP server object."""
        tools = []
        resources = []
        prompts = []

        # Extract tools
        for tool in getattr(server, 'tools', []):
            if hasattr(tool, 'name'):
                tools.append(MCPTool(
                    name=tool.name,
                    description=getattr(tool, 'description', ''),
                    input_schema=getattr(tool, 'inputSchema', {})
                ))

        # Extract resources
        for resource in getattr(server, 'resources', []):
            if hasattr(resource, 'uri'):
                resources.append(MCPResource(
                    uri=resource.uri,
                    name=getattr(resource, 'name', ''),
                    description=getattr(resource, 'description', '')
                ))

        # Extract prompts
        for prompt in getattr(server, 'prompts', []):
            if hasattr(prompt, 'name'):
                prompts.append(MCPPrompt(
                    name=prompt.name,
                    description=getattr(prompt, 'description', ''),
                    arguments=getattr(prompt, 'arguments', [])
                ))

        return MCPServer(
            name=getattr(server, 'name', 'mcp_server'),
            command=getattr(server, 'command', ''),
            args=getattr(server, 'args', []),
            env=getattr(server, 'env', {}),
            tools=tools,
            resources=resources,
            prompts=prompts
        )

    def _build_graph(self, servers: List[MCPServer]) -> MappedGraph:
        """Build MappedGraph from MCP servers."""
        nodes = []
        edges = []

        for server in servers:
            # Add server node
            server_node = MappedNode(
                id=f"server_{server.name}",
                name=server.name,
                node_type=NodeType.AGENT,
                framework=FrameworkType.MCP,
                description=f"MCP Server: {server.command}",
                tools=[t.name for t in server.tools],
                config={
                    "command": server.command,
                    "args": server.args,
                    "env": server.env
                }
            )
            nodes.append(server_node)

            # Add tool nodes
            for tool in server.tools:
                tool_node = MappedNode(
                    id=f"tool_{server.name}_{tool.name}",
                    name=tool.name,
                    node_type=NodeType.TOOL,
                    framework=FrameworkType.MCP,
                    description=tool.description,
                    config={
                        "input_schema": tool.input_schema,
                        "annotations": tool.annotations
                    }
                )
                nodes.append(tool_node)

                edges.append(MappedEdge(
                    source=server_node.id,
                    target=tool_node.id,
                    edge_type="provides_tool"
                ))

            # Add resource nodes
            for resource in server.resources:
                resource_node = MappedNode(
                    id=f"resource_{server.name}_{resource.name}",
                    name=resource.name,
                    node_type=NodeType.TOOL,  # Resources as tools
                    framework=FrameworkType.MCP,
                    description=resource.description,
                    config={
                        "uri": resource.uri,
                        "mime_type": resource.mime_type
                    }
                )
                nodes.append(resource_node)

                edges.append(MappedEdge(
                    source=server_node.id,
                    target=resource_node.id,
                    edge_type="provides_resource"
                ))

        entry_point = nodes[0].id if nodes else None

        return MappedGraph(
            name="mcp_workflow",
            framework=FrameworkType.MCP,
            nodes=nodes,
            edges=edges,
            entry_point=entry_point,
            exit_points=[]
        )

    def to_langgraph(self, graph: MappedGraph) -> Any:
        """Convert to LangGraph StateGraph with MCP tools."""
        try:
            from langgraph.graph import StateGraph, END
            from typing import TypedDict, Annotated
            import operator
        except ImportError:
            raise ImportError("langgraph is required for conversion")

        class MCPState(TypedDict):
            messages: Annotated[list, operator.add]
            tool_results: dict

        workflow = StateGraph(MCPState)

        # Add server nodes
        server_nodes = [n for n in graph.nodes if n.node_type == NodeType.AGENT]

        for node in server_nodes:
            def make_server_node(server_node: MappedNode):
                async def server_func(state: MCPState) -> MCPState:
                    return {
                        "messages": [{"role": "assistant", "content": f"MCP Server {server_node.name}"}],
                        "tool_results": {}
                    }
                return server_func

            workflow.add_node(node.id, make_server_node(node))

        # Set entry point
        if server_nodes:
            workflow.set_entry_point(server_nodes[0].id)
            workflow.add_edge(server_nodes[-1].id, END)

        return workflow

    def to_langchain_tools(self, graph: MappedGraph) -> List[Any]:
        """
        Convert MCP tools to LangChain tools.

        Returns:
            List of LangChain StructuredTool instances
        """
        try:
            from langchain_core.tools import StructuredTool
            from pydantic import create_model
        except ImportError:
            raise ImportError("langchain-core and pydantic are required")

        tools = []
        tool_nodes = [n for n in graph.nodes if n.node_type == NodeType.TOOL]

        for node in tool_nodes:
            input_schema = node.config.get("input_schema", {})

            # Create dynamic Pydantic model from input schema
            fields = {}
            properties = input_schema.get("properties", {})
            required = input_schema.get("required", [])

            for prop_name, prop_config in properties.items():
                prop_type = self._json_type_to_python(prop_config.get("type", "string"))
                default = ... if prop_name in required else None
                fields[prop_name] = (prop_type, default)

            if fields:
                InputModel = create_model(f"{node.name}Input", **fields)
            else:
                InputModel = None

            # Create tool function
            def make_tool_func(tool_node: MappedNode):
                def tool_func(**kwargs) -> str:
                    # Placeholder - actual MCP call would happen here
                    return f"Called MCP tool {tool_node.name} with {kwargs}"
                return tool_func

            tool = StructuredTool.from_function(
                func=make_tool_func(node),
                name=node.name,
                description=node.description or f"MCP tool: {node.name}",
                args_schema=InputModel
            )
            tools.append(tool)

        return tools

    def _json_type_to_python(self, json_type: str) -> type:
        """Convert JSON schema type to Python type."""
        type_map = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        return type_map.get(json_type, str)


class MCPClient:
    """
    Client for connecting to MCP servers.

    Usage:
        client = MCPClient()
        await client.connect("npx", ["-y", "@modelcontextprotocol/server-filesystem"])
        tools = await client.list_tools()
        result = await client.call_tool("read_file", {"path": "/tmp/test.txt"})
    """

    def __init__(self):
        self._process: Optional[asyncio.subprocess.Process] = None
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._request_id = 0
        self._pending: Dict[int, asyncio.Future] = {}

    async def connect(
        self,
        command: str,
        args: List[str] = None,
        env: Dict[str, str] = None
    ) -> None:
        """Connect to an MCP server."""
        import os

        process_env = os.environ.copy()
        if env:
            process_env.update(env)

        self._process = await asyncio.create_subprocess_exec(
            command,
            *(args or []),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=process_env
        )

        # Start reading responses
        asyncio.create_task(self._read_responses())

        # Initialize connection
        await self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "company-researcher",
                "version": "1.0.0"
            }
        })

    async def _read_responses(self) -> None:
        """Read responses from MCP server."""
        if not self._process or not self._process.stdout:
            return

        while True:
            try:
                line = await self._process.stdout.readline()
                if not line:
                    break

                response = json.loads(line.decode())
                request_id = response.get("id")

                if request_id in self._pending:
                    self._pending[request_id].set_result(response)
                    del self._pending[request_id]

            except (json.JSONDecodeError, asyncio.CancelledError):
                break

    async def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a request to the MCP server."""
        if not self._process or not self._process.stdin:
            raise RuntimeError("Not connected to MCP server")

        self._request_id += 1
        request_id = self._request_id

        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }

        # Create future for response
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[request_id] = future

        # Send request
        self._process.stdin.write((json.dumps(request) + "\n").encode())
        await self._process.stdin.drain()

        # Wait for response
        response = await asyncio.wait_for(future, timeout=30.0)

        if "error" in response:
            raise RuntimeError(f"MCP error: {response['error']}")

        return response.get("result", {})

    async def list_tools(self) -> List[MCPTool]:
        """List available tools from the MCP server."""
        result = await self._send_request("tools/list")
        tools = []

        for tool_data in result.get("tools", []):
            tools.append(MCPTool(
                name=tool_data.get("name", ""),
                description=tool_data.get("description", ""),
                input_schema=tool_data.get("inputSchema", {})
            ))

        return tools

    async def call_tool(self, name: str, arguments: Dict[str, Any] = None) -> Any:
        """Call a tool on the MCP server."""
        result = await self._send_request("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })
        return result.get("content", [])

    async def list_resources(self) -> List[MCPResource]:
        """List available resources from the MCP server."""
        result = await self._send_request("resources/list")
        resources = []

        for resource_data in result.get("resources", []):
            resources.append(MCPResource(
                uri=resource_data.get("uri", ""),
                name=resource_data.get("name", ""),
                description=resource_data.get("description", ""),
                mime_type=resource_data.get("mimeType", "text/plain")
            ))

        return resources

    async def read_resource(self, uri: str) -> Any:
        """Read a resource from the MCP server."""
        result = await self._send_request("resources/read", {"uri": uri})
        return result.get("contents", [])

    async def list_prompts(self) -> List[MCPPrompt]:
        """List available prompts from the MCP server."""
        result = await self._send_request("prompts/list")
        prompts = []

        for prompt_data in result.get("prompts", []):
            prompts.append(MCPPrompt(
                name=prompt_data.get("name", ""),
                description=prompt_data.get("description", ""),
                arguments=prompt_data.get("arguments", [])
            ))

        return prompts

    async def get_prompt(self, name: str, arguments: Dict[str, str] = None) -> Dict[str, Any]:
        """Get a prompt from the MCP server."""
        result = await self._send_request("prompts/get", {
            "name": name,
            "arguments": arguments or {}
        })
        return result

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self._process:
            self._process.terminate()
            await self._process.wait()
            self._process = None


def map_mcp_to_langgraph(
    config: Union[Dict[str, Any], MCPServer],
    compile: bool = False
) -> Any:
    """
    Convenience function to map MCP config to LangGraph.

    Args:
        config: MCP configuration or server
        compile: Whether to compile the graph

    Returns:
        LangGraph StateGraph or CompiledGraph
    """
    mapper = MCPMapper()
    graph = mapper.analyze(config)
    langgraph = mapper.to_langgraph(graph)

    if compile:
        return langgraph.compile()
    return langgraph


def get_mcp_tools(config: Union[Dict[str, Any], MCPServer]) -> List[Any]:
    """
    Get LangChain tools from MCP configuration.

    Args:
        config: MCP configuration or server

    Returns:
        List of LangChain tools
    """
    mapper = MCPMapper()
    graph = mapper.analyze(config)
    return mapper.to_langchain_tools(graph)
