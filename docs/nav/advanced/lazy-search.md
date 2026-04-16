# Lazy Search (Where)

The [`Where`](../reference/where.md) object doesn't hit the server until you ask for results. UIDs are cached after the first call.

```python
from email_profile.advanced import ImapClient

client = ImapClient("imap.gmail.com", "user", "pw")
client.connect()

inbox = client.mailboxes["INBOX"]

search = inbox.where()     # no IMAP call yet

search.count()             # NOW it hits the server
search.uids()              # cached, no second call
search.first()             # fetches first email
search.last()              # fetches last email
search.list()              # fetches all emails
search[0]                  # by index
search[0:5]                # by slice

for msg in search:         # iterate
    print(msg.subject)

len(search)                # same as count()
bool(search)               # same as exists()

search.clear_cache()       # force re-fetch on next call

client.close()
```

## Reference

- [Where](../reference/where.md)
- [Query & Q](../reference/query.md)
- [Message](../reference/email-serializer.md)
- [MailBox](../reference/mailbox.md)
