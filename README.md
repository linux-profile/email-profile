# email-profile

![GitHub Org's stars](https://img.shields.io/github/stars/linux-profile?label=LinuxProfile&style=flat-square)

---

- **Documentation**: [Link](https://github.com/FernandoCelmer/email-profile)
- **Source Code**: [Link](https://github.com/FernandoCelmer/email-profile)

---

## Check list

- [x] Query API Structure
- [x] Data table structure
- [ ] SQLlite Backup
- [ ] CLI Email
- [ ] Documentation

## How to install?

```python
pip install email-profile
```

## Config

```python
from email_profile import Email

def main():
    app = Email(
        server="EMAIL-SERVER"
        user="EMAIL_USERNAME",
        password="EMAIL_PASSWORD"
    )
```

## Query instance

```python
from datetime import datetime, date

query = app.select(mailbox="Inbox").where(
    since=datetime(1996, 5, 31),
    before=date.today(),
    subject='abc'
)
```

## Query count

```python
print(query.count())
```


## List IDs

```python
ids = query.list_id()
print(ids)
```

## List Data

```python
data = query.list_data()

for content in data:
    # Email data model
    print(content.email.subject)

    # Attachments data model
    print(content.attachments)

    # Dump Json
    print(content.json())
```

## Commit Style

- ⚙️ FEATURE
- 📝 PEP8
- 📌 ISSUE
- 🪲 BUG
- 📘 DOCS
- 📦 PyPI
- ❤️️ TEST
- ⬆️ CI/CD
- ⚠️ SECURITY

## License

This project is licensed under the terms of the MIT license.
