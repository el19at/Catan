import socket
import threading
import pygame
from pygame import Color
from Board import Board, Point, json_to_board, Player, Dev_card, Tile
import math
import json
from Indexable import Indexable
from Constatnt import LUMBER,BRICK, ORE, WOOL, GRAIN, \
                    VILLAGE, CITY, ROAD, DEV_CARD, DESERT, WHITE, RED, \
                    BLUE, ORANGE, KNIGHT, VICTORY_POINT, YEAR_OF_PLENTY,\
                    MONOPOLY, ROADS_BUILD, SEA, PHASE_FIRST_ROLL,\
                    RESOURCE_TO_STR, RESOURCE_TO_INT, GIVE, TAKE, convert_to_int_dict, EMPTY_PROPOSE

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
        self.clicked_point: Point = None
        self.trade_mode = True
        self.button_pos_to_card: dict[tuple:Dev_card] = {}
        self.robb_mode: bool = False
        self.tile_to_robb: Tile = None
        self.year_of_plenty_mode: bool = False
        self.year_of_plenty_mode_last_recsource: int = -1
        self.monopoly_mode: bool = False
        self.road_building_state: int = 0
        self.trade_propose: dict[bool:dict[int:int]]= {}
        self.trade_propose[GIVE] = {ORE: 0, LUMBER:0, WOOL:0, BRICK:0, GRAIN:0}
        self.trade_propose[TAKE] = {ORE: 0, LUMBER:0, WOOL:0, BRICK:0, GRAIN:0}
        self.player_propose: dict[bool:dict[int:int]]= {}
        self.player_propose[GIVE] = {ORE: 0, LUMBER:0, WOOL:0, BRICK:0, GRAIN:0}
        self.player_propose[TAKE] = {ORE: 0, LUMBER:0, WOOL:0, BRICK:0, GRAIN:0}
        self.button_pos_trade: dict[tuple[int]: tuple] = {}
        self.board.turn = self.player_id
        self.client = None
        self.lock = threading.Lock()
        self.update()
    
    def set_client(self, socket):
        self.client = socket
    
    def is_my_turn(self):
        return self.board.turn == self.player_id
    
    def update_player_propose(self, propose):
        self.player_propose = propose
        self.update()
        
    def update_board(self, board):
        self.board = board
        self.update()
        
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
        return self.board.get_point_board(x, y)
    
    def write_text(self, center, txt: str, size: int=24, color = pygame.Color('black')):
        if not pygame.font.get_init():
            pygame.font.init()
        font = pygame.font.SysFont(None, size)
        text_surface = font.render(txt, True, color)
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
                    self.draw_hexagon(COLORS[tile.resource], center_round, c-2, 0 if tile.is_robbed() else tile.number, "")
                    
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
            if point.equal(logicalPoint):
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
        self.write_text((910, 25), 'turn:', 30)
        self.draw_circle(COLORS[self.board.turn], (943, 25), 8)
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
    
    def add_button(self, position, width, height, txt, color = pygame.Color('black')):
        self.draw_rectangle(pygame.Color('white'), color, position, width, height, 3)
        text_pos = (position[0]+width//2, position[1]+height//2)
        self.write_text(text_pos, txt, height-3)
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
            
    def button_clicked(self, button_text, position = (-1, -1)):
        if button_text == 'roll dice':
            self.send_action(button_text)
        elif button_text == 'end turn':
            self.send_action(button_text)
            self.board.players[self.player_id].end_turn()
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
        elif button_text == 'knight':
            if not self.board.use_dev_card(self.board.players[self.player_id], self.button_pos_to_card[position]):
                return
            self.robb_mode = True
            self.tile_to_robb = None
        elif button_text == 'monopoly':
            if not self.board.use_dev_card(self.board.players[self.player_id], self.button_pos_to_card[position]):
                return
            self.monopoly_mode = True
        elif button_text == 'year of plenty':
            if not self.board.use_dev_card(self.board.players[self.player_id], self.button_pos_to_card[position]):
                return
            self.year_of_plenty_mode = True
        elif button_text == 'roads build':
            if not self.board.use_dev_card(self.board.players[self.player_id], self.button_pos_to_card[position]):
                return
            self.road_building_state = 1
        elif button_text == 'bank trade':
            if self.board.players[self.player_id].valid_bank_trade(self.trade_propose):
                self.send_action('bank trade', [self.trade_propose])
        elif button_text == 'player trade':
            self.send_action('send propose', [self.trade_propose])
        elif button_text in ['accept', 'refuse']:
            self.send_action(button_text, [])
            self.remove_button('accept')
            self.remove_button('refuse')
        elif button_text in RESOURCE_TO_STR.values():
            self.resource_clicked(button_text, position)
        elif position in self.button_pos_trade.keys():
            self.trade_resource_clicked(position)
        self.clicked_point = None
    
    def have_player_propose(self):
        return sum(self.player_propose[TAKE].values()) > 0 and sum(self.player_propose[GIVE].values()) > 0
    
    def trade_resource_clicked(self, position):
        resource = self.button_pos_trade[position]
        flag  = position[0] > 800
        if self.trade_propose[flag][resource] > 0:
            self.trade_propose[flag][resource] -= 1
        
    def resource_clicked(self, button_text, position):
        if self.monopoly_mode:
            self.send_action('monopoly', [RESOURCE_TO_INT[button_text]])
            self.board.use_monopoly(self.board.players[self.player_id], RESOURCE_TO_INT[button_text])
            self.monopoly_mode = False
        elif self.year_of_plenty_mode:
            if self.year_of_plenty_mode_last_recsource == -1:
                self.year_of_plenty_mode_last_recsource = RESOURCE_TO_INT[button_text]
            else:
                self.send_action('year of plenty', [self.year_of_plenty_mode_last_recsource, RESOURCE_TO_INT[button_text]])
                self.board.use_year_of_plenty(self.board.players[self.player_id], self.year_of_plenty_mode_last_recsource, RESOURCE_TO_INT[button_text])
                self.year_of_plenty_mode = False
        elif self.trade_mode:
            take = position[0] < 730
            resource = RESOURCE_TO_INT[button_text]
            if not take:
                if self.board.players[self.player_id].resources[resource] > self.trade_propose[GIVE][resource]:
                    self.trade_propose[GIVE][resource] += 1
            else:
                self.trade_propose[TAKE][resource] += 1 
            
        self.update()

    def click_in_trade(self, pos):
        i_s, j_s, i_e, j_e = 670, 170, 950, 426
        return i_s<pos[0] and pos[0] < i_e and j_s<pos[1] and pos[1] < j_e
    
    def handle_click(self, pos):
        if not self.is_my_turn() and not self.click_in_trade(pos):
            self.update()
            return
        tile_pos = self.get_tile_pos_by_click(pos)
        intersection = self.get_intersection_by_click(pos)
        if self.robb_mode and not self.tile_to_robb:
            if tile_pos == (-1, -1):
                self.update()
                return
            else:
                tile = self.board.tiles[tile_pos[0]][tile_pos[1]]
                if self.board.robbed_tile == tile:
                    self.update()
                    return
                self.tile_to_robb = tile
                self.update()
                return
        if self.robb_mode and self.tile_to_robb:
            if not intersection:
                self.update()
                return
            if not intersection in self.tile_to_robb.points:
                self.update()
                return
            village = intersection.get_collector()
            if village:
                self.send_action('robb', [self.tile_to_robb, self.board.players[village.player_id]])
                self.board.robb(self.board.players[self.player_id], self.tile_to_robb, self.board.players[village.player_id])
            else:
                self.send_action('robb', [self.tile_to_robb])
                self.board.robb(self.board.players[self.player_id], self.tile_to_robb)
            self.robb_mode = False
            self.tile_to_robb = None
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
                free_road = False
                if self.road_building_state > 0 or self.board.players[self.player_id].constructions_counter[ROAD] - 15 < 2:
                    free_road = True
                self.send_action('build road', [self.clicked_point, intersection, free_road])
                placed = self.board.place_road(self.board.players[self.player_id], self.clicked_point, intersection, free_road)
                self.clicked_point = None
                self.build_road_mode = False
                if placed:
                    self.force_build_road_mode = False
                    if self.road_building_state > 0:
                        self.road_building_state += 1
                    if self.road_building_state == 3:
                        self.road_building_state = 0
                self.update()
                return
        if self.force_build_road_mode:
            self.update()
            return
        if intersection and self.build_city_mode:
            self.send_action('build city', [intersection])
            self.board.place_city(self.board.players[self.player_id], intersection)
            self.build_city_mode = False
            self.update()
            return
        button_text, button_pos = "", (-1, -1)
        for button in self.buttons:
            if self.click_in_button(button, pos):
                 button_text, button_pos = button[3], button[0]
                 break
        if button_text == "":
            return
        self.button_clicked(button_text, button_pos)
        self.update()
    
    def update(self):
        self.draw_tiles(0, 0, self.tile_size)
        self.buttons = []
        if self.road_building_state > 0:
            self.build_road_mode = True
            self.force_build_road_mode = True
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

    def send_action(self, action: str, arguments:list = []):
        data = json.dumps({'action': action, 'arguments': [argument.to_index() for argument in arguments if isinstance(argument, Indexable)]})
        data_dict = json.loads(data)
        for i, val in enumerate([val for val in arguments if not isinstance(val, Indexable)]):
            data_dict[f'value{i}'] = val
        data = json.dumps(data_dict)
        if self.client:
            self.client.sendall(data)
            self.wait_for_server = True
            self.listen_to_server()

    def listen_to_server(self):
        while True:
            data = self.recive_data()
            data_dict = json.loads(data)
            if "propose" == data[:7]:
                new_propose = convert_to_int_dict(data_dict["propose"])
                self.update_player_propose(new_propose)
                with self.lock:  # Lock to safely update the current proposal
                    self.player_propose = new_propose
                threading.Thread(target=self.process_proposal).start()
            else:
                self.update_board(self.dict_to_board(data_dict))
                
    def process_proposal(self):
        while True:
            with self.lock:
                if self.player_propose == EMPTY_PROPOSE:
                    break
                self.accept_or_refuse()
                break
    
    def accept_or_refuse(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    button_text = 'not found'
                    for button in self.buttons:
                        if self.click_in_button(button, event.pos):
                            button_text = button[3]
                            break
                    if button_text in ['accept', 'refuse']:
                        self.handle_click(event.pos)
                        running = False
        
    def dict_to_board(data):
        json_data = json.loads(data)
        return json_to_board(json_data)

    def recive_data(self):
         # Buffer to hold the incoming data
        buffer = ""
        while True:
            # Continuously receive data in chunks of 4096 bytes
            data = self.client.recv(4096).decode('utf-8')
            if not data:
                break
            buffer += data
        return buffer
    
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
        if not self.is_my_turn():
            self.draw_trade_accept()
        elif self.year_of_plenty_mode or self.monopoly_mode:
            self.draw_resource_picking_dashboard()
        elif self.trade_mode:
            self.draw_trade_dashboard()
        else:
            self.draw_cards_dashboard()
            
    def draw_trade_accept(self):
        i_start, j_start = 670, 170
        width, height = 280, 256
        self.write_text((i_start + width//2, j_start+17), 'player propose:', 40)
        self.write_text((i_start + width//4, j_start+46), 'take', 38)
        self.write_text((i_start + 3*width//4, j_start+46), 'give', 35)
        j = j_start + 75
        for key in self.player_propose[TAKE]:
            self.write_text((i_start + width//4, j), f'{RESOURCE_TO_STR[key]}: {self.player_propose[GIVE][key]}', 30, COLORS[key])
            self.write_text((i_start + 3*width//4, j), f'{RESOURCE_TO_STR[key]}: {self.player_propose[TAKE][key]}', 30, COLORS[key])
            j += 25
        if self.have_player_propose():
            self.add_button((i_start + 8, j_start + height - 45), (width-10)//2 - 5, 30, 'accept', Color('green') if self.board.players[self.player_id].valid_player_trade(self.trade_propose) else Color('red'))
            self.add_button((i_start + (width-10)//2 + 8, j_start + height - 45), (width-10)//2 - 5, 30, 'refuse')
        

    def draw_resource_picking_dashboard(self):
        i_start, j_start = 670, 170
        width, height = 280, 256
        self.add_button((i_start + 5, j_start + 10),width-10, 30, 'lumber', COLORS[LUMBER])
        self.add_button((i_start + 5, j_start + 45),width-10, 30, 'ore', COLORS[ORE])
        self.add_button((i_start + 5, j_start + 80),width-10, 30, 'grain', COLORS[GRAIN])
        self.add_button((i_start + 5, j_start + 115),width-10, 30, 'brick', COLORS[BRICK])
        self.add_button((i_start + 5, j_start + 150),width-10, 30, 'wool', COLORS[WOOL])
    
    def draw_cards_dashboard(self):
        i_start, j_start = 670, 170
        width, height = 280, 256
        self.add_button((i_start + 5, j_start + 5),width-10, 30, 'buy card')
        i, j = i_start + 6, j_start + 40
        cards = self.board.players[self.player_id].constructions[DEV_CARD]
        for card in cards:
            self.add_button((i, j), 86, 21, f'{card.get_action_str()}', Color('green') if card.usable() and self.board.players[self.player_id].dev_card_allowed else Color('red'))
            self.button_pos_to_card[(i, j)] = card
            i += 91
            if i + 86 >= i_start + width:
                i = i_start + 6
                j += 26
    
    def draw_trade_dashboard(self):
        i_start, j_start = 670, 185
        width, height = 280, 256
        self.write_text((i_start + width//4, j_start-3), 'take:', 25)
        self.add_button((i_start + 8, j_start + 10), (width-10)//2 - 5, 30, 'lumber', COLORS[LUMBER])
        self.add_button((i_start + 8, j_start + 45),  (width-10)//2 - 5, 30, 'ore', COLORS[ORE])
        self.add_button((i_start + 8, j_start + 80),  (width-10)//2 - 5, 30, 'grain', COLORS[GRAIN])
        self.add_button((i_start + 8, j_start + 115),  (width-10)//2 - 5, 30, 'brick', COLORS[BRICK])
        self.add_button((i_start + 8, j_start + 150),  (width-10)//2 - 5, 30, 'wool', COLORS[WOOL])
        
        self.write_text((i_start + 3*width//4, j_start-3), 'give:', 25)
        self.add_button((i_start + (width-10)//2 + 8, j_start + 10), (width-10)//2 - 5, 30, 'lumber', COLORS[LUMBER])
        self.add_button((i_start + (width-10)//2 + 8, j_start + 45), (width-10)//2 - 5, 30, 'ore', COLORS[ORE])
        self.add_button((i_start + (width-10)//2 + 8, j_start + 80), (width-10)//2 - 5, 30, 'grain', COLORS[GRAIN])
        self.add_button((i_start + (width-10)//2 + 8, j_start + 115), (width-10)//2 - 5, 30, 'brick', COLORS[BRICK])
        self.add_button((i_start + (width-10)//2 + 8, j_start + 150), (width-10)//2 - 5, 30, 'wool', COLORS[WOOL])
        
        i = i_start + 9
        button_size = 23
        for resource in self.trade_propose[TAKE].keys():
            self.add_button((i, j_start + 183), button_size, button_size, f'{self.trade_propose[TAKE][resource]}', COLORS[resource])
            self.add_button((i + (width-10)//2, j_start + 183), button_size, button_size, f'{self.trade_propose[GIVE][resource]}', COLORS[resource])
            self.button_pos_trade[(i, j_start + 183)], self.button_pos_trade[(i + (width-10)//2, j_start + 183)] = resource, resource
            i += (button_size+3)
        
        self.add_button((i_start + 8, j_start + height - 45), (width-10)//2 - 5, 25, 'bank trade', Color('green') if self.board.players[self.player_id].valid_bank_trade(self.trade_propose) else Color('red'))
        self.add_button((i_start + (width-10)//2 + 8, j_start + height - 45), (width-10)//2 - 5, 25, 'player trade')
            
            
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