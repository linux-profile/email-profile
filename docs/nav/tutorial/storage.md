# Storage

## Default Storage

By default, emails are stored in `./email.db` (SQLite). The database file is lazily created — only when `sync()` or `restore()` is first called.

{* ./docs_src/storage.py ln[9:11] *}

## Custom Path

{* ./docs_src/storage.py ln[13:16] *}

## In-Memory (testing)

{* ./docs_src/storage.py ln[18:21] *}

## Full Code

{* ./docs_src/storage.py *}

## Reference

- [StorageSQLite](../reference/storage.md)
- [StorageABC](../reference/storage-abc.md)
- [Email](../reference/email.md)
