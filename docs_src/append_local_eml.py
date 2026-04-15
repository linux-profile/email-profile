"""Upload a local .eml file to a mailbox via IMAP APPEND."""

from pathlib import Path

from email_profile import Email


def main() -> None:
    eml = Path("./drafts/welcome.eml").read_bytes()

    with Email.from_env() as app:
        app.drafts.append(eml)
        print("Uploaded to Drafts.")


if __name__ == "__main__":
    main()
