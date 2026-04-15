"""Inspect IMAP host discovery for a custom domain.

Useful when you want to understand which host ``Email(user=...)`` will
pick for an arbitrary address — known providers map first, then DNS SRV,
then DNS MX with provider hints, then ``imap.<domain>`` as a fallback.
"""

from email_profile import resolve_imap_host


def main() -> None:
    addresses = [
        "alice@gmail.com",
        "you@outlook.com",
        "contato@suaempresa.com.br",
        "user@unknown-domain.example",
    ]

    for address in addresses:
        host = resolve_imap_host(address)
        print(f"{address:<40}  ->  {host.host}:{host.port}")


if __name__ == "__main__":
    main()
