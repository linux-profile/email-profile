# email-profile

A Python library for email management. Connect to any IMAP/SMTP server, read and send emails, sync your mailbox to a local database, and restore backups — all with a single, unified API.

```python
from email_profile import Email

with Email("user@gmail.com", "app_password") as app:
    for msg in app.inbox.where().messages():
        print(f"{msg.date} | {msg.from_} | {msg.subject}")
```

---

- **Source Code**: [github.com/linux-profile/email-profile](https://github.com/linux-profile/email-profile)

---

## Install

```bash
pip install email-profile
```

## Quick Start

### Connect

```python
from email_profile import Email

# Auto-discovery (detects IMAP server from email domain)
with Email("user@gmail.com", "app_password") as app:
    print(app.mailboxes())

# From environment variables (.env)
with Email.from_env() as app:
    print(app.mailboxes())

# Explicit server
with Email("imap.gmail.com", "user@gmail.com", "app_password") as app:
    print(app.mailboxes())
```

### Read Emails

```python
with Email.from_env() as app:
    # Count
    print(app.inbox.where().count())

    # Read all
    for msg in app.inbox.where().messages():
        print(f"{msg.date} | {msg.from_} | {msg.subject}")

    # Headers only (faster)
    for msg in app.inbox.where().messages(mode="headers"):
        print(msg.subject)
```

### Search with Q

```python
from email_profile import Email, Q
from datetime import date

with Email.from_env() as app:
    # Composable queries
    q = Q.subject("meeting") & Q.unseen()
    print(app.inbox.where(q).count())

    # OR
    q = Q.from_("alice@x.com") | Q.from_("bob@x.com")

    # NOT
    q = ~Q.seen()

    # Date range
    q = Q.since(date(2025, 1, 1)) & Q.before(date(2025, 12, 31))

    # Size filter
    q = Q.larger(1_000_000)
```

### Search with Query (validated kwargs)

```python
from email_profile import Email, Query
from datetime import date

with Email.from_env() as app:
    # Simple
    query = Query(subject="report", unseen=True, since=date(2025, 1, 1))
    print(app.inbox.where(query).count())

    # Exclude and OR
    query = Query(subject="report").exclude(subject="spam").or_(subject="urgent")
```

### Shortcuts

```python
with Email.from_env() as app:
    app.unread().count()
    app.recent(days=7).count()
    app.search("invoice").count()
```

### Send Emails

```python
with Email.from_env() as app:
    # Simple
    app.send(to="recipient@x.com", subject="Hello", body="Hi there!")

    # HTML + attachments
    app.send(
        to=["alice@x.com", "bob@x.com"],
        subject="Report",
        body="See attached.",
        html="<h1>Report</h1>",
        attachments=["report.pdf"],
    )

    # Reply
    msg = list(app.inbox.where().messages(chunk_size=1))[0]
    app.reply(msg, body="Thanks!")

    # Forward
    app.forward(msg, to="colleague@x.com", body="FYI")
```

### Sync (server to local database)

```python
with Email.from_env() as app:
    # Sync all mailboxes
    result = app.sync()
    print(f"{result.inserted} new, {result.skipped} skipped")

    # Sync one mailbox
    result = app.sync(mailbox="INBOX")
```

### Restore (local database to server)

```python
with Email.from_env() as app:
    # Restore all
    count = app.restore()

    # Restore one mailbox
    count = app.restore(mailbox="INBOX")
```

### Mailbox Operations

```python
with Email.from_env() as app:
    # List
    print(app.mailboxes())

    # Access
    inbox = app.mailbox("INBOX")

    # Shortcuts
    app.inbox
    app.sent
    app.trash
    app.drafts
    app.spam

    # Message operations
    inbox.mark_seen(uid)
    inbox.mark_unseen(uid)
    inbox.flag(uid)
    inbox.delete(uid)
    inbox.move(uid, "INBOX.Archive")
    inbox.copy(uid, "INBOX.Backup")
```

### Custom Storage

```python
from email_profile import Email, StorageSQLite

# Default: ./email.db
with Email.from_env() as app:
    app.sync()

# Custom path
with Email.from_env(storage=StorageSQLite("./backup.db")) as app:
    app.sync()

# In-memory (testing)
with Email.from_env(storage=StorageSQLite("sqlite:///:memory:")) as app:
    app.sync()
```

## Features

| Feature | Description |
|---|---|
| **Auto-discovery** | Detects IMAP/SMTP servers from email domain (50+ providers) |
| **Unified API** | IMAP + SMTP in a single `Email` class |
| **Query Builder** | Composable search with `Q` (AND, OR, NOT) and validated `Query` kwargs |
| **Sync** | Incremental backup from server to SQLite with progress bars |
| **Restore** | Upload emails back to server with duplicate detection |
| **Parallel** | Multi-threaded sync and restore with configurable workers |
| **Progress** | Rich progress bars with per-mailbox status |
| **Retry** | Exponential backoff on transient failures |
| **Send** | Send, reply, forward with HTML and attachments |
| **Storage** | Pluggable storage backend (SQLite default) |
| **Flags** | Read/unread, flag, delete, move, copy operations |
| **Context Manager** | `with Email(...) as app:` for automatic cleanup |

## Supported Providers

Auto-discovery works out of the box for:

Gmail, Outlook, Hotmail, Yahoo, iCloud, Zoho, Fastmail, ProtonMail (Bridge), AOL, Yandex, Mail.ru, GMX, Hostinger, Titan, GoDaddy, Namecheap, Gandi, OVH, Ionos, Rackspace, Locaweb, KingHost, UOL, Terra, and any server with DNS SRV/MX records.

## Environment Variables

```env
EMAIL_USERNAME=user@example.com
EMAIL_PASSWORD=app_password
EMAIL_SERVER=imap.example.com  # optional, auto-discovered
```

## License

MIT

## Commit Style

- ⚙️ FEATURE
- 📝 PEP8
- 📌 ISSUE
- 🪲 BUG
- 📘 DOCS
- 📦 PyPI
- ❤️️ TEST
- ⬆️ CI/CD
- ⚠️ SECURITY
