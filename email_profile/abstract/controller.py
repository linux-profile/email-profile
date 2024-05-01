"""
Controller Module
"""

from abc import abstractmethod, ABC


class AbstractController(ABC):

    def __init__(self, model=None, data=None) -> None:
        self.model = model
        self.data = data

    @abstractmethod
    def create(self) -> None:
        pass

    @abstractmethod
    def read(self) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def delete(self) -> None:
        pass
