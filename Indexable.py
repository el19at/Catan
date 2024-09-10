from abc import ABC, abstractmethod

class Indexable(ABC):
    @abstractmethod
    def to_index(self):
        pass
    