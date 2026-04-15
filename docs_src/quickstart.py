"""Read your inbox in 4 lines.

Auto-discovers the IMAP host from your email domain (works with Gmail,
Outlook, iCloud, Hostinger, custom domains, ...).
"""

from email_profile import Email


def main() -> None:
    with Email.from_email("you@yourdomain.com", "your-password") as app:
        for msg in app.unread():
            print(f"{msg.date}  {msg.from_:<40}  {msg.subject}")


if __name__ == "__main__":
    main()
