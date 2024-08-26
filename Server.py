import socket
import threading
from Board import Board
from sys import argv

def handle_client(client_socket):
    client_socket.sendall(b'hello')
    client_socket.close()

def update_player(client_socket: socket, board: Board):
    json_board = board.board_to_json()
    client_socket.sendall(json_board.encode('utf-8'))

def accept_clients(players):
    server_address = ('0.0.0.0', 50000)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(server_address)
    server.listen(players)
    print('Server is listening on {}:{}'.format(*server_address))
    clients = []
    while len(clients) < players:
        client_socket, client_address = server.accept()
        print('Accepted connection from {}:{}'.format(*client_address))
        clients.append(client_socket)
    print('all conncted!')
    return clients

def update_players(clients, board):
    for client in clients:
        threading.Thread(target=update_player, args=(client,board,)).start()
        
def main():
    # Define the server address and port
    players = int(argv[1]) if len(argv) > 1 else 3    
    clients = accept_clients(players)
    board = Board()
    update_players(clients, board)
    

if __name__ == '__main__':
    main()
