"""Sync every mailbox on the server with local SQLite."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        # Sync all mailboxes (skips emails already stored)
        stats = app.sync()
        print(
            f"Synced all: "
            f"{stats.inserted} new, "
            f"{stats.updated} updated, "
            f"{stats.skipped} skipped"
        )

        # Force re-download everything (no duplicate check)
        stats = app.sync(skip_duplicates=False)


if __name__ == "__main__":
    main()
