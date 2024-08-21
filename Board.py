from Tile import Tile
from Point import Point
from Player import Player, points_to_coords
from Construction import Constrution, Dev_card
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
KNIGHT = 15
VICTORY_POINT = 16
MONOPOLY = 17
ROADS_BUILD = 18
YEAR_OF_PLENTY = 19

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
        self.dev_cards = [Dev_card(DEV_CARD, KNIGHT) for _ in range(14)]+[Dev_card(DEV_CARD, VICTORY_POINT) for _ in range(5)]+[Dev_card(DEV_CARD, ROADS_BUILD) for _ in range(2)]+[Dev_card(DEV_CARD, YEAR_OF_PLENTY) for _ in range(2)]+[Dev_card(DEV_CARD, MONOPOLY) for _ in range(2)]
                    
    def set_valid_village_postions(self, tile: Tile):
        for player in self.players.values():
            for point in tile.points:
                if not point in player.valid_village_postions: 
                    player.valid_village_postions.append(point)


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
    
    def get_tiles_of_point(self, point: Point) -> list['Tile']:
        return [tile for tile in self.tiles if point in tile.points]
            
    def roll_dices(self):
        return [random.randint(1, 6), random.randint(1,6)]
    
    def place_village(self, player: Player, point: Point, isFirst: bool = False, isSecond: bool = False):
        village: Constrution = None
        if isFirst or isSecond:
            village = player.constructions[VILLAGE][-1 if isFirst else -2]
        else:
            village  = player.buy(VILLAGE)
            if village == None:
                return False
        player.place_village(point)
        tiles = self.get_tiles_of_point(point)
        self.update_valid_road_positions(player, point)
        neib_points = [self.get_point(coord[0], coord[1]) for coord in point.get_neib_points_coord() if self.get_point(coord[0], coord[1])]
        for playerGame in self.players:
            if point in playerGame.valid_village_postions:
                playerGame.valid_village_postions.remove(point)
            for neib_point in neib_points:
                if neib_point in playerGame.valid_village_postions:
                    playerGame.valid_village_postions.remove(neib_point)
        if isSecond:
            for tile in tiles:
                if not tile.resurce in [DESERT, SEA]:
                    player.resources[tile.resurce] += 1
        return True
    
    def update_valid_road_positions(self, player:Player, point: Point):
        neib_points = [self.get_point(coord[0], coord[1]) for coord in point.get_neib_points_coord() if self.get_point(coord[0], coord[1])]
        for neib_point in neib_points:
            if not self.is_sea_point(neib_point):
                road_poses = [] 
                for gamePlayer in self.players:
                    for pos in self.get_construction_position(gamePlayer, ROAD):
                        road_poses.append(set(pos))
                if not set(point, neib_point) in road_poses:
                    player.valid_roads_positions.append((point, neib_points))
                
    def place_road(self, player: Player, point1: Point, point2: Point, isStart: bool):
        road: Constrution = None
        if isStart:
            road = player.constructions[ROAD][-2 if player.constructions[ROAD][-1].isPlaced() else -2]
        else:
            road = player.buy(ROAD)
            if not road:
                return False
        player.place_road(road, point1, point2)
        for gamePlayer in self.players.values():
            if set(point1, point2) in gamePlayer.valid_roads_positions:
                gamePlayer.valid_roads_positions.remove(set(point1, point2))
        for point in [point1, point2]:
            self.update_valid_road_positions(player, point)
        return True
    
    def place_city(self, player:Player, point: Point):
        city = player.buy(CITY)
        if not city:
            return False
        return player.place_city(city, point)
    
    def give_recources(self, dice_sum: int):
        for tile in self.tiles:
            if tile.number != dice_sum:
                continue
            for point in tile.points:
                collector = point.get_collector()
                if not collector:
                    continue
                self.players[collector.player_id].resources[tile.recource] += (1 if collector.type_of == VILLAGE else 2)
        
    def is_sea_point(self, point: Point):
        return all(x == SEA for x in [tile.resurce for tile in self.get_tiles_of_point(point)])
    
    def get_construction_position(self, player: Player, type_of: int):
        return [construction.coord for construction in player.constructions[type_of]]
    
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