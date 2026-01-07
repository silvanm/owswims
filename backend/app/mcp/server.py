"""
FastMCP Server with Django ApiToken authentication.
"""
from typing import Optional

from asgiref.sync import sync_to_async
from django.utils import timezone
from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken, TokenVerifier


class DjangoApiTokenAuth(TokenVerifier):
    """
    Custom auth provider that validates tokens against Django's ApiToken model.
    Subclasses TokenVerifier to get the proper middleware interface.
    """

    async def verify_token(self, token: str) -> Optional[AccessToken]:
        """
        Verify a bearer token against the Django ApiToken table.
        Returns AccessToken with user info if valid, None otherwise.
        """
        from app.models import ApiToken as DjangoApiToken

        @sync_to_async
        def get_and_update_token():
            try:
                api_token = DjangoApiToken.objects.select_related(
                    'user'
                ).get(token=token)
                # Update last_used_at
                api_token.last_used_at = timezone.now()
                api_token.save(update_fields=['last_used_at'])
                return api_token
            except DjangoApiToken.DoesNotExist:
                return None

        api_token = await get_and_update_token()

        if api_token is None:
            return None

        # Return FastMCP AccessToken with claims
        return AccessToken(
            token=token,
            client_id=str(api_token.user.id),
            scopes=["read", "write"],
            expires_at=None,  # ApiTokens don't expire
            extra={
                "user_id": api_token.user.id,
                "username": api_token.user.username,
                "email": api_token.user.email,
                "token_name": api_token.name,
            }
        )


# Create the FastMCP server instance
mcp = FastMCP(
    name="OpenWaterSwims MCP Server",
    version="1.0.0",
    auth=DjangoApiTokenAuth(),
)


def get_mcp_app():
    """
    Returns the FastMCP ASGI application for mounting in Django.
    """
    # Import tools to register them with the server
    from app.mcp.tools import events, races, locations, organizers  # noqa: F401

    return mcp.http_app(path="/")
