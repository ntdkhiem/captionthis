import socket
from threading import Thread

client = None 

def connect(ip, port):
    global client 

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("10.0.0.113", 5000))

def send(msg):
    msg = msg.encode('utf-8')
    client.send(msg)

def start_listen(incoming_callback):
    Thread(target=listen, args=(incoming_callback,), daemon=True).start()

def listen(incoming_callback):
    while True:
        msg = client.recv(1024)
        incoming_callback(msg.decode('utf-8'))