"""Use IMAP flags to filter messages."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        print(f"Unread     : {app.inbox.where(seen=False).count()}")
        print(f"Read       : {app.inbox.where(seen=True).count()}")
        print(f"Answered   : {app.inbox.where(answered=True).count()}")
        print(f"Flagged    : {app.inbox.where(flagged=True).count()}")
        print(f"Drafts     : {app.inbox.where(draft=True).count()}")


if __name__ == "__main__":
    main()
