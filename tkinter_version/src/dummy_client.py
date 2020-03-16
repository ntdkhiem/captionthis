import socket
import pickle
import time

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(("10.0.0.113", 5000))

client.send("kevin".encode("utf-8"))
time.sleep(0.5)
game = client.recv(4096)
game = pickle.loads(game)
print(game.get_players_ingame())
# client.send("c hello world".encode("utf-8"))
time.sleep(2)
# client.send(f"v ")
client.close()