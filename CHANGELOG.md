# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Auto-discovery for 50+ email providers (Gmail, Outlook, Yahoo, iCloud, Zoho, and more)
- Unified `Email` class combining IMAP + SMTP in a single API
- Composable query builder with `Q` expressions (AND, OR, NOT)
- Validated `Query` kwargs with Pydantic
- Incremental backup to SQLite with `sync()`
- Parallel restore from SQLite with `restore()`
- Multi-threaded sync and restore with configurable workers
- Rich progress bars with per-mailbox status
- Send, reply, and forward with HTML, attachments, CC/BCC
- Automatic SMTP server discovery
- Pluggable storage backend (SQLite default)
- Flag operations: read/unread, flag, delete, move, copy
- Context manager support for automatic cleanup
- Exponential backoff retry on transient failures
- Built-in mailbox shortcuts (inbox, sent, trash, drafts, spam, archive)
- DNS SRV and MX record-based server auto-detection
- Environment variable configuration with `.env` support

[Unreleased]: https://github.com/linux-profile/email-profile/compare/main...develop
