from Board import LUMBER, BRICK, ORE, WOOL, GRAIN, VILLAGE, CITY, ROAD, DEV_CARD
from Construction import Constrution
from Point import Point
class Player():
    def __init__(self) -> None:
        self.constructions = {}
        self.constructions_counter = {}
        self.resources = {}
        self.init_constructions()
        self.init_resources()
        self.longest_road_size = 0
        self.army_size = 0
        self.game_point = 0
        self.valid_village_postions: list['Point'] = []
        self.valid_roads_positions: list[set['Point']] = []
    
    def init_constructions(self):
        self.constructions[ROAD] = [Constrution(ROAD, self) for _ in range(15)]
        self.constructions[VILLAGE] = [Constrution(VILLAGE, self) for _ in range(5)]
        self.constructions[CITY] = [Constrution(CITY, self) for _ in range(4)]
        self.constructions[DEV_CARD] = []
        self.constructions_counter = {ROAD:15, VILLAGE:5, CITY:4, DEV_CARD:0}
    
    def init_resources(self):
        self.resources = {LUMBER:0, BRICK:0, ORE:0, WOOL:0, GRAIN:0}
        
    