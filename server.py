import threading
import socket
import time

HOST = 'localhost'
PORT = 55555

ADMIN_PREFIX = '[ADMIN] '

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

#The following class was not on original code
class Client():
    def __init__(self, clientSocket, name=None, isAdmin=False):
        self.clientSocket = clientSocket
        self.nickname = name
        self.isAdmin = isAdmin
        

clients = []

def remove_disconnected(client: Client):
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
                message = f"[ADMIN] {client.nickname}: {decoded_message}".encode() if client.isAdmin else f"{client.nickname}: {decoded_message}".encode()
                broadcast(message)
                continue

            command = decoded_message.split(' ')
            opcode = command[0]
            args = command[1:]

            if opcode.lower() == '/whisper':
                message_to_target = ' '.join(args[1:])
                if message_to_target.isspace() or message_to_target == '':
                        client.clientSocket.send("You can't send an empty message!".encode())
                        continue

                targetExists = False
                for possibleWhisperTarget in clients:
                    if possibleWhisperTarget.nickname == args[0]:
                        if possibleWhisperTarget == client:
                            client.clientSocket.send("You can't whisper to yourself!".encode())
                            continue

                        possibleWhisperTarget.clientSocket.send(f'{client.nickname} whispered you: {message_to_target}'.encode())
                        client.clientSocket.send(f'You sent "{message_to_target}" to {possibleWhisperTarget.nickname}'.encode())
                        targetExists = True

                        for maybeEve in clients:
                            if maybeEve.nickname == "Eve":
                                maybeEve.clientSocket.send(f'{client.nickname} whispered "{message_to_target}" to {possibleWhisperTarget.nickname}'.encode())

                if not targetExists:
                    client.clientSocket.send("Target doesn't exist!".encode())
                    continue
            
            elif opcode.lower() == '/kickme':
                ask_to_leave(client, "You got kicked!")

            else:
                client.clientSocket.send('Invalid command!'.encode())

        except Exception as e:
            if client in clients:
                remove_disconnected(client)
    

def receive():
    print('listening...')

    while True:
        clientSocket, address = server.accept()
        client = Client(clientSocket=clientSocket)
        print(f'Connected with {str(address)}')

        
        client.clientSocket.send("NICK".encode())
        nickname = client.clientSocket.recv(1024).decode()

        if clients == []:
            client.isAdmin = True
            client.clientSocket.send("You are now Admin!".encode())

        client.nickname = nickname

        clients.append(client)

        print(f'Nickname of the client is {nickname}!')
        broadcast(f'[ADMIN] {nickname} joined the chat!'.encode() if client.isAdmin else f'{nickname} joined the chat!'.encode())
        time.sleep(0.1)
        client.clientSocket.send('Connected to the server!'.encode())

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

if __name__ == '__main__':
    receive()