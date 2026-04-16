"""Connect to an email server."""

from email_profile import Email


def main() -> None:

    # Auto-discovery (recommended)
    with Email("user@gmail.com", "app_password") as app:
        print(f"Connected to {app.server}")
        print(f"Mailboxes: {app.mailboxes()}")

    # Explicit server
    with Email("imap.gmail.com", "user@gmail.com", "app_password") as app:
        print(f"Connected to {app.server}")

    # From environment variables (.env)
    with Email.from_env() as app:
        print(f"Connected as {app.user}")


if __name__ == "__main__":
    main()
