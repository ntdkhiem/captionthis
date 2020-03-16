import socket
import pickle
from threading import Thread

client_socket = None 

def connect(ip=None, port=None, username=None, error_callback=None):
    global client_socket 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((ip, port))
    except Exception as e:
        error_callback(f"Connection error: {str(e)}")
        return False
    # server expects username when connect
    client_socket.send(username.encode("utf-8"))
    return True

def send(msg):
    client_socket.send(msg.encode("utf-8"))

# start a thread to listen
def start_listen(incoming_message_callback, error_callback):
    Thread(target=listen, args=(incoming_message_callback, error_callback), daemon=True).start()

def listen(incoming_message_callback, error_callback):
    global client_socket
    while True:
        try:
            # server will send game object
            res = client_socket.recv(4096)
            game = pickle.loads(res)
            incoming_message_callback(game)
        except Exception as e:
            error_callback(f"Reading Error from listen: {str(e)}")
