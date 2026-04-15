"""Dump messages to JSON and HTML files for offline use."""

from email_profile import Email


def main() -> None:
    with Email(user="you@yourdomain.com", password="your-password") as app:
        for msg in app.recent(days=1).messages():
            msg.save_json("./out/json")
            msg.save_html("./out/html")
            msg.save_attachments("./out/attachments")


if __name__ == "__main__":
    main()
