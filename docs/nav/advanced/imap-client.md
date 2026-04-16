# Direct IMAP Client

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

## Reference

- [ImapClient](../reference/imap-client.md)
- [MailBox](../reference/mailbox.md)
- [Where](../reference/where.md)
