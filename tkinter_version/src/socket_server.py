import socket 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("10.0.0.113", 5000))

server.listen()
print("listening")

while True:
    client, addr = server.accept()
    print("Got a connection")
    while True:
        msg = client.recv(1024).decode("utf-8")
        print(msg)
        client.send(msg.encode('utf-8'))