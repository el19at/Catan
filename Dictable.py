from abc import ABC, abstractmethod

class Dictable(ABC):
    @abstractmethod
    def to_dict(self):
        pass
    
    @abstractmethod
    @classmethod
    def from_dict(cls, data):
        pass