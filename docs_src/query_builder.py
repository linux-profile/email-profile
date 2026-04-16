"""Search emails with Q builder and Query."""

from datetime import date

from email_profile import Email, Q, Query


def main() -> None:
    with Email.from_env() as app:
        # Shortcuts
        print(f"Unread: {app.unread().count()}")
        print(f"Recent 7 days: {app.recent(days=7).count()}")
        print(f"Search 'invoice': {app.search('invoice').count()}")

        # Q builder (composable)
        q = Q.subject("meeting") & Q.unseen()
        print(f"Unseen meetings: {app.inbox.where(q).count()}")

        # OR
        q = Q.from_("alice@x.com") | Q.from_("bob@x.com")
        print(f"From Alice or Bob: {app.inbox.where(q).count()}")

        # NOT
        q = ~Q.seen()
        print(f"Not seen: {app.inbox.where(q).count()}")

        # Date range
        q = Q.since(date(2025, 1, 1)) & Q.before(date(2025, 12, 31))
        print(f"Year 2025: {app.inbox.where(q).count()}")

        # Size filter
        q = Q.larger(1_000_000)
        print(f"Larger than 1MB: {app.inbox.where(q).count()}")

        # Query (Pydantic, validated)
        query = Query(subject="report", unseen=True, since=date(2025, 1, 1))
        print(f"Query: {app.inbox.where(query).count()}")

        # Check if exists
        if app.inbox.where(Q.unseen()).exists():
            print("You have unread emails!")


if __name__ == "__main__":
    main()
