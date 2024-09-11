from Point import Point
from Indexable import Indexable
class Tile(Indexable):
    def __init__(self, resource, number):
        self.resource = resource
        self.number = number
        self.points: list['Point'] = []
        self.robbed = False
        self.row = -1
        self.column = -1
    

    
    def set_index(self, row: int, column: int):
        self.row = row
        self.column= column
        
    def equal(self, other: object) -> bool:
        if isinstance(other, Point):
            return self.row == other.row and self.column == other.column
        return False
    
    def robb(self):
        self.robbed = True
    
    def unrobb(self):
        self.robbed = False
    
    def is_robbed(self):
        return self.robbed
    
    def to_index(self):
        return {
            'type': 'Tile',
            'row': self.row,
            'column': self.column
        }
    
    def to_dict(self):
        return {
            'resource' :self.resource,
            'number': self.number,
            'points': [point.to_dict() for point in self.points],
            'robbed': self.robbed,
            'row': self.row,
            'column': self.column
        }
        
    @classmethod
    def from_dict(cls, data):
        tile = cls(
            resource=int(data['resource']),
            number=int(data['number'])
        )
        # Reconstruct points from their dictionaries
        tile.points = [Point.from_dict(point_data) for point_data in data['points']]
        tile.robbed = bool(data['robbed'])
        tile.row = int(data['row'])
        tile.column = int(data['column'])
        
        return tile
