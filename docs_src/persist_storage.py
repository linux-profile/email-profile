"""Persist messages to a SQLite database with Storage."""

from email_profile import Email, Storage


def main() -> None:
    storage = Storage("./mail.db")

    with Email.from_email("you@yourdomain.com", "your-password") as app:
        saved = storage.save_many(app.recent(days=7).iter_messages())
        print(f"Persisted {saved} messages to ./mail.db")

    storage.dispose()


if __name__ == "__main__":
    main()
