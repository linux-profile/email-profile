"""SQLite persistence for fetched messages."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Union

from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from email_profile.core.abc import StorageABC
from email_profile.models.raw import RawModel
from email_profile.serializers.raw import RawSerializer
from email_profile.storage.db import Base, make_session

logger = logging.getLogger(__name__)


class StorageSQLite(StorageABC):
    """SQLite persistence backed by a single ``raw`` table."""

    def __init__(self, url: Union[str, Path] = "./email.db") -> None:
        self.url = self._coerce_url(url)
        self._engine, self._session_factory = make_session(self.url)
        Base.metadata.create_all(bind=self._engine)

    @staticmethod
    def _coerce_url(value: Union[str, Path]) -> str:
        if isinstance(value, Path):
            return f"sqlite:///{value}"

        if "://" in value:
            return value

        return f"sqlite:///{value}"

    def ids(self, mailbox: Optional[str] = None) -> set[str]:
        """Return stored email IDs."""
        with self._session_factory() as session:
            query = session.query(RawModel.message_id)
            if mailbox:
                query = query.filter(RawModel.mailbox == mailbox)
            return {row[0] for row in query.all()}

    def uids(self, mailbox: str) -> set[str]:
        """Return stored IMAP UIDs for a mailbox."""
        with self._session_factory() as session:
            return {
                row[0]
                for row in session.query(RawModel.uid)
                .filter(RawModel.mailbox == mailbox)
                .all()
            }

    def save(self, raw: RawSerializer) -> bool:
        """Persist the RFC822 source. Returns True if inserted, False if updated."""
        with self._session_factory() as session:
            exists = (
                session.query(RawModel.uid)
                .filter(
                    RawModel.uid == raw.uid,
                    RawModel.mailbox == raw.mailbox,
                )
                .first()
                is not None
            )

            stmt = sqlite_insert(RawModel).values(
                message_id=raw.message_id,
                uid=raw.uid,
                mailbox=raw.mailbox,
                flags=raw.flags,
                file=raw.file,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["uid", "mailbox"],
                set_={
                    "message_id": stmt.excluded.message_id,
                    "flags": stmt.excluded.flags,
                    "file": stmt.excluded.file,
                },
            )
            session.execute(stmt)
            session.commit()
            return not exists

    def get(self, message_id: str) -> Optional[RawSerializer]:
        """Retrieve the RFC822 source by email id."""
        with self._session_factory() as session:
            row = (
                session.query(RawModel)
                .filter(RawModel.message_id == message_id)
                .first()
            )

            if row is None:
                return None

            return RawSerializer(
                message_id=row.message_id,
                uid=row.uid,
                mailbox=row.mailbox,
                file=row.file,
                flags=row.flags,
            )

    def __repr__(self) -> str:
        return f"StorageSQLite(url={self.url!r})"
