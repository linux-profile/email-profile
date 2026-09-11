# MCP Server

Expose one email account to any MCP client — Claude Desktop, Claude Code,
Cursor — as tools the model can call.

```bash
pip install email-profile[mcp]
email-profile-mcp --allow-send
```

Credentials come from the environment (`EMAIL_USERNAME`, `EMAIL_PASSWORD`,
optional `EMAIL_SERVER`) or a `.env` file. No tool accepts a password.

## Configure a client

### Claude Code

```bash
claude mcp add email \
  --env EMAIL_USERNAME=you@gmail.com --env EMAIL_PASSWORD=app-password \
  -- uvx --from "email-profile[mcp]" email-profile-mcp --allow-send
```

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "email": {
      "command": "uvx",
      "args": ["--from", "email-profile[mcp]", "email-profile-mcp", "--allow-send"],
      "env": { "EMAIL_USERNAME": "you@gmail.com", "EMAIL_PASSWORD": "app-password" }
    }
  }
}
```

Cursor reads the same shape from `.cursor/mcp.json`.

### As a Claude Code plugin

The repository doubles as a plugin — the server from `.mcp.json` plus the
skills under `skills/`:

```bash
claude plugin marketplace add linux-profile/email-profile
claude plugin install email-profile@email-profile
```

Set `EMAIL_USERNAME` and `EMAIL_PASSWORD` in your shell; `.mcp.json` reads
them, and `EMAIL_MCP_ALLOW_SEND=true` turns sending on.

| Skill | Leads to |
|---|---|
| `triage-inbox` | Unread first, grouped by sender, nothing changed |
| `find-message` | The most specific filter, then a pick list |
| `read-message` | Full body, re-read when truncated, attachments to disk |
| `draft-reply` | Read the thread, show the text, send on approval |
| `send-email` | Recipients and body confirmed verbatim before sending |
| `organize-mailbox` | Flags and moves first, delete last and only when allowed |

## Tools

Every message is addressed by the pair `(mailbox, uid)`. UIDs are unique
inside one mailbox and change when a message is moved, so take them from
a fresh `search_messages` call.

| Tool | Annotation | What it does |
|---|---|---|
| `list_mailboxes` | read-only | Server-side folder names |
| `search_messages` | read-only | Filter one mailbox; headers only, newest first, paginated |
| `read_message` | read-only | Headers, body (truncated to `max_chars`) and attachment metadata |
| `list_attachments` | read-only | Name, type and size of each attachment |
| `save_attachment` | reversible | Write one attachment to disk |
| `mark_seen` / `mark_unseen` | reversible | Read state |
| `flag_message` / `unflag_message` | reversible | Star |
| `move_message` | reversible | Move to another mailbox |
| `send_email` | destructive | New message over SMTP — `--allow-send` |
| `reply_message` | destructive | Reply keeping thread headers — `--allow-send` |
| `forward_message` | destructive | Forward with attachments — `--allow-send` |
| `delete_message` | destructive | Flag, or expunge with `expunge=true` — `--allow-delete` |

Bodies come back truncated; when `truncated` is `true` the model is told
to read again with a larger `max_chars`. Attachment bytes never cross the
wire.

## Prompts

| Prompt | Leads to |
|---|---|
| `triage_inbox` | `search_messages(unseen=true)` grouped by sender |
| `find_message` | The most specific filter first, then a pick list |
| `draft_reply` | `read_message` → approval → `reply_message` |
| `summarize_thread` | Every message of a subject, oldest first |

## Options

| Flag | Env | Default |
|---|---|---|
| `--allow-send` | `EMAIL_MCP_ALLOW_SEND` | off |
| `--allow-delete` | `EMAIL_MCP_ALLOW_DELETE` | off |
| `--max-chars` | `EMAIL_MCP_MAX_CHARS` | `4000` |
| — | `EMAIL_MCP_LIMIT` | `20` |
| — | `EMAIL_MCP_DEFAULT_MAILBOX` | `INBOX` |
| `--http --host --port` | — | stdio |

`--http` serves streamable HTTP for clients that connect over the network.

## From Python

```python
from email_profile import Email
from email_profile.mcp import Settings, build

server = build(
    Settings(allow_send=True),
    email_factory=lambda: Email("imap.example.com", "user", "pw"),
)
server.run()
```

## Reference

- [Send Emails](../tutorial/send-email.md)
- [Query Builder](../tutorial/query-builder.md)
