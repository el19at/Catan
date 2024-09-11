import json
from Indexable import Indexable
from Tile import Tile
from Point import Point
from Player import Player, points_to_coords
from Construction import Construction, Dev_card
import random
from Constatnt import LUMBER, BRICK, ORE, WOOL, GRAIN, \
                    VILLAGE, CITY, ROAD, DEV_CARD, DESERT, WHITE, RED, \
                    BLUE, ORANGE, KNIGHT, VICTORY_POINT, YEAR_OF_PLENTY,\
                    MONOPOLY, ROADS_BUILD, SEA, TILES_NUMBERS, TILES_RESOURCES,\
                    PHASE_FIRST_VILLAGE, PHASE_SECOND_VILLAGE, PHASE_INGAME

#from Game import TILES_NUMBERS, TILES_RESOURCES, DESERT, SEA, LUMBER, BRICK, ORE, WOOL, GRAIN
class Board(Indexable):
    def __init__(self, num_of_players: int = 3, point_limit: int = 10):
        self.turn = -1
        self.point_limit = point_limit
        numbers = TILES_NUMBERS.copy()
        resources = TILES_RESOURCES.copy()
        self.village_locations: list[Point] = []
        self.road_locations: list[set[Point]] = []
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
        for i, row in enumerate(self.tiles):
            for j, tile in enumerate(row):
                tile.set_index(i, j)
        self.ROWS, self.COLUMNS = 2*(len(self.tiles)+1), 2*len(self.tiles[0])
        self.points = {}
        self.init_points()
        self.set_tiles_points()
        self.num_of_players = num_of_players
        self.dice_rolled: bool = True
        self.players: dict[int:Player] = {RED: Player(RED), BLUE:Player(BLUE), ORANGE: Player(ORANGE)}
        if num_of_players == 4:
            self.players[WHITE] = Player(WHITE)
        for row in self.tiles:
            for tile in row:
                if tile.resource != SEA:
                    self.set_valid_village_postions(tile)
                    self.set_valid_road_positions(tile)
        self.dev_cards: list[Dev_card] = [Dev_card(KNIGHT) for _ in range(14)] \
        +[Dev_card(VICTORY_POINT) for _ in range(5)] \
        +[Dev_card(ROADS_BUILD) for _ in range(2)] \
        +[Dev_card(YEAR_OF_PLENTY) for _ in range(2)] \
        +[Dev_card(MONOPOLY) for _ in range(2)]
        random.shuffle(self.dev_cards)
        for i, card in enumerate(self.dev_cards):
            card.i = i
        self.dev_card_index = 0
        self.game_phase = PHASE_FIRST_VILLAGE
                    
    def set_valid_village_postions(self, tile: Tile):
        for point in tile.points:
            if not point in self.village_locations:
                self.village_locations.append(point)
    
    def set_valid_road_positions(self, tile: Tile):
        for i in range(1, len(tile.points)):
            toAdd = set([tile.points[i-1], tile.points[i]])
            if not toAdd in self.road_locations:
                self.road_locations.append(toAdd)
        if not set([tile.points[0], tile.points[-1]]) in self.road_locations:
            self.road_locations.append(set([tile.points[0], tile.points[-1]]))
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
    
    def get_point_board(self, row, column) -> Point:
        return self.points[f'({row}, {column})'] if f'({row}, {column})' in self.points.keys() else None
        
    def set_tiles_points(self):
        for i, row in enumerate(self.tiles):
            r = i % 2
            for j, tile in enumerate(row):
                tile.points = [self.get_point_board(i*2, 2*j+1+r),
                               self.get_point_board(2*i+1, 2*(j+1)+r),
                               self.get_point_board(2*(i+1), 2*(j+1)+r),
                               self.get_point_board(i*2+3, 2*j+1+r),
                               self.get_point_board(2*(i+1), 2*j+r),
                               self.get_point_board(2*i +1, 2*j+r)]
    
    def get_tiles_of_point(self, point: Point) -> list['Tile']:
        res = []
        for row in self.tiles:
            for tile in row:
                if point in tile.points:
                    res.append(tile)
        return res
            
    def roll_dices(self):
        return [random.randint(1, 6), random.randint(1,6)]
    
    def place_village(self, point: Point, isFirst: bool = False, isSecond: bool = False):
        player: Player = self.players[self.turn]
        village: Construction = None
        if isFirst or isSecond:
            village = player.constructions[VILLAGE][-1 if isFirst else -2]
        else:
            village  = player.buy(VILLAGE)
            if village == None:
                return False
        if not point in self.valid_village_positions(player.id):
            return False
        player.place_village(village, point, isFirst, isSecond)        
        if isSecond:
            tiles = self.get_tiles_of_point(point)
            for tile in tiles:
                if not tile.resource in [DESERT, SEA]:
                    player.resources[tile.resource] += 1
        point.vacant = False
        for coord in point.get_neib_points_coord():
            i, j = coord
            self.get_point_board(i, j).vacant = False
        return True
    
    def place_road(self, point1: Point, point2: Point, freeRoad: bool):
        player: Player = self.players[self.turn]
        road: Construction = None
        if freeRoad:
            for playerRoad in player.constructions[ROAD]:
                if not playerRoad.is_placed():
                    road = playerRoad
                    break
        else:
            road = player.buy(ROAD)
        if not road:
            return False
        if not set([point1, point2]) in self.road_locations:
            return False
        if not set([point1, point2]) in self.valid_road_positions(player.id):
            return False
        player.place_road(road, point1, point2)
        self.road_locations.remove(set([point1, point2]))
        longest_path = max([gamePlayer.calc_longest_path() for gamePlayer in self.other_players(player)])
        if longest_path < player.calc_longest_path():
            for gamePlayer in self.other_players(player):
                gamePlayer.longest_road = False
            player.longest_path = True
        return True
    
    def place_city(self, point: Point):
        player: Player = self.players[self.turn]
        city = player.buy(CITY)
        if not city:
            return False
        return player.place_city(city, point)
    
    def give_recources(self, dice_sum: int):
        if self.dice_rolled:
            return
        for tile in self.tiles:
            if tile.number != dice_sum or tile.is_robbed():
                continue
            for point in tile.points:
                collector = point.get_collector()
                if not collector:
                    continue
                self.players[collector.player_id].resources[tile.recource] += (1 if collector.type_of == VILLAGE else 2)
        self.dice_rolled = True
    
    def player_dev_cards(self, player: Player):
        return [card for card in self.dev_cards if card.player_id == player.id]    
        
    def buy_dev_card(self):
        player: Player = self.players[self.turn]
        if self.dev_card_index >= len(self.dev_cards):
            return
        if player.buy_dev_card(self.dev_cards[self.dev_card_index]):
            self.dev_card_index += 1
    
    def get_real_points(self, player: Player):
        return player.get_visible_points() + len([card for card in self.dev_cards if card.action == VICTORY_POINT and card.player_id==player.id])
    
    def end_turn(self):
        player: Player = self.players[self.turn]
        player.end_turn()
        for dev_card in self.dev_cards[:self.dev_card_index]:
            dev_card.allow_use()
        self.turn = RED + ((self.turn + (-1 if self.game_phase == PHASE_SECOND_VILLAGE else 1)) % self.num_of_players) 
        if self.game_phase == PHASE_INGAME:
            self.dice_rolled = False
            
    def is_sea_point(self, point: Point):
        return all(x == SEA for x in [tile.resource for tile in self.get_tiles_of_point(point)])
    
    def get_construction_position(self, player: Player, type_of: int):
        return [construction.coord for construction in player.constructions[type_of]]
    
    def use_dev_card(self, card: Dev_card):
        player: Player = self.players[self.turn]
        if not card or card.action == VICTORY_POINT:
            return False
        if not (player.dev_card_allowed and card.allow_use and not card.used):
            return False
        card.set_used()
        return True
    
    def use_year_of_plenty(self, first_resource: int, second_resource: int):
        player = self.players[self.turn]
        player.resources[first_resource] += 1
        player.resources[second_resource] += 1
    
    def use_monopoly(self, resource: int):
        player: Player = self.players[self.turn]
        get = 0
        for gamePlayer in self.players.values():
            get += gamePlayer.resources[resource]
            gamePlayer.resources[resource] = 0
        player.resources[resource] = get
    
    
    def robb(self, tile: Tile, playerToRobb: Player = None, fromDice:bool = True):
        player = self.players[self.turn]
        if tile.eq(self.robbed_tile):
            return False
        self.robbed_tile.unrobb()
        self.robbed_tile = tile
        tile.robb()
        if playerToRobb and playerToRobb.get_num_of_resources() > 0:
            resource = random.choice([key for key in playerToRobb.resources.keys() if playerToRobb.resources[key]>0])
            playerToRobb.resources[resource] -= 1
            player.resources[resource] += 1
        if not fromDice:
            player.army_size += 1
            biggest_army = max([gamePlayer.army_size for gamePlayer in self.players.values()])
            if player.army_size >= 3:
                if player.army_size > biggest_army:
                    for gamePlayer in self.players:
                        gamePlayer.biggest_army = False
                    player.biggest_army = True
        return True
    
    def get_players_on_tile(self, tile: Tile):
        players_id: list[int] = []
        for point in tile.points:
            for construction in point.constructions:
                if construction.type_of in [CITY, VILLAGE]:
                    if not construction.player_id in players_id:
                        players_id.append(players_id)
        return [self.players[player_id] for player_id in players_id]
        
    def other_players(self, player: Player):
        return [gamePlayer for gamePlayer in self.players.values() if gamePlayer != player]
    
    def win(self):
        return max([player.get_real_points() for player in self.players.values()]) >= self.point_limit
    
    def valid_road_positions(self, player_id: int):
        player = self.players[player_id]
        res  = []
        for type_of, constructionsList in player.constructions.items(): 
            if type_of == DEV_CARD:
                continue
            for construction in constructionsList:
                for coord in construction.coord:
                    point = self.get_point_board(coord[0], coord[1])
                    for neib_coord in point.get_neib_points_coord():
                        toAdd = set([point, self.get_point_board(neib_coord[0], neib_coord[1])])
                        if not toAdd in res and toAdd in self.road_locations:
                            res.append(toAdd)
        return res
        
    def valid_village_positions(self, player_id: int):
        player = self.players[player_id]
        if player.get_real_points() < 2:
            return [point for point in self.village_locations if point.vacant]
        return [point for point in self.village_locations if point.vacant and point.have_road(player.id)]
    
    def get_construction(self, index)->Construction:
        type_of = int(index['type_of'])
        player_id = int(index['player_id'])
        i = int(index['i'])
        return self.players[player_id][type_of][i]
    
    def get_dev_card(self, index)->Dev_card:
        return self.dev_cards[int(index['i'])]
    
    def get_player(self, index) -> Player:
        return self.players[int(index['id'])]
    
    def get_point(self, index) -> Point:
        i = int(index['row'])
        j = int(index['column'])
        return self.get_point_board((i, j))
    
    def get_tile(self, index) -> Tile:
        i = int(index['row'])
        j = int(index['column'])
        return self.tiles[i][j]
    
    def get_object(self, index):
        if index['type'] == 'Construction':
            return self.get_construction(index)
        if index['type'] == 'Dev_card':
            return self.get_dev_card(index)
        if index['type'] == 'Player':
            return self.get_player(index)
        if index['type'] == 'Point':
            return self.get_point(index)
        if index['type'] == 'Tile':
            return self.get_tile(index)

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
        board = cls(int(data['num_of_players']), int(data['point_limit']))
        board.turn = int(data['turn'])
        board.tiles = [[Tile.from_dict(tile) for tile in row] for row in data['tiles']]
        board.robbed_tile = Tile.from_dict(data['robbed_tile']) if data['robbed_tile'] else None
        board.points = {tuple(map(int, k.strip('()').split(', '))): Point.from_dict(v) for k, v in data['points'].items()}
        board.players = {int(k): Player.from_dict(v) for k, v in data['players'].items()}
        board.dev_cards = [Dev_card.from_dict(card) for card in data['dev_cards']]
        return board

def json_to_board(data):
    if isinstance(data, str):
        data = json.loads(data)
    return Board.from_dict(data)
    