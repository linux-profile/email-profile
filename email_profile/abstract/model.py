"""
Model Module
"""

from dataclasses import dataclass
from abc import abstractclassmethod, ABC


@dataclass
class AbstractModel(ABC):

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
