import socket
import threading
import json
import time
from Board import Board
from Game import Game
from sys import argv
from Constatnt import RED, PHASE_FIRST_VILLAGE, PHASE_SECOND_VILLAGE, PHASE_INGAME
import random

from Player import Player

def update_player(client_socket: socket.socket, board: Board):
    print(type(board.turn))
    json_board = board.board_to_json()
    client_socket.sendall(json_board.encode('utf-8'))

def send_player_id(client_socket: socket.socket, player_id: int):
    toSend = json.dumps({"player_id": player_id})
    client_socket.sendall(toSend.encode('utf-8'))
    time.sleep(1)
    
def send_player_propose(clients: dict[socket.socket:Player], player_id: int, propose: dict[int:int]):
    for client, id in clients.items():
        if id == player_id:
            continue
        toSend = json.dumps({"propse": propose})
        client.sendall(toSend.encode('utf-8'))

def accept_clients(players, gamePlayers):
    server_address = ('0.0.0.0', 50000)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(server_address)
    server.listen(players)
    print('Server is listening on {}:{}'.format(*server_address))
    
    clients = {}
    i = RED
    while len(clients) < players:
        client_socket, client_address = server.accept()
        print(f'Accepted connection from {client_address}')
        clients[client_socket] = gamePlayers[i]
        i += 1
    
    print('All players connected!')
    return clients

def update_players(clients, board):
    for client in clients.keys():
        threading.Thread(target=update_player, args=(client, board,)).start()

def player_to_socket(clients, player_id: int)->socket.socket:
    for key, value in clients:
        if value.id == player_id:
            return key
    return None

def recive_data(client:socket.socket) -> str:
    # Buffer to hold the incoming data
    buffer = ""
    while True:
        # Continuously receive data in chunks of 4096 bytes
        data = client.recv(4096).decode('utf-8')
        if not data:
            break
        buffer += data
    return buffer

def receive_action(client_socket):
    buffer = ""
    while True:
        data = client_socket.recv(4096).decode('utf-8')
        if not data:
            break
        buffer += data
        
    data_dict = json.loads(buffer)
    action = data_dict.get('action')
    args = data_dict.get('arguments', [])
    additional_args = [data_dict.get(f'value{i}') for i in range(len(data_dict)) if f'value{i}' in data_dict]
    args.extend(additional_args)
    return action, args
 
    
def main():
    players = 1 #int(argv[1]) if len(argv) > 1 else 3    
    board = Board(num_of_players=players)
    clients = accept_clients(players, board.players)
    board.turn = random.choice([player.id for player in clients.values()])
    starter = board.turn
    ender = RED + (starter-1) % len(clients)
    
    for socket, player in clients.items():
        send_player_id(socket, player.id)
    
    while not board.win():
        turn_socket = player_to_socket(clients, board.turn)
        action = 'start turn'
        while action != 'end turn':
            action, arguments = receive_action(turn_socket)
            if action == 'end turn':
                board.end_turn()
                if board.game_phase == PHASE_FIRST_VILLAGE and board.turn == ender:
                    board.game_phase = PHASE_SECOND_VILLAGE
                    board.turn = ender
                if board.game_phase == PHASE_SECOND_VILLAGE and starter == board.turn():
                    board.game_phase = PHASE_INGAME
            if action == 'buy card':
                board.buy_dev_card()
                update_players(clients, board)
            if action == 'bank trade':
                clients[turn_socket].bank_trade(arguments[0])
                update_players(clients, board)
            if action == 'player trade':
                send_player_propose(clients, board.turn, arguments[0])
            if action == 'roll dice':
                dices = board.roll_dices()
                board.give_recources(dices)
                update_players(clients, board)
            
        
    
    
    update_players(clients, board)
    
    # Proceed with game logic using the collected dice rolls

if __name__ == '__main__':
    main()
