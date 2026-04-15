"""Migrate a full account from one IMAP server to another via Storage."""

from email_profile import Email, Storage


def main() -> None:
    storage = Storage("./migration.db")

    with Email.from_email("old-account@gmail.com", "app-password") as src:
        for name in src.mailboxes():
            print(f"Backing up {name}...")
            storage.save_many(src.mailbox(name).where().iter_messages())

    with Email.from_email("new-account@yourdomain.com", "password") as dst:
        n = dst.restore(storage)
        print(f"Restored {n} messages to the new account")

    storage.dispose()


if __name__ == "__main__":
    main()
