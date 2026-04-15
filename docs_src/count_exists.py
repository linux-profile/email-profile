"""Cheap operations that don't fetch message bodies."""

from email_profile import Email


def main() -> None:
    with Email.from_email("you@yourdomain.com", "your-password") as app:
        if app.unread().exists():
            print(f"You have {app.unread().count()} unread messages.")

        first = app.inbox.where(subject="invoice").first()
        if first is not None:
            print(f"First invoice: {first.date}  {first.subject}")


if __name__ == "__main__":
    main()
