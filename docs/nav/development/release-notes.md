# Release

August 4, 2026

---

## v1.0.1

- [📌 v1.0.1: Bug fixes, security patches, and test coverage](https://github.com/linux-profile/email-profile/issues/85)
- [⚠️ Fix open Dependabot security alerts (idna, pymdown-extensions)](https://github.com/linux-profile/email-profile/issues/83)
- [🪲 Email() port/ssl kwargs silently ignored when auto-discovery is used](https://github.com/linux-profile/email-profile/issues/69)
- [🪲 Sender.send_message mutates caller's EmailMessage by writing From header](https://github.com/linux-profile/email-profile/issues/68)
- [🪲 MailBox.move fallback expunges every deleted message, not just the moved UID](https://github.com/linux-profile/email-profile/issues/67)
- [🪲 Query OR/NOT produce wrong IMAP search when combining multi-clause Query objects](https://github.com/linux-profile/email-profile/issues/66)
- [🪲 Backup/restore corrupts non-UTF8 RFC822 content (binary attachments lost)](https://github.com/linux-profile/email-profile/issues/65)
- [🪲 IMAP connect ignores port and ssl flag — non-default ports cannot connect](https://github.com/linux-profile/email-profile/issues/64)
- [❤️ Sync and Restore modules have zero test coverage](https://github.com/linux-profile/email-profile/issues/38)
- [❤️ SMTP host resolution (resolve_smtp_host) has no test coverage](https://github.com/linux-profile/email-profile/issues/37)
- [⚠️ Path traversal vulnerability in attachment filename parsing](https://github.com/linux-profile/email-profile/issues/29)

## v1.0.0

- [📦 PyPI - Build 1.0.0](https://github.com/linux-profile/email-profile/releases/tag/v1.0.0)
- [📌 RFC: Refactor _email_profile/ — fix critical bugs and ship a clean v1.0.0 API](https://github.com/linux-profile/email-profile/issues/6)
- [⚠️ Password stored as plain Python string — no secure memory handling](https://github.com/linux-profile/email-profile/issues/50)
- [🪲 Restore loads all messages into memory causing OOM on large backups](https://github.com/linux-profile/email-profile/issues/31)
- [🪲 UID parser fallback returns wrong value (sequence number instead of UID)](https://github.com/linux-profile/email-profile/issues/32)
- [🪲 UID cache in Where clause grows unbounded — no TTL or size limit](https://github.com/linux-profile/email-profile/issues/33)
- [🪲 last() temporarily mutates internal cache — exception leaves corrupt state](https://github.com/linux-profile/email-profile/issues/34)
- [🪲 Race condition in SQLite save() — concurrent sync can duplicate records](https://github.com/linux-profile/email-profile/issues/36)
- [🪲 Query(unseen=False) has ambiguous semantics — should use Optional[bool]](https://github.com/linux-profile/email-profile/issues/40)
- [🪲 No attachment size validation in SMTP client — risk of OOM and timeouts](https://github.com/linux-profile/email-profile/issues/41)
- [🪲 StorageSQLite.get() drops flags field from RawSerializer round-trip](https://github.com/linux-profile/email-profile/issues/42)
- [🪲 Email() constructor creates email.db file even when sync/restore is not used](https://github.com/linux-profile/email-profile/issues/43)
- [🪲 Silent charset fallback with errors='replace' can corrupt email content](https://github.com/linux-profile/email-profile/issues/44)
- [⚙️ validate_status() has confusing raise_error parameter with inconsistent behavior](https://github.com/linux-profile/email-profile/issues/39)
- [⚙️ Feature: Add IMAP write operations (mark_seen, delete, move, copy, expunge)](https://github.com/linux-profile/email-profile/issues/12)
- [⚙️ API: Slim public exports — split essentials from advanced](https://github.com/linux-profile/email-profile/issues/13)
- [⚙️ Feature: Add SMTP send support (outgoing mail)](https://github.com/linux-profile/email-profile/issues/18)
- [⚙️ Refactor: Rename Where.refresh() to Where.clear_cache()](https://github.com/linux-profile/email-profile/issues/9)
- [⚙️ Refactor: Add public properties Email.user / .server / .is_connected](https://github.com/linux-profile/email-profile/issues/10)
- [⚙️ Refactor: Move AppendedUID and IMAPHost to email_profile.types](https://github.com/linux-profile/email-profile/issues/11)
- [⚙️ Refactor: Deduplicate Email.from_email and EmailFactories.from_address](https://github.com/linux-profile/email-profile/issues/20)
- [⚙️ Refactor: Rename email_profile/factories.py](https://github.com/linux-profile/email-profile/issues/21)
- [⚙️ Refactor: Uniform naming across IMAP/SMTP clients](https://github.com/linux-profile/email-profile/issues/22)
- [⚙️ Refactor: Remove dead EmailFactories.PROVIDER_HOSTS or wire it up](https://github.com/linux-profile/email-profile/issues/23)
- [⚙️ Refactor: Remove per-provider classmethods from Email](https://github.com/linux-profile/email-profile/issues/28)
- [⬆️ Improve repository SEO and discoverability](https://github.com/linux-profile/email-profile/issues/63)

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
