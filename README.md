# email-profile

[![PyPI](https://img.shields.io/pypi/v/email-profile)](https://pypi.org/project/email-profile/)
[![Python](https://img.shields.io/pypi/pyversions/email-profile)](https://pypi.org/project/email-profile/)
[![Tests](https://img.shields.io/github/actions/workflow/status/linux-profile/email-profile/test.yml?branch=develop&label=tests)](https://github.com/linux-profile/email-profile/actions)
[![License](https://img.shields.io/github/license/linux-profile/email-profile)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/email-profile)](https://pypi.org/project/email-profile/)

The simplest way to work with email in Python. No boilerplate, no low-level IMAP commands, no headaches.

Just connect, read, search, send, backup, and restore — with one class.

```python
from email_profile import Email

with Email("user@gmail.com", "app_password") as app:
    for msg in app.inbox.where().messages():
        print(f"{msg.date} | {msg.from_} | {msg.subject}")
```

That's it. No server configuration needed — email-profile auto-discovers your IMAP server from your email address.

---

- **Documentation**: [linux-profile.github.io/email-profile](https://linux-profile.github.io/email-profile/)
- **Source Code**: [github.com/linux-profile/email-profile](https://github.com/linux-profile/email-profile)
- **PyPI**: [pypi.org/project/email-profile](https://pypi.org/project/email-profile/)

---

## Install

```bash
pip install email-profile
```

## Why email-profile?

Most Python email libraries make you deal with `imaplib` directly, parse raw bytes, manage connections manually, and write dozens of lines just to read your inbox.

**email-profile gives you a clean, human API:**

- Write `Email("user@gmail.com", "pw")` instead of configuring IMAP servers manually
- Write `app.inbox.where(Q.unseen()).first()` instead of raw IMAP search commands
- Write `app.sync()` instead of building your own backup system
- Write `app.send(to="...", subject="...", body="...")` instead of constructing MIME messages

It combines IMAP + SMTP + storage + sync in a single library. No other Python package does this.

## Quick Start

### Connect

Three ways to connect — pick the one that fits:

```python
from email_profile import Email

# Just email + password (auto-discovers the server)
with Email("user@gmail.com", "app_password") as app:
    print(app.mailboxes())

# From .env file (great for production)
with Email.from_env() as app:
    print(app.mailboxes())

# Explicit server (when you need full control)
with Email("imap.gmail.com", "user@gmail.com", "app_password") as app:
    print(app.mailboxes())
```

### Read Emails

```python
with Email.from_env() as app:
    # How many emails?
    print(app.inbox.where().count())

    # Read them
    for msg in app.inbox.where().messages():
        print(f"{msg.date} | {msg.from_} | {msg.subject}")

    # Just the first one
    msg = app.inbox.where().first()

    # Only headers (much faster for large mailboxes)
    for msg in app.inbox.where().messages(mode="headers"):
        print(msg.subject)
```

### Search

Find exactly what you need with composable queries:

```python
from email_profile import Email, Q
from datetime import date

with Email.from_env() as app:
    # Combine conditions with & (AND), | (OR), ~ (NOT)
    q = Q.subject("meeting") & Q.unseen()
    print(app.inbox.where(q).count())

    # From Alice or Bob
    q = Q.from_("alice@x.com") | Q.from_("bob@x.com")

    # Everything except seen emails
    q = ~Q.seen()

    # Emails from 2025, larger than 1MB
    q = Q.since(date(2025, 1, 1)) & Q.before(date(2025, 12, 31)) & Q.larger(1_000_000)
```

Or use validated kwargs if you prefer:

```python
from email_profile import Query

query = Query(subject="report", unseen=True, since=date(2025, 1, 1))
query = Query(subject="report").exclude(subject="spam").or_(subject="urgent")
```

Built-in shortcuts for common searches:

```python
app.unread().count()
app.recent(days=7).count()
app.search("invoice").count()
```

### Send Emails

Send, reply, and forward — with automatic SMTP discovery:

```python
with Email.from_env() as app:
    # Simple
    app.send(to="recipient@x.com", subject="Hello", body="Hi there!")

    # HTML + attachments + CC
    app.send(
        to=["alice@x.com", "bob@x.com"],
        subject="Report",
        body="See attached.",
        html="<h1>Report</h1>",
        attachments=["report.pdf"],
        cc="manager@x.com",
    )

    # Reply to an email (preserves threading)
    msg = app.inbox.where().first()
    app.reply(msg, body="Thanks!")

    # Forward
    app.forward(msg, to="colleague@x.com", body="FYI")
```

### Backup & Restore

Sync your entire mailbox to a local SQLite database. Incremental — only downloads new emails. Parallel — multiple mailboxes at once. With progress bars.

```python
with Email.from_env() as app:
    # Backup everything (compares by Message-ID, skips duplicates)
    result = app.sync()
    print(f"{result.inserted} new, {result.skipped} skipped")

    # Backup one mailbox
    result = app.sync(mailbox="INBOX")

    # Force re-download (skip duplicate check)
    result = app.sync(skip_duplicates=False)

    # Restore to server (e.g. after migrating)
    count = app.restore()
```

<img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/sync-demo.svg" alt="Sync demo">

### Mailbox Operations

```python
with Email.from_env() as app:
    # Built-in folder shortcuts (auto-detected across languages)
    app.inbox      # INBOX
    app.sent       # Sent / Enviados / Enviadas
    app.trash      # Trash / Lixeira / Papelera
    app.drafts     # Drafts / Rascunhos
    app.spam       # Spam / Junk / Lixo Eletrônico

    # Any folder by name
    work = app.mailbox("INBOX.Work")

    # Message operations
    work.mark_seen(uid)
    work.move(uid, "INBOX.Archive")
    work.delete(uid)
```

### Custom Storage

Storage is lazily initialized — `email.db` is only created when `sync()` or `restore()` is first called.

```python
from email_profile import Email, StorageSQLite

# Default: saves to ./email.db on first sync
with Email.from_env() as app:
    app.sync()

# Custom path
with Email.from_env() as app:
    app.storage = StorageSQLite("./backup.db")
    app.sync()
```

## Features

| Feature | Description |
|---|---|
| **Auto-discovery** | Detects IMAP/SMTP servers from email domain (50+ providers) |
| **Unified API** | IMAP + SMTP in a single `Email` class |
| **Query Builder** | Composable search with `Q` (AND, OR, NOT) and validated `Query` kwargs |
| **Sync & Restore** | Incremental backup to SQLite, restore to any server |
| **Parallel** | Multi-threaded sync and restore with configurable workers |
| **Progress** | Rich progress bars with per-mailbox status |
| **Retry** | Exponential backoff on transient failures |
| **Send** | Send, reply, forward with HTML, attachments, CC/BCC |
| **Storage** | Pluggable storage backend (SQLite default) |
| **Flags** | Read/unread, flag, delete, move, copy operations |
| **Context Manager** | `with Email(...) as app:` for automatic cleanup |

## Supported Providers

Auto-discovery works out of the box. Just use your email and password — no server configuration needed.

| | Provider | IMAP Server |
|---|---|---|
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/gmail.svg" width="16"> | Gmail | imap.gmail.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/outlook.svg" width="16"> | Outlook / Hotmail / Live | outlook.office365.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/yahoo.svg" width="16"> | Yahoo | imap.mail.yahoo.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/icloud.svg" width="16"> | iCloud | imap.mail.me.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/zoho.svg" width="16"> | Zoho | imap.zoho.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/protonmail.svg" width="16"> | ProtonMail (Bridge) | 127.0.0.1:1143 |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/aol.svg" width="16"> | AOL | imap.aol.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/yandex.svg" width="16"> | Yandex | imap.yandex.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/mailru.svg" width="16"> | Mail.ru | imap.mail.ru |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/gmx.svg" width="16"> | GMX | imap.gmx.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/hostinger.svg" width="16"> | Hostinger | imap.hostinger.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/godaddy.svg" width="16"> | GoDaddy | imap.secureserver.net |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/namecheap.svg" width="16"> | Namecheap | mail.privateemail.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/gandi.svg" width="16"> | Gandi | mail.gandi.net |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/ovh.svg" width="16"> | OVH | ssl0.ovh.net |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/ionos.svg" width="16"> | Ionos (1&1) | imap.ionos.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | Fastmail | imap.fastmail.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | Rackspace | secure.emailsrvr.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | Titan | imap.titan.email |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | Locaweb | imap.locaweb.com.br |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | KingHost | imap.kinghost.net |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | UOL | imap.uol.com.br |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | Terra | imap.terra.com.br |

Any server with DNS SRV or MX records is also detected automatically.

## MCP Server

Expose the account to any MCP client — Claude Desktop, Claude Code, Cursor — as
tools the model can call: search, read, flag, move, and (when allowed) send.

```bash
pip install email-profile[mcp]
email-profile-mcp --allow-send
```

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

Cursor uses the same shape in `.cursor/mcp.json` — see [examples/](examples/).

### Claude Code plugin

The repository is also a plugin: the server plus six skills that keep the
model from sending before you approve.

```bash
claude plugin marketplace add linux-profile/email-profile
claude plugin install email-profile@email-profile
```

### Tools

| Tool | What it does |
|---|---|
| `list_mailboxes` | Server-side folder names |
| `search_messages` | Filter one mailbox; headers only, newest first, paginated |
| `read_message` | Headers, body (truncated) and attachment metadata |
| `list_attachments` / `save_attachment` | Attachment metadata; write one to disk |
| `mark_seen` / `mark_unseen` / `flag_message` / `unflag_message` | Flags |
| `move_message` | Move to another mailbox |
| `send_email` / `reply_message` / `forward_message` | SMTP — needs `--allow-send` |
| `delete_message` | Flag or expunge — needs `--allow-delete` |

Sending and deleting are off by default and marked destructive, so clients
that support it ask the human first. Credentials come from the environment
only; no tool accepts a password.

Prompts `triage_inbox`, `find_message`, `draft_reply` and `summarize_thread`
put the tools in the order a task needs.

### Options

| Flag | Env | Default |
|---|---|---|
| `--allow-send` | `EMAIL_MCP_ALLOW_SEND` | off |
| `--allow-delete` | `EMAIL_MCP_ALLOW_DELETE` | off |
| `--max-chars` | `EMAIL_MCP_MAX_CHARS` | 4000 |
| — | `EMAIL_MCP_LIMIT` | 20 |
| — | `EMAIL_MCP_DEFAULT_MAILBOX` | `INBOX` |
| `--http --host --port` | — | stdio |

## Environment Variables

```env
EMAIL_USERNAME=user@example.com
EMAIL_PASSWORD=app_password
EMAIL_SERVER=imap.example.com  # optional, auto-discovered
```

## License

MIT
