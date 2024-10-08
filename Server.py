import socket
import threading
import json
import logging
import random
from sys import argv
from Constatnt import RED, PHASE_FIRST_VILLAGE, PHASE_SECOND_VILLAGE, PHASE_INGAME, EMPTY_PROPOSE, convert_to_bool_dict, convert_to_int_dict, MONOPOLY, YEAR_OF_PLENTY, KNIGHT, ROADS_BUILD, get_message, send_message
from Board import Board, Player, Point, Tile, Dev_card

clients = {}
# Set up logging configuration
logging.basicConfig(filename='server.log', filemode='w', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def update_player(client_socket: socket.socket, board: Board):
    json_board = board.board_to_json()
    logging.info(f'send: {json_board}')
    send_message(client_socket, json_board)

def send_player_id(client_socket: socket.socket, player_id: int):
    toSend = json.dumps({"player_id": player_id})
    logging.info(f'send: {toSend}')
    send_message(client_socket, toSend)

def send_robb(client_socket: socket.socket):
    toSend = json.dumps({"robb": "robb"})
    send_message(client_socket, toSend)
    
def send_player_propose(clients: dict[socket.socket:Player], player_id: int, propose: dict[bool:dict[int:int]]):
    for client, id in clients.items():
        if id == player_id:
            continue
        toSend = json.dumps({"propse": propose})
        send_message(client, toSend)

def send_seven(clients: dict[socket.socket:Player]):
    for client, id in clients.items():
        toSend = json.dumps({"seven": "seven"})
        send_message(client, toSend)

def accept_clients(players, gamePlayers) -> dict[socket.socket:Player]:
    server_address = ('0.0.0.0', 50000)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(server_address)
    server.listen(players)
    logging.info(f'Server is listening on {server_address[0]}:{server_address[1]}')
    
    clients = {}
    i = RED
    while len(clients) < players:
        client_socket, client_address = server.accept()
        logging.info(f'Accepted connection from {client_address}')
        clients[client_socket] = gamePlayers[i]
        i += 1
    
    logging.info('All players connected!')
    return clients

def update_players(clients, board):
    # threads  = []
    for client in clients.keys():
        update_player(client, board)
        """
        t: threading.Thread = threading.Thread(target=update_player, args=(client, board,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print('end of update players')
    """
    

def wait_for_player_response(clients: dict, proposer_id: int):
    response_event = threading.Event()  # Event to signal an accepted response
    accepted_socket = [-1]  # Shared variable to store the socket of the player who accepts
    lock = threading.Lock()  # Lock to safely update the accepted_socket variable

    def wait_for_response(client_socket, player_id):
        nonlocal accepted_socket
        if player_id == proposer_id:
            return  # Skip the player who proposed the trade
        response, _ = receive_action(client_socket)
        if response == "accept":
            with lock:
                accepted_socket[0] = client_socket  # Set the accepted player's socket
            response_event.set()  # Signal that someone accepted            
        else:
            return
    threads = []
    for client_socket, player_id in clients.items():
        thread = threading.Thread(target=wait_for_response, args=(client_socket, player_id))
        thread.start()
        threads.append(thread)

    # Wait for either an acceptance or for all threads to finish
    response_event.wait()  # Blocks until one of the players accepts

    # Ensure all threads have finished before continuing
    for thread in threads:
        thread.join()

    return accepted_socket[0]  # Return the accepted player's socket, or -1 if no one accepted

def wait_for_player_resource(clients: dict):
    def wait_for_response(client_socket, player_id):
        action, arg = receive_action(client_socket)
        if action == "give to robb":
            player: Player = clients[client_socket]
            for key, val in convert_to_int_dict(arg).items():
                player.resources[key] -= val
        else:
            return
    threads = []
    for client_socket in clients.keys():
        thread = threading.Thread(target=wait_for_response, args=(client_socket))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

def player_to_socket(clients: dict, player_id: int)->socket.socket:
    for key, value in clients.items():
        if value.id == player_id:
            return key
    return None

def receive_action(client_socket):
    buffer = get_message(client_socket)
    logging.info(f'get: {buffer}')
    data_dict = json.loads(buffer)
    action = data_dict.get('action')
    args = data_dict.get('arguments', {})
    return action, args
    
def main():
    players = 2 # int(argv[1]) if len(argv) > 1 else 3    
    board = Board(num_of_players=players)
    clients = accept_clients(players, board.players)
    board.turn = random.choice([player.id for player in clients.values()])
    starter = board.turn
    ender = RED + ((starter + board.num_of_players - 1) % board.num_of_players)
    
    for socket, player in clients.items():
        send_player_id(socket, player.id)
    
    update_players(clients, board)
    
    while not board.win():
        turn_socket = player_to_socket(clients, board.turn)
        print(board.turn)
        turn_player: Player = clients[turn_socket]
        action = 'start turn'
        dices = -1
        while action != 'end turn':
            action, arguments = receive_action(turn_socket)
            if action == 'end turn':
                turn = board.turn
                board.end_turn()
                if board.game_phase == PHASE_FIRST_VILLAGE and turn == ender:
                    board.game_phase = PHASE_SECOND_VILLAGE
                    board.turn = ender
                    break
                if board.game_phase == PHASE_SECOND_VILLAGE and starter == turn:
                    board.game_phase = PHASE_INGAME
                    break
            elif action == 'buy card':
                board.buy_dev_card()
                
            elif action == 'bank trade':
                turn_player.bank_trade(convert_to_bool_dict(arguments['propse']))
                
            elif action == 'player trade':
                send_player_propose(clients, board.turn, convert_to_bool_dict(arguments['propse']))
                socket = wait_for_player_response(clients, board.turn)
                send_player_propose(clients, board.turn, EMPTY_PROPOSE)
                if socket in clients.keys():
                    turn_player.make_trade(clients[socket], convert_to_bool_dict(arguments['propse']))
                
            elif action == 'roll dice':
                dices = board.roll_dices()
                if dices == 7:
                    send_seven(clients)
                    wait_for_player_resource(clients)
                    send_robb(turn_socket)
                else:
                    board.give_recources(dices)
                
            elif action == 'monopoly':
                resource = int(arguments['resource'])
                card = board.get_object(arguments['card'])
                if card and board.use_dev_card(clients[turn_socket], card):
                    board.use_monopoly(resource)
                
            elif action == 'year of plenty':
                resource = [int(arguments['first resource']), int(arguments['second resource'])]
                card = board.get_object(arguments['card'])
                if card and board.use_dev_card(clients[turn_socket], card):
                    board.use_year_of_plenty(resource[0], resource[1])
                
            elif action == 'build village':
                point:Point = board.get_object(arguments['point']) 
                board.place_village(point, board.game_phase == PHASE_FIRST_VILLAGE, board.game_phase == PHASE_SECOND_VILLAGE)
                
            elif action == 'build road':
                point1: Point = board.get_object(arguments['point1'])
                point2: Point = board.get_object(arguments['point2'])
                board.place_road(point1, point2, board.game_phase != PHASE_INGAME)
                
            elif action == 'build city':
                point:Point = board.get_object(arguments['point'])
                board.place_city(point)
                

            elif action == 'robb':
                tile: Tile = board.get_object(arguments['tile'])
                player: Player = board.get_object(arguments['player']) if 'player' in arguments.keys() else None
                card: Dev_card = board.get_object(arguments['card']) if 'player' in arguments.keys() else None
                if not card and dices != 7:
                    continue
                if card:
                    board.use_dev_card(card)
                    board.robb(tile, player, fromDice=False)
                else:
                    board.robb(tile, player, fromDice=True)
                        
            update_players(clients, board)
    
if __name__ == '__main__':
    main()
