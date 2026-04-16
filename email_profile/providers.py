"""IMAP and SMTP server discovery for arbitrary email addresses.

Resolution strategy, in order:

1. Hard-coded map of well-known providers (Gmail, Outlook, iCloud, Yahoo,
   Hostinger, Zoho, etc.).
2. RFC 6186 SRV lookup — ``_imaps._tcp.<d>`` / ``_submission._tcp.<d>``.
3. MX record lookup — infer the host from the mail exchanger
   (e.g. ``mx1.hostinger.com`` → ``imap.hostinger.com``).
4. Convention fallback — ``imap.<domain>`` / ``smtp.<domain>``.
"""

from __future__ import annotations

from typing import Optional

from email_profile.core.types import IMAPHost, SMTPHost

try:
    import dns.resolver
    from dns.exception import DNSException

    _HAS_DNS = True
except ImportError:
    _HAS_DNS = False


class ProviderResolutionError(RuntimeError):
    """Raised when no IMAP host can be discovered for an address."""


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
    "pm.me": IMAPHost("127.0.0.1", port=1143, ssl=False),
    "aol.com": IMAPHost("imap.aol.com"),
    "yandex.com": IMAPHost("imap.yandex.com"),
    "yandex.ru": IMAPHost("imap.yandex.com"),
    "mail.ru": IMAPHost("imap.mail.ru"),
    "gmx.com": IMAPHost("imap.gmx.com"),
    "gmx.net": IMAPHost("imap.gmx.net"),
    "mail.com": IMAPHost("imap.mail.com"),
    "titan.email": IMAPHost("imap.titan.email"),
    "privateemail.com": IMAPHost("mail.privateemail.com"),
    "secureserver.net": IMAPHost("imap.secureserver.net"),
    "gandi.net": IMAPHost("mail.gandi.net"),
    "ovh.net": IMAPHost("ssl0.ovh.net"),
    "ionos.com": IMAPHost("imap.ionos.com"),
    "locaweb.com.br": IMAPHost("imap.locaweb.com.br"),
    "kinghost.net": IMAPHost("imap.kinghost.net"),
    "uol.com.br": IMAPHost("imap.uol.com.br"),
    "bol.com.br": IMAPHost("imap.uol.com.br"),
    "terra.com.br": IMAPHost("imap.terra.com.br"),
    "rackspace.com": IMAPHost("secure.emailsrvr.com"),
}


