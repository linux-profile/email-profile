"""Discover every mailbox on the server and count messages in each."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        for name in app.mailboxes():
            count = app.mailbox(name).where().count()
            print(f"{count:>6}  {name}")


if __name__ == "__main__":
    main()
