import socket
import threading

def handle_client(client_socket):
    client_socket.sendall(b'hello')
    client_socket.close()

def main():
    # Define the server address and port
    server_address = ('0.0.0.0', 50000)
    
    # Create a TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the address and port
    server.bind(server_address)
    
    # Listen for incoming connections (max 3 connections in the queue)
    server.listen(3)
    print('Server is listening on {}:{}'.format(*server_address))

    # Wait for 3 clients to connect
    clients = []
    while len(clients) < 3:
        client_socket, client_address = server.accept()
        print('Accepted connection from {}:{}'.format(*client_address))
        clients.append(client_socket)
    
    # Send "hello" to all connected clients
    for client in clients:
        threading.Thread(target=handle_client, args=(client,)).start()

if __name__ == '__main__':
    main()
