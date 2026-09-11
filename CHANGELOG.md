# Changelog

## v1.1.0

### What's Changed

- [📦 PyPI - Build 1.1.0](https://github.com/linux-profile/email-profile/releases/tag/v1.1.0)
- [📌 v1.1.0: MCP server, Claude Code plugin and security hardening](https://github.com/linux-profile/email-profile/issues/92)
- [⚙️ Add optional MCP server (email-profile[mcp])](https://github.com/linux-profile/email-profile/issues/88)
- [⚠️ Bump mkdocs-material to 9.7.7 (CVE-2026-73295, DOM XSS in search)](https://github.com/linux-profile/email-profile/issues/90)

**Full Changelog**: https://github.com/linux-profile/email-profile/compare/v1.0.1...v1.1.0

## v1.0.1

*2026-08-16*

### What's Changed

- [📦 PyPI - Build 1.0.1](https://github.com/linux-profile/email-profile/releases/tag/v1.0.1)
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

**Full Changelog**: https://github.com/linux-profile/email-profile/compare/v1.0.0...v1.0.1

## v1.0.0

*2026-04-17*

### What's Changed

- ISSUE-2: Initial Documentation by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/3
- ISSUE-4 by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/5
- ⚙️ FEATURE-#6: API ergonomics overhaul (v1.0.0) by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/7
- ⚙️ FEATURE-#9: Rename Where.refresh() to Where.clear_cache() by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/14
- ⚙️ FEATURE-#10: Add Email public properties by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/15
- ⚙️ FEATURE-#11: Move AppendedUID and IMAPHost to email_profile.types by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/17
- ⚙️ FEATURE-#18: Add SMTP send + split Email into 6 classes by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/19
- ⚙️ FEATURE-#23: Wire up EmailFactories.PROVIDER_HOSTS by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/24
- ⚙️ FEATURE-#20: Dedupe Email.from_email / EmailFactories.from_address by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/25
- ⚙️ FEATURE-#21: Rename factories.py to credentials.py by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/26
- ⚙️ FEATURE-#22: Uniform naming across IMAP/SMTP clients by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/27
- 🪲 BUG-#42: Include flags field in StorageSQLite.get() response by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/51
- Lazily initialize storage to avoid creating email.db unnecessarily by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/57
- Split validate_status into validate and check for clarity by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/61
- 🪲 BUG-#34: Use try/finally to restore cache in last() and __getitem__ by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/54
- 🪲 BUG-#32: Remove UID parser fallback that returns sequence number by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/52
- Fix OOM on large backup restores by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/58
- 🪲 BUG-#33: Auto-clear UID cache after iteration and warn on large caches by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/53
- 🪲 BUG-#44: Try common charset fallbacks before using replacement characters by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/56
- 🪲 BUG-#36: Fix race condition in SQLite save() by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/55
- 🔒 SEC-#50: Clear password references on close and mask in repr by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/59
- Add attachment size validation to SMTP client by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/62
- ⚙️ FEATURE-#40: Use Optional[bool] for Query flags to remove ambiguity by @FernandoCelmer in https://github.com/linux-profile/email-profile/pull/60

**Full Changelog**: https://github.com/linux-profile/email-profile/compare/v0.4.0...v1.0.0

## v1.0.0.dev1

*2026-04-16* — pre-release with the same changes as v1.0.0.

**Full Changelog**: https://github.com/linux-profile/email-profile/compare/v0.4.0...v1.0.0.dev1
