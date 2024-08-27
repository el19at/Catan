import pygame
from Board import Board, Point, json_to_board
import math
from Constatnt import LUMBER, BRICK, ORE, WOOL, GRAIN, \
                    VILLAGE, CITY, ROAD, DEV_CARD, DESERT, WHITE, RED, \
                    BLUE, ORANGE, KNIGHT, VICTORY_POINT, YEAR_OF_PLENTY,\
                    MONOPOLY, ROADS_BUILD, SEA

COLORS = {SEA: pygame.Color('aqua'), GRAIN: pygame.Color('gold2'), BRICK: pygame.Color('brown1'), WOOL: pygame.Color('chartreuse'), LUMBER:pygame.Color('darkgreen'), ORE:pygame.Color('grey63'), DESERT:pygame.Color('lemonchiffon1')}
DEBUG = False
class Game():
    def __init__(self, num_of_players: int = 3, point_limit: int = 10, json: str=""):
        pygame.init()
        self.board = None
        if json != "":
            self.board = json_to_board(json)
        else:
            self.board = Board(num_of_players, point_limit)
        self.tile_centers = {}
        self.intersections = {}
        self.main_screen = pygame.display.set_mode((1000, 550))
        self.main_screen.fill(pygame.Color('white'))
        self.tile_size = 50
        self.draw_tiles(0, 0, self.tile_size)
    
    def print_intersections(self):
        for key, value in self.intersections.items():
            if value:
                print(f'{key}: ({value.row}, {value.column})')
            else:
                print(f'{key}: None')
        
    def draw_hexagon(self, color, center, edge_length, num_to_display: int = 0, txt = ""):
        # Convert rotation angle to radians
        rotation_radians = math.radians(30)
        
        # Calculate the vertices of the rotated hexagon
        points = []
        for i in range(6):
            angle = math.radians(60 * i) + rotation_radians
            x = center[0] + edge_length * math.cos(angle)
            y = center[1] + edge_length * math.sin(angle)
            x, y = round(x), round(y)
            n = len(self.get_tile_by_click(center).points)
            intersectionToAdd = self.get_tile_by_click(center).points[(i+2)%n]
            if not intersectionToAdd in self.intersections.values():
                self.intersections[(x, y)] = intersectionToAdd
            points.append((x, y))
        pygame.draw.polygon(self.main_screen, color, points)
        
        if num_to_display > 1 and not DEBUG:
            if not pygame.font.get_init():
                pygame.font.init()
            font = pygame.font.SysFont(None, 24)
            text_surface = font.render(str(num_to_display), True, pygame.Color('black'))
            text_rect = text_surface.get_rect()
            text_rect.center = center
            self.main_screen.blit(text_surface, text_rect)
        if DEBUG:
            if not pygame.font.get_init():
                pygame.font.init()
            font = pygame.font.SysFont(None, 24)
            text_surface = font.render(txt, True, pygame.Color('black'))
            text_rect = text_surface.get_rect()
            text_rect.center = center
            self.main_screen.blit(text_surface, text_rect)
    
    def coord_from_hex_point(self, center, index):
        i, j = self.get_tile_pos_by_click(center)
        r = i % 2
        x, y = 0, 0
        if index == 0:
            x, y = 2*(i+1), 2*(j+1)+r
        if index == 1:
            x, y = 2*i+3, 2*j+r+1
        if index == 2:
            x, y = 2*i+1, 2*j+r
        if index == 3:
            x, y = 2*i+1, 2*j+r
        if index == 4:
            x, y = i*2, 2*j+1+r 
        if index == 5:
            x, y = 2*i+1, 2*(j+1)+r
        return self.board.get_point(x, y)
    
    def write_text(self, center, txt: str):
        if not pygame.font.get_init():
            pygame.font.init()
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(txt, True, pygame.Color('black'))
        text_rect = text_surface.get_rect()
        text_rect.center = center
        self.main_screen.blit(text_surface, text_rect)
        
    def draw_tiles(self, x, y, c):
        for i, row in enumerate(self.board.tiles):
            moving = (3**0.5)*c if i%2==1 else 0.5*(3**0.5)*c
            for j, tile in enumerate(row):
                center = (j*c*(3**0.5)+moving+x, c*(1+(3*i)/2)+y)
                center_round = (round(center[0]), round(center[1]))
                self.tile_centers[center_round] = (i, j)
                self.draw_hexagon(pygame.Color('white'), center_round, c)
                if DEBUG:
                    self.draw_hexagon(COLORS[tile.resurce], center_round, c-2, 0, f'{center_round}')
                else:
                    self.draw_hexagon(COLORS[tile.resource], center_round, c-2, tile.number, "")
    
    def handle_click(self, pos):
        tile_pos = self.get_tile_pos_by_click(pos)
        intersection = self.get_intersection_by_click(pos)
        if tile_pos[0]>=0:
            print(tile_pos)
        if intersection:
            print(f'{intersection.row}, {intersection.column}')
        
    def get_tile_pos_by_click(self, pos):
        c = self.tile_size
        for screen_pos, array_pos in self.tile_centers.items():
            if distance(pos, screen_pos) <= c*(3/4)**0.5:
                return (array_pos[0], array_pos[1])
        return (-1, -1)
    
    def get_tile_by_click(self, pos):
        x, y = self.get_tile_pos_by_click(pos)
        if x>=0:
            return self.board.tiles[x][y]
        return None
    
    def get_intersection_by_click(self, click) -> Point:
        for pos, point in self.intersections.items():
            if distance(pos, click) < self.tile_size//4:
                return point
        return None
                
    def start(self):
        # Update the display
        pygame.display.flip()

        # Keep the window open until closed by the user
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

        pygame.quit()    

def distance(pos1, pos2):
    return ((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)**0.5

def main():
    game = Game()
    print(game.board.board_to_json())
    game.start()
    
if __name__ == '__main__':
    main()