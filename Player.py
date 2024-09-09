from Constatnt import LUMBER, BRICK, ORE, WOOL, GRAIN, VILLAGE,\
                    CITY, ROAD, DEV_CARD, VICTORY_POINT, THREE_TO_ONE,\
                    TAKE, GIVE
from Construction import Construction, Dev_card
from Point import Point
from Dictable import Dictable
class Player(Dictable):
    def __init__(self, id) -> None:
        self.id = id
        self.constructions: dict[int:list['Construction']] = {}
        self.constructions_counter: dict[int:int]= {}
        self.resources: dict[int:int] = {}
        self.init_constructions()
        self.init_resources()
        self.army_size = 0
        self.biggest_army = False
        self.longest_road_points = False
        self.dev_card_allowed = True
        self.ports = {LUMBER:False, BRICK:False, ORE:False, WOOL:False, GRAIN:False, THREE_TO_ONE:False}
    
    def init_constructions(self):
        self.constructions[ROAD] = [Construction(ROAD, self.id) for _ in range(15)]
        self.constructions[VILLAGE] = [Construction(VILLAGE, self.id) for _ in range(5)]
        self.constructions[CITY] = [Construction(CITY, self.id) for _ in range(4)]
        self.constructions[DEV_CARD] = []
        self.constructions_counter = {ROAD:15, VILLAGE:5, CITY:4, DEV_CARD:0}
    
    def init_resources(self):
        self.resources = {LUMBER:0, BRICK:0, ORE:0, WOOL:0, GRAIN:0}
    
    def buy(self, constType:int) -> Construction | None:
        if self.constructions_counter[constType] < 1:
            return None
        price = self.constructions[constType][0].price
        for resource, amount in self.resources.items():
            if resource in price.keys() and amount < price[resource]:
                return None
        for resource, amount in self.resources.items():
            if resource in price.keys():
                self.resources[resource] -= price[resource]
        for construction in self.constructions[constType]:
            if not construction.is_placed():
                return construction
        return None
    
    def place_village(self, village: Construction, point: Point, isFirst: bool = False, isSecond: bool = False):
        self.place_construction(village, [point])
        return True
    
    def place_construction(self, construction: Construction, points: list['Point']):
        for point in points:
            point.build_on_point(construction)
        construction.place(points_to_coords(points))
        self.constructions_counter[construction.type_of] -= 1
     
    def place_road(self, road: Construction, point1: Point, point2: Point):
        self.place_construction(road, [point1, point2])
        return True
    
    def place_city(self, city: Construction, point:Point):
        village_to_replace = None
        for village in self.constructions[VILLAGE]:
            if village.coord == points_to_coords([point]):
                village_to_replace = village
                break
        if not village_to_replace:
            return False
        self.constructions_counter[VILLAGE] += 1
        self.constructions_counter[CITY] -= 1
        city.coord = village_to_replace.coord
        village_to_replace.remove()
        point.constructions.remove(village_to_replace)
        point.build_on_point(city)
        return True
    
    def buy_dev_card(self, dev_card: Dev_card):
        for resource, amount in dev_card.price.items():
            if amount > self.resources[resource]:
                return False
        for resource, amount in dev_card.price.items():
            self.resources[resource] -= dev_card.price[resource]
        self.constructions[DEV_CARD].append(dev_card)
        self.constructions_counter[DEV_CARD] += 1
        return True
    
    def accept_propse(self, propse: list[dict[int:int]]):
        give = propse[0]
        take = propse[1]
        for resource in give.keys():
            if self.resources[resource] < give[resource]:
                return False
        for resource in give.keys():
            self.resources[resource] -= give[resource]
        for resource in take.keys():
            self.resources[resource] += take[resource]
        return True
    
    def get_num_of_resources(self):
        return sum([self.resources[key] for key in [LUMBER, BRICK, ORE, WOOL, GRAIN]])
    
    def get_visible_points(self):
        res = 5-self.constructions_counter[VILLAGE]
        res += 2*(4-self.constructions_counter[CITY])
        if self.biggest_army:
            res += 2
        if self.longest_road_points:
            res += 2
        return res
    
    def get_real_points(self):
        return self.get_visible_points() + len([card for card in self.constructions[DEV_CARD] if card.action == VICTORY_POINT])
    
    def drop_resource(self, resource: int):
        if self.resources[resource] > 0:
            self.resources[resource] -= 1
    
    def calc_longest_path(self):
        explored = {}
        for road in self.constructions[ROAD]:
            if road.is_placed():
                for c in road.coord:
                    explored[tuple(c)] = False 
        if len(explored) == 0:
            return 0
        res = []
        for c in explored.keys():
            res.append(self.farest_path(c, self.deep_copy(explored)))
        return max(res)
    
    def farest_path(self, c: tuple[int], explored):
        if explored[c]:
            return 0
        explored[c] = True
        to_explore = []
        for neib in neib_coord(c):
            if neib in explored.keys() and not explored[neib] and self.road_exist_at_position(neib, c):
                to_explore.append(neib)
        if len(to_explore) == 0:
            return 0
        return 1 + max([self.farest_path(c1, self.deep_copy(explored)) for c1 in to_explore])
                    
    def deep_copy(self, dictionary):
        res = {}
        for key, value in dictionary.items():
            res[key] = value
        return res
    
    def road_exist_at_position(self, c1, c2):
        for road in [road for road in self.constructions[ROAD] if road.is_placed()]:
            p1, p2 = tuple(road.coord[0]), tuple(road.coord[1])
            if set([p1, p2]) == set([c1, c2]):
                return True
        return False
    
    def have_road(self, a, b):
        for road in self.constructions[ROAD]:
            if not road.is_placed():
                continue
            if [a, b] == road.coord[0] or [a, b] == road.coord[1]:
                return True
        return False
    
    def find_roads(self, road: Construction):
        res = []
        for playerRoad in self.constructions[ROAD]:
            if road == playerRoad:
                continue
            if road.coord[0] in playerRoad.coord or road.coord[1] in playerRoad.coord:
                res.append(playerRoad)
        return res
    
    def valid_bank_trade(self, propose:dict[bool:dict[int:int]]):
        resource_to_change = sum(propose[TAKE].values())
        for resource, amount in propose[GIVE].items():
            trade_rate = 4
            if self.ports[THREE_TO_ONE]:
                trade_rate = 3
            if self.ports[resource]:
                trade_rate = 2
            if amount % trade_rate != 0 or amount > self.resources[resource]:
                return False
            resource_to_change -= amount//trade_rate
        
        return resource_to_change == 0
    
    def bank_trade(self, propose):
        if not self.valid_bank_trade(propose):
            return False
        for resource in propose[TAKE].keys():
            self.resources[resource] += propose[TAKE][resource]
            self.resources[resource] -= propose[GIVE][resource]
        return False
        
    def end_turn(self):
        for card in self.constructions[DEV_CARD]:
            card.allow_use()
        self.dev_card_allowed = True
    
    def to_dict(self):
        return {
            'id': self.id,
            'constructions': {k: [c.to_dict() for c in v] for k, v in self.constructions.items()},
            'constructions_counter': self.constructions_counter,
            'resources': self.resources,
            'army_size': self.army_size,
            'biggest_army': self.biggest_army,
            'dev_card_allowed': self.dev_card_allowed,
            'ports': self.ports
        }
    
    @classmethod
    def from_dict(cls, data):
        obj = cls(data['id'])
        obj.constructions = {int(k): [Construction.from_dict(c) for c in v] for k, v in data['constructions'].items()}
        obj.constructions_counter = data['constructions_counter']
        obj.resources = data['resources']
        obj.army_size = data['army_size']
        obj.biggest_army = data['biggest_army']
        obj.dev_card_allowed = data['dev_card_allowed']
        obj.ports = data['ports']
        return obj
    
def points_to_coords(points: list['Point']):
    return [[point.row, point.column] for point in points]

def neib_coord(l):
    i, j = l[0], l[1]
    if i % 2 == 0:
        return [tuple([i-1, j]), tuple([i+1,j-1]), tuple([i+1, j+1])]
    return [tuple([i-1, j-1]), tuple([i-1, j+1]), tuple([i+1, j])]