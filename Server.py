import socket
import threading
import json
import time
from Board import Board
from Game import Game
from sys import argv
from Constatnt import RED
import random

def update_player(client_socket: socket.socket, board: Board):
    json_board = board.board_to_json()
    client_socket.sendall(json_board.encode('utf-8'))

def send_player_id(client_socket: socket.socket, player_id: int):
    toSend = json.dumps({"player_id": player_id})
    client_socket.sendall(toSend.encode('utf-8'))
    time.sleep(1)

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
    for client in clients:
        threading.Thread(target=update_player, args=(client, board,)).start()


def main():
    players = int(argv[1]) if len(argv) > 1 else 3    
    board = Board(num_of_players=players)
    clients = accept_clients(players, board.players)
    
    for socket, player in clients.items():
        send_player_id(socket, player.id)
    
    update_players(clients.keys(), board)
    
    board.turn = random.choice(list(clients.keys()))
    update_players(clients.keys(), board)
    # Proceed with game logic using the collected dice rolls

if __name__ == '__main__':
    main()
