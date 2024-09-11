import json
from Game import Game
import socket
from Board import Board, json_to_board

server_address = ('localhost', 50000)

def start_client() -> socket.socket:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server_address)
    return client

def end_of_transmition(chunk:str):
    return chunk[-3:] == 'EOF'

def get_message(client):
    # Buffer to hold the incoming data
    buffer = ''
    while True:
        # Continuously receive data in chunks of 4096 bytes
        data = client.recv(4096).decode('utf-8')
        if end_of_transmition(data):
            buffer += data[:-3]
            break
        buffer += data
    return buffer

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
    print('board recived')
    game = Game(player_id,client=client, board=board)
    game.set_client(client)
    game.start()
