import threading
import socket

HOST = 'localhost'
PORT = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

class Client():
    def __init__(self, clientSocket, name=None):
        self.clientSocket = clientSocket
        self.nickname = name

clients = []

def remove_disconnected(client: Client, msg=''):
    clients.remove(client)
    client.clientSocket.close()
    broadcast(f'{client.nickname} has left!'.encode())

def ask_to_leave(client: Client, msg):
    client.clientSocket.send(f'LEAVE_CHAT:{msg}'.encode())

def broadcast(message):
    for client in clients:
        client.clientSocket.send(message)

def handle(client: Client):
    while True:
        try:
            message = client.clientSocket.recv(1024)
            decoded_message = message.decode()
            if not decoded_message.startswith('/'):
                broadcast(message)
                continue

            command = decoded_message.split(' ')
            opcode = command[0]
            args = command[1:]

            
            

            if opcode.lower() == '/whisper':

                message_to_target = ' '.join(args[1:])
                if message_to_target.isspace() or message_to_target == '':
                        client.clientSocket.send("You can't whisper an empty message!".encode())
                        continue

                targetExists = False
                for possibleTarget in clients:
                    if possibleTarget.nickname == args[0]:
                        if possibleTarget == client:
                            client.clientSocket.send("You can't whisper to yourself!".encode())
                            continue

                        possibleTarget.clientSocket.send(f'{client.nickname} whispered you: {message_to_target}'.encode())
                        client.clientSocket.send(f'You sent "{message_to_target}" to {possibleTarget.nickname}'.encode())
                        targetExists = True

                        for maybeEve in clients:
                            if maybeEve.nickname == "Eve":
                                maybeEve.clientSocket.send(f'{client.nickname} whispered "{message_to_target}" to {possibleTarget.nickname}'.encode())

                if not targetExists:
                    client.clientSocket.send("Target doesn't exist!".encode())
                    continue
            
            elif opcode.lower() == '/kickme':
                ask_to_leave(client, 'You Got Kicked!')
            else:
                client.clientSocket.send('Invalid command!'.encode())


        except Exception as e:
            if client in clients:
                remove_disconnected(client)
    

def receive():
    print('listening...')

    while True:
        clientSocket, address = server.accept()
        print(f'Connected with {str(address)}')

        client = Client(clientSocket=clientSocket)
        client.clientSocket.send("NICK".encode())
        nickname = client.clientSocket.recv(1024).decode()

        client.nickname = nickname

        clients.append(client)

        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} joined the chat!'.encode())
        client.clientSocket.send('Connected to the server!'.encode())

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

if __name__ == '__main__':
    receive()
    