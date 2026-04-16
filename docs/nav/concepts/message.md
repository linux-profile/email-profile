# Message

When you read an email, email-profile returns a `Message` object. It contains all the parsed fields from the RFC822 source plus the raw content.

## Fields

### Essential

| Field | Type | Description |
|---|---|---|
| `message_id` | `str` | Message-ID header (or sha256 hash fallback) |
| `uid` | `str` | IMAP UID |
| `date` | `datetime` | Date the email was sent |
| `mailbox` | `str` | Mailbox name (e.g. `INBOX`) |
| `from_` | `str` | Sender email address |
| `to_` | `str` | Recipient email address |
| `subject` | `str` | Subject line |
| `file` | `str` | Complete RFC822 raw content |
| `body_text_plain` | `str` | Plain text body |
| `body_text_html` | `str` | HTML body |

### Metadata

| Field | Type | Description |
|---|---|---|
| `cc` | `str` | CC recipients |
| `bcc` | `str` | BCC recipients |
| `reply_to` | `str` | Reply-To address |
| `content_type` | `str` | MIME content type |
| `in_reply_to` | `str` | In-Reply-To header (threading) |
| `references` | `str` | References header (threading) |
| `list_id` | `str` | Mailing list ID |
| `list_unsubscribe` | `str` | Unsubscribe link |
| `attachments` | `list[Attachment]` | File attachments |

### Headers Bag

Any header not listed above is available in `msg.headers`:

```python
msg.headers["DKIM-Signature"]
msg.headers["X-Mailer"]
msg.headers["Importance"]
```

Repeated headers are collapsed into a list:

```python
msg.headers["Received"]  # ["from mx1...", "from mx2..."]
```

## Usage

```python
from email_profile import Email

with Email.from_env() as app:
    msg = app.inbox.where().first()

    print(msg.subject)
    print(msg.from_)
    print(msg.date)
    print(msg.body_text_plain[:200])

    for att in msg.attachments:
        att.save("./downloads")
```

## Creating from Raw Bytes

```python
from email_profile import Message

msg = Message.from_raw(
    uid="1",
    mailbox="INBOX",
    raw=b"From: alice@x.com\r\nSubject: Hello\r\n\r\nHi!",
)
```
