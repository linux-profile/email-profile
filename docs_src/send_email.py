"""Send an email via SMTP.

The SMTP host is auto-discovered from the user's domain (same way as IMAP).
By default the message is also appended to the Sent folder so it shows up
in the account history on providers that don't auto-save outgoing mail
(Hostinger, cPanel, etc.).
"""

from email_profile import Email


def main() -> None:
    with Email(user="you@yourdomain.com", password="your-password") as app:
        app.send(
            to="bob@example.com",
            subject="Hello from email-profile",
            body="This was sent via SMTP auto-discovery.",
            html="<p>This was sent via <b>SMTP</b> auto-discovery.</p>",
            attachments=["./report.pdf"],
            cc=["alice@example.com"],
        )
        print("Sent.")


if __name__ == "__main__":
    main()
