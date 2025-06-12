# Server for retreiving testing suite data and execute tests from any suite
# this mcp is intended to be used with the MCP client (as claude desktop or chatgpt)
# It is a simple example of how to create an MCP server with a tool and a resource

from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

# Create an MCP server
mcp = FastMCP("qa_tester_mcp", "1.0.0")

# Define a tool to fetch test suite data
@mcp.tool(annotations=ToolAnnotations(
    title="Fetch Test Suite",
    readOnlyHint=True,
    description="Fetch test suite data from a given URL",
    parameters={
        "url": {"type": "string", "description": "The URL of the test suite"},
        "params": {"type": "object", "description": "Optional parameters for the request"}
    },
    responses={
        200: {"description": "Test suite data retrieved successfully"},
        404: {"description": "Test suite not found"},
        500: {"description": "Internal server error"}
    }
))
async def fetch_test_suite(url: str, params: dict[str, Any] | None = None) -> dict:
    """Fetch test suite data from a given URL"""
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"