from Board import LUMBER, BRICK, ORE, WOOL, GRAIN, VILLAGE, CITY, ROAD, DEV_CARD
from Construction import Constrution
from Point import Point
class Player():
    def __init__(self, id) -> None:
        self.id = id
        self.constructions: dict[int:list['Constrution']] = {}
        self.constructions_counter: dict[int:int]= {}
        self.resources: dict[int:int] = {}
        self.init_constructions()
        self.init_resources()
        self.longest_road_size = 0
        self.army_size = 0
        self.game_point = 0
        self.valid_village_postions: list['Point'] = []
        self.valid_roads_positions: list[set['Point']] = []
        self.dev_card_allowed = True
    
    def init_constructions(self):
        self.constructions[ROAD] = [Constrution(ROAD, self.id) for _ in range(15)]
        self.constructions[VILLAGE] = [Constrution(VILLAGE, self.id) for _ in range(5)]
        self.constructions[CITY] = [Constrution(CITY, self.id) for _ in range(4)]
        self.constructions[DEV_CARD] = []
        self.constructions_counter = {ROAD:15, VILLAGE:5, CITY:4, DEV_CARD:0}
    
    def init_resources(self):
        self.resources = {LUMBER:0, BRICK:0, ORE:0, WOOL:0, GRAIN:0}
    
    def buy(self, constType:int) -> Constrution | None:
        if self.constructions_counter[constType] < 1:
            return None
        price = self.constructions[constType][0].price
        for resource, amount in self.resources.items():
            if amount < price[resource]:
                return None
        for resource, amount in self.resources.items():
            self.resources[resource] -= price[resource]
        for construction in self.constructions[constType]:
            if not construction.isPlaced():
                return construction
        return None
    
    def place_village(self, village: Constrution, point: Point, isFirst: bool = False, isSecond: bool = False):
        if not point in self.valid_village_postions:
            return False
        if not(isFirst or isSecond):
            road_points = []
            for road in self.constructions[ROAD]:
                for road_edge in road.coord:
                    road_points.append(road_edge)
            if not points_to_coords([point])[0] in road_points:
                return False
        self.place_construction(village, point)
    
    def place_construction(self, construction: Constrution, points: list['Point']):
        for point in points:
            point.build_on_point(construction)
        construction.place(points_to_coords(points))
        self.constructions_counter[construction.type_of] -= 1
     
    def place_road(self, road: Constrution, point1: Point, point2: Point):
        if not set(point1, point2) in self.valid_roads_positions:
            return False
        self.place_construction(road, [point1, point2])
        return True
    
    def place_city(self, city: Constrution, point:Point):
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

def points_to_coords(points: list['Point']):
    return [[point.row, point.column] for point in points]    