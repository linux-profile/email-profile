"""Stream a huge mailbox without loading every message into memory."""

from email_profile import Email


def main() -> None:
    with Email(user="you@yourdomain.com", password="your-password") as app:
        processed = 0
        for _msg in app.archive.where().messages():
            processed += 1
            if processed % 100 == 0:
                print(f"processed {processed} messages...")

        print(f"done — {processed} messages.")


if __name__ == "__main__":
    main()
