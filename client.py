import socket
import threading

nickname = input("Choose a nickname: ")

HOST = '192.168.1.145'
PORT = 55555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            if message == 'NICK':
                client.send(nickname.encode())              
            else:
                print(message)

        #This exception was my addition!
        except ConnectionResetError:
            quit("Server Closed!")
        
        except Exception as e:
            quit("An error occurred!")



def write():
    while True:
        message = f'{nickname}: {input("")}'
        client.send(message.encode())

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

# This helper function was my addition (I decided to put that in a func)!
def quit(cause):
    print(cause)
    client.close()
    exit()
