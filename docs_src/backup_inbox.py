"""Back up your entire inbox into a local SQLite database."""

from email_profile import Email, StorageSQLite


def main() -> None:
    storage = StorageSQLite("./inbox.db")

    with Email.from_env() as app:
        already = storage.existing_uids("INBOX")
        total = app.all().count()

        print(
            f"Backing up {total} messages (skipping {len(already)} already saved)"
        )

        saved = 0

        for msg in app.all().messages(
            on_progress=lambda d, t: print(f"  fetched {d}/{t}")
        ):
            if msg.uid in already:
                continue

            storage.save(msg)
            saved += 1

        print(f"Done — {saved} new messages saved to ./inbox.db")

    storage.dispose()


if __name__ == "__main__":
    main()
