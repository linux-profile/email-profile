---
name: draft-reply
description: Write a reply or forward, show it to the person, and send only after they approve.
---

# Replying and forwarding

`reply_message` and `forward_message` are **irreversible and marked destructive**. They
exist only when the server was started with `--allow-send`; when they are missing from the
tool list, write the text and hand it to the person — do not look for another way to send.

## Before writing

`read_message` the original in full (see `read-message`: re-read if `truncated`). Match its
language and tone. For a thread, read the earlier messages too; a reply that ignores what
was already answered wastes everyone's time.

## Before sending

Show the person the complete text, and for a forward, the recipients. Wait for a clear yes.
"Looks good" is a yes; silence is not.

## Sending

- `reply_message` with `mailbox`, `uid` and `body`. The subject, the recipients and the
  thread headers (`In-Reply-To`, `References`) come from the original; only `body` is yours.
  `reply_all=true` also answers every To/Cc address — ask before using it.
- `forward_message` with `mailbox`, `uid`, `to` and an optional `body`. Attachments travel
  with it.

`to` takes one address, a list, or a comma-separated string.

## After

The tool answers with `action` and the recipients. Report that, and nothing more — a copy
lands in the Sent folder on servers that support it.
