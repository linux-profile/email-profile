"""High-level query shortcuts that operate on the inbox."""

from __future__ import annotations

from datetime import date, timedelta

from email_profile.folders import FolderAccess
from email_profile.searches import Where


class QueryShortcuts:
    """Convenience queries over :attr:`FolderAccess.inbox`."""

    def __init__(self, folders: FolderAccess) -> None:
        self._folders = folders

    def unread(self) -> Where:
        """Unread messages in the inbox."""
        return self._folders.inbox.where(unseen=True)

    def recent(self, days: int = 7) -> Where:
        """Messages from the last N days."""
        return self._folders.inbox.where(
            since=date.today() - timedelta(days=days)
        )

    def search(self, text: str) -> Where:
        """Full-text search in the inbox."""
        return self._folders.inbox.where(text=text)

    def all(self) -> Where:
        """All messages in the inbox."""
        return self._folders.inbox.where()
