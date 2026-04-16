"""Custom storage configuration.

Storage is lazily initialized — the database file is only created
when sync() or restore() is first called, not on Email() construction.
"""

from email_profile import Email, StorageSQLite


def main() -> None:
    # Default storage (./email.db, created on first sync/restore)
    with Email.from_env() as app:
        app.sync()  # email.db is created here, not before

    # Custom storage path
    storage = StorageSQLite("./backup.db")
    with Email.from_env() as app:
        app.storage = storage
        app.sync()

    # In-memory storage (for testing)
    storage = StorageSQLite("sqlite:///:memory:")
    with Email.from_env() as app:
        app.storage = storage
        app.sync()


if __name__ == "__main__":
    main()
