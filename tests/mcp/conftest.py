"""Fixtures: a server over the fake IMAP client, and a tool caller."""

from __future__ import annotations

import asyncio

import pytest

pytest.importorskip("mcp")

from email_profile.mcp import Settings, build  # noqa: E402


def call(server, name: str, **kwargs):
    """Call a tool and return its structured result."""
    result = asyncio.run(server.call_tool(name, kwargs))
    structured = result.structured_content or {}
    return structured.get("result", structured)


def tool_names(server) -> set[str]:
    return {t.name for t in asyncio.run(server.list_tools())}


@pytest.fixture
def make_server(app):
    def factory(**overrides):
        return build(Settings(**overrides), email_factory=lambda: app)

    return factory


@pytest.fixture
def server(make_server):
    return make_server(allow_send=True, allow_delete=True)
