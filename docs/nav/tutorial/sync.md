# Sync

Sync downloads emails from your IMAP server to a local SQLite database. It's incremental — only new emails are downloaded. Already synced emails are skipped based on their IMAP UID.

## Why Sync?

- **Backup** — keep a local copy of all your emails in case the server goes down
- **Offline access** — read and search emails without an internet connection
- **Migration** — download from one server, restore to another
- **Analysis** — query your emails with SQL directly on the SQLite file

## Sync All Mailboxes

{* ./docs_src/sync_and_restore.py ln[8:10] *}

## Sync One Mailbox

{* ./docs_src/sync_and_restore.py ln[12:14] *}

## Parallel Workers

By default, sync uses 3 threads — one per mailbox. You can increase for faster syncs or decrease if the server limits connections.

```python
result = app.sync(max_workers=5)
```

## Output

Each mailbox shows a progress bar while downloading. When complete, it prints a summary:

<img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/sync-demo.svg" width="100%">

- **new** — emails downloaded and saved for the first time
- **updated** — emails that existed but were re-saved (e.g. UID changed)
- **skipped** — emails already in the database

## SyncResult

The `sync()` method returns a [`SyncResult`](../reference/sync-result.md) with all the counts:

```python
result = app.sync()

print(result.inserted)
print(result.updated)
print(result.skipped)
print(result.errors)
print(result.total_processed)
print(result.has_errors)
```

## Where are emails stored?

By default, in `./email.db` (SQLite). You can change this:

```python
from email_profile import Email, StorageSQLite

with Email.from_env(storage=StorageSQLite("./backup.db")) as app:
    app.sync()
```

## How to see the data?

Open the SQLite file with any tool:

```bash
sqlite3 email.db "SELECT count(*) FROM raw"
sqlite3 email.db "SELECT uid, mailbox, message_id FROM raw LIMIT 10"
sqlite3 email.db "SELECT mailbox, count(*) FROM raw GROUP BY mailbox"
```

Or with Python:

```python
from email_profile import StorageSQLite

storage = StorageSQLite("./email.db")
print(f"Total: {len(storage.ids())}")
print(f"INBOX: {len(storage.uids('INBOX'))}")
```

## Reference

- [`Email`](../reference/email.md)
- [`Sync`](../reference/sync.md)
- [`SyncResult`](../reference/sync-result.md)
- [`StorageSQLite`](../reference/storage.md)
