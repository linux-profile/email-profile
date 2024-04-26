import imaplib
import email

from typing import List, Tuple
from uuid import uuid4

from email.header import decode_header
from email.utils import parsedate_to_datetime

from models.email import Email as EmailModel
from models.attachment import Attachment as AttachmentModel


class Status:

    OK = 'OK'
    NO = 'NO'

    @staticmethod
    def validate(status: str) -> bool:
        return {Status.OK: True, Status.NO: False}.get(status)


class Data:

    def __init__(self):
        self.email: List[EmailModel] = list()
        self.attachment: List[AttachmentModel] = list()

    def add_email(self, value: EmailModel) -> None:
        self.email.append(value)

    def add_attachment(self, value: AttachmentModel) -> None:
        self.attachment.append(value)


class Email:

    def __init__(self, server: str, username: str, password: str):
        self.messages = 0
        self.status = Status.NO
        self.server = imaplib.IMAP4_SSL(server)
        self.data = Data()

        self.username = username
        self.password = password

    def _decode_header(self, header) -> str:
        field = ""
        field_temp = decode_header(header)

        for sub in field_temp:
            encoding = sub[1] or "utf-8"

            try:
                field += sub[0].decode(encoding)
            except Exception as error:
                field += sub[0]

        return field

    def login(self):
        self.server.login(
            self.username,
            self.password
        )

    def select(self, mailbox: str = 'INBOX') -> Tuple[str, int]:
        try:
            status, messages = self.server.select(mailbox)
            self.status = status
            self.messages = int(messages[0])
        except Exception as error:
            self.status = Status.NO
            self.messages = 0

        return self.status, self.messages

    def backup(self, number: int = 0) -> Data:
        if not self.messages:
            self.select()

        if not number:
            number = self.messages

        for i in range(self.messages, self.messages-number, -1):
            res, msg = self.server.fetch(str(i), "(RFC822)")
            hex_id = uuid4().hex

            for response in msg:
                body = ""
                body_text_plain = ""
                body_text_html = ""

                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])

                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()

                            if content_type == "text/plain":
                                try:
                                    body_text_plain = part.get_payload(decode=True).decode()
                                except Exception as error:
                                    body_text_plain = part.get_payload(decode=True)

                            if content_type == "text/html":
                                try:
                                    body_text_html = part.get_payload(decode=True).decode()
                                except Exception as error:
                                    body_text_html = part.get_payload(decode=True)
                                    if isinstance(body_text_html, bytes):
                                        body_text_html = part.get_payload()

                            if "attachment" in str(part.get("Content-Disposition")):
                                filename = part.get_filename()

                                if filename:
                                    self.data.add_attachment(
                                        value=AttachmentModel(
                                            id=uuid4().hex,
                                            email_id=hex_id,
                                            file_name=filename,
                                            content_type=part.get_content_type(),
                                            content_ascii=part.get_payload().encode("ascii")
                                        )
                                    )

                    else:
                        if content_type == "text/plain":
                            try:
                                body_text_plain = msg.get_payload(decode=True).decode()
                            except Exception as error:
                                body_text_plain = msg.get_payload(decode=True)

                        if content_type == "text/html":
                            try:
                                body_text_html = msg.get_payload(decode=True).decode()
                            except Exception as error:
                                body_text_html = msg.get_payload(decode=True)
                                if isinstance(body_text_html, bytes):
                                    body_text_html = msg.get_payload()

                    self.data.add_email(
                        value=EmailModel(
                            id=hex_id,
                            number=i,
                            body_text_plain=body_text_plain,
                            body_text_html=body_text_html,
                            return_path=msg.get("Return-Path"),
                            delivered_to=msg.get("Delivered-To"),
                            received=msg.get("Received"),
                            dkim_signature=msg.get("DKIM-Signature"),
                            content_type=msg.get_content_type(),
                            date=parsedate_to_datetime(msg.get("Date")),
                            _from=self._decode_header(msg.get("From")),
                            mime_version=msg.get("Mime-Version"),
                            message_id=msg.get("Message-ID"),
                            subject=self._decode_header(msg["Subject"]),
                            reply_to=msg.get("Reply-To"),
                            precedence=msg.get("Precedence"),
                            x_sg_eid=msg.get("X-SG-EID"),
                            x_sg_id=msg.get("X-SG-ID"),
                            to=msg.get("To"),
                            x_entity_id=msg.get("X-Entity-ID")
                        )
                    )

        return self.data
