import socket
import threading


hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
HOST = ip_address
PORT = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []


# broadcast

def broadcast(message):
    for client in clients:
        client.send(message)


# handle
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            print(f"{nicknames[clients.index(client)]}")
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(index)
            clients.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break


# recieve

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with: {str(address)}")
        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024)
        nicknames.append(nickname)

        print(f"Nickname of the client is: {nickname}")
        clients.append(client)
        broadcast(f"{nickname} connected to the server!\n".encode('utf-8'))
        client.send("Connected to the server\n".encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("server is running... ")

receive()
