from Construction import Constrution
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