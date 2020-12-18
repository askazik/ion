# Abstract classes
from abc import ABC, abstractmethod


class AbstractSource(ABC):

    @property
    @abstractmethod
    def source(self):
        pass
