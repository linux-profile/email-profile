# RFC822 Parser

Parse raw email bytes without connecting to any server.

```python
from email_profile.advanced import parse_rfc822

raw = b"From: alice@x.com\r\nSubject: Hello\r\n\r\nHi there!"
parsed = parse_rfc822(raw)

print(parsed.subject)
print(parsed.from_)
print(parsed.body_text_plain)
print(parsed.attachments)
print(parsed.headers)
```

Returns a `ParsedBody` with all essential fields, metadata, and a `headers` bag for everything else.
