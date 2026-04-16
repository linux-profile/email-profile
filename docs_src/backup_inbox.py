"""Back up your entire inbox into a local SQLite database."""

from email_profile import Email


def main() -> None:

    with Email.from_env() as app:
        result = app.sync(mailbox="INBOX")
        print(f"Done — {result.inserted} new, {result.skipped} skipped")


if __name__ == "__main__":
    main()
