"""Read emails from INBOX."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        # Count
        print(f"Total: {app.inbox.where().count()}")

        # Read all
        for msg in app.inbox.where().messages():
            print(f"{msg.date} | {msg.from_} | {msg.subject}")

        # Read only headers (faster)
        for msg in app.inbox.where().messages(mode="headers"):
            print(f"{msg.subject}")

        # Read first 10
        for msg in app.inbox.where().messages(chunk_size=10):
            print(f"{msg.uid}: {msg.subject}")
            break


if __name__ == "__main__":
    main()
