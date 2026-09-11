"""MCP (Model Context Protocol) server built on top of ``Email``.

Requires the ``mcp`` extra::

    pip install email-profile[mcp]
    email-profile-mcp --allow-send
"""

from email_profile.mcp.config import Settings
from email_profile.mcp.server import build, main

__all__ = ["Settings", "build", "main"]
