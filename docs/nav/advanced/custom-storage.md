# Custom Storage Backend

email-profile uses `StorageABC` as the contract for persistence. The default implementation is `StorageSQLite`, but you can replace it with any backend — PostgreSQL, Redis, S3, MongoDB, or even a plain dict.

## The Contract

Your storage must implement 4 methods:

| Method | What it does | When it's called |
|---|---|---|
| `save(raw)` | Persist one email. Return `True` if inserted, `False` if updated. | During `sync()` for each new email |
| `get(message_id)` | Retrieve one email by message_id. Return `None` if not found. | During `restore()` to read stored emails |
| `ids(mailbox=None)` | Return all stored message_ids. Filter by mailbox if provided. | During `restore()` to iterate all emails |
| `uids(mailbox)` | Return all stored IMAP UIDs for a mailbox. | During `sync()` to skip already downloaded emails |

## The Data Model

Every email is stored as a `RawSerializer`:

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

```python
from typing import Optional

from email_profile.advanced import StorageABC
from email_profile.serializers.raw import RawSerializer


class DictStorage(StorageABC):

    def __init__(self) -> None:
        self._data: dict[tuple[str, str], RawSerializer] = {}

    def save(self, raw: RawSerializer) -> bool:
        key = (raw.uid, raw.mailbox)

        if key in self._data:
            self._data[key] = raw
            return False

        self._data[key] = raw
        return True

    def get(self, message_id: str) -> Optional[RawSerializer]:
        for raw in self._data.values():
            if raw.message_id == message_id:
                return raw
        return None

    def ids(self, mailbox: Optional[str] = None) -> set[str]:
        return {
            raw.message_id
            for raw in self._data.values()
            if mailbox is None or raw.mailbox == mailbox
        }

    def uids(self, mailbox: str) -> set[str]:
        return {
            raw.uid
            for raw in self._data.values()
            if raw.mailbox == mailbox
        }
```

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

```python
import psycopg2
from email_profile.advanced import StorageABC
from email_profile.serializers.raw import RawSerializer


class PostgresStorage(StorageABC):

    def __init__(self, dsn: str) -> None:
        self._conn = psycopg2.connect(dsn)
        self._ensure_table()

    def _ensure_table(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    uid TEXT NOT NULL,
                    mailbox TEXT NOT NULL,
                    message_id TEXT NOT NULL,
                    flags TEXT NOT NULL DEFAULT '',
                    file TEXT,
                    PRIMARY KEY (uid, mailbox)
                )
            """)
            self._conn.commit()

    def save(self, raw: RawSerializer) -> bool:
        with self._conn.cursor() as cur:
            cur.execute(
                """INSERT INTO emails (uid, mailbox, message_id, flags, file)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (uid, mailbox) DO UPDATE
                   SET message_id = EXCLUDED.message_id,
                       flags = EXCLUDED.flags,
                       file = EXCLUDED.file
                   RETURNING xmax""",
                (raw.uid, raw.mailbox, raw.message_id, raw.flags, raw.file),
            )
            xmax = cur.fetchone()[0]
            self._conn.commit()
            return xmax == 0

    def get(self, message_id: str) -> RawSerializer | None:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT message_id, uid, mailbox, flags, file FROM emails WHERE message_id = %s LIMIT 1",
                (message_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return RawSerializer(
                message_id=row[0], uid=row[1], mailbox=row[2],
                flags=row[3], file=row[4],
            )

    def ids(self, mailbox: str | None = None) -> set[str]:
        with self._conn.cursor() as cur:
            if mailbox:
                cur.execute("SELECT message_id FROM emails WHERE mailbox = %s", (mailbox,))
            else:
                cur.execute("SELECT message_id FROM emails")
            return {row[0] for row in cur.fetchall()}

    def uids(self, mailbox: str) -> set[str]:
        with self._conn.cursor() as cur:
            cur.execute("SELECT uid FROM emails WHERE mailbox = %s", (mailbox,))
            return {row[0] for row in cur.fetchall()}
```

## Rules

1. **`save()` must be idempotent** — calling it twice with the same `uid + mailbox` should update, not duplicate
2. **`save()` returns `bool`** — `True` if a new row was inserted, `False` if an existing row was updated
3. **`get()` returns `None`** when the message_id doesn't exist — never raise
4. **`uids()` filters by mailbox** — this is how sync knows which emails to skip
5. **`ids()` with `mailbox=None`** returns all message_ids across all mailboxes
6. **Thread safety** — sync runs with multiple threads, your storage must handle concurrent writes
