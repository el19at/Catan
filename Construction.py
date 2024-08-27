from Constatnt import LUMBER, BRICK, ORE, WOOL, GRAIN, VILLAGE, CITY, ROAD, DEV_CARD

class Construction():
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
    
    def to_dict(self):
        return {
            'type_of': self.type_of,
            'player_id': self.player_id,
            'coord': self.coord,
            'price': self.price
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data['type_of'], data['player_id'])
        obj.coord = data['coord']
        obj.price = data['price']
        return obj
class Dev_card(Construction):
    def __init__(self, action: int) -> None:
        super().__init__(DEV_CARD, -1)
        self.action = action
        self.is_allowed = False
        self.used = False
    
    def allow_use(self):
        self.is_allowed = True
    
    def set_used(self):
        self.used = True

    def to_dict(self):
        return {
            **super().to_dict(),
            'action': self.action,
            'is_allowed': self.is_allowed,
            'used': self.used
        }
    @classmethod
    def from_dict(cls, data):
        obj = cls(data['action'])
        obj.is_allowed = data['is_allowed']
        obj.used = data['used']
        return obj