"""High-level inbox shortcuts: unread, recent, full-text search."""

from email_profile import Email


def main() -> None:
    with Email(user="you@yourdomain.com", password="your-password") as app:
        print(f"Unread: {app.unread().count()}")

        for msg in app.recent(days=3).messages():
            print(f"  recent: {msg.subject}")

        for msg in app.search("invoice").messages():
            print(f"  match : {msg.subject}")


if __name__ == "__main__":
    main()
