"""Inspect non-standard headers via the `headers` bag."""

from collections import Counter

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        seen: Counter[str] = Counter()
        sample = 0

        for msg in app.recent(days=90).messages():
            seen.update(msg.headers.keys())
            sample += 1

        print(
            f"Sampled {sample} messages, found {len(seen)} unique extra headers.\n"
        )
        print("Top 20:")
        for name, count in seen.most_common(20):
            print(f"  {count:>4}x  {name}")


if __name__ == "__main__":
    main()
