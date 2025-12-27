"""
Langfuse instrumentation for LlamaIndex tracing.

This module initializes OpenTelemetry-based tracing for LlamaIndex operations,
sending traces to Langfuse for observability and debugging.
"""

import logging
import os

logger = logging.getLogger(__name__)

_initialized = False


def init_langfuse_instrumentation():
    """
    Initialize Langfuse instrumentation for LlamaIndex.

    This should be called once during application startup.
    The function is idempotent and will only initialize once.

    Required environment variables:
    - LANGFUSE_PUBLIC_KEY
    - LANGFUSE_SECRET_KEY
    - LANGFUSE_BASE_URL (optional, defaults to https://cloud.langfuse.com)
    """
    global _initialized

    if _initialized:
        return

    # Check if Langfuse credentials are configured
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")

    if not public_key or not secret_key:
        logger.warning(
            "Langfuse credentials not configured. "
            "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to enable tracing."
        )
        return

    try:
        from langfuse import get_client
        from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

        # Initialize Langfuse client
        langfuse = get_client()

        # Verify connection
        if langfuse.auth_check():
            logger.info("Langfuse client authenticated successfully")
        else:
            logger.warning("Langfuse authentication failed - tracing may not work")
            return

        # Initialize LlamaIndex instrumentation
        LlamaIndexInstrumentor().instrument()

        _initialized = True
        logger.info("Langfuse instrumentation for LlamaIndex initialized")

    except ImportError as e:
        logger.warning(f"Langfuse instrumentation packages not installed: {e}")
    except Exception as e:
        logger.error(f"Failed to initialize Langfuse instrumentation: {e}")


def get_langfuse_client():
    """
    Get the Langfuse client for manual tracing operations.

    Returns None if Langfuse is not configured.
    """
    try:
        from langfuse import get_client
        return get_client()
    except Exception:
        return None
