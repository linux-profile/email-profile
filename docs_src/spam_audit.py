"""See who's filling your spam folder."""

from collections import Counter

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        senders: Counter[str] = Counter()

        for msg in app.spam.where().messages():
            if msg.from_:
                senders[msg.from_] += 1

        print(f"Top 10 spammers (out of {sum(senders.values())} messages):")
        for sender, count in senders.most_common(10):
            print(f"  {count:>4}x  {sender}")


if __name__ == "__main__":
    main()
