from Board import LUMBER, BRICK, ORE, WOOL, GRAIN, VILLAGE, CITY, ROAD, DEV_CARD
from Player import Player

class Constrution():
    def __init__(self, type_of: int, player: Player) -> None:
        self.type_of: int = type_of
        self.player: int = player
        self.coord: list[list['int']] = []
        self.price = self.init_price()
    
    def place(self, coord: list[list['int']]):
        self.coord = coord
    
    def is_placed(self):
        return len(self.coord)>0
    
    def init_price(self):
        if self.type_of == VILLAGE:
            return {LUMBER:1, BRICK:1, WOOL:1, GRAIN:1}
        if self.type_of == CITY:
            return {ORE:3, GRAIN:2}
        if self.type_of == ROAD:
            return {LUMBER:1, BRICK:1}
        if self.type_of == DEV_CARD:
            return {ORE:1, WOOL:1, GRAIN:1}