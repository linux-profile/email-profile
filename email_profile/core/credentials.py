"""Connection-building helpers: from env, from address."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from email_profile.providers import resolve_imap_host


@dataclass(frozen=True)
class Credentials:
    """Resolved (server, user, password, port, ssl) tuple."""

    server: str
    user: str
    password: str
    port: int = 993
    ssl: bool = True

    def __repr__(self) -> str:
        return f"Credentials(server={self.server!r}, user={self.user!r}, password='***')"

    def __str__(self) -> str:
        return self.__repr__()


class EmailFactories:
    """Build :class:`Credentials` without the user spelling out a hostname."""

    @classmethod
    def from_address(
        cls,
        address: str,
        password: str,
        *,
        port: Optional[int] = None,
        ssl: Optional[bool] = None,
    ) -> Credentials:
        """Auto-discover the IMAP host from the email address.

        ``port`` and ``ssl`` override the discovered values when given.
        """
        host = resolve_imap_host(address)
        return Credentials(
            server=host.host,
            user=address,
            password=password,
            port=host.port if port is None else port,
            ssl=host.ssl if ssl is None else ssl,
        )

    @classmethod
    def from_env(
        cls,
        server_var: str = "EMAIL_SERVER",
        user_var: str = "EMAIL_USERNAME",
        password_var: str = "EMAIL_PASSWORD",
        load_dotenv: bool = True,
        *,
        port: Optional[int] = None,
        ssl: Optional[bool] = None,
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
            return Credentials(
                server=server,
                user=user,
                password=password,
                port=993 if port is None else port,
                ssl=True if ssl is None else ssl,
            )

        return cls.from_address(user, password, port=port, ssl=ssl)
