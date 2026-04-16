"""Restore emails from a local SQLite backup to an IMAP server."""

from email_profile import Email


def main() -> None:

    with Email.from_env() as app:
        count = app.restore()
        print(f"Restored {count} messages to INBOX")


if __name__ == "__main__":
    main()
