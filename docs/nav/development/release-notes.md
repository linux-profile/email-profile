# Release Notes

## v0.6.0 (in progress)

### Features
- ⚙️ Simplify storage to raw-only with RawSerializer contract
- ⚙️ Add sync (server → storage) with parallel fetch and Rich progress bars
- ⚙️ Add restore (storage → server) with parallel upload and auto-create mailboxes
- ⚙️ Add Query builder with `exclude()` and `or_()` chaining
- ⚙️ Add Q composable expressions (AND, OR, NOT)
- ⚙️ Add F fetch spec builder
- ⚙️ Add ImapFetch, ImapSearch, EmailParser protocol parsers
- ⚙️ Add auto-discovery for 50+ email providers (DNS SRV, MX, known hosts)
- ⚙️ Rename EmailSerializer to Message
- ⚙️ Add `Where.first()`, `last()`, `list()`, `[index]`, `len()`, `bool()`
- ⚙️ Reorganize into `clients/imap/` and `clients/smtp/` subpackages
- ⚙️ Add retry with exponential backoff on sync/restore
- ⚙️ Change PK to uid+mailbox composite key
- ⚙️ Restructure Restore with orchestrate pattern matching Sync

### Bug Fixes
- 🪲 Fix UID extraction (sequence number vs real UID)
- 🪲 Fix FLAGS parsing for servers that return flags as separate bytes
- 🪲 Fix mailbox names with spaces (IMAP quoting)
- 🪲 Fix broken imports in advanced.py
- 🪲 Show error reason in sync/restore failure messages

### Documentation
- 📘 Add MkDocs Material documentation with tutorials, concepts, and API reference
- 📘 Rewrite README with examples, provider icons, and human-friendly copy
- 📘 Add animated terminal demos for sync and restore
- 📘 Add 16 examples covering all public API features
- 📘 Add Advanced usage guide (IMAP/SMTP direct, custom storage, parser, retry)

### Dependencies
- 📦 Add rich for progress bars
- 📦 Add mkdocs-material and mkdocstrings

---

## v0.4.0

- [📦 PyPI - Build 0.4.0](https://github.com/linux-profile/email-profile/releases/tag/v0.4.0)
- ⚙️ Update project structure
- ❤️ Update tests
- 📘 Update documentation

## v0.3.0

- [📦 PyPI - Build 0.3.0](https://github.com/linux-profile/email-profile/releases/tag/v0.3.0)
- ⚙️ Dump HTML export
- ⚙️ SQLite dump
- ⚙️ Removal of the sqlite feature (moved to SQLAlchemy)
- ❤️ Update tests
- 📘 Update documentation

## v0.2.0

- [📦 PyPI - Build 0.2.0](https://github.com/linux-profile/email-profile/releases/tag/v0.2.0)
- ⚙️ Initial implementation for SQLite storage
- ⚙️ Change connection structure to the Database
- ⚙️ Improved code
- ❤️ Update tests
- 📘 Update documentation

## v0.1.0

- [📦 PyPI - Build 0.1.0](https://github.com/linux-profile/email-profile/releases/tag/v0.1.0)
- ⚙️ Initial release
- ⚙️ IMAP client with email fetching
- ⚙️ Query API structure (mailbox, since, before, subject)
- ⬆️ CI/CD setup
- 📘 Initial documentation
