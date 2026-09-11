# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This file is the single source of release notes; the documentation site renders it as-is.

## [Unreleased]

## [1.1.0] — 2026-09-11

Tracking: [#92](https://github.com/linux-profile/email-profile/issues/92)

### Added
- Optional MCP server — `pip install email-profile[mcp]`, `email-profile-mcp` — with 14 tools and 4 prompts for Claude Code, Claude Desktop and Cursor; sending and deleting are opt-in via `--allow-send` / `--allow-delete` ([#88](https://github.com/linux-profile/email-profile/issues/88))
- Claude Code plugin: `.mcp.json`, plugin manifests and six skills under `skills/` ([#88](https://github.com/linux-profile/email-profile/issues/88))
- `EMAIL_MCP_*` settings: `ALLOW_SEND`, `ALLOW_DELETE`, `MAX_CHARS`, `LIMIT`, `DEFAULT_MAILBOX`, `ATTACHMENTS_DIR`

### Security
- IMAP search strings now escape `"` and `\` per RFC 3501 quoted-string rules ([#88](https://github.com/linux-profile/email-profile/issues/88))
- MCP: `uid` accepts a single id only (sequence sets refused), `save_attachment` is confined to `EMAIL_MCP_ATTACHMENTS_DIR`, and IMAP access is serialized across tool threads ([#88](https://github.com/linux-profile/email-profile/issues/88))
- Bump `mkdocs-material` to 9.7.7 — CVE-2026-73295, DOM XSS in docs search ([#90](https://github.com/linux-profile/email-profile/issues/90))

## [1.0.1] — 2026-08-16

Tracking: [#85](https://github.com/linux-profile/email-profile/issues/85)

### Fixed
- `Email()` port/ssl kwargs silently ignored when auto-discovery is used ([#69](https://github.com/linux-profile/email-profile/issues/69))
- `Sender.send_message` mutated the caller's `EmailMessage` by writing the From header ([#68](https://github.com/linux-profile/email-profile/issues/68))
- `MailBox.move` fallback expunged every deleted message, not just the moved UID ([#67](https://github.com/linux-profile/email-profile/issues/67))
- Query OR/NOT produced wrong IMAP search when combining multi-clause `Query` objects ([#66](https://github.com/linux-profile/email-profile/issues/66))
- Backup/restore corrupted non-UTF8 RFC822 content; binary attachments were lost ([#65](https://github.com/linux-profile/email-profile/issues/65))
- IMAP connect ignored port and ssl flag; non-default ports could not connect ([#64](https://github.com/linux-profile/email-profile/issues/64))

### Security
- Path traversal in attachment filename parsing ([#29](https://github.com/linux-profile/email-profile/issues/29))
- Bump `idna` and `pymdown-extensions` to patched versions ([#83](https://github.com/linux-profile/email-profile/issues/83))

### Tests
- Sync and Restore coverage ([#38](https://github.com/linux-profile/email-profile/issues/38))
- `resolve_smtp_host` coverage ([#37](https://github.com/linux-profile/email-profile/issues/37))

## [1.0.0] — 2026-04-17

Tracking: [#6](https://github.com/linux-profile/email-profile/issues/6)

### Added
- Auto-discovery for 50+ email providers, plus DNS SRV and MX fallback
- Unified `Email` class combining IMAP + SMTP
- Composable query builder `Q` (AND, OR, NOT) and validated `Query` kwargs
- Incremental `sync()` to SQLite and parallel `restore()` with duplicate detection
- Rich progress bars with per-mailbox status
- Send, reply and forward with HTML, attachments, CC/BCC ([#18](https://github.com/linux-profile/email-profile/issues/18))
- IMAP write operations: mark_seen, delete, move, copy, expunge ([#12](https://github.com/linux-profile/email-profile/issues/12))
- Pluggable storage backend (SQLite default)
- Exponential backoff retry on transient failures
- Built-in mailbox shortcuts (inbox, sent, trash, drafts, spam, archive)
- Environment variable configuration with `.env` support
- Slimmer public exports: essentials vs advanced ([#13](https://github.com/linux-profile/email-profile/issues/13))

### Fixed
- Restore loaded all messages into memory, OOM on large backups ([#31](https://github.com/linux-profile/email-profile/issues/31))
- UID parser fallback returned the sequence number instead of the UID ([#32](https://github.com/linux-profile/email-profile/issues/32))
- UID cache in `Where` grew unbounded ([#33](https://github.com/linux-profile/email-profile/issues/33))
- `last()` left the cache corrupt when an exception was raised ([#34](https://github.com/linux-profile/email-profile/issues/34))
- Race in SQLite `save()` could duplicate records under concurrent sync ([#36](https://github.com/linux-profile/email-profile/issues/36))
- `validate_status()` `raise_error` parameter had inconsistent behavior ([#39](https://github.com/linux-profile/email-profile/issues/39))
- `Query(unseen=False)` was ambiguous; now `Optional[bool]` ([#40](https://github.com/linux-profile/email-profile/issues/40))
- No attachment size validation in the SMTP client ([#41](https://github.com/linux-profile/email-profile/issues/41))
- `StorageSQLite.get()` dropped the flags field on round-trip ([#42](https://github.com/linux-profile/email-profile/issues/42))
- `Email()` created `email.db` even when sync/restore was never used ([#43](https://github.com/linux-profile/email-profile/issues/43))
- Silent charset fallback with `errors='replace'` could corrupt content ([#44](https://github.com/linux-profile/email-profile/issues/44))

### Security
- Password no longer kept as a plain Python string longer than needed ([#50](https://github.com/linux-profile/email-profile/issues/50))

[Unreleased]: https://github.com/linux-profile/email-profile/compare/v1.1.0...develop
[1.1.0]: https://github.com/linux-profile/email-profile/releases/tag/v1.1.0
[1.0.1]: https://github.com/linux-profile/email-profile/releases/tag/v1.0.1
[1.0.0]: https://github.com/linux-profile/email-profile/releases/tag/v1.0.0
