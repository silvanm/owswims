"""
MCP Server package for Open Water Swims.

Provides an MCP (Model Context Protocol) server for managing events, races,
locations, and organizers via tools compatible with Claude and other MCP clients.
"""
from app.mcp.server import mcp, get_mcp_app

__all__ = ['mcp', 'get_mcp_app']
