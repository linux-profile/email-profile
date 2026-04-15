"""Optional SQLite persistence for fetched messages."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Optional, Union

from email_profile._internal import _build_serializer
from email_profile.eml import EmailModel, EmailSerializer
from email_profile.session import Base, make_session


class Storage:
    """SQLAlchemy persistence; call save() explicitly."""

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

    def save_many(self, serializers: Iterator[EmailSerializer]) -> int:
        """Persist many messages in a single transaction."""
        count = 0
        with self._session_factory() as session:

            for serializer in serializers:
                session.add(EmailModel.from_serializer(serializer))
                count += 1

            session.commit()

        return count

    def iter_messages(
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
        return f"Storage(url={self.url!r})"
