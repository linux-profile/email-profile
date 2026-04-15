"""Rank the busiest senders in your inbox."""

from collections import Counter

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        senders: Counter[str] = Counter()

        for msg in app.recent(days=90):
            if msg.from_:
                senders[msg.from_] += 1

        print("Top 20 senders (last 90 days):")
        for sender, count in senders.most_common(20):
            print(f"  {count:>5}  {sender}")


if __name__ == "__main__":
    main()
