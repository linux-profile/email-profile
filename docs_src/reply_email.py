"""Reply to a message — preserves `In-Reply-To` and `References`."""

from email_profile import Email


def main() -> None:
    with Email(user="you@yourdomain.com", password="your-password") as app:
        original = next(app.inbox.where(subject="invoice").messages(), None)
        if original is None:
            print("Nothing to reply to.")
            return

        app.reply(
            original,
            body="Thanks — processing now.",
            reply_all=False,
        )
        print(f"Replied to: {original.subject}")


if __name__ == "__main__":
    main()
