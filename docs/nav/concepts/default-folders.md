# Default Folders

When you connect to an email server, email-profile automatically maps the standard folders to properties on the `Email` object.

## How it Works

After login, the IMAP server returns all available mailboxes. Email-profile matches them against known names in multiple languages (English, Portuguese, Spanish) and creates shortcuts:

```python
with Email.from_env() as app:
    app.inbox     # INBOX
    app.sent      # Sent folder
    app.trash     # Trash folder
    app.drafts    # Drafts folder
    app.spam      # Spam/Junk folder
    app.archive   # Archive folder
```

## Name Mapping

Each property tries multiple names until it finds one that exists on the server:

| Property | EN | PT | ES |
|---|---|---|---|
| `app.inbox` | INBOX | INBOX | INBOX |
| `app.sent` | Sent | Enviados, Enviadas | Enviados |
| `app.trash` | Trash | Lixeira | Papelera |
| `app.drafts` | Drafts | Rascunhos | Borradores |
| `app.spam` | Spam, Junk | Lixo Eletrônico | Correo no deseado |
| `app.archive` | Archive | Arquivo | Archivados |

## Custom Mailboxes

For any mailbox that is not a default folder, use `app.mailbox()`:

```python
with Email.from_env() as app:
    work = app.mailbox("INBOX.Work")
    linkedin = app.mailbox("INBOX.Work.Linkedin")
```

## Listing All Mailboxes

```python
with Email.from_env() as app:
    for name in app.mailboxes():
        print(name)
```

## Reference

- [Email](../reference/email.md)
- [MailBox](../reference/mailbox.md)
