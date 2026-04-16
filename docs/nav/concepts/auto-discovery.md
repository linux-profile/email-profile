# Auto-Discovery

Email-profile automatically detects the IMAP and SMTP server for your email address using multiple strategies.

## How it Works

1. **Known providers** — checks a built-in map of 50+ providers (Gmail, Outlook, Yahoo, etc.)
2. **DNS SRV records** — queries `_imaps._tcp.<domain>` for RFC 6186 compliant servers
3. **MX record hints** — resolves MX records and matches against known patterns
4. **Convention fallback** — tries `imap.<domain>` as a last resort

## Supported Providers

| | Provider | IMAP Server |
|---|---|---|
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/gmail.svg" width="16"> | Gmail | imap.gmail.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/outlook.svg" width="16"> | Outlook / Hotmail / Live | outlook.office365.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/yahoo.svg" width="16"> | Yahoo | imap.mail.yahoo.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/icloud.svg" width="16"> | iCloud | imap.mail.me.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/zoho.svg" width="16"> | Zoho | imap.zoho.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/protonmail.svg" width="16"> | ProtonMail (Bridge) | 127.0.0.1:1143 |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/aol.svg" width="16"> | AOL | imap.aol.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/yandex.svg" width="16"> | Yandex | imap.yandex.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/mailru.svg" width="16"> | Mail.ru | imap.mail.ru |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/gmx.svg" width="16"> | GMX | imap.gmx.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/hostinger.svg" width="16"> | Hostinger | imap.hostinger.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/godaddy.svg" width="16"> | GoDaddy | imap.secureserver.net |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/namecheap.svg" width="16"> | Namecheap | mail.privateemail.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/gandi.svg" width="16"> | Gandi | mail.gandi.net |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/ovh.svg" width="16"> | OVH | ssl0.ovh.net |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/ionos.svg" width="16"> | Ionos (1&1) | imap.ionos.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | Fastmail | imap.fastmail.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | Rackspace | secure.emailsrvr.com |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | Titan | imap.titan.email |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | Locaweb | imap.locaweb.com.br |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | KingHost | imap.kinghost.net |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | UOL | imap.uol.com.br |
| <img src="https://raw.githubusercontent.com/linux-profile/email-profile/develop/docs/assets/icons/email.svg" width="16"> | Terra | imap.terra.com.br |

Any server with proper DNS SRV or MX records is also detected automatically.

## Usage

{* ./docs_src/auto_discovery.py *}

## Reference

- [Email](../reference/email.md)
- [Types](../reference/types.md)
- [Credentials](../reference/credentials.md)
