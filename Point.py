import Construction
from Construction import Construction, VILLAGE, CITY, ROAD
from Indexable import Indexable
class Point(Indexable):
    def __init__(self, row: int, column: int) -> None:
        self.row: int = row
        self.column: int = column
        self.constructions: list['Construction'] = []
        self.vacant = True
    
    def equal(self, other):
        if isinstance(other, Point):
            return self.row == other.row and self.column == other.column
        return False
    
    def build_on_point(self, construction: Construction):
        self.constructions.append(construction)
        if construction.type_of != ROAD:
            self.vacant + False
    
    def get_neib_points_coord(self):
        i, j = self.row, self.column
        if self.row % 2 == 0:
            return [[i-1, j], [i+1,j-1], [i+1, j+1]]
        return [[i-1, j-1], [i-1, j+1], [i+1, j]]
    
    def get_collector(self) -> Construction:
        for Construction in self.constructions:
            if Construction.type_of in [VILLAGE, CITY]:
                return Construction
        return None
    
    def have_road(self, player_id: int):
        for road in self.constructions:
            if road.type_of == ROAD and road.player_id == player_id:
                return True
        return False
    
    def to_index(self):
        return {
            'type': 'Point',
            'row': self.row,
            'column': self.column
        }
        
    def to_dict(self):
        return {
            'row': self.row,
            'column': self.column,
            'constructions': [construction.to_dict() for construction in self.constructions], 
            'vaccant': self.vacant
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Point':
        point = cls(int(data['row']), int(data['column']))
        point.constructions = [Construction.from_dict(c) for c in data['constructions']]
        point.vacant = bool(data['vacant'])
        return point