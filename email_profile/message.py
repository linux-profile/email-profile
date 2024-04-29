"""
Message Module
"""

from email import message_from_bytes
from email.header import decode_header
from email.utils import parsedate_to_datetime

from email_profile.data import DataClass as Data
from email_profile.models import AttachmentModel, EmailModel


class Message:

    def __init__(self, message: bytes, id: int) -> None:
        self.message = message_from_bytes(message)
        self.id = id
        self.body_text_plain = ""
        self.body_text_html = ""
        self.data = Data()

    def decode_field(self, header) -> str:
        field = ""
        for sub in decode_header(header):
            encoding = sub[1] or "utf-8"
            try:
                field += sub[0].decode(encoding)
            except Exception:
                field += sub[0]
        return field

    def parsedate_to_datetime(self, date):
        try:
            return parsedate_to_datetime(date)
        except ValueError:
            pass
        return None

    def get_content(self, part) -> None:
        content_type = part.get_content_type()

        if content_type == "text/plain":
            try:
                self.body_text_plain = part.get_payload(decode=True).decode()
            except Exception:
                self.body_text_plain = part.get_payload(decode=True)

        if content_type == "text/html":
            try:
                self.body_text_html = part.get_payload(decode=True).decode()
            except Exception:
                self.body_text_html = part.get_payload(decode=True)
                if isinstance(self.body_text_html, bytes):
                    self.body_text_html = part.get_payload()

        if "attachment" in str(part.get("Content-Disposition")):
            filename = part.get_filename()
            if filename:
                self.data.add_attachment(
                    AttachmentModel(
                        email_id=self.id,
                        file_name=filename,
                        content_type=part.get_content_type(),
                        content_ascii=part.get_payload().encode("ascii")
                    )
                )

    def result(self) -> EmailModel:
        for part in self.message.walk():
            self.get_content(part=part)

        self.data.add_email(
            EmailModel(
                id=self.id,
                body_text_plain=self.body_text_plain,
                body_text_html=self.body_text_html,
                return_path=self.message.get("Return-Path"),
                delivered_to=self.message.get("Delivered-To"),
                received=self.message.get("Received"),
                dkim_signature=self.message.get("DKIM-Signature"),
                content_type=self.message.get_content_type(),
                date=self.parsedate_to_datetime(self.message.get("Date")),
                from_who=self.decode_field(self.message.get("From")),
                mime_version=self.message.get("Mime-Version"),
                message_id=self.message.get("Message-ID"),
                subject=self.decode_field(self.message["Subject"]),
                reply_to=self.message.get("Reply-To"),
                precedence=self.message.get("Precedence"),
                x_sg_eid=self.message.get("X-SG-EID"),
                x_sg_id=self.message.get("X-SG-ID"),
                to_who=self.message.get("To"),
                x_entity_id=self.message.get("X-Entity-ID")
            )
        )

        return self.data
