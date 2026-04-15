"""Mailbox name hints (EN/PT/ES) and the matching helper."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from email_profile.mailbox import MailBox


INBOX_HINTS = (
    "inbox",
    "entrada",
    "caixa de entrada",
    "bandeja de entrada",
)

SENT_HINTS = (
    "sent",
    "sent items",
    "sent mail",
    "[gmail]/sent",
    "enviados",
    "enviadas",
    "itens enviados",
    "elementos enviados",
)

SPAM_HINTS = (
    "spam",
    "junk",
    "junk email",
    "[gmail]/spam",
    "lixo eletrônico",
    "lixo eletronico",
    "correo no deseado",
    "correo basura",
)

TRASH_HINTS = (
    "trash",
    "deleted",
    "deleted items",
    "bin",
    "[gmail]/trash",
    "lixeira",
    "itens excluídos",
    "itens excluidos",
    "papelera",
    "elementos eliminados",
)

DRAFTS_HINTS = (
    "drafts",
    "[gmail]/drafts",
    "rascunhos",
    "borradores",
)

ARCHIVE_HINTS = (
    "archive",
    "all mail",
    "[gmail]/all mail",
    "arquivo",
    "todos os emails",
    "todas as mensagens",
    "archivo",
    "todo el correo",
    "todos los mensajes",
)


def find_mailbox(
    mailboxes: dict[str, MailBox],
    hints: tuple[str, ...],
) -> Optional[MailBox]:
    """First mailbox whose name matches any hint (case-insensitive)."""

    for hint in hints:

        for name, mb in mailboxes.items():

            if hint == name.lower() or hint in name.lower():
                return mb

    return None