MX_HINTS: list[tuple[str, IMAPHost]] = [
    ("hostinger", IMAPHost("imap.hostinger.com")),
    ("titan", IMAPHost("imap.titan.email")),
    ("google.com", IMAPHost("imap.gmail.com")),
    ("googlemail", IMAPHost("imap.gmail.com")),
    ("outlook.com", IMAPHost("outlook.office365.com")),
    ("office365", IMAPHost("outlook.office365.com")),
    ("protection.outlook.com", IMAPHost("outlook.office365.com")),
    ("zoho", IMAPHost("imap.zoho.com")),
    ("yahoodns", IMAPHost("imap.mail.yahoo.com")),
    ("yandex", IMAPHost("imap.yandex.com")),
    ("mail.ru", IMAPHost("imap.mail.ru")),
    ("gmx", IMAPHost("imap.gmx.com")),
    ("locaweb", IMAPHost("imap.locaweb.com.br")),
    ("kinghost", IMAPHost("imap.kinghost.net")),
    ("uol.com", IMAPHost("imap.uol.com.br")),
    ("terra.com", IMAPHost("imap.terra.com.br")),
    ("fastmail", IMAPHost("imap.fastmail.com")),
    ("gandi", IMAPHost("mail.gandi.net")),
    ("ovh", IMAPHost("ssl0.ovh.net")),
    ("ionos", IMAPHost("imap.ionos.com")),
    ("secureserver", IMAPHost("imap.secureserver.net")),
    ("emailsrvr", IMAPHost("secure.emailsrvr.com")),
    ("privateemail", IMAPHost("mail.privateemail.com")),
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


KNOWN_SMTP_PROVIDERS: dict[str, SMTPHost] = {
    "gmail.com": SMTPHost("smtp.gmail.com"),
    "googlemail.com": SMTPHost("smtp.gmail.com"),
    "outlook.com": SMTPHost(
        "smtp.office365.com", port=587, ssl=False, starttls=True
    ),
    "hotmail.com": SMTPHost(
        "smtp.office365.com", port=587, ssl=False, starttls=True
    ),
    "live.com": SMTPHost(
        "smtp.office365.com", port=587, ssl=False, starttls=True
    ),
    "msn.com": SMTPHost(
        "smtp.office365.com", port=587, ssl=False, starttls=True
    ),
    "office365.com": SMTPHost(
        "smtp.office365.com", port=587, ssl=False, starttls=True
    ),
    "icloud.com": SMTPHost(
        "smtp.mail.me.com", port=587, ssl=False, starttls=True
    ),
    "me.com": SMTPHost("smtp.mail.me.com", port=587, ssl=False, starttls=True),
    "mac.com": SMTPHost(
        "smtp.mail.me.com", port=587, ssl=False, starttls=True
    ),
    "yahoo.com": SMTPHost("smtp.mail.yahoo.com"),
    "ymail.com": SMTPHost("smtp.mail.yahoo.com"),
    "zoho.com": SMTPHost("smtp.zoho.com"),
    "hostinger.com": SMTPHost("smtp.hostinger.com"),
    "fastmail.com": SMTPHost("smtp.fastmail.com"),
    "aol.com": SMTPHost("smtp.aol.com"),
}


SMTP_MX_HINTS: list[tuple[str, SMTPHost]] = [
    ("hostinger", SMTPHost("smtp.hostinger.com")),
    ("google.com", SMTPHost("smtp.gmail.com")),
    ("googlemail", SMTPHost("smtp.gmail.com")),
    (
        "outlook.com",
        SMTPHost("smtp.office365.com", port=587, ssl=False, starttls=True),
    ),
    (
        "office365",
        SMTPHost("smtp.office365.com", port=587, ssl=False, starttls=True),
    ),
    (
        "protection.outlook.com",
        SMTPHost("smtp.office365.com", port=587, ssl=False, starttls=True),
    ),
    ("zoho", SMTPHost("smtp.zoho.com")),
    ("yahoodns", SMTPHost("smtp.mail.yahoo.com")),
    ("yandex", SMTPHost("smtp.yandex.com")),
    ("mail.ru", SMTPHost("smtp.mail.ru")),
    ("locaweb", SMTPHost("smtp.locaweb.com.br")),
    ("kinghost", SMTPHost("smtp.kinghost.net")),
    ("uol.com", SMTPHost("smtp.uol.com.br")),
    ("fastmail", SMTPHost("smtp.fastmail.com")),
]


def _lookup_smtp_srv(domain: str) -> Optional[SMTPHost]:
    if not _HAS_DNS:
        return None
    try:
        answers = dns.resolver.resolve(
            f"_submission._tcp.{domain}", "SRV", lifetime=3.0
        )
    except DNSException:
        return None
    for rdata in sorted(answers, key=lambda r: (r.priority, -r.weight)):
        host = str(rdata.target).rstrip(".")
        if host and host != ".":
            port = int(rdata.port)
            return SMTPHost(
                host=host,
                port=port,
                ssl=port == 465,
                starttls=port == 587,
            )
    return None


def _lookup_smtp_mx(domain: str) -> Optional[SMTPHost]:
    if not _HAS_DNS:
        return None
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=3.0)
    except DNSException:
        return None
    for rdata in sorted(answers, key=lambda r: r.preference):
        host = str(rdata.exchange).rstrip(".").lower()
        for hint, smtp in SMTP_MX_HINTS:
            if hint in host:
                return smtp
    return None


def resolve_smtp_host(address: str) -> SMTPHost:
    """Discover the SMTP host for an email address.

    Mirrors :func:`resolve_imap_host`: known providers, DNS SRV, DNS MX hints,
    convention fallback (``smtp.<domain>`` on 465/SSL).
    """
    _, domain = _split_email(address)

    if domain in KNOWN_SMTP_PROVIDERS:
        return KNOWN_SMTP_PROVIDERS[domain]

    srv = _lookup_smtp_srv(domain)
    if srv is not None:
        return srv

    mx = _lookup_smtp_mx(domain)
    if mx is not None:
        return mx

    return SMTPHost(host=f"smtp.{domain}")
