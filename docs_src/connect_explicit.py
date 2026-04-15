"""Connect with the full explicit form.

Use this when you know the IMAP host or want to override the port/SSL.
"""

from email_profile import Email


def main() -> None:
    with Email(
        server="imap.gmail.com",
        user="you@gmail.com",
        password="your-app-password",
        port=993,
        ssl=True,
    ) as app:
        print(f"Connected. Mailboxes: {app.mailboxes()}")


if __name__ == "__main__":
    main()
