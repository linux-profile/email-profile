"""Message operations: mark, delete, move, copy."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        inbox = app.inbox

        # Get first email UID
        uids = inbox.where().uids()
        if not uids:
            print("No emails")
            return

        uid = uids[0]

        # Mark as read
        inbox.mark_seen(uid)

        # Mark as unread
        inbox.mark_unseen(uid)

        # Flag / unflag
        inbox.flag(uid)
        inbox.unflag(uid)

        # Copy to another mailbox
        inbox.copy(uid, "INBOX.Archive")

        # Move to another mailbox
        inbox.move(uid, "INBOX.Archive")

        # Delete (marks as \Deleted)
        inbox.delete(uid)

        # Delete and expunge immediately
        inbox.delete(uid, expunge=True)

        # Expunge all deleted
        inbox.expunge()


if __name__ == "__main__":
    main()
