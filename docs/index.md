# Welcome to email-profile

<div align="center">
  <a aria-label="Documentation" href="https://linux-profile.github.io/email-profile/">Documentation</a>
  &nbsp;•&nbsp;
  <a aria-label="Pypi" href="https://pypi.org/project/email-profile/">PyPI</a>
  &nbsp;•&nbsp;
  <a aria-label="Source Code" href="https://github.com/linux-profile/email-profile">Source Code</a>
</div>

![GitHub Org's stars](https://img.shields.io/github/stars/linux-profile?label=LinuxProfile&style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/linux-profile/email-profile?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/email-profile?style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/email-profile?style=flat-square)
![PyPI - Downloads](https://img.shields.io/pypi/dm/email-profile?style=flat-square)

A Python library for email management. Connect to any IMAP/SMTP server, read and send emails, sync your mailbox to a local database, and restore backups — all with a single, unified API.

{* ./docs_src/quickstart.py *}

Start with the basics [here](nav/tutorial/install.md).

## Features

| Feature | Description |
|---|---|
| **Auto-discovery** | Detects IMAP/SMTP servers from email domain (50+ providers) |
| **Unified API** | IMAP + SMTP in a single `Email` class |
| **Query Builder** | Composable search with `Q` (AND, OR, NOT) and validated `Query` kwargs |
| **Sync** | Incremental backup from server to SQLite with progress bars |
| **Restore** | Upload emails back to server with duplicate detection |
| **Parallel** | Multi-threaded sync and restore with configurable workers |
| **Progress** | Rich progress bars with per-mailbox status |
| **Retry** | Exponential backoff on transient failures |
| **Send** | Send, reply, forward with HTML and attachments |
| **Storage** | Pluggable storage backend (SQLite default) |
| **Flags** | Read/unread, flag, delete, move, copy operations |
| **Context Manager** | `with Email(...) as app:` for automatic cleanup |

## Getting Help

We use GitHub issues for tracking bugs and feature requests.

- 🐛 [Bug Report](https://github.com/linux-profile/email-profile/issues/new/choose)
- 📕 [Documentation](https://github.com/linux-profile/email-profile/issues/new/choose)
- 🚀 [Feature Request](https://github.com/linux-profile/email-profile/issues/new/choose)
- 💬 [General Question](https://github.com/linux-profile/email-profile/issues/new/choose)

## License

This project is licensed under the terms of the MIT license.
