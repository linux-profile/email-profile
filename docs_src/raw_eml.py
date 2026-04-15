"""Access the full raw RFC822 source of any message via msg.file."""

from email import message_from_string

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        msg = app.inbox.where().first()
        if msg is None:
            print("Empty inbox.")
            return

        raw = msg.file
        print(f"Raw size: {len(raw)} chars")
        print("---")
        print(raw[:500])
        print("...")

        parsed = message_from_string(raw)
        print(f"\nReceived chain has {len(parsed.get_all('Received', []))} hops.")


if __name__ == "__main__":
    main()
