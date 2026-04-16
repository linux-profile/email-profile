"""The shortest possible connection — Email() with no arguments.

Reads EMAIL_USERNAME and EMAIL_PASSWORD from the environment (a `.env`
in the current directory is loaded automatically). EMAIL_SERVER is
optional — when missing, the host is auto-discovered.
"""

from email_profile import Email


def main() -> None:
    with Email() as app:
        print(f"Connected as {app.user}")
        print(f"Unread: {app.unread().count()}")


if __name__ == "__main__":
    main()
