"""Cheap operations that don't fetch message bodies."""

from email_profile import Email


def main() -> None:
    with Email(user="you@yourdomain.com", password="your-password") as app:
        if app.unread().exists():
            print(f"You have {app.unread().count()} unread messages.")

        first = next(app.inbox.where(subject="invoice").messages(), None)
        if first is not None:
            print(f"First invoice: {first.date}  {first.subject}")


if __name__ == "__main__":
    main()
