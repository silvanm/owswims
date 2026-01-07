"""
MCP Tools package - imports all tool modules to register them with the server.
"""
from app.mcp.tools import events, races, locations, organizers

__all__ = ['events', 'races', 'locations', 'organizers']
