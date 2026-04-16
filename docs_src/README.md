# Examples

Self-contained scripts that show one feature each. Run any of them with:

```bash
python docs_src/quickstart.py
```

Most examples use `Email.from_env()` — set `EMAIL_USERNAME` / `EMAIL_PASSWORD`
in a `.env` file at the repo root.

## Getting started

| File | What it shows |
|------|---------------|
| [quickstart.py](quickstart.py) | Read mail in 4 lines with auto-discovery |
| [connect_zero_args.py](connect_zero_args.py) | `Email()` — pulls everything from `.env` |
| [connect_address.py](connect_address.py) | `Email("u@domain", "pw")` — auto-discovers host |
| [connect_explicit.py](connect_explicit.py) | `Email(server=..., user=..., password=..., port=..., ssl=...)` |
| [provider_factories.py](provider_factories.py) | `Email.gmail`, `outlook`, `icloud`, `hostinger`, ... |
| [from_env.py](from_env.py) | `Email.from_env()` classmethod |
| [manual_login.py](manual_login.py) | Bypass auto-discovery and pass an explicit host |
| [custom_domain_resolver.py](custom_domain_resolver.py) | How auto-discovery picks an IMAP host |

## Browsing folders

| File | What it shows |
|------|---------------|
| [list_mailboxes.py](list_mailboxes.py) | Discover every mailbox and count messages |
| [mailbox_shortcuts.py](mailbox_shortcuts.py) | `app.inbox` / `sent` / `spam` / `trash` / `drafts` |
| [unread_recent_search.py](unread_recent_search.py) | `app.unread()`, `app.recent(days=7)`, `app.search(text)` |
| [all_messages.py](all_messages.py) | Iterate the entire inbox |

## Searching and filtering

| File | What it shows |
|------|---------------|
| [query_kwargs.py](query_kwargs.py) | Filter with validated keyword arguments |
| [query_builder_q.py](query_builder_q.py) | Compose searches with `Q` (`&`, `\|`, `~`) |
| [filter_by_date.py](filter_by_date.py) | `since`, `before`, `on` filters |
| [filter_by_size.py](filter_by_size.py) | `larger` / `smaller` to find heavy or tiny mail |
| [filter_by_flags.py](filter_by_flags.py) | `seen`, `answered`, `flagged`, `draft` |
| [count_exists.py](count_exists.py) | Cheap operations that skip the body fetch |
| [sent_search.py](sent_search.py) | Search the Sent folder, not the inbox |

## Working with messages

| File | What it shows |
|------|---------------|
| [attachments.py](attachments.py) | Save attachments to disk |
| [save_json_html.py](save_json_html.py) | Dump messages as JSON / HTML files |
| [raw_eml.py](raw_eml.py) | Access the raw RFC822 source |
| [headers_bag.py](headers_bag.py) | Inspect non-standard `X-*` headers |
| [threads.py](threads.py) | Reconstruct conversation threads |

## Sending mail (SMTP)

| File | What it shows |
|------|---------------|
| [send_email.py](send_email.py) | `app.send(to=, subject=, body=, ...)` with auto-discovered SMTP |
| [reply_email.py](reply_email.py) | `app.reply(msg, body=...)` preserving threading |
| [forward_email.py](forward_email.py) | `app.forward(msg, to=...)` with quoted body |

## Backup, restore, migration

| File | What it shows |
|------|---------------|
| [persist_storage.py](persist_storage.py) | Persist messages to SQLite via `Storage` |
| [backup_to_storage.py](backup_to_storage.py) | Back up a mailbox into SQLite |
| [export_eml_files.py](export_eml_files.py) | Export persisted messages to `.eml` files |
| [restore_to_server.py](restore_to_server.py) | Restore a backup back into an IMAP server |
| [migrate_provider.py](migrate_provider.py) | Move every message from one account to another |
| [append_local_eml.py](append_local_eml.py) | Upload a single `.eml` file via IMAP APPEND |
| [iterate_large_inbox.py](iterate_large_inbox.py) | Stream a huge mailbox without OOM |

## Audits and analytics

| File | What it shows |
|------|---------------|
| [top_senders.py](top_senders.py) | Rank the busiest senders |
| [spam_audit.py](spam_audit.py) | Who's filling your spam folder |
| [mailing_lists.py](mailing_lists.py) | Group by `List-Id` for newsletter cleanup |
| [auth_audit.py](auth_audit.py) | Inspect SPF/DKIM/DMARC results |
