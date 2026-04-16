"""Send emails via SMTP."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        # Simple send
        app.send(
            to="recipient@example.com",
            subject="Hello",
            body="Hi there!",
        )

        # With HTML
        app.send(
            to="recipient@example.com",
            subject="Report",
            body="See attached report.",
            html="<h1>Report</h1><p>See attached.</p>",
        )

        # With attachments
        app.send(
            to=["alice@x.com", "bob@x.com"],
            subject="Files",
            body="Here are the files.",
            attachments=["report.pdf", "data.csv"],
        )

        # With CC/BCC
        app.send(
            to="recipient@example.com",
            subject="Meeting",
            body="Tomorrow at 10am.",
            cc="manager@example.com",
            bcc="hr@example.com",
        )

        # Reply to an email
        msg = list(app.inbox.where().messages(chunk_size=1))[0]
        app.reply(msg, body="Thanks for your email!")

        # Forward an email
        app.forward(msg, to="colleague@example.com", body="FYI")


if __name__ == "__main__":
    main()
