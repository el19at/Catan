from Point import Point
class Tile():
    def __init__(self, resource, number):
        self.resource = resource
        self.number = number
        self.points: list['Point'] = []
        self.robbed = False
        
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
        obj = cls(data['resource'], data['number'])
        obj.points = [Point.from_dict(p) for p in data['points']]
        obj.robbed = data['robbed']
        return obj