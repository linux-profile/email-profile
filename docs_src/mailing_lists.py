"""Group inbox by mailing list (List-Id header) for newsletter cleanup."""

from collections import Counter

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        lists: Counter[str] = Counter()
        unsubscribe: dict[str, str] = {}

        for msg in app.recent(days=180):
            if msg.list_id:
                lists[msg.list_id] += 1
                if msg.list_unsubscribe:
                    unsubscribe[msg.list_id] = msg.list_unsubscribe

        for list_id, count in lists.most_common(15):
            url = unsubscribe.get(list_id, "—")
            print(f"{count:>4}x  {list_id}")
            print(f"        unsubscribe: {url[:80]}")


if __name__ == "__main__":
    main()
