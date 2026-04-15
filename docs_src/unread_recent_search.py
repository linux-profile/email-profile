"""High-level inbox shortcuts: unread, recent, full-text search."""

from email_profile import Email


def main() -> None:
    with Email.from_email("you@yourdomain.com", "your-password") as app:
        print(f"Unread: {app.unread().count()}")

        for msg in app.recent(days=3):
            print(f"  recent: {msg.subject}")

        for msg in app.search("invoice"):
            print(f"  match : {msg.subject}")


if __name__ == "__main__":
    main()
