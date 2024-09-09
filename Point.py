import Construction
from Construction import Construction, VILLAGE, CITY, ROAD
from Dictable import Dictable
class Point(Dictable):
    def __init__(self, row: int, column: int) -> None:
        self.row: int = row
        self.column: int = column
        self.constructions: list['Construction'] = []
        self.vacant = True
        
    def build_on_point(self, construction: Construction):
        self.constructions.append(construction)
    
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
    
    def to_dict(self):
        return {
            'row': self.row,
            'column': self.column,
            'constructions': [c.to_dict() for c in self.constructions]
        }
    
    @classmethod
    def from_dict(cls, data):
        obj = cls(int(data['row']), int(data['column']))
        obj.constructions = [Construction.from_dict(c) for c in data['constructions']]
        return obj