"""Mailbox and folder operations."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        # List all mailboxes
        for name in app.mailboxes():
            print(f"  {name}")

        # Access by name
        box = app.mailbox("INBOX")
        print(f"INBOX has {box.where().count()} emails")

        # Shortcuts
        print(f"Inbox: {app.inbox.name}")
        print(f"Sent: {app.sent.name}")
        print(f"Trash: {app.trash.name}")
        print(f"Drafts: {app.drafts.name}")
        print(f"Spam: {app.spam.name}")

        # Create a new mailbox
        # app.mailbox("INBOX.Archive").create()

        # Rename a mailbox
        # app.mailbox("INBOX.Old").rename_to("INBOX.Archive")

        # Delete a mailbox
        # app.mailbox("INBOX.Temp").delete_mailbox()


if __name__ == "__main__":
    main()
