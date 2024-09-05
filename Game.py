import socket
import pygame
from Board import Board, Point, json_to_board, Player
import math
import json
from Dictable import Dictable
from Constatnt import LUMBER,BRICK, ORE, WOOL, GRAIN, \
                    VILLAGE, CITY, ROAD, DEV_CARD, DESERT, WHITE, RED, \
                    BLUE, ORANGE, KNIGHT, VICTORY_POINT, YEAR_OF_PLENTY,\
                    MONOPOLY, ROADS_BUILD, SEA, PHASE_FIRST_ROLL, PHASE_FIRST_VILLAGE, PHASE_SECOND_VILLAGE, PHASE_INGAME

COLORS = {
    SEA: pygame.Color('aqua'),
    GRAIN: pygame.Color('gold2'),
    BRICK: pygame.Color('brown1'),
    WOOL: pygame.Color('chartreuse'),
    LUMBER:pygame.Color('darkgreen'),
    ORE:pygame.Color('grey63'),
    DESERT:pygame.Color('lemonchiffon1'),
    RED:pygame.Color('red'),
    BLUE: pygame.Color('blue'),
    ORANGE: pygame.Color('orange'),
    WHITE: pygame.Color('antiquewhite1'),
    KNIGHT: pygame.Color('gray49')
    }
