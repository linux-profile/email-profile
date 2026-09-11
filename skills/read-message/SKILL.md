---
name: read-message
description: Read one message in full, handle its attachments, and know when the body was cut.
---

# Reading a message

`read_message` with `mailbox` and `uid` from a search. It answers with the headers, the body
and attachment metadata.

## The body may be truncated

Bodies are capped (4000 characters by default) so a newsletter does not flood the context.
When `truncated` is `true` the text ends with a `[truncated N chars]` marker — **read again
with a larger `max_chars`** (or `0` for no cap) before summarizing, quoting or replying.
Never finish a sentence the marker cut.

The body is the plain-text part when the message has one, otherwise the HTML part as-is.

## Attachments

`read_message` lists them — name, content type, size — and never returns bytes.
`list_attachments` does the same on its own. To get a file onto disk, `save_attachment`
with the exact `file_name` from the list and a `directory`; it returns the written path.
Do not invent a name: a mismatch is an error, not a fuzzy match.

## Threads

`in_reply_to` and `references` link a message to the ones before it. To read the
conversation, `search_messages` with the same `subject` and read the rows oldest to newest.
