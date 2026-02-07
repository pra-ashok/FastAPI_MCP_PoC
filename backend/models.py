from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ToolConfig(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    code: str  # Python code to execute for this tool

class ResourceConfig(BaseModel):
    name: str
    description: str
    uri: str
    content: str # Can be a template or static content

class ServerConfig(BaseModel):
    name: str = "Flexible MCP Server"
    version: str = "0.1.0"
    tools: List[ToolConfig] = []
    resources: List[ResourceConfig] = []
