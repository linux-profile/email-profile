"""Skip auto-discovery — connect to a specific server explicitly."""

from email_profile import Email


def main() -> None:
    app = Email(
        server="imap.example.com",
        user="you@example.com",
        password="your-password",
        port=993,
        ssl=True,
    )

    with app:
        print(app.mailboxes())


if __name__ == "__main__":
    main()
