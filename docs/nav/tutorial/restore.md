# Restore

Restore uploads emails from your local SQLite database back to an IMAP server. It preserves the original mailbox structure, flags (read/unread), and dates.

## Why Restore?

- **Migration** — move emails between servers (Hostinger to Gmail, Gmail to Outlook, etc.)
- **Disaster recovery** — re-upload emails after a server failure
- **Account merge** — consolidate multiple accounts into one
- **Testing** — populate a test server with real data

## Restore All Mailboxes

Each email is uploaded to its original mailbox. If a mailbox doesn't exist on the target server, it's created automatically.

{* ./docs_src/sync_and_restore.py ln[16:18] *}

## Restore One Mailbox

{* ./docs_src/sync_and_restore.py ln[20:22] *}

## Skip Duplicates

By default, restore checks if an email already exists on the server (by Message-ID) and skips it. Disable this for faster restores when you know the server is empty:

```python
count = app.restore(skip_duplicates=False)
```

## Parallel Workers

Like sync, restore uses threads — one per mailbox:

```python
count = app.restore(max_workers=5)
```

## Output

Each mailbox shows a progress bar while uploading:

<img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/restore-demo.svg" width="100%">

- **uploaded** — emails sent to the server
- **skipped** — emails already on the server (duplicate detection)

## Restore to a Different Server

Sync from one server, restore to another:

```python
from email_profile import Email, StorageSQLite

storage = StorageSQLite("./backup.db")

# Step 1: sync from source server
with Email("user@old-server.com", "password") as source:
    source.sync()

# Step 2: restore to target server
with Email("user@new-server.com", "password", storage=storage) as target:
    count = target.restore()
    print(f"Migrated {count} emails")
```

## What gets restored?

| Data | Restored? |
|---|---|
| Email content (RFC822) | Yes |
| Mailbox/folder | Yes (created if missing) |
| Flags (read/unread, flagged) | Yes |
| Original date | Yes (from Date header) |
| IMAP UID | No (new UID assigned by server) |

## Reference

- [`Email`](../reference/email.md)
- [`Restore`](../reference/restore.md)
- [`StorageSQLite`](../reference/storage.md)
