import socket
import threading

nickname = input("Choose a nickname: ").replace(' ', "_")

if nickname == "Eve":
    print("Activated evesdropper mode!")

HOST = '10.38.199.48'
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
        message = input("")
        if not message.startswith('/'):
            message = f'{nickname}: {message}'

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
