"""IMAP server discovery for arbitrary email addresses.

Resolution strategy, in order:

1. Hard-coded map of well-known providers (Gmail, Outlook, iCloud, Yahoo,
   Hostinger, Zoho, etc.).
2. RFC 6186 SRV record lookup — ``_imaps._tcp.<domain>``.
3. MX record lookup — infer the IMAP host from the mail exchanger
   (e.g. ``mx1.hostinger.com`` → ``imap.hostinger.com``).
4. Convention fallback — ``imap.<domain>`` on port 993.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

try:
    import dns.resolver
    from dns.exception import DNSException

    _HAS_DNS = True
except ImportError:
    _HAS_DNS = False


class ProviderResolutionError(RuntimeError):
    """Raised when no IMAP host can be discovered for an address."""


@dataclass(frozen=True)
class IMAPHost:
    host: str
    port: int = 993
    ssl: bool = True


KNOWN_PROVIDERS: dict[str, IMAPHost] = {
    "gmail.com": IMAPHost("imap.gmail.com"),
    "googlemail.com": IMAPHost("imap.gmail.com"),
    "outlook.com": IMAPHost("outlook.office365.com"),
    "hotmail.com": IMAPHost("outlook.office365.com"),
    "live.com": IMAPHost("outlook.office365.com"),
    "msn.com": IMAPHost("outlook.office365.com"),
    "office365.com": IMAPHost("outlook.office365.com"),
    "icloud.com": IMAPHost("imap.mail.me.com"),
    "me.com": IMAPHost("imap.mail.me.com"),
    "mac.com": IMAPHost("imap.mail.me.com"),
    "yahoo.com": IMAPHost("imap.mail.yahoo.com"),
    "ymail.com": IMAPHost("imap.mail.yahoo.com"),
    "zoho.com": IMAPHost("imap.zoho.com"),
    "hostinger.com": IMAPHost("imap.hostinger.com"),
    "fastmail.com": IMAPHost("imap.fastmail.com"),
    "protonmail.com": IMAPHost("127.0.0.1", port=1143, ssl=False),
    "aol.com": IMAPHost("imap.aol.com"),
}


MX_HINTS: list[tuple[str, IMAPHost]] = [
    ("hostinger", IMAPHost("imap.hostinger.com")),
    ("google.com", IMAPHost("imap.gmail.com")),
    ("googlemail", IMAPHost("imap.gmail.com")),
    ("outlook.com", IMAPHost("outlook.office365.com")),
    ("office365", IMAPHost("outlook.office365.com")),
    ("protection.outlook.com", IMAPHost("outlook.office365.com")),
    ("zoho", IMAPHost("imap.zoho.com")),
    ("yahoodns", IMAPHost("imap.mail.yahoo.com")),
    ("yandex", IMAPHost("imap.yandex.com")),
    ("mail.ru", IMAPHost("imap.mail.ru")),
    ("locaweb", IMAPHost("imap.locaweb.com.br")),
    ("kinghost", IMAPHost("imap.kinghost.net")),
    ("uol.com", IMAPHost("imap.uol.com.br")),
    ("fastmail", IMAPHost("imap.fastmail.com")),
]


def _split_email(address: str) -> tuple[str, str]:
    if "@" not in address:
        raise ValueError(f"Not a valid email address: {address!r}")
    local, _, domain = address.rpartition("@")
    if not local or not domain:
        raise ValueError(f"Not a valid email address: {address!r}")
    return local, domain.lower()


def _lookup_srv(domain: str) -> Optional[IMAPHost]:
    if not _HAS_DNS:
        return None
    try:
        answers = dns.resolver.resolve(
            f"_imaps._tcp.{domain}", "SRV", lifetime=3.0
        )
    except DNSException:
        return None
    for rdata in sorted(answers, key=lambda r: (r.priority, -r.weight)):
        host = str(rdata.target).rstrip(".")
        if host and host != ".":
            return IMAPHost(host=host, port=int(rdata.port), ssl=True)
    return None


def _lookup_mx(domain: str) -> Optional[IMAPHost]:
    if not _HAS_DNS:
        return None
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=3.0)
    except DNSException:
        return None
    for rdata in sorted(answers, key=lambda r: r.preference):
        host = str(rdata.exchange).rstrip(".").lower()
        for hint, imap in MX_HINTS:
            if hint in host:
                return imap
    return None


def resolve_imap_host(address: str) -> IMAPHost:
    """Discover the IMAP host for an email address.

    Tries known providers, then DNS SRV, then DNS MX (with hint matching),
    then falls back to ``imap.<domain>:993``. Raises
    :class:`ProviderResolutionError` only on malformed input — the convention
    fallback always returns *something*.
    """
    _, domain = _split_email(address)

    if domain in KNOWN_PROVIDERS:
        return KNOWN_PROVIDERS[domain]

    srv = _lookup_srv(domain)
    if srv is not None:
        return srv

    mx = _lookup_mx(domain)
    if mx is not None:
        return mx

    return IMAPHost(host=f"imap.{domain}")
