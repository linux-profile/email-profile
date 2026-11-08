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

## Security

Messages are stored as **plaintext** RFC822 sources (headers, body and attachments). Anyone who can read the database file can read every synced email.

- New database files are created with owner-only permissions (`0600`), and existing files are tightened to `0600` on open (POSIX only).
- Keep the file out of shared or synced folders and out of version control (add `*.db` to `.gitignore`).
- For encryption at rest, use an encrypted disk or volume, or implement a custom storage (see [Custom Storage](../advanced/custom-storage.md)).

## Reference

- [StorageSQLite](../reference/storage.md)
- [StorageABC](../reference/storage-abc.md)
- [Email](../reference/email.md)
