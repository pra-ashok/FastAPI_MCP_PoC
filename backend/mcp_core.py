import asyncio
from typing import Any, Dict, List, Optional
from mcp.server import Server
import mcp.types as types
from config_manager import ConfigManager
from models import ToolConfig, ResourceConfig
from vector_service import VectorService

class MCPCore:
    """
    Handles the MCP protocol logic, including tool registration,
    resource management, and dynamic execution of Python code.
    Now integrated with VectorService for Knowledge Base access.
    """
    def __init__(self, config_manager: ConfigManager, vector_service: VectorService):
        self.config_manager = config_manager
        self.vector_service = vector_service
        self.server = Server(self.config_manager.config.name)
        self._setup_handlers()
        
        # Simple metrics
        self.metrics = {
            "tools_called": 0,
            "resources_read": 0,
            "vector_queries": 0,
            "errors": 0
        }

    def _setup_handlers(self):
        """Registers MCP handlers for listing/calling tools and resources."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            # Default vector tools + configured tools
            base_tools = [
                types.Tool(
                    name="kb_search",
                    description="Search the knowledge base for information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="kb_add",
                    description="Add information to the knowledge base",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Content to add"}
                        },
                        "required": ["content"]
                    }
                )
            ]
            
            config_tools = [
                types.Tool(
                    name=t.name,
                    description=t.description,
                    inputSchema=t.input_schema
                )
                for t in self.config_manager.config.tools
            ]
            return base_tools + config_tools

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any] | None
        ) -> List[types.TextContent]:
            self.metrics["tools_called"] += 1
            arguments = arguments or {}

            # Handle internal vector tools
            if name == "kb_search":
                self.metrics["vector_queries"] += 1
                results = await self.vector_service.query(arguments.get("query", ""))
                return [types.TextContent(type="text", text="\n".join(results))]
            
            if name == "kb_add":
                doc_id = await self.vector_service.add_document(arguments.get("content", ""))
                return [types.TextContent(type="text", text=f"Added to KB with ID: {doc_id}")]

            # Handle dynamic configured tools
            tool = next((t for t in self.config_manager.config.tools if t.name == name), None)
            if not tool:
                self.metrics["errors"] += 1
                raise ValueError(f"Tool {name} not found")
            
            return await self._execute_tool(tool, arguments)

        @self.server.list_resources()
        async def handle_list_resources() -> List[types.Resource]:
            return [
                types.Resource(
                    uri=r.uri,
                    name=r.name,
                    description=r.description,
                    mimeType="text/plain"
                )
                for r in self.config_manager.config.resources
            ]

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            self.metrics["resources_read"] += 1
            resource = next((r for r in self.config_manager.config.resources if r.uri == uri), None)
            if not resource:
                self.metrics["errors"] += 1
                raise ValueError(f"Resource {uri} not found")
            return resource.content

    async def _execute_tool(self, tool: ToolConfig, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Dynamically executes Python code defined in the tool configuration."""
        try:
            # Prepare execution environment
            exec_globals = {
                "__builtins__": __builtins__,
                "asyncio": asyncio,
                "import_module": __import__,
                "vector_service": self.vector_service  # Allow tools to access vector service
            }
            # Inject arguments directly into the local scope
            exec_locals = arguments.copy()
            
            # Wrap tool code in an async function
            indented_code = "\n".join(f"    {line}" for line in tool.code.splitlines())
            wrapper = f"async def __mcp_execute__():\n{indented_code}"
            
            exec(wrapper, exec_globals, exec_locals)
            func = exec_locals["__mcp_execute__"]
            
            # Execute and capture result
            result = await func()
            
            return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            self.metrics["errors"] += 1
            return [types.TextContent(type="text", text=f"Execution Error: {str(e)}")]

    def get_metrics(self) -> Dict[str, Any]:
        """Returns internal metrics for the dashboard."""
        stats = self.vector_service.get_stats()
        return {**self.metrics, "kb_count": stats["count"]}
