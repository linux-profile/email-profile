"""Search the Sent folder, not the inbox."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        for msg in app.sent.where(subject="proposal").messages():
            print(msg.date, msg.to_, msg.subject)


if __name__ == "__main__":
    main()
