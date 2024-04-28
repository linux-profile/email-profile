"""
Dataclass Module
"""

from typing import Union
from datetime import date
from pydantic import BaseModel, Field, field_validator


class WhereSerializer(BaseModel):
    """
    ------
    URL: https://www.rfc-editor.org/rfc/rfc3501.html#page-53
    ------

    SUBJECT <string>
        Messages that contain the specified string in the envelope
        structure's SUBJECT field.

    TEXT <string>
        Messages that contain the specified string in the header or
        body of the message.

    TO <string>
        Messages that contain the specified string in the envelope
        structure's TO field.

    UID <sequence set>
        Messages with unique identifiers corresponding to the specified
        unique identifier set.  Sequence set ranges are permitted.

    UNANSWERED
        Messages that do not have the \Answered flag set.

    UNDELETED
        Messages that do not have the \Deleted flag set.

    UNDRAFT
        Messages that do not have the \Draft flag set.

    UNFLAGGED
        Messages that do not have the \Flagged flag set.

    UNKEYWORD <flag>
        Messages that do not have the specified keyword flag set.

    UNSEEN
        Messages that do not have the \Seen flag set.
    """

    since: date = Field(default="")
    before: date = Field(default="")
    subject: str  = Field(default="")
    from_who: str = Field(default="")

    @field_validator('since')
    @classmethod
    def format_since(cls, value: Union[date, str]) -> str:
        if value:
            return '(SINCE {})'.format(value.strftime('%d-%b-%Y'))
        return ''

    @field_validator('before')
    @classmethod
    def format_before(cls, value: Union[date, str]) -> str:
        if value:
            return '(BEFORE {})'.format(value.strftime('%d-%b-%Y'))
        return ''

    @field_validator('subject')
    @classmethod
    def format_subject(cls, value: str) -> str:
        if value:
            return '(SUBJECT "{}")'.format(
                value.encode("ASCII", 'ignore').decode()
            )
        return ''

    @field_validator('from_who')
    @classmethod
    def format_from_who(cls, value: str) -> str:
        if value:
            return '(FROM "{}")'.format(value)
        return ''

    def result(self):
        data = []
        for field in self.model_fields:
            content = getattr(self, field)
            if content:
                data.append(content)
        return " ".join(data)
