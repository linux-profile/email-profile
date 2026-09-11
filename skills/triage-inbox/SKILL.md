---
name: triage-inbox
description: Report what is new in a mailbox and what needs an answer, without changing anything.
---

# Triaging a mailbox

Read-only. Nothing here marks, moves or replies.

## Start with what is unread

`search_messages` with `unseen=true` and the mailbox the person means (`INBOX` unless they
say otherwise). It returns headers only — sender, subject, date, attachment count — newest
first, `limit` 20 by default and capped at 200. Page with `offset` = `next_offset` until it
is null; **absence from one page is not absence from the mailbox**.

Group the rows by sender. For each, say what it is about and whether it looks like it wants a
reply. The subject is usually enough; open a message with `read_message` only when it is not.

## Do not touch state

Reading with `read_message` does not mark a message as seen — the server fetches without
setting the flag — so triage leaves the mailbox as it found it. Do not call `mark_seen`
during triage unless asked; the unread count is the person's own to-do list.

## Mailbox names

Use `list_mailboxes` when the person names a folder you have not seen: Gmail calls Sent
`[Gmail]/Sent Mail`, and a typo returns an IMAP error rather than an empty page.
