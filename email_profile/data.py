"""
Data Module
"""

import logging

from typing import List, Dict
from abc import abstractmethod, ABC

from email_profile.config.controller import Controller

try:
    from email_profile.models.peewee import (
        AttachmentModel,
        EmailModel
    )
except Exception as error:
    logging.error(error)

    AttachmentModel = None
    EmailModel = None


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

    @abstractmethod
    def sqllite(self) -> None:
        pass


class DataClass(DataAbstract):

    def json(self) -> Dict:
        attachments_temp = []
        for attachment in self.attachments:
            attachments_temp.append(attachment.__dict__)

        return {
            "email": self.email.__dict__,
            "attachments": attachments_temp
        }

    def sqllite(self) -> None:
        Controller(
            model=EmailModel,
            data=self.email
        ).create()

        for attachment in self.attachments:
            Controller(
                model=AttachmentModel,
                data=attachment
            ).create()
