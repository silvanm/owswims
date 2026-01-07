"""
ASGI config for owswims project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'owswims.settings')

# Initialize Django ASGI application early to ensure settings are loaded
django_asgi_app = get_asgi_application()

# MCP app instance (lazy initialized)
_mcp_app = None
_mcp_lifespan_started = False


def get_mcp_app():
    """Lazy initialize the MCP app."""
    global _mcp_app
    if _mcp_app is None:
        from app.mcp import get_mcp_app as create_mcp_app
        _mcp_app = create_mcp_app()
    return _mcp_app


async def application(scope, receive, send):
    """
    Combined ASGI application that routes:
    - lifespan events to MCP app (for initialization)
    - /mcp/* requests to FastMCP server
    - All other requests to Django
    """
    global _mcp_lifespan_started

    # Handle lifespan protocol - needed for FastMCP session manager
    if scope['type'] == 'lifespan':
        mcp_app = get_mcp_app()
        # Pass lifespan events to MCP app
        await mcp_app(scope, receive, send)
        _mcp_lifespan_started = True
        return

    if scope['type'] == 'http':
        path = scope.get('path', '')

        # Route MCP requests to FastMCP
        if path.startswith('/mcp'):
            mcp_app = get_mcp_app()

            # Modify scope to strip /mcp prefix
            scope = dict(scope)
            if path == '/mcp' or path == '/mcp/':
                scope['path'] = '/'
                scope['raw_path'] = b'/'
            else:
                scope['path'] = path[4:]  # Remove /mcp, keep the rest
                raw_path = scope.get('raw_path', b'')
                if raw_path:
                    scope['raw_path'] = raw_path[4:]

            await mcp_app(scope, receive, send)
            return

    # All other requests go to Django
    await django_asgi_app(scope, receive, send)
