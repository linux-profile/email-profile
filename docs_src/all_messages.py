"""Iterate the entire inbox without filters."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        print(f"Total in inbox: {app.all().count()}")

        for msg in app.all():
            print(f"  {msg.uid}  {msg.subject}")


if __name__ == "__main__":
    main()
