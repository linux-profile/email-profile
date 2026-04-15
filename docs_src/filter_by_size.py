"""Find big or small messages without downloading them."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        huge = app.inbox.where(larger=10 * 1024 * 1024).count()
        tiny = app.inbox.where(smaller=2048).count()

        print(f"Larger than 10 MB : {huge}")
        print(f"Smaller than 2 KB : {tiny}")

        for msg in app.inbox.where(larger=5 * 1024 * 1024).messages():
            print(
                f"  {msg.subject[:50] if msg.subject else '?'}  ({msg.from_})"
            )


if __name__ == "__main__":
    main()
