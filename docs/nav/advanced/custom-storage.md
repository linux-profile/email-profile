# Custom Storage Backend

email-profile uses [`StorageABC`](../reference/storage-abc.md) as the contract for persistence. The default implementation is [`StorageSQLite`](../reference/storage.md), but you can replace it with any backend — PostgreSQL, Redis, S3, MongoDB, or even a plain dict.

## The Contract

Your storage must implement 4 methods:

| Method | What it does | When it's called |
|---|---|---|
| `save(raw)` | Persist one email. Return `True` if inserted, `False` if updated. | During `sync()` for each new email |
| `get(message_id)` | Retrieve one email by message_id. Return `None` if not found. | During `restore()` to read stored emails |
| `ids(mailbox=None)` | Return all stored message_ids. Filter by mailbox if provided. | During `restore()` to iterate all emails |
| `uids(mailbox)` | Return all stored IMAP UIDs for a mailbox. | During `sync()` to skip already downloaded emails |

## The Data Model

Every email is stored as a [`RawSerializer`](../reference/raw-serializer.md):

```python
RawSerializer(
    message_id="<abc@example.com>",  # Message-ID header (unique per email)
    uid="17935",                      # IMAP UID (unique per mailbox)
    mailbox="INBOX",                  # Mailbox name
    flags="\\Seen",                   # IMAP flags
    file="From: alice@x.com\r\n...", # Complete RFC822 content
)
```

The primary key is `uid + mailbox` — the same email can exist in multiple mailboxes.

## Minimal Example

{* ./docs_src/storage_dict.py *}

## Usage

Pass your storage to `Email`:

```python
from email_profile import Email

storage = DictStorage()

with Email.from_env(storage=storage) as app:
    app.sync()
    print(f"Stored {len(storage.ids())} emails")
```

## PostgreSQL Example

{* ./docs_src/storage_postgres.py *}

## Rules

1. **`save()` must be idempotent** — calling it twice with the same `uid + mailbox` should update, not duplicate
2. **`save()` returns `bool`** — `True` if a new row was inserted, `False` if an existing row was updated
3. **`get()` returns `None`** when the message_id doesn't exist — never raise
4. **`uids()` filters by mailbox** — this is how sync knows which emails to skip
5. **`ids()` with `mailbox=None`** returns all message_ids across all mailboxes
6. **Thread safety** — sync runs with multiple threads, your storage must handle concurrent writes

## Reference

- [StorageABC](../reference/storage-abc.md)
- [StorageSQLite](../reference/storage.md)
- [RawSerializer](../reference/raw-serializer.md)
