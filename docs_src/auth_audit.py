"""Inspect SPF/DKIM/DMARC results to spot suspicious mail."""

from email_profile import Email


def main() -> None:
    with Email.from_env() as app:
        for msg in app.recent(days=7):
            auth = msg.authentication_results or ""

            spf = "spf=pass" in auth
            dkim = "dkim=pass" in auth
            dmarc = "dmarc=pass" in auth

            flag = "OK " if (spf and dkim and dmarc) else "WARN"
            print(f"{flag}  {msg.from_:<40}  {msg.subject}")


if __name__ == "__main__":
    main()
