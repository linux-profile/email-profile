"""
Dataclass Module
"""

from datetime import date
from dataclasses import dataclass, field


class Validations:

    def __post_init__(self):
        for name, _field in self.__dataclass_fields__.items():
            if method := getattr(self, f"validate_{name}"):
                setattr(self, name, method(field=_field))


@dataclass
class WhereSerializer(Validations):

    since: date = field(default="")
    before: date = field(default="")
    subject: str = field(default="")
    from_who: str = field(default="")

    def validate_since(self, field) -> str:
        if self.since:
            if not isinstance(self.since, field.type):
                raise AttributeError(
                    "Attribute validation error (SINCE)."
                )
            return '(SINCE {})'.format(
                self.since.strftime('%d-%b-%Y')
            )
        return ''

    def validate_before(self, field) -> str:
        if self.before:
            if not isinstance(self.before, field.type):
                raise AttributeError(
                    "Attribute validation error (BEFORE)."
                )
            return '(BEFORE {})'.format(
                self.before.strftime('%d-%b-%Y')
            )
        return ''

    def validate_subject(self, field) -> str:
        if self.subject:
            if not isinstance(self.subject, field.type):
                raise AttributeError(
                    "Attribute validation error (SUBJECT)."
                )
            return '(SUBJECT "{}")'.format(
                self.subject.encode("ASCII", 'ignore').decode()
            )
        return ''

    def validate_from_who(self, field) -> str:
        if self.from_who:
            if not isinstance(self.from_who, field.type):
                raise AttributeError(
                    "Attribute validation error (FRON_WHO)."
                )
            return '(FROM "{}")'.format(
                self.from_who.encode("ASCII", 'ignore').decode()
            )
        return ''

    def result(self):
        data = []
        for _field in self.__dataclass_fields__:
            content = getattr(self, _field)
            if content:
                data.append(content)
        return " ".join(data)
