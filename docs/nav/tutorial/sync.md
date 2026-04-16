# Sync

Sync downloads emails from your IMAP server to a local SQLite database. It's incremental — only new emails are downloaded. Already synced emails are skipped based on their IMAP UID.

## Why Sync?

- **Backup** — keep a local copy of all your emails in case the server goes down
- **Offline access** — read and search emails without an internet connection
- **Migration** — download from one server, restore to another
- **Analysis** — query your emails with SQL directly on the SQLite file

## Sync All Mailboxes

{* ./docs_src/sync_and_restore.py ln[8:10] *}

## Sync One Mailbox

{* ./docs_src/sync_and_restore.py ln[12:14] *}

## Parallel Workers

By default, sync uses 3 threads — one per mailbox. You can increase for faster syncs or decrease if the server limits connections.

```python
result = app.sync(max_workers=5)
```

## Output

Each mailbox shows a progress bar while downloading. When complete, it prints a summary:

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
    .st { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 13px; }
    .sp { fill: #8b949e; }
    .sc { fill: #c9d1d9; }
    .sg { fill: #3fb950; }
    .sy { fill: #58a6ff; }
    .sd { fill: #8b949e; }
  </style>
  <rect width="720" height="420" rx="8" fill="#0d1117"/>
  <circle cx="20" cy="18" r="6" fill="#f85149"/>
  <circle cx="38" cy="18" r="6" fill="#e0a434"/>
  <circle cx="56" cy="18" r="6" fill="#3fb950"/>
  <text x="310" y="22" fill="#8b949e" font-size="12" text-anchor="middle" class="st">email-profile — sync</text>
  <text x="20" y="55" class="st sp">$</text>
  <text x="35" y="55" class="st sc">python docs_src/sync_inbox.py</text>
  <g style="animation: fadebar1 8s infinite">
    <text x="30" y="90" class="st sy">INBOX.Work</text>
    <rect x="200" y="78" width="280" height="14" fill="#30363d" rx="2"/>
    <rect x="200" y="78" height="14" fill="#58a6ff" rx="2" style="animation: bar1 3s ease-out 1.5s both"/>
    <text x="490" y="90" class="st sd">100%</text>
  </g>
  <g style="animation: fade1 8s infinite">
    <text x="30" y="90" class="st sg">✓</text>
    <text x="50" y="90" class="st sc">INBOX.Work — 45 new, 0 updated, 0 skipped</text>
  </g>
  <g style="animation: fadebar2 8s infinite">
    <text x="30" y="115" class="st sy">INBOX.Sent</text>
    <rect x="200" y="103" width="280" height="14" fill="#30363d" rx="2"/>
    <rect x="200" y="103" height="14" fill="#58a6ff" rx="2" style="animation: bar2 3s ease-out 2.5s both"/>
    <text x="490" y="115" class="st sd">100%</text>
  </g>
  <g style="animation: fade2 8s infinite">
    <text x="30" y="115" class="st sg">✓</text>
    <text x="50" y="115" class="st sc">INBOX.Sent — 41 new, 0 updated, 0 skipped</text>
  </g>
  <g style="animation: fadebar3 8s infinite">
    <text x="30" y="140" class="st sy">INBOX</text>
    <rect x="200" y="128" width="280" height="14" fill="#30363d" rx="2"/>
    <rect x="200" y="128" height="14" fill="#58a6ff" rx="2" style="animation: bar3 4s ease-out 3.5s both"/>
    <text x="490" y="140" class="st sd">100%</text>
  </g>
  <g style="animation: fade3 8s infinite">
    <text x="30" y="140" class="st sg">✓</text>
    <text x="50" y="140" class="st sc">INBOX — 23455 new, 0 updated, 0 skipped</text>
  </g>
  <g style="animation: fade3 8s infinite">
    <text x="20" y="180" class="st sc">Synced: 23541 new, 0 skipped, 0 errors</text>
    <text x="20" y="210" class="st sp">$</text>
    <rect x="35" y="199" width="8" height="14" fill="#c9d1d9" style="animation: blink 1s step-end infinite"/>
  </g>
</svg>
</div>

- **new** — emails downloaded and saved for the first time
- **updated** — emails that existed but were re-saved (e.g. UID changed)
- **skipped** — emails already in the database

## SyncResult

The `sync()` method returns a [`SyncResult`](../reference/sync-result.md) with all the counts:

```python
result = app.sync()

print(result.inserted)
print(result.updated)
print(result.skipped)
print(result.errors)
print(result.total_processed)
print(result.has_errors)
```

## Where are emails stored?

By default, in `./email.db` (SQLite). You can change this:

```python
from email_profile import Email, StorageSQLite

with Email.from_env(storage=StorageSQLite("./backup.db")) as app:
    app.sync()
```

## How to see the data?

Open the SQLite file with any tool:

```bash
sqlite3 email.db "SELECT count(*) FROM raw"
sqlite3 email.db "SELECT uid, mailbox, message_id FROM raw LIMIT 10"
sqlite3 email.db "SELECT mailbox, count(*) FROM raw GROUP BY mailbox"
```

Or with Python:

```python
from email_profile import StorageSQLite

storage = StorageSQLite("./email.db")
print(f"Total: {len(storage.ids())}")
print(f"INBOX: {len(storage.uids('INBOX'))}")
```

## Reference

- [`Email`](../reference/email.md)
- [`Sync`](../reference/sync.md)
- [`SyncResult`](../reference/sync-result.md)
- [`StorageSQLite`](../reference/storage.md)
