# email-profile

![GitHub Org's stars](https://img.shields.io/github/stars/linux-profile?label=LinuxProfile&style=flat-square)

---

- **Documentation**: [https://linux-profile.github.io/email-profile](https://github.com/FernandoCelmer/email-profile)
- **Source Code**: [https://github.com/FernandoCelmer/email-profile](https://github.com/FernandoCelmer/email-profile)

---

## Features

- [x] Query API Structure
    - [x] Mailbox
    - [x] Since
    - [x] Before
    - [x] Subject
    - [x] From Who
    - [ ] Body
    - [ ] Unseen
- [x] Data table structure
- [x] Get emails
- [ ] Create email
- [ ] Answer email
- [ ] Get folders
- [ ] Get contacts
- [x] Download Attachments
- [x] Response JSON
- [x] Dump File JSON
- [x] Response HTML
- [x] Dump File HTML
- [x] Response Attachment File
- [ ] Dump Attachment File
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

    # Dump File JSON
    json = content.json()

    # Response JSON
    print(json)

    # Dump File HMTL
    html = content.html()

    # Response HTML
    print(html)
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
