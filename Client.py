import json
from Game import Game
import socket
from Board import Board, json_to_board

server_address = ('localhost', 50000)

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server_address)
    return client

def recive_board(client):
    # Buffer to hold the incoming data
    buffer = ""
    while True:
        # Continuously receive data in chunks of 4096 bytes
        data = client.recv(4096).decode('utf-8')
        if not data:
            break
        buffer += data
    json_data = json.loads(buffer)
    return json_to_board(json_data)

def recive_player_id(client):
    data = client.recv(512).decode('utf-8')
    return json.loads(data)['player_id']

if __name__ == "__main__":
    client = start_client()
    player_id = recive_player_id(client)
    print(f'playerid: {player_id}')
    board = recive_board(client)
    game = Game(board, client=client, player_id=player_id)
    game.start()
