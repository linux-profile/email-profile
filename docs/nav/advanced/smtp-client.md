# Direct SMTP Client

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
