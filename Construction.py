from Constatnt import LUMBER, BRICK, ORE, WOOL, GRAIN, VILLAGE, CITY, ROAD, DEV_CARD, KNIGHT, VICTORY_POINT, MONOPOLY, ROADS_BUILD, YEAR_OF_PLENTY, convert_to_int_dict, convert_to_int_list_of_lists
from Indexable import Indexable

class Construction(Indexable):
    def __init__(self, type_of: int, player_id: int, i: int) -> None:
        self.type_of: int = type_of
        self.player_id = player_id
        self.i = i
        self.coord: list[list['int']] = []
        self.price = self.init_price()
    
    def equal(self, other: object) -> bool:
        if isinstance(other, Construction):
            return self.player_id == other.player_id and self.type_of == other.type_of and self.coord == other.coord
        return False
    
    def place(self, coord: list[list['int']]):
        self.coord = deep_copy(coord)
    
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
    
    def to_index(self):
        return {
            'type' : 'Construction',
            'type_of': self.type_of,
            'player_id': self.player_id,
            'i' : self.i
        }
    def to_dict(self):
        return {
            'type_of': self.type_of,
            'player_id': self.player_id,
            'i': self.i,
            'coord': self.coord,
            'price': self.price,
        }
        
    @classmethod
    def from_dict(cls, data):
        obj = cls(int(data['type_of']), int(data['player_id']), int(data['i']))
        obj.coord = convert_to_int_list_of_lists(data['coord'])
        obj.price = convert_to_int_dict(data['price'])
        return obj

def deep_copy(l):
    res = []
    for a in l:
        toAppend = []
        for b in a:
            toAppend.append(b)
        res.append(toAppend)
    return res
class Dev_card(Construction):
    def __init__(self, action: int, i: int = -1, player_id: int = -1) -> None:
        super().__init__(DEV_CARD, player_id, i)
        self.action = action
        self.is_allowed = False
        self.used = False
    
    def allow_use(self):
        self.is_allowed = True
    
    def set_used(self):
        self.used = True

    def usable(self):
        if self.action == VICTORY_POINT:
            return False
        if self.used:
            return False
        return self.is_allowed
    
    def get_action_str(self):
        if self.action == KNIGHT:
            return 'knight'
        if self.action == VICTORY_POINT:
            return 'victory point'
        if self.action == YEAR_OF_PLENTY:
            return 'year of plenty'
        if self.action == MONOPOLY:
            return 'monopoly'
        if self.action == ROADS_BUILD:
            return 'roads build'
    
    def to_index(self):
        return {
            'type': 'Dev_card',
            'i': self.i
        }
    
    def to_dict(self):
        a = super().to_dict()
        a['action'] = self.action
        a['is_alowed'] = self.is_allowed
        a['used'] = self.used
        return a

    @classmethod
    def from_dict(cls, data):
        obj = cls(int(data['action']), int(data['i']), int(data['player_id']))
        obj.is_allowed = bool(data['is_alowed'])
        obj.used = bool(data['used'])
        return obj