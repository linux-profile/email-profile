"""Compose IMAP searches with Q expressions (& | ~)."""

from datetime import date, timedelta

from email_profile import Email, Q


def main() -> None:
    expr = (
        (Q.subject("invoice") | Q.subject("receipt"))
        & Q.since(date.today() - timedelta(days=14))
        & ~Q.from_("noreply@")
    )

    with Email.from_email("you@yourdomain.com", "your-password") as app:
        for msg in app.inbox.where(expr):
            print(msg.from_, msg.subject)


if __name__ == "__main__":
    main()
