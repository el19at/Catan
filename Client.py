import json
from Game import Game
import socket

def start_client():
    server_address = ('localhost', 50000)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server_address)

    try:
        # Buffer to hold the incoming data
        buffer = ""
        while True:
            # Continuously receive data in chunks of 4096 bytes
            data = client.recv(4096).decode('utf-8')
            if not data:
                break
            buffer += data
        json_data = json.loads(buffer)
        game = Game(json=json_data)
        game.start()

    finally:
        client.close()

if __name__ == "__main__":
    start_client()

