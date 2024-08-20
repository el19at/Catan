class Tile():
    def __init__(self, resource, number):
        self.resurce = resource
        self.number = number
        self.points = []
        self.robbed = False
        
    def robb(self):
        self.robbed = True
    
    def unrobb(self):
        self.robbed = False