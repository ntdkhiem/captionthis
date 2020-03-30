import socket, pickle, uuid
from _thread import start_new_thread
from threading import Timer, Lock
from game import CaptionThisGame

SERVER = "10.0.0.60"
PORT = 5000
TOTAL_PLAYERS = 2
DURATION_OF_CAPTION = 120

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

def send_to_all_ingame(game_id, msg, except_socket=None):
    for client_socket, data in connect_clients.items():
        if data["gameId"] == game_id and client_socket != except_socket:
            client_socket.send(msg)

def disconnect_all_ingame(game_id):
    remove_clients = []

    for client_socket, data in connect_clients.items():
        if data["gameId"] == game_id:
            remove_clients.append(client_socket)
            client_socket.close()

    # to avoid dictionary changed size
    for client in remove_clients:
        remove_socket(client)

def remove_socket(client_socket):
    if connect_clients.get(client_socket) != None:
        del connect_clients[client_socket]

def time_up(game_id):
    '''
        Stop caption submission and proceed to next stage
    '''
    global game_list
    game = game_list[game_id]
    game.set_flag("vote")
    send_to_all_ingame(game_id, pickle.dumps(game.to_json()))

def client_handler(conn):
    global connect_clients, game_list, current_total_player, game_id, threaded_timers
    
    player = connect_clients[conn]
    game = game_list[player["gameId"]]

    while True:
        try:
            msg_cmd = receive_message(conn)

            if not msg_cmd:    
                if game_list.get(game.get_gameId()):
                    game.remove_player(player["id"])
                    
                    if game.get_gameId() == game_id:
                        current_total_player -= 1
                    else:
                        if not game.is_playable():
                            print(f"Removing game {player['gameId']}")

                            game.set_flag("quit")
                            send_to_all_ingame(game.get_gameId(), pickle.dumps(game.to_json()), except_socket=conn)

                            disconnect_all_ingame(game.get_gameId())
                            del game_list[game.get_gameId()]
                    remove_socket(conn)
                break
            

            if msg_cmd[0] == "c":
                cap_text = msg_cmd[1:]
                if game.get_flag() == "reset":
                    game.set_flag("caption")
                game.add_caption(player["id"], cap_text)

                # set timer when first captions submitted
                if len(game.get_captions()) == 1:
                    threaded_timers[game.get_gameId()] = Timer(DURATION_OF_CAPTION, time_up, args=(game.get_gameId(),))
                    threaded_timers[game.get_gameId()].start()
                    
                    game_list[game.get_gameId()].start_timer = True

                if game.all_players_submitted():
                    game.set_flag("vote")
                    # cancel timer if exist
                    if threaded_timers[game.get_gameId()].is_alive():
                        threaded_timers[game.get_gameId()].cancel()
                        del threaded_timers[game.get_gameId()]
            
            elif msg_cmd[0] == "v":
                player_id = msg_cmd.split()[1]
                game.vote_caption(player_id)

                if game.all_players_voted():
                    game.set_flag("final")

                game.calculate_winners()

            elif msg_cmd[0] == "r":
                game.reset()

            send_to_all_ingame(game.get_gameId(), pickle.dumps(game.to_json()))

        except Exception as e:
            print("Error from client_handler:", str(e))
            break

    print(f"Closed connection from {player['username']}")
    conn.close()


current_total_player = 0
game_id = uuid.uuid1().int
game_list = {game_id:CaptionThisGame(game_id, TOTAL_PLAYERS, DURATION_OF_CAPTION, Lock())}
threaded_timers = {}

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

            if current_total_player == TOTAL_PLAYERS:
                game_list[game_id].start_game()
                
            send_to_all_ingame(game_id, pickle.dumps(game_list[game_id].to_json()))

        if current_total_player == TOTAL_PLAYERS:
            # init new game
            current_total_player = 0
            game_id = uuid.uuid1().int
            game_list[game_id] = CaptionThisGame(game_id, TOTAL_PLAYERS, DURATION_OF_CAPTION, Lock())

        start_new_thread(client_handler, (client_socket,))

    except socket.error as e:
        print("Error from main loop:", str(e))
        break
    