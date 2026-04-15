"""Filter by exact date or date range."""

from datetime import date, timedelta

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        today = app.inbox.where(on=date.today()).count()
        print(f"Today           : {today}")

        last_week = app.inbox.where(
            since=date.today() - timedelta(days=7),
            before=date.today(),
        ).count()
        print(f"Last 7 days     : {last_week}")

        last_month = app.inbox.where(
            since=date.today().replace(day=1) - timedelta(days=30),
            before=date.today().replace(day=1),
        ).count()
        print(f"Previous month  : {last_month}")


if __name__ == "__main__":
    main()
