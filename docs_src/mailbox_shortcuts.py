"""Access common folders without knowing the server-side names.

`app.sent`, `app.spam`, `app.trash`, `app.drafts`, `app.archive` resolve
across providers (Gmail uses `[Gmail]/Sent Mail`, Hostinger uses `Sent`,
some Brazilian providers use `Enviados`, etc.).
"""

from email_profile import Email


def main() -> None:
    with Email.from_email("you@yourdomain.com", "your-password") as app:
        print(f"Inbox:   {app.inbox.name}")
        print(f"Sent:    {app.sent.name}")
        print(f"Spam:    {app.spam.name}")
        print(f"Trash:   {app.trash.name}")
        print(f"Drafts:  {app.drafts.name}")

        print(f"Sent items: {app.sent.where().count()}")


if __name__ == "__main__":
    main()
