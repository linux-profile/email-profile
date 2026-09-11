"""Fails when the skills and the server disagree about the tools.

A tool ships and no skill mentions it, or a skill keeps naming one that
was removed. This turns that into a red build instead of something a
reviewer finds.
"""

from __future__ import annotations

import asyncio
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

sys.path.insert(0, str(ROOT))


def server_tools() -> set[str]:
    from email_profile.mcp import Settings, build

    server = build(Settings(allow_send=True, allow_delete=True))
    return {tool.name for tool in asyncio.run(server.list_tools())}


def mentioned_tools() -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for path in sorted(SKILLS.glob("*/SKILL.md")):
        names = set(re.findall(r"`([a-z]+(?:_[a-z]+)+)`", path.read_text()))
        found[path.parent.name] = names
    return found


def main() -> int:
    tools = server_tools()
    per_skill = mentioned_tools()
    named = set().union(*per_skill.values()) if per_skill else set()

    prefixes = (
        "list_",
        "search_",
        "read_",
        "save_",
        "mark_",
        "flag_",
        "unflag_",
        "move_",
        "delete_",
        "send_",
        "forward_",
    )
    # `reply_` alone would flag the `reply_to` argument.
    prefixes += ("reply_message",)
    invented = {n for n in named if n.startswith(prefixes)} - tools
    uncovered = tools - named

    if invented:
        print(
            f"skills name tools the server does not have: {sorted(invented)}"
        )
    if uncovered:
        print(f"tools no skill mentions: {sorted(uncovered)}")

    print(f"{len(tools)} tools, {len(per_skill)} skills")
    return 1 if invented or uncovered else 0


if __name__ == "__main__":
    raise SystemExit(main())
