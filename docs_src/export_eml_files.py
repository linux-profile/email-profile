"""Export every persisted message to .eml files (one per message, by mailbox)."""

from email_profile import Storage


def main() -> None:
    storage = Storage("./backup/mail.db")

    n = storage.export_eml("./backup/eml")
    print(f"Wrote {n} .eml files to ./backup/eml/<mailbox>/<uid>.eml")

    storage.dispose()


if __name__ == "__main__":
    main()
