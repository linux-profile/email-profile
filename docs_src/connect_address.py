"""Connect by passing only your email address — host is auto-discovered.

When ``server`` is omitted but ``user`` looks like an email, the IMAP host
is resolved via known providers, DNS SRV, MX, then a final convention
fallback (``imap.<domain>``).
"""

from email_profile import Email


def main() -> None:
    with Email(
        user="contato@suaempresa.com.br", password="your-password"
    ) as app:
        print(f"Auto-discovered. Connected as {app.user}")
        print(f"Inbox: {app.all().count()} messages")


if __name__ == "__main__":
    main()
