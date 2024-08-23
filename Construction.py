from Board import LUMBER, BRICK, ORE, WOOL, GRAIN, VILLAGE, CITY, ROAD, DEV_CARD
from Player import Player

class Constrution():
    def __init__(self, type_of: int, player_id: int) -> None:
        self.type_of: int = type_of
        self.player_id = player_id
        self.coord: list[list['int']] = []
        self.price = self.init_price()
    
    def place(self, coord: list[list['int']]):
        self.coord = coord
    
    def remove(self):
        if self.type_of == VILLAGE:
            self.coord = []
        
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
    

class Dev_card(Constrution):
    def __init__(self, action: int) -> None:
        super().__init__(DEV_CARD, -1)
        self.action = action
        self.is_allowed = False
        self.used = False
    
    def allow_use(self):
        self.is_allowed = True
