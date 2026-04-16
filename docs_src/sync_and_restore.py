"""Sync and restore emails."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        # Sync all mailboxes
        result = app.sync()
        print(f"Synced: {result.inserted} new, {result.skipped} skipped")

        # Sync one mailbox
        result = app.sync(mailbox="INBOX")
        print(f"INBOX: {result.inserted} new")

        # Restore all mailboxes to server
        count = app.restore()
        print(f"Restored {count} emails")

        # Restore one mailbox
        count = app.restore(mailbox="INBOX")
        print(f"Restored {count} to INBOX")

        # Restore without duplicate check (faster)
        count = app.restore(skip_duplicates=False)

        # Control parallelism
        result = app.sync(max_workers=5)
        count = app.restore(max_workers=5)


if __name__ == "__main__":
    main()
