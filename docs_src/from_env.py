"""Load credentials from environment variables (or a `.env` file).

Set EMAIL_USERNAME and EMAIL_PASSWORD. EMAIL_SERVER is optional — if
missing, the host is auto-discovered from EMAIL_USERNAME's domain.
A `.env` in the current directory is loaded automatically.
"""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        print(f"Inbox has {app.all().count()} messages")


if __name__ == "__main__":
    main()
