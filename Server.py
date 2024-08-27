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

def all_start_game(clients):
    player_nums = {}
    lock = threading.Lock()
    r = [_ for _ in range(len(clients))]

    def handle_roll(client: socket.socket):
        try:
            buffer = ""
            while True:
                data = client[0].recv(1024).decode('utf-8')
                if not data:
                    break
                buffer += data
            
            with lock:
                num = random.choice(r)
                player_nums[client[1].id] = num
                r.remove(num)
                print(f"Player {client[1].id} rolled: {player_nums[client[1].id]}")

        finally:
            client[0].close()

    threads = []
    for client in clients:
        thread = threading.Thread(target=handle_roll, args=(client,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    for player_id, value in player_nums:
        if value == len(clients) - 1:
            return player_id
    
    return -1

def main():
    players = int(argv[1]) if len(argv) > 1 else 3    
    board = Board(num_of_players=players)
    clients = accept_clients(players, board.players)
    
    for socket, player in clients.items():
        send_player_id(socket, player.id)
    
    update_players(clients.keys(), board)
    
    # Wait until all players have rolled their dice
    board.turn = RED#all_start_game(clients)
    #update_players(clients.keys(), board)
    # Proceed with game logic using the collected dice rolls

if __name__ == '__main__':
    main()
