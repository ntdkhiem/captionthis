import socket, pickle, uuid
from _thread import start_new_thread
from src.game import CaptionThisGame

SERVER = "10.0.0.113"
PORT = 5000
TOTAL_PLAYERS = 3

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# allow to reuse the port
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server_socket.bind((SERVER,PORT))
except socket.error as e:
    print(str(e))

# listen to unlimited connections
server_socket.listen()

connect_clients = {}

print(f"Listening for connections on {SERVER}:{PORT}...")

def receive_message(client_socket):
    try:
        message = client_socket.recv(2048)

        if not len(message):
            return False

        return message.decode("utf-8")
    except:
        return False

def send_to_all_ingame(game_id, msg):
    for client_socket, data in connect_clients.items():
        if data["gameId"] == game_id:
            client_socket.send(msg)

def disconnect_all_ingame(game_id):
    for client_socket, data in connect_clients.items():
        if data["gameId"] == game_id:
            remove_socket(client_socket)

def remove_socket(client_socket):
    if connect_clients.get(client_socket) != None:
        del connect_clients[client_socket]

def client_handler(conn):
    global connect_clients, game_list, current_total_player, game_id
    
    player = connect_clients[conn]
    game = game_list[player["gameId"]]

    while True:
        try:
            msg_cmd = receive_message(conn)

            if not msg_cmd:    
                game.remove_player(player["id"])
                
                # if there is new game then remove this game if not playable
                if game.get_gameId() != game_id:
                    if not game.is_playable():
                        print(f"Removing game {player['gameId']}")
                        disconnect_all_ingame(player["gameId"])
                        del game_list[player["gameId"]]
                else:
                    # client disconnected while at the wait screen therefore add new connection to this game
                    current_total_player -= 1
                
                remove_socket(conn)

                break
            

            if msg_cmd[0] == "c":
                cap_text = msg_cmd[1:]
                print("adding caption")
                game.add_caption(player["id"], cap_text)

                if game.all_players_submitted():
                    game.set_flag("vote")
            
            elif msg_cmd[0] == "v":
                player_id = msg_cmd.split()[1]
                print("voting caption")
                game.vote_caption(player_id)

                if game.all_players_voted():
                    game.set_flag("final")

                game.calculate_winners()

            elif msg_cmd[0] == "r":
                game.reset()

            send_to_all_ingame(player["gameId"], pickle.dumps(game))

        except Exception as e:
            print("Error from client_handler:", str(e))
            break

    print(f"Closed connection from {player['username']}")
    conn.close()


current_total_player = 0
game_id = uuid.uuid1().int
game_list = {game_id:CaptionThisGame(game_id, TOTAL_PLAYERS)}

while True:
    client_socket, client_address = server_socket.accept()
    try:
        # client should send a username right away, receive it
        username = receive_message(client_socket)

        if username is False:
            print("Client disconnected before sending username")
            continue
        
        print("Accepting new connection from {}:{}, username: {}".format(*client_address, username))

        connect_clients[client_socket] = {"id": str(uuid.uuid1().int), "username": username}

        if current_total_player < TOTAL_PLAYERS:
            connect_clients[client_socket]["gameId"] = game_id
            current_total_player += 1

            game_list[game_id].add_player(connect_clients[client_socket]["id"], username)

            send_to_all_ingame(game_id, pickle.dumps(game_list[game_id]))

        # TODO: the game isn't start when full of players
        if current_total_player == TOTAL_PLAYERS:
            print(f"start game {game_id}")
            game_list[game_id].start_game()

            # init new game
            current_total_player = 0
            game_id = uuid.uuid1().int
            game_list[game_id] = CaptionThisGame(game_id, TOTAL_PLAYERS)

        start_new_thread(client_handler, (client_socket,))

    except socket.error as e:
        print("Error from main loop:", str(e))
        break
    