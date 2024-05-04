"""
Model Module
"""

from dataclasses import dataclass
from abc import abstractclassmethod, ABC


class Validations:

    def __post_init__(self):
        for name, _field in self.__dataclass_fields__.items():
            method_name = f"validate_{name}"

            if hasattr(self, method_name):
                if method := getattr(self, method_name):
                    setattr(self, name, method(field=_field))


@dataclass
class AbstractModel(ABC, Validations):

    @abstractclassmethod
    class Meta:
        table_name = None

    def get_table_name(self):
        return self.Meta.table_name

    def get_fields(self):
        fields = self.__dataclass_fields__.items()
        return [name for name, field in fields]

    def get_values(self):
        values = [value for value in self.__dict__.items()]
        return [f"'{str(item)}'" for x, item in values]
