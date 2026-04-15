"""Back up an inbox into a SQLite database."""

from email_profile import Email, Storage


def main() -> None:
    storage = Storage("./backup/mail.db")

    with Email.from_env() as app:
        saved = storage.save_many(app.recent(days=30).messages())
        print(f"Backed up {saved} messages to ./backup/mail.db")

    storage.dispose()


if __name__ == "__main__":
    main()
