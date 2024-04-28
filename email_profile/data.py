"""
Data Module
"""

from typing import List, Dict
from abc import abstractmethod, ABC


class DataAbstract(ABC):

    def __init__(self) -> None:
        self.email: object = None
        self.attachments: List[object] = list()

    def add_email(self, model: object):
        self.email = model

    def add_attachment(self, model: object):
        self.attachments.append(model)

    @abstractmethod
    def json(self) -> Dict:
        return {
            "email": {},
            "attachments": [{}]
        }


class DataClass(DataAbstract):

    def json(self) -> Dict:
        attachments_temp = []
        for attachment in self.attachments:
            attachments_temp.append(attachment.__dict__)

        return {
            "email": self.email.__dict__,
            "attachments": attachments_temp
        }
