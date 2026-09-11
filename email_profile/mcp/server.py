"""Builds the MCP server and runs it over the chosen transport."""

from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version
from typing import Optional

from mcp.server.mcpserver import MCPServer

from email_profile.mcp import prompts
from email_profile.mcp.config import Settings
from email_profile.mcp.session import EmailFactory, Session
from email_profile.mcp.tools import mailbox, message, send

INSTRUCTIONS = """Read, search and manage one email account over IMAP,
and send through its SMTP server when the operator allowed it.

Every message is addressed by the pair (mailbox, uid). uids are only
unique inside their mailbox and change when a message is moved, so take
them from a fresh search_messages call rather than from memory.

Bodies come back truncated by default; when `truncated` is true, read
again with a larger max_chars before summarizing or replying.

Sending, replying and forwarding are irreversible: show the user the
recipients and the full text and wait for approval first. Deleting with
expunge cannot be undone either."""


def build(
    settings: Optional[Settings] = None,
    *,
    email_factory: Optional[EmailFactory] = None,
) -> MCPServer:
    """Assemble an ``MCPServer`` around one lazy ``Email`` connection.

    ``email_factory`` defaults to ``Email.from_env``; nothing connects
    until the first tool call.
    """
    resolved = settings or Settings.from_env()

    if email_factory is None:
        from email_profile.email import Email

        email_factory = Email.from_env

    session = Session(email_factory)
    mcp = MCPServer(
        "email-profile",
        instructions=INSTRUCTIONS,
        version=_version(),
    )
    mailbox.register(mcp, session, resolved)
    message.register(mcp, session, resolved)
    send.register(mcp, session, resolved)
    prompts.register(mcp)
    return mcp


def _version() -> str:
    try:
        return version("email-profile")
    except PackageNotFoundError:  # pragma: no cover
        return "0.0.0"


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="email-profile-mcp",
        description="Expose an email account as MCP tools.",
    )
    parser.add_argument(
        "--allow-send",
        action="store_true",
        help="Expose send_email, reply_message and forward_message.",
    )
    parser.add_argument(
        "--allow-delete",
        action="store_true",
        help="Expose delete_message.",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=None,
        help="Default body cap for read_message (env EMAIL_MCP_MAX_CHARS).",
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="Serve streamable HTTP on --host/--port instead of stdio.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args(argv)


def settings_from_args(args: argparse.Namespace) -> Settings:
    env = Settings.from_env()
    return Settings(
        allow_send=env.allow_send or args.allow_send,
        allow_delete=env.allow_delete or args.allow_delete,
        max_chars=env.max_chars if args.max_chars is None else args.max_chars,
        default_mailbox=env.default_mailbox,
    )


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)
    mcp = build(settings_from_args(args))
    if args.http:
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
