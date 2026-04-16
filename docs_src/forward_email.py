"""Forward a message to another recipient."""

from email_profile import Email


def main() -> None:
    with Email(user="you@yourdomain.com", password="your-password") as app:
        msg = next(app.recent(days=1).messages(), None)
        if msg is None:
            print("Nothing recent to forward.")
            return

        app.forward(
            msg,
            to="colleague@example.com",
            body="FYI — heads up on this one.",
        )
        print(f"Forwarded: {msg.subject}")


if __name__ == "__main__":
    main()
