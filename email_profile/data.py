"""
Data Module
"""

import json

from pathlib import Path
from typing import List, Dict
from abc import abstractmethod, ABC

from email_profile.utils import mkdir


class DataAbstract(ABC):

    _id = None

    def __init__(self) -> None:
        self.email: object = None
        self.attachments: List[object] = list()

    def add_email(self, model: object):
        self._id = str(model.id)
        self.email = model

    def add_attachment(self, model: object):
        self.attachments.append(model)

    @abstractmethod
    def json(self) -> None:
        pass

    @abstractmethod
    def html(self) -> None:
        pass


class DataClass(DataAbstract):

    def json(self,
             path: str = "json",
             create_file: bool = True) -> Dict:
        data = self.email.__dict__

        if create_file:
            path = Path(path)
            mkdir(path)

            with open(
                file=path.joinpath(f"{self._id}.json"),
                mode="w",
                errors="ignore"
            ) as file:
                file.write(
                    json.dumps(data, indent=4)
                )

        return data

    def html(self,
             path: str = "html",
             create_file: bool = True) -> str:
        data = self.email.body_text_html

        if create_file:
            path = Path(path, self._id)
            mkdir(path)

            with open(
                file=path.joinpath("index.html"),
                mode="w",
                errors="ignore"
            ) as file:
                file.write(
                    self.email.body_text_html
                )

        return data
