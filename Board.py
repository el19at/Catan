from Tile import Tile
from Point import Point
from Player import Player
import random
DESERT = 0
SEA = 1
LUMBER = 2
BRICK = 3
ORE = 4
WOOL = 5
GRAIN = 6
VILLAGE = 7
CITY = 8
ROAD = 9
DEV_CARD = 10
RED = 11
BLUE = 12
ORANGE = 13
WHITE = 14

TILES_NUMBERS = 2*[i for i in range(3, 7)] + 2*[i for i in range(8, 12)] + [2, 12, 0]
TILES_RESOURCES = [DESERT] + 4*[WOOL, GRAIN, LUMBER] + 3*[BRICK, ORE]
#from Game import TILES_NUMBERS, TILES_RESOURCES, DESERT, SEA, LUMBER, BRICK, ORE, WOOL, GRAIN
class Board:
    def __init__(self, num_of_player: int = 3):
        self.turn = -1
        numbers = TILES_NUMBERS.copy()
        resources = TILES_RESOURCES.copy()
        random.shuffle(numbers)
        random.shuffle(resources)
        self.tiles = [[Tile(resources[0], numbers[0])]]
        for i in range(1, 5):
            newTile = Tile(resources[i], numbers[i])
            self.tiles[0].append(newTile)
        self.init_row(self.tiles[0], numbers[5:], resources[5:], False)
        self.init_row(self.tiles[0], numbers[12:], resources[12:], True)
        self.swap_desert()
        self.sea_padding(7)
        self.ROWS, self.COLUMNS = 2*(len(self.tiles)+1), 2*len(self.tiles[0])
        self.points = {}
        self.init_points()
        self.set_tiles_points()
        self.players = {RED: Player(), BLUE:Player(), ORANGE: Player()}
        if num_of_player == 4:
            self.players[WHITE] = Player()
        for row in self.tiles:
            for tile in row:
                if tile.resurce != SEA:
                    self.set_valid_village_postions(tile)
                    self.set_valid_road_positions(tile)
                    
    def set_valid_village_postions(self, tile: Tile):
        for player in self.players.values():
            for point in tile.points:
                if not point in player.valid_village_postions: 
                    player.valid_village_postions.append(point)

    def set_valid_road_positions(self, tile: Tile):
        for point in tile.points:
            for neib in point.get_neib_points_coord()

    def init_row(self, row: list["Tile"], numbers, resources, up: bool):
        if len(row) <= 3:
            return
        newRow: list["Tile"] = [Tile(resources[0], numbers[0])]
        for i in range(1, len(row)-1):
            newTile = Tile(resources[i], numbers[i])
            newRow.append(newTile)
        if up:
            self.tiles.insert(0, newRow)
        else:
            self.tiles.append(newRow)
        
        self.init_row(newRow, numbers[len(newRow):], resources[len(newRow):], up)
        
    def swap_desert(self):
        desert, zero = None, None
        for row in self.tiles:
            for tile in row:
                if tile.number == 0:
                    zero = tile
                if tile.resurce == DESERT:
                    desert = tile
                if desert != None and zero != None:
                    break
        zero.number = desert.number
        desert.number = 0
    
    def sea_padding(self, size):
        if (size - len(self.tiles)) % 2 != 0:
            raise('Exception padding and board not match')
        row_to_add = (size - len(self.tiles)) // 2
        for _ in range(row_to_add):
            self.tiles.insert(0, [Tile(SEA, 0) for _ in range(size)])
            self.tiles.append([Tile(SEA, 0) for _ in range(size)])
        for row in self.tiles:
            cell_to_add = (size - len(row)) // 2
            for _ in range(cell_to_add):
                row.insert(0, Tile(SEA, 0))
                row.append(Tile(SEA, 0))
            if len(row) < size:
                row.append(Tile(SEA, 0))
                
    def init_points(self):
        for i in range(self.ROWS):
            for j in range(self.COLUMNS):
                self.points[f'({i}, {j})'] = Point(i, j)
    
    def get_point(self, row, column):
        return self.points[f'({row}, {column})'] if f'({row}, {column})' in self.points.keys() else None
        
    def set_tiles_points(self):
        for i, row in enumerate(self.tiles):
            r = i % 2
            for j, tile in enumerate(row):
                tile.points = [self.get_point(i*2, 2*j+1+r),
                               self.get_point(2*i+1, 2*(j+1)+r),
                               self.get_point(2*(i+1), 2*(j+1)+r),
                               self.get_point(i*2+3, 2*j+1+r),
                               self.get_point(2*(i+1), 2*j+r),
                               self.get_point(2*i +1, 2*j+r)]
            
    def to_string(self):
        num_to_rec = {}
        num_to_rec[0] = 'DESERT'
        num_to_rec[1] = 'SEA'
        num_to_rec[2] = 'LUMBER'
        num_to_rec[3] = 'BRICK' 
        num_to_rec[4] = 'ORE'
        num_to_rec[5] = 'WOOL'
        num_to_rec[6] = 'GRAIN'
        res = ''
        for row in self.tiles:
            res += (5-len(row)) * '    '
            for tile in row:
                res += f'({num_to_rec[tile.resurce]}, {tile.number})'
            res += '\n'
        return res

def main():
    b = Board()
    print(b.to_string())

if __name__ == '__main__':
    main()
    #print(b.to_string())