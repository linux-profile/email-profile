"""Optional SQLite persistence for fetched messages."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Optional, Union

from email_profile._internal import _build_serializer
from email_profile.core.abc import StorageABC
from email_profile.models.email import EmailModel
from email_profile.serializers.email import EmailSerializer
from email_profile.storage.db import Base, make_session


class StorageSQLite(StorageABC):
    """SQLAlchemy persistence; call save() explicitly."""

    BULK_BATCH = 500

    def __init__(self, url: Union[str, Path] = "sqlite:///:memory:") -> None:
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

    def save(self, serializer: EmailSerializer) -> EmailModel:
        """Persist one message."""
        model = EmailModel.from_serializer(serializer)

        with self._session_factory() as session:
            session.add(model)
            session.commit()

        return model

    def save_many(
        self,
        serializers: Iterable[EmailSerializer],
        *,
        batch_size: Optional[int] = None,
    ) -> int:
        """Persist many messages using SQLAlchemy bulk insert."""
        size = batch_size or self.BULK_BATCH
        total = 0
        buffer: list[EmailModel] = []

        with self._session_factory() as session:
            for serializer in serializers:
                buffer.append(EmailModel.from_serializer(serializer))
                if len(buffer) >= size:
                    session.bulk_save_objects(buffer)
                    session.commit()
                    total += len(buffer)
                    buffer.clear()

            if buffer:
                session.bulk_save_objects(buffer)
                session.commit()
                total += len(buffer)

        return total

    def existing_ids(self, mailbox: Optional[str] = None) -> set[str]:
        """Return the set of stored message ``id`` values (Message-ID/UUID).

        Useful for resumable backups: skip messages already in the database.
        """
        with self._session_factory() as session:
            query = session.query(EmailModel.id)
            if mailbox is not None:
                query = query.filter(EmailModel.mailbox == mailbox)
            return {row[0] for row in query.all()}

    def existing_uids(self, mailbox: str) -> set[str]:
        """Return persisted IMAP UIDs for a mailbox."""
        with self._session_factory() as session:
            query = session.query(EmailModel.uid).filter(
                EmailModel.mailbox == mailbox
            )
            return {row[0] for row in query.all()}

    def messages(
        self, mailbox: Optional[str] = None
    ) -> Iterator[EmailSerializer]:
        """Reconstruct serializers from persisted rows."""
        with self._session_factory() as session:
            query = session.query(EmailModel)
            if mailbox is not None:
                query = query.filter(EmailModel.mailbox == mailbox)

            for row in query.yield_per(100):
                yield EmailSerializer.from_raw(
                    uid=row.uid,
                    mailbox=row.mailbox,
                    raw=row.file.encode("utf-8"),
                    message_id=row.id,
                    date=row.date,
                    from_=row.from_,
                    to_=row.to_,
                    file=row.file,
                )

    def export_eml(
        self, path: Union[str, Path], mailbox: Optional[str] = None
    ) -> int:
        """Dump every persisted message to <path>/<mailbox>/<uid>.eml."""

        target = Path(path)
        count = 0

        with self._session_factory() as session:
            query = session.query(EmailModel)
            if mailbox is not None:
                query = query.filter(EmailModel.mailbox == mailbox)

            for row in query.yield_per(100):
                folder = target / row.mailbox
                folder.mkdir(parents=True, exist_ok=True)
                (folder / f"{row.uid}.eml").write_bytes(
                    row.file.encode("utf-8")
                )
                count += 1

        return count

    def import_eml(
        self, path: Union[str, Path], mailbox: Optional[str] = None
    ) -> int:
        """Read every .eml under <path>; mailbox = parent dir name."""
        source = Path(path)
        if not source.exists():
            raise FileNotFoundError(source)

        count = 0
        with self._session_factory() as session:
            for eml_path in source.rglob("*.eml"):
                raw = eml_path.read_bytes()
                box = mailbox or eml_path.parent.name
                uid = eml_path.stem.encode()

                serializer = _build_serializer(
                    raw_uid=uid,
                    raw_message=raw,
                    mailbox=box,
                )

                session.add(EmailModel.from_serializer(serializer))
                count += 1

            session.commit()

        return count

    def dispose(self) -> None:
        """Release the engine."""
        self._engine.dispose()

    def __repr__(self) -> str:
        return f"StorageSQLite(url={self.url!r})"
