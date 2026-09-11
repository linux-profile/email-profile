---
name: send-email
description: Compose and send a new message, after the person has seen exactly what will go out.
---

# Sending a new message

`send_email` is **irreversible and marked destructive**. It is only registered when the
server runs with `--allow-send`; if it is absent, draft the text and give it to the person.

## Compose

Ask for what is missing rather than inventing it: the recipient, the subject, what to say.
Write `body` as plain text. Pass `html` as well only when the person wants formatting; it is
an alternative rendering, not a replacement, so both should say the same thing.

`to`, `cc` and `bcc` each take one address, a list, or a comma-separated string.
`reply_to` sets where answers go when that is not the sending account.

## Confirm

Show the person, verbatim:

- every recipient, by field;
- the subject;
- the full body.

Send only after an explicit yes. There is no draft step on the server and no undo.

## Attachments

`send_email` does not attach files. When the person needs one, say so plainly and suggest
`forward_message` for something already in the mailbox, or the Python API
(`Email.send(attachments=[...])`) for a local file.