DEBUG = False
class Game():
    def __init__(self, player_id,num_of_players: int = 3, point_limit: int = 10, board: Board=None, client:socket = None):
        pygame.init()
        pygame.display.set_caption('Catan')
        self.board = None
        if  board:
            self.board = board
        else:
            self.board = Board(num_of_players, point_limit)
        self.player_id = player_id
        self.client: socket = None
        if client:
            self.client = client
        self.tile_centers = {}
        self.intersections = {}
        self.main_screen = pygame.display.set_mode((970, 550))
        self.main_screen.fill(pygame.Color('white'))
        self.tile_size = 50
        self.draw_tiles(0, 0, self.tile_size)
        self.buttons = []
        self.build_village_mode = False
        self.build_road_mode = False
        self.build_city_mode = False
        self.force_build_road_mode = False
        self.game_phase = PHASE_FIRST_ROLL
        self.clicked_point: Point = None
        self.trade_mode = True
        self.update()
        # for tests only
        self.board.players[self.player_id].resources[GRAIN] = 30
        self.board.players[self.player_id].resources[ORE] = 30
        self.board.players[self.player_id].resources[LUMBER] = 30
        self.board.players[self.player_id].resources[BRICK] = 30
        self.board.players[self.player_id].resources[WOOL] = 30
        
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
    
    def write_text(self, center, txt: str, size: int=24):
        if not pygame.font.get_init():
            pygame.font.init()
        font = pygame.font.SysFont(None, size)
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
    
    def intersection_gui_to_logical(self, intersection)->Point:
        return self.intersections[intersection]
    
    def intersection_logical_to_gui(self, point: Point):
        for pos, logicalPoint in self.intersections.items():
            if point == logicalPoint:
                return pos
          
    def intersection_coord_to_gui(self, coord):
        if (type(coord[0])== type([])):
            coord = coord[0]
        for pos, logicalPoint in self.intersections.items():
            if logicalPoint and coord[0] == logicalPoint.row and coord[1] == logicalPoint.column:
                return pos
          
    def draw_filled_rectangle(self, color, position, width, height):
        rect = pygame.Rect(position[0], position[1], width, height)
        pygame.draw.rect(self.main_screen, color, rect)
    
    def draw_rectangle(self, inner_color, border_color, position, width, height, border_size):
        self.draw_filled_rectangle(border_color, position, width, height)
        inner_position = (position[0]+border_size, position[1]+border_size)
        self.draw_filled_rectangle(inner_color, inner_position, width-2*border_size, height-2*border_size)
    
    def draw_dashboard(self):
        
        self.draw_rectangle(pygame.Color('white'), pygame.Color('black'), (660, 10), 300, 530, 3)
        
        self.write_text((720,30), 'Resources')
        self.draw_rectangle(pygame.Color('white'), pygame.Color('black'), (670, 37), 280, 40, 3)
        i = 690
        for res, amount in self.board.players[self.player_id].resources.items():
            self.draw_circle(COLORS[res], (i, 57), 7)
            self.write_text((i+15, 57), f'{amount}')
            i+=50
        self.write_text((700,95), 'Build')
        self.draw_rectangle(pygame.Color('white'), pygame.Color('black'), (670, 102), 280, 40, 3)
        self.add_button((675, 108), 85, 28, 'road')
        self.add_button((768, 108), 85, 28, 'village')
        self.add_button((860, 108), 85, 28, 'city')
        
        self.add_button((670, 148), 135, 28, 'card')
        self.add_button((815, 148), 135, 28, 'trade')
        
        self.draw_cards_trade()
        
        self.write_text((700,438), 'Stats')
        self.draw_rectangle(pygame.Color('white'), pygame.Color('black'), (670, 445), 280, 40, 3)
        
        self.write_text((701,463), 'points:')
        self.write_text((737, 463), f'{self.board.players[self.player_id].get_real_points()}')
        self.write_text((775,463), 'path:')
        player: Player =  self.board.players[self.player_id]
        self.write_text((803, 463), f'{player.calc_longest_path()}')
        self.write_text((875,463), 'army size: ')
        self.write_text((920, 463), f'{self.board.players[self.player_id].army_size}')
        
        self.add_button((670, 490), 130, 40, 'roll dice')
        self.add_button((820, 490), 130, 40, 'end turn')
        
    def draw_circle(self, color, position, radius):
        pygame.draw.circle(self.main_screen, color, position, radius)
    
    def add_button(self, position, width, height, txt):
        self.draw_rectangle(pygame.Color('white'), pygame.Color('black'), position, width, height, 3)
        text_pos = (position[0]+width//2, position[1]+height//2)
        self.write_text(text_pos, txt)
        self.buttons.append((position, width, height, txt))
    
    def remove_button(self, button_txt):
        button = None
        for b in self.buttons:
            if b[3] == button_txt:
                button = b
                break
        if not button:
            return
        position, width, height, txt = button
        self.draw_filled_rectangle(pygame.Color('white'), position, width, height)
        self.buttons.remove(button)
    
    def click_in_button(self, button, pos):
        i_start, j_start = button[0]
        i_end, j_end = i_start+button[1], j_start+button[2]
        x, y = pos
        return i_start <= x and x <= i_end and j_start <= y and y <= j_end
    
    def draw_line(self, point1, point2, color):
        pygame.draw.line(self.main_screen, color, point1, point2, 3)
    
    def draw_valid_road_positions(self):
        for points in self.board.road_locations:
            pointList = list(points)
            if self.build_road_mode:
                if points in self.board.valid_road_positions(self.player_id):
                    self.draw_line(self.intersection_logical_to_gui(pointList[0]), self.intersection_logical_to_gui(pointList[1]), pygame.Color("green"))    
                else:
                    self.draw_line(self.intersection_logical_to_gui(pointList[0]), self.intersection_logical_to_gui(pointList[1]), pygame.Color("red"))    
            else:
                self.draw_line(self.intersection_logical_to_gui(pointList[0]), self.intersection_logical_to_gui(pointList[1]), pygame.Color("white"))    

    def draw_valid_village_positions(self):
        for point in self.board.village_locations:
            if not self.build_village_mode and not point.get_collector():
                self.draw_circle(pygame.Color('white'), self.intersection_logical_to_gui(point), 5)
            else:
                if not point.get_collector():
                    self.draw_circle(pygame.Color('green') if point in self.board.valid_village_positions(self.player_id) else pygame.Color('red'), self.intersection_logical_to_gui(point), 5)
        
    def draw_valid_city_postions(self):
        for village in self.board.players[self.player_id].constructions[VILLAGE]:
            if village.is_placed():
                self.draw_circle(pygame.Color('green'), self.intersection_coord_to_gui(village.coord), 5)
            
    def draw_city(self):
        for id, player in self.board.players.items():
            for city in player.constructions[CITY]:
                if city.is_placed():
                    x, y = self.intersection_coord_to_gui(city.coord)
                    self.draw_filled_rectangle(COLORS[id], (x-10, y-10), 20, 20)
            
    def button_clicked(self, button_text):
        if button_text == 'roll dice':
            self.send_action(button_text)
        elif button_text == 'end turn':
            self.send_action(button_text)
        elif button_text == 'village':
            self.build_village_mode = not self.build_village_mode
            self.build_road_mode = False
            self.build_city_mode = False
        elif button_text == 'road':
            self.build_road_mode = not self.build_road_mode
            self.build_village_mode = False
            self.build_city_mode = False
        elif button_text == 'city':
            self.build_road_mode = False
            self.build_village_mode = False
            self.build_city_mode = not self.build_city_mode
        elif button_text == 'trade':
            self.trade_mode = True
        elif button_text == 'card':
            self.trade_mode = False
        elif button_text == 'buy card':
            self.send_action(button_text, [])
            self.board.buy_dev_card(self.board.players[self.player_id])
        self.clicked_point = None

    def handle_click(self, pos):
        tile_pos = self.get_tile_pos_by_click(pos)
        intersection = self.get_intersection_by_click(pos)
        if tile_pos[0]>=0:
            self.update()
            return
        if intersection and self.build_village_mode:
            self.send_action('build village', [intersection])
            if 5 - self.board.players[self.player_id].constructions_counter[VILLAGE] == 0:
                self.board.place_village(self.board.players[self.player_id], intersection, True)
                self.force_build_road_mode = True
            elif 5 - self.board.players[self.player_id].constructions_counter[VILLAGE] == 1:
                self.board.place_village(self.board.players[self.player_id], intersection, False, True)
                self.force_build_road_mode = True
            else:
                self.board.place_village(self.board.players[self.player_id], intersection)
            self.build_village_mode = False
            self.update()
            return
        if intersection and self.build_road_mode:
            if not self.clicked_point:
                self.clicked_point = intersection
                return
            elif self.clicked_point:
                self.send_action('build road', [self.clicked_point, intersection])
                placed = self.board.place_road(self.board.players[self.player_id], self.clicked_point, intersection, self.board.players[self.player_id].constructions_counter[ROAD] - 15 < 2)
                self.clicked_point = None
                self.build_road_mode = False
                if placed:
                    self.force_build_road_mode = False
                self.update()
                return
        if intersection and self.build_city_mode:
            self.send_action('build city', [intersection])
            self.board.place_city(self.board.players[self.player_id], intersection)
            self.build_city_mode = False
            self.update()
            return
        button_text = ""
        for button in self.buttons:
            if self.click_in_button(button, pos):
                 button_text = button[3]
                 break
        if button_text == "":
            return
        self.button_clicked(button_text)
        self.update()

    def update(self):
        if self.force_build_road_mode and not self.build_road_mode:
            self.button_clicked('road')
        self.draw_dashboard()
        self.draw_valid_road_positions()
        self.draw_valid_village_positions()
        self.draw_roads()
        self.draw_villages()
        self.draw_city()
        if self.build_city_mode:
            self.draw_valid_city_postions()
        pygame.display.flip()

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

    def send_action(self, action: str, arguments:list = [Dictable]):
        data = json.dumps({'action': action, 'arguments': [argument.to_dict() for argument in arguments]})
        if self.client:
            self.client.sendall(data)

    def draw_villages(self):
        for id, player in self.board.players.items():
            for village in player.constructions[VILLAGE]:
                if len(village.coord) > 0:
                    self.draw_circle(COLORS[id], self.intersection_coord_to_gui(village.coord[0]), 10)
    
    def draw_roads(self):
        for id, player in self.board.players.items():
            for road in player.constructions[ROAD]:
                if len(road.coord) > 0:
                    self.draw_line(self.intersection_coord_to_gui(road.coord[0]), self.intersection_coord_to_gui(road.coord[1]), COLORS[id])
    
    def draw_cards_trade(self):
        self.draw_rectangle(pygame.Color('white'), pygame.Color('black'), (670, 170), 280, 256, 3)
        self.remove_cards_trade_buttons()
        if self.trade_mode:
            self.draw_trade_dashboard()
        else:
            self.draw_cards_dashboard()
    
    def draw_cards_dashboard(self):
        i_start, j_start = 670, 170
        width, height = 280, 256
        self.add_button((i_start + 5, j_start + 5),width-10, 30, 'buy card')
        i, j = i_start + 5, j_start + 40
        for card in self.board.players[self.player_id].constructions[DEV_CARD]:
            self.add_button((i, j), 130, 20, f'{card.get_action_str()}')
            i += 135
            if i + 130 >= i_start + width:
                i = i_start + 5
                j += 25
    
    def draw_trade_dashboard(self):
        pass
            
    def remove_cards_trade_buttons(self):
        i_start, j_start = 670, 170
        i_end, j_end = i_start + 280, j_start + 256
        for button in self.buttons:
            i, j = button[0]
            if i_start <= i and i <= i_end and j_start <= j and j <= j_end: 
                self.remove_button(button[3])
    
def distance(pos1, pos2):
    return ((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)**0.5

def main():
    game = Game(player_id=RED+1)
    game.start()
    
if __name__ == '__main__':
    main()