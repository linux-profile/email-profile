"""Auto-discovery connects with just email and password."""

from email_profile import Email


def main() -> None:

    # Gmail
    with Email("user@gmail.com", "app_password") as app:
        print(f"Gmail: {app.server}")

    # Outlook
    with Email("user@outlook.com", "app_password") as app:
        print(f"Outlook: {app.server}")

    # Any provider — auto-discovers IMAP host
    with Email("user@company.com", "password") as app:
        print(f"Discovered: {app.server}")


if __name__ == "__main__":
    main()
