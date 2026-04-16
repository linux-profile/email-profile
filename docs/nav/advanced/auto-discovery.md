# Auto-Discovery Functions

Resolve IMAP/SMTP hosts programmatically without connecting.

```python
from email_profile.advanced import resolve_imap_host, resolve_smtp_host

imap = resolve_imap_host("user@company.com")
print(f"IMAP: {imap.host}:{imap.port}")

smtp = resolve_smtp_host("user@company.com")
print(f"SMTP: {smtp.host}:{smtp.port}")
```

The resolution follows this order:

1. Known providers map (50+)
2. DNS SRV records (`_imaps._tcp.<domain>`)
3. MX record hints
4. Convention fallback (`imap.<domain>`)

## Reference

- [Types](../reference/types.md)
- [Credentials](../reference/credentials.md)
