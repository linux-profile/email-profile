"""Sync and restore emails."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        # Sync all mailboxes (compares by Message-ID)
        result = app.sync()
        print(f"Synced: {result.inserted} new, {result.skipped} skipped")

        # Sync one mailbox
        result = app.sync(mailbox="INBOX")
        print(f"INBOX: {result.inserted} new")

        # Force re-download (skip duplicate check)
        result = app.sync(skip_duplicates=False)

        # Restore all mailboxes to server (compares by Message-ID)
        count = app.restore()
        print(f"Restored {count} emails")

        # Restore one mailbox
        count = app.restore(mailbox="INBOX")
        print(f"Restored {count} to INBOX")

        # Force re-upload (skip duplicate check)
        count = app.restore(skip_duplicates=False)

        # Control parallelism
        result = app.sync(max_workers=5)
        count = app.restore(max_workers=5)


if __name__ == "__main__":
    main()
