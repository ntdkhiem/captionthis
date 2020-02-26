import socket
import pickle
import time

from threading import Thread

# global variable to be reuse
client_socket = None 

# connects to the server
def connect(ip, port, my_username, error_callback):

    global client_socket

    # create a socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to a given ip and port
        client_socket.connect((ip, port))
    except Exception as e:
        # connection error
        error_callback(f'Connection error: {str(e)}')
        return False
    
    # server expects username when connect therefore send this username
    print(client_socket.send(my_username.encode('utf-8')))

    return True


# sends a message to the server
def send(message):
    message = message.encode('utf-8')
    # print(message)
    print(client_socket.send(message))

# starts listening function in a thread
# incoming_message_callback - callback to be called when new message arrives
# error_callback - callback to be called on error
def start_listening(incoming_message_callback, error_callback):
    Thread(target=listen, args=(incoming_message_callback, error_callback), daemon=True).start()

# listen for incoming messages
def listen(incoming_message_callback, error_callback):
    while True:
        try:
            # assuming the server will always send back game object
            message = client_socket.recv(4096)

            game = pickle.loads(message)

            # return the game object to whatever it got called from
            incoming_message_callback(game)

        except Exception as e:
            error_callback(f'Reading error: {str(e)}')
