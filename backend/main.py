from fastapi import FastAPI, Request
from mcp.server import NotificationOptions, InitializationOptions
from mcp.server.sse import SseServerTransport
from config_manager import ConfigManager
from vector_service import VectorService
from mcp_core import MCPCore
import uvicorn
import os

# 1. Initialize Modular Components
config_manager = ConfigManager(config_path="config.yaml")
vector_service = VectorService(db_path="./db")
mcp_core = MCPCore(config_manager, vector_service)

# 2. FastAPI Application Setup
app = FastAPI(
    title=config_manager.config.name,
    version=config_manager.config.version,
    description="FastAPI_MCP_PoC: Unified MCP & Knowledge Base"
)

# 3. MCP SSE Transport Setup
# This exposes the MCP protocol over SSE.
# The SseServerTransport handles the SSE connection and message routing.
mcp_transport = SseServerTransport("/mcp/messages")

@app.get("/")
async def health_check():
    """Simple health check and version info."""
    return {
        "status": "online",
        "server": config_manager.config.name,
        "version": config_manager.config.version,
        "mcp_endpoint": "/mcp/sse"
    }

@app.get("/metrics")
async def get_metrics():
    """Exposes internal metrics to the Python Frontend."""
    return mcp_core.get_metrics()

@app.get("/config")
async def get_config():
    """Returns the current raw YAML configuration."""
    return {"yaml": config_manager.get_raw_yaml()}

@app.post("/config/update")
async def update_config(request: Request):
    """Updates the configuration from the Frontend."""
    data = await request.json()
    new_config_yaml = data.get("yaml")
    if new_config_yaml:
        config_manager.update_from_yaml(new_config_yaml)
        return {"status": "success", "message": "Configuration updated"}
    return {"status": "error", "message": "No YAML provided"}

# --- SSE Endpoints for MCP Protocol ---
@app.get("/mcp/sse")
async def sse(request: Request):
    """SSE endpoint for MCP client connections."""
    async with mcp_transport.connect_sse(request.scope, request.receive, request.send) as (read_stream, write_stream):
        await mcp_core.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=config_manager.config.name,
                server_version=config_manager.config.version,
                capabilities=mcp_core.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

@app.post("/mcp/messages")
async def messages(request: Request):
    """Post messages endpoint for MCP protocol."""
    await mcp_transport.handle_post_message(request.scope, request.receive, request.send)

if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
