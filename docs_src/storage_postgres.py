"""PostgreSQL storage backend."""

from typing import Optional

import psycopg2

from email_profile.advanced import StorageABC
from email_profile.serializers.raw import RawSerializer


class PostgresStorage(StorageABC):

    def __init__(self, dsn: str) -> None:
        self._conn = psycopg2.connect(dsn)
        self._ensure_table()

    def _ensure_table(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    uid TEXT NOT NULL,
                    mailbox TEXT NOT NULL,
                    message_id TEXT NOT NULL,
                    flags TEXT NOT NULL DEFAULT '',
                    file TEXT,
                    PRIMARY KEY (uid, mailbox)
                )
            """)
            self._conn.commit()

    def save(self, raw: RawSerializer) -> bool:
        with self._conn.cursor() as cur:
            cur.execute(
                """INSERT INTO emails (uid, mailbox, message_id, flags, file)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (uid, mailbox) DO UPDATE
                   SET message_id = EXCLUDED.message_id,
                       flags = EXCLUDED.flags,
                       file = EXCLUDED.file
                   RETURNING xmax""",
                (raw.uid, raw.mailbox, raw.message_id, raw.flags, raw.file),
            )
            xmax = cur.fetchone()[0]
            self._conn.commit()
            return xmax == 0

    def get(self, message_id: str) -> Optional[RawSerializer]:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT message_id, uid, mailbox, flags, file "
                "FROM emails WHERE message_id = %s LIMIT 1",
                (message_id,),
            )
            row = cur.fetchone()

            if row is None:
                return None

            return RawSerializer(
                message_id=row[0],
                uid=row[1],
                mailbox=row[2],
                flags=row[3],
                file=row[4],
            )

    def ids(self, mailbox: Optional[str] = None) -> set[str]:
        with self._conn.cursor() as cur:
            if mailbox:
                cur.execute(
                    "SELECT message_id FROM emails WHERE mailbox = %s",
                    (mailbox,),
                )
            else:
                cur.execute("SELECT message_id FROM emails")

            return {row[0] for row in cur.fetchall()}

    def uids(self, mailbox: str) -> set[str]:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT uid FROM emails WHERE mailbox = %s",
                (mailbox,),
            )
            return {row[0] for row in cur.fetchall()}
