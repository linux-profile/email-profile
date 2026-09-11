---
name: find-message
description: Locate one message from a description, narrowing by sender, subject, text or period.
---

# Finding a message

## Pick the most specific filter first

`search_messages` combines every filter with AND:

- `sender` when a person or domain is named — it matches the From header.
- `subject` when words from the title are given.
- `text` when only the content is described; it searches headers and body and is the
  slowest and the noisiest.
- `since` / `before` (ISO dates, `since` inclusive, `before` exclusive) when a period is
  mentioned. "Last week" is a `since`, not a guess.
- `flagged` / `unseen` when the person says "starred" or "unread".

Start narrow. If nothing comes back, drop the least certain filter and search again, and say
which one you dropped.

## Several matches

List them — date, sender, subject — and let the person choose. Do not open the newest one and
assume; the same subject repeats across a thread.

## What to keep

Every other tool takes the pair `mailbox` + `uid`. A uid is only unique inside its mailbox,
and a moved message gets a new one, so keep the pair from the row the person picked and
search again after any `move_message`.

## Other mailboxes

The default is `INBOX`. "Sent", "Archive", "Trash" have server-side names that differ by
provider — call `list_mailboxes` and use the exact string.
