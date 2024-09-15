import json
from Game import Game
import socket
from Board import Board, json_to_board
from Constatnt import get_message

server_address = ('localhost', 50000)

def start_client() -> socket.socket:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server_address)
    return client

def recive_board(client):
    message = get_message(client)
    json_data = json.loads(message)
    return json_to_board(json_data)

def recive_player_id(client):
    data = get_message(client)
    return json.loads(data)['player_id']

if __name__ == "__main__":
    client = start_client()
    player_id = recive_player_id(client)
    print(f'playerid: {player_id}')
    board = recive_board(client)
    game = Game(player_id,client=client, board=board)
    game.set_client(client)
    game.start()
