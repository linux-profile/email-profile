"""Stream a huge mailbox without loading every message into memory."""

from email_profile import Email


def main() -> None:
    with Email.from_email("you@yourdomain.com", "your-password") as app:
        processed = 0
        for msg in app.archive.where().iter_messages():
            processed += 1
            if processed % 100 == 0:
                print(f"processed {processed} messages...")

        print(f"done — {processed} messages.")


if __name__ == "__main__":
    main()
