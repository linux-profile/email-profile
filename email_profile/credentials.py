"""Connection-building helpers: from env, from email, per-provider hosts."""

from __future__ import annotations

import os
from dataclasses import dataclass

from email_profile.providers import resolve_imap_host


@dataclass(frozen=True)
class Credentials:
    """Resolved (server, user, password, port, ssl) tuple."""

    server: str
    user: str
    password: str
    port: int = 993
    ssl: bool = True


class EmailFactories:
    """Ways to build :class:`Credentials` without the user spelling out
    an IMAP hostname."""

    PROVIDER_HOSTS: dict[str, str] = {
        "gmail": "imap.gmail.com",
        "outlook": "outlook.office365.com",
        "icloud": "imap.mail.me.com",
        "yahoo": "imap.mail.yahoo.com",
        "hostinger": "imap.hostinger.com",
        "zoho": "imap.zoho.com",
        "fastmail": "imap.fastmail.com",
    }

    @classmethod
    def from_address(cls, address: str, password: str) -> Credentials:
        """Auto-discover the IMAP host from the email address."""
        host = resolve_imap_host(address)
        return Credentials(
            server=host.host,
            user=address,
            password=password,
            port=host.port,
            ssl=host.ssl,
        )

    @classmethod
    def from_env(
        cls,
        server_var: str = "EMAIL_SERVER",
        user_var: str = "EMAIL_USERNAME",
        password_var: str = "EMAIL_PASSWORD",
        load_dotenv: bool = True,
    ) -> Credentials:
        """Read credentials from env vars (or `.env`)."""
        if load_dotenv:
            try:
                from dotenv import load_dotenv as _ld

                _ld()
            except ImportError:
                pass

        user = os.environ.get(user_var)
        password = os.environ.get(password_var)
        if not user or not password:
            raise KeyError(
                f"Missing {user_var!r} or {password_var!r} in environment."
            )

        server = os.environ.get(server_var)
        if server:
            return Credentials(server=server, user=user, password=password)

        return cls.from_address(user, password)

    @classmethod
    def from_provider(
        cls, provider: str, user: str, password: str
    ) -> Credentials:
        """Build credentials for a well-known provider by short name."""
        key = provider.lower()
        host = cls.PROVIDER_HOSTS.get(key)
        if host is None:
            raise KeyError(
                f"Unknown provider {provider!r}. "
                f"Known: {sorted(cls.PROVIDER_HOSTS)}"
            )
        return Credentials(server=host, user=user, password=password)
