"""Read your unread mail in 4 lines."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        for msg in app.unread().messages():
            print(f"{msg.date}  {msg.from_:<40}  {msg.subject}")


if __name__ == "__main__":
    main()
