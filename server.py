import socket
import threading
import rsa

# Generate RSA key pair
public_key, private_key = rsa.newkeys(2048)

# Convert keys to PEM format
public_key_pem = public_key.save_pkcs1().decode('utf-8')
private_key_pem = private_key.save_pkcs1().decode('utf-8')

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
            encrypted_message = client.recv(1024)
            decrypted_message = rsa.decrypt(encrypted_message, private_key).decode('utf-8')
            print(f"{nicknames[clients.index(client)]}: {decrypted_message}")
            broadcast(encrypted_message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break


# receive
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with: {str(address)}")
        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)

        print(f"Nickname of the client is: {nickname}")
        clients.append(client)
        broadcast(f"{nickname} connected to the server!\n".encode('utf-8'))
        client.send(public_key_pem.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server is running... ")

receive()
