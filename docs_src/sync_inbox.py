"""Sync your inbox with the local SQLite database."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        stats = app.sync("INBOX")
        print(
            f"Synced: "
            f"{stats.inserted} new, "
            f"{stats.skipped} skipped, "
            f"{len(stats.errors)} errors"
        )


if __name__ == "__main__":
    main()
