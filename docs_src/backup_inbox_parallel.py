"""Same as backup_inbox.py, but with a producer/consumer pipeline.

While the producer thread streams messages from IMAP, the main thread
batches them into SQLite. Network and disk overlap — typical speedup is
1.5x-2x for big inboxes.

Caveats:
- imaplib is not thread-safe per connection. Only ONE thread (producer)
  ever talks to IMAP. The main thread only writes to SQLite.
- Errors from the producer are re-raised in the main thread so a failure
  doesn't silently hang.

Run with:

    poetry run python docs_src/backup_inbox_parallel.py
"""

import queue
import threading

from email_profile import Email, EmailSerializer, Storage

DB_PATH = "./inbox.db"
CHUNK = 200
QUEUE_LIMIT = 4 * CHUNK  # backpressure: ~800 messages buffered max


_STOP = object()  # sentinel for "no more messages"


def _producer(
    app: Email,
    already: set[str],
    out: "queue.Queue",
    error_box: list,
) -> None:
    """Stream messages from IMAP into the queue. Push the sentinel at the end."""
    try:
        for message in app.all().messages(
            mode="full",
            chunk_size=CHUNK,
            on_progress=lambda d, t: print(f"  fetched {d}/{t}"),
        ):
            if message.uid in already:
                continue
            out.put(message)
    except Exception as error:
        error_box.append(error)
    finally:
        out.put(_STOP)


def main() -> None:
    storage = Storage(DB_PATH)

    with Email.from_env() as app:
        total = app.all().count()
        already = storage.existing_uids("INBOX")
        print(
            f"Backing up {total} messages to {DB_PATH} "
            f"(skipping {len(already)} already persisted)"
        )

        q: queue.Queue = queue.Queue(maxsize=QUEUE_LIMIT)
        error_box: list[Exception] = []

        producer = threading.Thread(
            target=_producer,
            args=(app, already, q, error_box),
            daemon=True,
        )
        producer.start()

        saved = 0
        batch: list[EmailSerializer] = []

        while True:
            item = q.get()
            if item is _STOP:
                break

            batch.append(item)
            if len(batch) >= CHUNK:
                storage.save_many(batch)
                saved += len(batch)
                print(f"  saved {saved}")
                batch = []

        if batch:
            storage.save_many(batch)
            saved += len(batch)

        producer.join()
        if error_box:
            raise error_box[0]

        print(f"\nDone — {saved} new messages persisted in {DB_PATH}")

    storage.dispose()


if __name__ == "__main__":
    main()
