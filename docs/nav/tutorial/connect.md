# Connect

## Auto-discovery

The recommended way. Detects the IMAP server from your email domain automatically.

{* ./docs_src/connect.py ln[8:11] *}

Supports 50+ providers including Gmail, Outlook, Yahoo, iCloud, Zoho, Hostinger, and more.

## Explicit Server

Specify the IMAP server directly.

{* ./docs_src/connect.py ln[13:15] *}

## From Environment Variables

Read credentials from `.env` or environment variables.

{* ./docs_src/connect.py ln[17:19] *}

Expected variables:

```env
EMAIL_USERNAME=user@example.com
EMAIL_PASSWORD=app_password
EMAIL_SERVER=imap.example.com  # optional, auto-discovered
```

## Full Code

{* ./docs_src/connect.py *}
