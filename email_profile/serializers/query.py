"""
Dataclass Module
"""

from datetime import date
from dataclasses import dataclass, field

from email_profile.abstract.model import Validator


@dataclass
class Query(Validator):

    since: date = field(default="")
    before: date = field(default="")
    subject: str = field(default="")
    from_who: str = field(default="")

    def validate_since(self, value) -> str:
        if value:
            return "(SINCE {})".format(value.strftime("%d-%b-%Y"))
        return ""

    def validate_before(self, value) -> str:
        if value:
            return "(BEFORE {})".format(value.strftime("%d-%b-%Y"))
        return ""

    def validate_subject(self, value) -> str:
        if value:
            return '(SUBJECT "{}")'.format(
                value.encode("ASCII", "ignore").decode()
            )
        return ""

    def validate_from_who(self, value) -> str:
        if value:
            return '(FROM "{}")'.format(
                self.from_who.encode("ASCII", "ignore").decode()
            )
        return ""

    def result(self):
        data = []
        for _field in self.__dataclass_fields__:
            content = getattr(self, _field)
            if content:
                data.append(content)
        return " ".join(data)

    def mount(self):
        data = []
        for _field in self.__dataclass_fields__:
            content = getattr(self, _field)
            if content:
                data.append(content)

        if data:
            return " ".join(data)

        return "ALL"
