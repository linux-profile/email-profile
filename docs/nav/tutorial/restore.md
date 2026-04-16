# Restore

Restore uploads emails from your local SQLite database back to an IMAP server. It preserves the original mailbox structure, flags (read/unread), and dates.

## Why Restore?

- **Migration** — move emails between servers (Hostinger to Gmail, Gmail to Outlook, etc.)
- **Disaster recovery** — re-upload emails after a server failure
- **Account merge** — consolidate multiple accounts into one
- **Testing** — populate a test server with real data

## Restore All Mailboxes

Each email is uploaded to its original mailbox. If a mailbox doesn't exist on the target server, it's created automatically.

{* ./docs_src/sync_and_restore.py ln[16:18] *}

## Restore One Mailbox

{* ./docs_src/sync_and_restore.py ln[20:22] *}

## Skip Duplicates

By default, restore checks if an email already exists on the server (by Message-ID) and skips it. Disable this for faster restores when you know the server is empty:

```python
count = app.restore(skip_duplicates=False)
```

## Parallel Workers

Like sync, restore uses threads — one per mailbox:

```python
count = app.restore(max_workers=5)
```

## Output

Each mailbox shows a progress bar while uploading:

<div markdown="block">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420">
  <style>
    @keyframes blink { 0%,100% { opacity: 1 } 50% { opacity: 0 } }
    @keyframes bar1 { 0% { width: 0 } 100% { width: 280px } }
    @keyframes bar2 { 0% { width: 0 } 100% { width: 280px } }
    @keyframes bar3 { 0% { width: 0 } 100% { width: 280px } }
    @keyframes fade1 { 0%,59% { opacity: 0 } 60% { opacity: 1 } }
    @keyframes fade2 { 0%,74% { opacity: 0 } 75% { opacity: 1 } }
    @keyframes fade3 { 0%,89% { opacity: 0 } 90% { opacity: 1 } }
    @keyframes fadebar1 { 0%,19% { opacity: 0 } 20%,59% { opacity: 1 } 60% { opacity: 0 } }
    @keyframes fadebar2 { 0%,34% { opacity: 0 } 35%,74% { opacity: 1 } 75% { opacity: 0 } }
    @keyframes fadebar3 { 0%,49% { opacity: 0 } 50%,89% { opacity: 1 } 90% { opacity: 0 } }
    .rt { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 13px; }
    .rp { fill: #8b949e; }
    .rc { fill: #c9d1d9; }
    .rg { fill: #3fb950; }
    .ry { fill: #58a6ff; }
    .rd { fill: #8b949e; }
  </style>
  <rect width="720" height="420" rx="8" fill="#0d1117"/>
  <circle cx="20" cy="18" r="6" fill="#f85149"/>
  <circle cx="38" cy="18" r="6" fill="#e0a434"/>
  <circle cx="56" cy="18" r="6" fill="#3fb950"/>
  <text x="310" y="22" fill="#8b949e" font-size="12" text-anchor="middle" class="rt">email-profile — restore</text>
  <text x="20" y="55" class="rt rp">$</text>
  <text x="35" y="55" class="rt rc">python docs_src/restore_inbox.py</text>
  <g style="animation: fadebar1 8s infinite">
    <text x="30" y="90" class="rt ry">INBOX.Work</text>
    <rect x="200" y="78" width="280" height="14" fill="#30363d" rx="2"/>
    <rect x="200" y="78" height="14" fill="#58a6ff" rx="2" style="animation: bar1 2s ease-out 1.5s both"/>
    <text x="490" y="90" class="rt rd">100%</text>
  </g>
  <g style="animation: fade1 8s infinite">
    <text x="30" y="90" class="rt rg">✓</text>
    <text x="50" y="90" class="rt rc">INBOX.Work — 45 uploaded, 0 skipped</text>
  </g>
  <g style="animation: fadebar2 8s infinite">
    <text x="30" y="115" class="rt ry">INBOX.Sent</text>
    <rect x="200" y="103" width="280" height="14" fill="#30363d" rx="2"/>
    <rect x="200" y="103" height="14" fill="#58a6ff" rx="2" style="animation: bar2 2s ease-out 2.5s both"/>
    <text x="490" y="115" class="rt rd">100%</text>
  </g>
  <g style="animation: fade2 8s infinite">
    <text x="30" y="115" class="rt rg">✓</text>
    <text x="50" y="115" class="rt rc">INBOX.Sent — 41 uploaded, 0 skipped</text>
  </g>
  <g style="animation: fadebar3 8s infinite">
    <text x="30" y="140" class="rt ry">INBOX</text>
    <rect x="200" y="128" width="280" height="14" fill="#30363d" rx="2"/>
    <rect x="200" y="128" height="14" fill="#58a6ff" rx="2" style="animation: bar3 3s ease-out 3.5s both"/>
    <text x="490" y="140" class="rt rd">100%</text>
  </g>
  <g style="animation: fade3 8s infinite">
    <text x="30" y="140" class="rt rg">✓</text>
    <text x="50" y="140" class="rt rc">INBOX — 23455 uploaded, 0 skipped</text>
  </g>
  <g style="animation: fade3 8s infinite">
    <text x="20" y="180" class="rt rc">Restored 23541 messages</text>
    <text x="20" y="210" class="rt rp">$</text>
    <rect x="35" y="199" width="8" height="14" fill="#c9d1d9" style="animation: blink 1s step-end infinite"/>
  </g>
</svg>
</div>

- **uploaded** — emails sent to the server
- **skipped** — emails already on the server (duplicate detection)

## Restore to a Different Server

Sync from one server, restore to another:

```python
from email_profile import Email, StorageSQLite

storage = StorageSQLite("./backup.db")

# Step 1: sync from source server
with Email("user@old-server.com", "password") as source:
    source.sync()

# Step 2: restore to target server
with Email("user@new-server.com", "password", storage=storage) as target:
    count = target.restore()
    print(f"Migrated {count} emails")
```

## What gets restored?

| Data | Restored? |
|---|---|
| Email content (RFC822) | Yes |
| Mailbox/folder | Yes (created if missing) |
| Flags (read/unread, flagged) | Yes |
| Original date | Yes (from Date header) |
| IMAP UID | No (new UID assigned by server) |

## Reference

- [`Email`](../reference/email.md)
- [`Restore`](../reference/restore.md)
- [`StorageSQLite`](../reference/storage.md)
