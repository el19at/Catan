import json
from Tile import Tile
from Point import Point
from Player import Player, points_to_coords
from Construction import Constrution, Dev_card
import random
from Constatnt import LUMBER, BRICK, ORE, WOOL, GRAIN, \
                    VILLAGE, CITY, ROAD, DEV_CARD, DESERT, WHITE, RED, \
                    BLUE, ORANGE, KNIGHT, VICTORY_POINT, YEAR_OF_PLENTY,\
                    MONOPOLY, ROADS_BUILD, SEA


TILES_NUMBERS = 2*[i for i in range(3, 7)] + 2*[i for i in range(8, 12)] + [2, 12, 0]
TILES_RESOURCES = [DESERT] + 4*[WOOL, GRAIN, LUMBER] + 3*[BRICK, ORE]
#from Game import TILES_NUMBERS, TILES_RESOURCES, DESERT, SEA, LUMBER, BRICK, ORE, WOOL, GRAIN
class Board:
    def __init__(self, num_of_players: int = 3, point_limit: int = 10):
        self.turn = -1
        self.point_limit = point_limit
        numbers = TILES_NUMBERS.copy()
        resources = TILES_RESOURCES.copy()
        random.shuffle(numbers)
        random.shuffle(resources)
        self.tiles:list[list['Tile']] = [[Tile(resources[0], numbers[0])]]
        for i in range(1, 5):
            newTile = Tile(resources[i], numbers[i])
            self.tiles[0].append(newTile)
        self.robbed_tile: Tile = None
        self.init_row(self.tiles[0], numbers[5:], resources[5:], False)
        self.init_row(self.tiles[0], numbers[12:], resources[12:], True)
        self.swap_desert()
        self.sea_padding(7)
        self.ROWS, self.COLUMNS = 2*(len(self.tiles)+1), 2*len(self.tiles[0])
        self.points = {}
        self.init_points()
        self.set_tiles_points()
        self.num_of_players = num_of_players
        self.players: dict[int:Player] = {RED: Player(RED), BLUE:Player(BLUE), ORANGE: Player(ORANGE)}
        if num_of_players == 4:
            self.players[WHITE] = Player(WHITE)
        for row in self.tiles:
            for tile in row:
                if tile.resource != SEA:
                    self.set_valid_village_postions(tile)
        self.dev_cards = [Dev_card(KNIGHT) for _ in range(14)] \
        +[Dev_card(VICTORY_POINT) for _ in range(5)] \
        +[Dev_card(ROADS_BUILD) for _ in range(2)] \
        +[Dev_card(YEAR_OF_PLENTY) for _ in range(2)] \
        +[Dev_card(MONOPOLY) for _ in range(2)]
        random.shuffle(self.dev_cards)
                    
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
                if tile.resource == DESERT:
                    desert = tile
                if desert != None and zero != None:
                    break
        zero.number = desert.number
        desert.number = 0
        self.robbed_tile = desert
    
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
                row.insert(0, Tile(SEA, 0))
                
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
                if not tile.resource in [DESERT, SEA]:
                    player.resources[tile.resource] += 1
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
                
    def place_road(self, player: Player, point1: Point, point2: Point, freeRoad: bool):
        road: Constrution = None
        if freeRoad:
            for playerRoad in player.constructions[ROAD]:
                if not playerRoad.is_placed():
                    road = playerRoad
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
        longest_path = max([gamePlayer.longest_path() for gamePlayer in self.other_payers(player)])
        if longest_path < player.longest_path():
            for gamePlayer in self.other_payers(player):
                gamePlayer.longest_road = False
            player.longest_path = True
        return True
    
    def place_city(self, player:Player, point: Point):
        city = player.buy(CITY)
        if not city:
            return False
        return player.place_city(city, point)
    
    def give_recources(self, dice_sum: int):
        for tile in self.tiles:
            if tile.number != dice_sum or tile.is_robbed():
                continue
            for point in tile.points:
                collector = point.get_collector()
                if not collector:
                    continue
                self.players[collector.player_id].resources[tile.recource] += (1 if collector.type_of == VILLAGE else 2)
    
    def buy_dev_card(self, player: Player):
        if len(self.dev_cards) < 1:
            return
        if player.buy_dev_card(self.dev_cards[0]):
            del self.dev_cards[0]
    
    def end_turn(self, player: Player):
        for dev_card in player.constructions[DEV_CARD]:
            dev_card.allow_use()
        self.turn = RED + ((self.turn+1) % self.num_of_players) 
       
    def is_sea_point(self, point: Point):
        return all(x == SEA for x in [tile.resource for tile in self.get_tiles_of_point(point)])
    
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
                res += f'({num_to_rec[tile.resource]}, {tile.number})'
            res += '\n'
        return res
    
    def use_dev_card(self, player: Player, card: Dev_card):
        if card.action == VICTORY_POINT:
            return False
        if not (player.dev_card_allowed and card.allow_use and not card.used):
            return False
        card.set_used()
        return True
    
    def use_year_of_plenty(self, player: Player, first_resource: int, second_resource: int):
        player.resources[first_resource] += 1
        player.resources[second_resource] += 1
    
    def use_monopoly(self, player: Player, resource: int):
        get = 0
        for gamePlayer in self.players:
            get += gamePlayer.resources[resource]
            gamePlayer.resources[resource] = 0
        player.resources[resource] = get
    
    def use_road_building(self, player: Player, location1: list[list[int]], location2:list[list[int]]):
        self.place_road(player, location1[0], location1[1], True)
        self.place_road(player, location2[0], location2[1], True)
    
    def use_knight(self, player: Player, tile: Tile, playerToRobb: Player, fromDice:bool = True):
        self.robbed_tile.unrobb()
        self.robbed_tile = tile
        tile.robb()
        if playerToRobb.get_num_of_resources() > 0:
            resource = random.choice([key for key in playerToRobb.resources.keys() if playerToRobb.resources[key]>0])
            playerToRobb.resources[resource] -= 1
            player.resources[resource] += 1
        if not fromDice:
            player.army_size += 1
            biggest_army = max([gamePlayer.army_size for gamePlayer in self.players])
            if player.army_size >= 3:
                if player.army_size > biggest_army:
                    for gamePlayer in self.players:
                        gamePlayer.biggest_army = False
                    player.biggest_army = True
    
    def get_players_on_tile(self, tile: Tile):
        players_id: list[int] = []
        for point in tile.points:
            for construction in point.constructions:
                if construction.type_of in [CITY, VILLAGE]:
                    if not construction.player_id in players_id:
                        players_id.append(players_id)
        return [self.players[player_id] for player_id in players_id]
        
    def other_payers(self, player: Player):
        return [gamePlayer for gamePlayer in self.players.values() if gamePlayer != player]
    
    def win(self):
        return max([player.get_real_points() for player in self.players.values()]) > self.point_limit
    
    def to_dict(self):
        return {
            'turn': self.turn,
            'point_limit': self.point_limit,
            'tiles': [[tile.to_dict() for tile in row] for row in self.tiles],
            'robbed_tile': self.robbed_tile.to_dict() if self.robbed_tile else None,
            'points': {str(k): v.to_dict() for k, v in self.points.items()},
            'num_of_players': self.num_of_players,
            'players': {k: v.to_dict() for k, v in self.players.items()},
            'dev_cards': [dev_card.to_dict() for dev_card in self.dev_cards]
        }
    def board_to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)
    
    @classmethod
    def from_dict(cls, data):
        board = cls(data['num_of_players'], data['point_limit'])
        board.turn = data['turn']
        board.tiles = [[Tile.from_dict(tile) for tile in row] for row in data['tiles']]
        board.robbed_tile = Tile.from_dict(data['robbed_tile']) if data['robbed_tile'] else None
        board.points = {int(k): Point.from_dict(v) for k, v in data['points'].items()}
        board.players = {int(k): Player.from_dict(v) for k, v in data['players'].items()}
        board.dev_cards = [Dev_card.from_dict(card) for card in data['dev_cards']]
        return board

def json_to_board(json_string: str) -> Board:
    data = json.loads(json_string)
    return Board.from_dict(data)
    