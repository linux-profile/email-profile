"""Access email details."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        for msg in app.inbox.where().messages(chunk_size=5):
            print(f"UID: {msg.uid}")
            print(f"Message-ID: {msg.message_id}")
            print(f"Date: {msg.date}")
            print(f"From: {msg.from_}")
            print(f"To: {msg.to_}")
            print(f"CC: {msg.cc}")
            print(f"Subject: {msg.subject}")
            print(f"Body (text): {msg.body_text_plain[:100]}")
            print(f"Body (html): {msg.body_text_html[:100]}")
            print(f"Content-Type: {msg.content_type}")
            print(f"In-Reply-To: {msg.in_reply_to}")
            print(f"References: {msg.references}")
            print(f"List-ID: {msg.list_id}")
            print(f"Attachments: {len(msg.attachments)}")

            for att in msg.attachments:
                print(
                    f"  {att.file_name} ({att.content_type}, {len(att.content)} bytes)"
                )

            print(f"Headers: {list(msg.headers.keys())}")
            print("---")
            break


if __name__ == "__main__":
    main()
