import socket
import threading
from time import sleep
import sys

stop_thread = False

nickname = input("Choose a nickname: ").replace(' ', "_")

if nickname == "Eve":
    print("Activated evesdropper mode!")

HOST = 'localhost'
PORT = 55555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    global stop_thread
    global nickname

    while not stop_thread:
        try:
            message = client.recv(1024).decode()
            if message == 'NICK':
                client.send(nickname.encode())

            elif message.startswith('LEAVE_CHAT:'):
                reason = message.removeprefix('LEAVE_CHAT:')
                client.close()
                quit(f'Oh no! {reason} Disconnecting!')

            elif message.startswith('NICK_UPDATE:'):
                nickname = message.removeprefix('NICK_UPDATE:')

            else:
                print(message)

            

        except ConnectionResetError:
            quit("Server Closed!")
        
        except Exception as e:
            quit("An error occurred!")



def write():
    global stop_thread
    while not stop_thread:
        message = input("")
        if not message.startswith('/'):
            message = f'{nickname}: {message}'

        client.send(message.encode())

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

def quit(cause):
    global stop_thread
    print(cause)
    client.close()
    stop_thread = True
    
    if threading.current_thread() is not receive_thread:
        receive_thread.join()

    if threading.current_thread() is not write_thread:
        write_thread.join()

    sys.exit()
