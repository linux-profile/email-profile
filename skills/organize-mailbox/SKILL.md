---
name: organize-mailbox
description: Flag, mark, move and delete messages — reversible operations first, deletion last and only when allowed.
---

# Organizing a mailbox

Every tool here takes `mailbox` + `uid` from a fresh `search_messages`.

## Reversible

- `mark_seen` / `mark_unseen` — read state.
- `flag_message` / `unflag_message` — the star.
- `move_message` with a `destination` that is an exact name from `list_mailboxes`. The
  message gets a new uid in the destination; search again to find it there.

These are safe to run on a list the person gave you, one call per message. Report what was
done as a count and a list, not one line per tool call.

## Deleting

`delete_message` only exists when the server was started with `--allow-delete`. It is
**marked destructive**:

- without `expunge`, it flags the message as deleted and the server keeps it until the
  mailbox is expunged — recoverable from the Python API with `undelete`;
- with `expunge=true`, it is gone.

Confirm which message before calling — quote the sender, subject and date — and confirm again
before `expunge=true`. Prefer `move_message` to the Trash folder when the person just wants
it out of sight; that is what a mail client does.

## Archive

"Archive" is a move, not a delete. `list_mailboxes` tells you the folder's real name
(`Archive`, `[Gmail]/All Mail`, …); on Gmail, removing from `INBOX` is the archive.
