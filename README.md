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

## Query instance - Test

```python
from datetime import date

query = app.select(
    mailbox="Inbox"
).where(
    since=date.today(),
    before=date.today(),
    subject="abc",
    from_who="email@abc.com"
)
```

## Query result

```python
print(query.execute())
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
