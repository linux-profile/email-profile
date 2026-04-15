"""Restore a backup back to an IMAP server.

Two flows:

1. From a SQLite backup created with `Storage.save_many`.
2. From a directory of .eml files (e.g. exported by Thunderbird).

Each message is re-uploaded with IMAP APPEND. The original mailbox name is
preserved unless `target=` is given.
"""

from email_profile import Email, Storage


def from_storage() -> None:
    storage = Storage("./backup/mail.db")

    with Email.from_env() as app:
        n = app.restore(storage)
        print(f"Restored {n} messages from ./backup/mail.db")

    storage.dispose()


def from_eml_files() -> None:
    with Email.from_env() as app:
        n = app.restore_eml("./backup/eml")
        print(f"Restored {n} .eml files")


def main() -> None:
    from_storage()
    # from_eml_files()


if __name__ == "__main__":
    main()
