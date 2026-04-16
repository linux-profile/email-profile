"""Error handling."""

from email_profile import (
    ConnectionFailure,
    Email,
    NotConnected,
)


def main() -> None:

    # Connection failure
    try:
        with Email("bad.server.xyz", "user", "pass") as app:
            pass
    except ConnectionFailure:
        print("Could not connect to server")

    # Not connected
    try:
        app = Email.from_env()
        app.mailbox("INBOX")
    except NotConnected:
        print("Call connect() or use 'with' first")

    # Unknown mailbox
    with Email.from_env() as app:
        try:
            app.mailbox("NONEXISTENT")
        except KeyError:
            print("Mailbox does not exist")


if __name__ == "__main__":
    main()
