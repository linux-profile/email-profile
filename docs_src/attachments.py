"""Save attachments from matching messages."""

from email_profile import Email


def main() -> None:
    with Email.from_email("you@yourdomain.com", "your-password") as app:
        for msg in app.inbox.where(subject="report"):
            if not msg.attachments:
                continue

            print(f"{msg.subject} — {len(msg.attachments)} file(s)")
            for att in msg.attachments:
                out = att.save(f"./attachments/{msg.id}")
                print(f"  saved: {out}")


if __name__ == "__main__":
    main()
