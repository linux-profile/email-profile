# Advanced Usage

For power users who need access to lower-level components. Everything below is importable from `email_profile.advanced`.

```python
from email_profile.advanced import ImapClient, SmtpClient, MailBox, Where
```

## Direct IMAP Client

Use `ImapClient` directly when you need full control over the IMAP session.

```python
from email_profile.advanced import ImapClient

client = ImapClient(
    server="imap.gmail.com",
    user="user@gmail.com",
    password="app_password",
)
client.connect()

for name, mailbox in client.mailboxes.items():
    count = mailbox.where().count()
    print(f"{name}: {count} emails")

client.close()
```

## Direct SMTP Client

Use `SmtpClient` for batch sending with a single connection.

```python
from email_profile.advanced import SmtpClient
from email_profile.clients.smtp.client import _build_message
from email_profile.core.types import SMTPHost

host = SMTPHost("smtp.gmail.com", port=465, ssl=True)

with SmtpClient(host, user="user@gmail.com", password="app_password") as smtp:
    for recipient in ["alice@x.com", "bob@x.com", "carol@x.com"]:
        msg = _build_message(
            sender="user@gmail.com",
            to=recipient,
            subject="Newsletter",
            body="Hello!",
        )
        smtp.send(msg)
```

## Custom Storage Backend

Implement `StorageABC` to use your own persistence layer (PostgreSQL, Redis, S3, etc).

```python
from email_profile.advanced import StorageABC
from email_profile.serializers.raw import RawSerializer


class RedisStorage(StorageABC):

    def save(self, raw: RawSerializer) -> bool:
        ...

    def get(self, message_id: str):
        ...

    def ids(self, mailbox=None) -> set[str]:
        ...

    def uids(self, mailbox: str) -> set[str]:
        ...
```

Then use it:

```python
from email_profile import Email

storage = RedisStorage()
with Email.from_env(storage=storage) as app:
    app.sync()
```

## Auto-Discovery Functions

Resolve IMAP/SMTP hosts programmatically.

```python
from email_profile.advanced import resolve_imap_host, resolve_smtp_host

imap = resolve_imap_host("user@company.com")
print(f"IMAP: {imap.host}:{imap.port}")

smtp = resolve_smtp_host("user@company.com")
print(f"SMTP: {smtp.host}:{smtp.port}")
```

## RFC822 Parser

Parse raw email bytes without connecting to any server.

```python
from email_profile.advanced import parse_rfc822

raw = b"From: alice@x.com\r\nSubject: Hello\r\n\r\nHi there!"
parsed = parse_rfc822(raw)

print(parsed.subject)
print(parsed.from_)
print(parsed.body_text_plain)
print(parsed.headers)
```

## Retry Decorator

Use the built-in retry with exponential backoff for your own functions.

```python
from email_profile.advanced import with_retry

@with_retry(attempts=5, base_delay=1.0)
def flaky_operation():
    ...
```

## Where (Lazy Search)

Build searches that only execute when you iterate.

```python
from email_profile.advanced import ImapClient, Where

client = ImapClient("imap.gmail.com", "user", "pw")
client.connect()

inbox = client.mailboxes["INBOX"]
search = inbox.where()  # no IMAP call yet

print(search.count())   # NOW it hits the server
print(search.uids())    # cached, no second call

client.close()
```

## Available Symbols

| Symbol | Description |
|---|---|
| `ImapClient` | Low-level IMAP session |
| `SmtpClient` | Low-level SMTP session |
| `MailBox` | Single mailbox operations |
| `Where` | Lazy IMAP search |
| `StorageABC` | Abstract storage contract |
| `ImapClientABC` | Abstract IMAP contract |
| `SmtpClientABC` | Abstract SMTP contract |
| `SenderABC` | Abstract sender contract |
| `RawModel` | SQLAlchemy ORM model |
| `Credentials` | Connection credentials |
| `EmailFactories` | Credential resolution |
| `IMAPHost` / `SMTPHost` | Server host dataclasses |
| `AppendedUID` | IMAP APPEND result |
| `Attachment` | Email attachment |
| `ParsedBody` | Parsed RFC822 result |
| `parse_rfc822` | RFC822 parser function |
| `resolve_imap_host` | IMAP auto-discovery |
| `resolve_smtp_host` | SMTP auto-discovery |
| `with_retry` | Retry decorator |
| `Retryable` | Retryable exception base |
| `IMAPError` | IMAP error |
| `Status` | IMAP status validator |
| `ProviderResolutionError` | Discovery failure |
