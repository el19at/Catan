import Construction
from Construction import Constrution, VILLAGE, CITY
class Point():
    def __init__(self, row: int, column: int) -> None:
        self.row: int = row
        self.column: int = column
        self.constructions: list['Constrution'] = []
        
    def build_on_point(self, construction: Constrution):
        self.construction.append(construction)
    
    def get_neib_points_coord(self):
        i, j = self.row, self.column
        if self.row % 2 == 0:
            return [[i-1, j], [i+i,j-1], [i+i, j+1]]
        return [[i-1, j-1], [i-1, j+1], [i+1, j]]
    
    def get_collector(self) -> Constrution:
        for constrution in self.constructions:
            if constrution.type_of in [VILLAGE, CITY]:
                return constrution
        return None
    
    def to_dict(self):
        return {
            'row': self.row,
            'column': self.column,
            'constructions': [c.to_dict() for c in self.constructions]
        }
    
    @classmethod
    def from_dict(cls, data):
        obj = cls(data['row'], data['column'])
        obj.constructions = [Construction.from_dict(c) for c in data['constructions']]
        return obj