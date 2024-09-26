import threading
import socket

HOST = '192.168.1.145' #localhost
PORT = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

#The following class was not on original code
class Client():
    def __init__(self, clientSocket, name=None):
        self.clientSocket = clientSocket
        self.nickname = name

clients = []
#nicknames = []

#def remove(client):
    # index = clients.index(client)
    # clients.remove(client)
    # client.close()
    # nickname = nicknames[index]
    # nicknames.remove(nickname)
    # broadcast(f'{client.nickname} has left!'.encode())

def remove(client: Client):
    client.clientRef.close()
    clients.remove(client)
    broadcast(f'{client.nickname} has left!'.encode())
    

def broadcast(message):
    for client in clients:
        client.clientSocket.send(message)

def handle(client: Client):
    while True:
        try:
            message = client.clientSocket.recv(1024)
            broadcast(message)

        except:
            remove(client)
            break

def receive():
    print('listening...')

    while True:
        clientSocket, address = server.accept()
        print(f'Connected with {str(address)}')

        #clients.append(client)
        clients.append(client := Client(clientSocket=clientSocket))

        client.clientSocket.send("NICK".encode())
        nickname = client.clientSocket.recv(1024).decode()
        #nicknames.append(nickname)
        client.nickname = nickname
        

        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} joined the chat!'.encode())
        client.clientSocket.send('Connected to the server!'.encode())

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

if __name__ == '__main__':
    receive()