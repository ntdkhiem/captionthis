import pytest
import socket
import pickle
import time

def listener(socket):
    time.sleep(0.2)
    try:
        msg = socket.recv(4096)
        game = pickle.loads(msg)
        return game
    except Exception as e:
        print(str(e))
        return None

class TestServer:

    def test_send_username(self):
        username = "kevin"
        self.c_socket.send(username.encode("utf-8"))
        assert listener(self.c_socket) != None        

    # time.sleep(1)

    # def test_submit_caption(self, client_socket):
    #     client_socket.send("c this is a test".encode("utf-8"))

    #     assert listener(client_socket) != None