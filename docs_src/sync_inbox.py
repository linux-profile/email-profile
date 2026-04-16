"""Sync your inbox with the local SQLite database."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        stats = app.sync()
        print(
            f"Synced INBOX: "
            f"{stats.inserted} new, "
            f"{stats.updated} moved, "
            f"{stats.deleted} deleted"
        )


if __name__ == "__main__":
    main()
