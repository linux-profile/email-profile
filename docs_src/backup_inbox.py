"""Back up your entire INBOX into a local SQLite database.

Resumable: re-running picks up where the previous run stopped (skips
messages whose Message-ID is already persisted).

Reads credentials from a `.env` file at the project root:

    EMAIL_USERNAME=you@yourdomain.com
    EMAIL_PASSWORD=your-password

Run with:

    poetry run python docs_src/backup_inbox.py
"""

from email_profile import Email, Storage

DB_PATH = "./inbox.db"
CHUNK = 100


def main() -> None:
    storage = Storage(DB_PATH)

    with Email.from_env() as app:
        total = app.all().count()
        already = storage.existing_uids("INBOX")
        print(
            f"Backing up {total} messages to {DB_PATH} "
            f"(skipping {len(already)} already persisted)"
        )

        saved = 0
        batch = []

        for message in app.all().messages(
            mode="full",
            chunk_size=CHUNK,
            on_progress=lambda d, t: print(f"  fetched {d}/{t}"),
        ):
            if message.uid in already:
                continue

            batch.append(message)

            if len(batch) >= CHUNK:
                storage.save_many(batch)
                saved += len(batch)
                batch = []

        if batch:
            storage.save_many(batch)
            saved += len(batch)

        print(f"\nDone — {saved} new messages persisted in {DB_PATH}")

    storage.dispose()


if __name__ == "__main__":
    main()
