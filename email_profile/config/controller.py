"""
Controller Module
"""


import logging

from email_profile.config.database import session
from email_profile.models import AttachmentModel, EmailModel


class Controller:

    def __init__(self, model=None) -> None:
        self.model = model
        self.fields = model.__dataclass_fields__.items()
        self.table_name = model.__tablename__

        self._validate_table()

    def _create_table(self) -> None:
        fields = [name for name, field in self.fields]
        query = ", ".join(fields)

        session.execute(f"CREATE TABLE {self.table_name} ({query})")

    def _validate_table(self) -> None:
        try:
            session.execute(f"SELECT * FROM {self.table_name}")
        except Exception as error:
            error_message = f'no such table: {self.table_name}'

            if error.args[0] == error_message:
                self._create_table()

    def create(self, data: object):
        logging.info("Not implemented")
        pass

    def read(self):
        logging.info("Not implemented")
        pass

    def update(self):
        logging.info("Not implemented")
        pass

    def delete(self):
        logging.info("Not implemented")
        pass


class AttachmentController(Controller):

    def __init__(self):
        super().__init__(model=AttachmentModel)


class EmailController(Controller):

    def __init__(self):
        super().__init__(model=EmailModel)
