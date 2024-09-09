from Point import Point
from Dictable import Dictable
class Tile(Dictable):
    def __init__(self, resource, number):
        self.resource = resource
        self.number = number
        self.points: list['Point'] = []
        self.robbed = False
    
    def  equal(self, other: object) -> bool:
        if isinstance(other, Point):
            return self.points == other.points
        return False
    
    def robb(self):
        self.robbed = True
    
    def unrobb(self):
        self.robbed = False
    
    def is_robbed(self):
        return self.robbed
    
    def to_dict(self):
        return {
            'resource': self.resource,
            'number': self.number,
            'points': [point.to_dict() for point in self.points if point],
            'robbed': self.robbed
        }
    
    @classmethod
    def from_dict(cls, data):
        obj = cls(int(data['resource']), int(data['number']))
        obj.points = [Point.from_dict(p) for p in data['points']]
        obj.robbed = bool(data['robbed'])
        return obj