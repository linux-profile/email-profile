"""
Controller Module
"""


import logging

from email_profile.models.peewee.base import db


class Controller:

    def __init__(self, model=None, data=None) -> None:
        self.model = model
        self.data = data

        db.connect()
        db.create_tables([self.model])

    def create(self):
        try:
            self.model.create(**self.data.__dict__)
        except Exception as error:
            message = f"\n{str(self.data.id)}: {str(error)}"
            logging.error(error)

            with open("log.txt", mode="a") as file:
                file.write(message)

        finally:
            db.close()

    def read(self):
        logging.warning("Not implemented")
        pass

    def update(self):
        logging.warning("Not implemented")
        pass

    def delete(self):
        logging.warning("Not implemented")
        pass
