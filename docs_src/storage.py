"""Custom storage configuration."""

from email_profile import Email, StorageSQLite


def main() -> None:

    # Default storage (./email.db)
    with Email.from_env() as app:
        print(f"Storage: {app.storage}")

    # Custom storage path
    with Email.from_env(storage=StorageSQLite("./backup.db")) as app:
        app.sync()

    # In-memory storage (for testing)
    with Email.from_env(storage=StorageSQLite("sqlite:///:memory:")) as app:
        app.sync()


if __name__ == "__main__":
    main()
