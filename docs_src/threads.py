"""Reconstruct conversation threads using In-Reply-To and References."""

from collections import defaultdict

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        threads: dict[str, list[str]] = defaultdict(list)

        for msg in app.recent(days=30).messages():
            root = (msg.references or msg.in_reply_to or msg.id or "").split()[
                0
            ]
            threads[root].append(f"{msg.date}  {msg.subject}")

        biggest = sorted(threads.items(), key=lambda kv: -len(kv[1]))[:5]

        for root, msgs in biggest:
            print(f"\nThread {root[:40]} — {len(msgs)} message(s)")
            for line in msgs:
                print(f"  {line}")


if __name__ == "__main__":
    main()
