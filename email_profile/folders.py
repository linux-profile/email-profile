"""Mailbox name hints (EN/PT/ES), matching helper, and FolderAccess class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from email_profile.imap_session import IMAPSession
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


class FolderAccess:
    """Resolve common folder properties (inbox/sent/spam/...) for a session."""

    def __init__(self, session: IMAPSession) -> None:
        self._session = session

    def mailboxes(self) -> list[str]:
        self._session.require()
        return list(self._session.mailboxes)

    def mailbox(self, name: str) -> MailBox:
        self._session.require()
        if name not in self._session.mailboxes:
            raise KeyError(
                f"Unknown mailbox: {name!r}. Available: {self.mailboxes()}"
            )
        return self._session.mailboxes[name]

    def _find(self, hints: tuple[str, ...]) -> MailBox:
        self._session.require()
        mb = find_mailbox(self._session.mailboxes, hints)
        if mb is None:
            raise KeyError(
                f"Could not find a mailbox matching {hints!r}. "
                f"Available: {self.mailboxes()}"
            )
        return mb

    @property
    def inbox(self) -> MailBox:
        return self._find(INBOX_HINTS)

    @property
    def sent(self) -> MailBox:
        return self._find(SENT_HINTS)

    @property
    def spam(self) -> MailBox:
        return self._find(SPAM_HINTS)

    @property
    def trash(self) -> MailBox:
        return self._find(TRASH_HINTS)

    @property
    def drafts(self) -> MailBox:
        return self._find(DRAFTS_HINTS)

    @property
    def archive(self) -> MailBox:
        return self._find(ARCHIVE_HINTS)
