from peewee import Model
from email_profile.config.database import engine_sqlite_database


db = engine_sqlite_database()


class BaseModel(Model):

    class Meta:
        database = db
