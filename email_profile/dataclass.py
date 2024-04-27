"""
Dataclass Module
"""

from typing import Union
from datetime import date
from pydantic import BaseModel, Field, field_validator


class WhereDataClass(BaseModel):

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
            return '(SUBJECT "{}")'.format(value)
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
