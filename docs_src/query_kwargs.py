"""Filter messages with validated keyword arguments."""

from datetime import date, timedelta

from email_profile import Email


def main() -> None:
    with Email(user="you@yourdomain.com", password="your-password") as app:
        results = app.inbox.where(
            subject="invoice",
            from_who="billing@vendor.com",
            since=date.today() - timedelta(days=30),
            unseen=True,
        ).messages()

        for msg in results:
            print(msg.subject, msg.from_, msg.date)


if __name__ == "__main__":
    main()
