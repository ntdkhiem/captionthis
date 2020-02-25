import socket
import select
import pickle
import uuid

from game import CaptionThisGame

TOTAL_PLAYERS = 2

server = "10.0.0.113"
port = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# allow to reuse the port
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try: 
    server_socket.bind((server, port))
except socket.error as e:
    print(str(e))

# listen to unlimited connections
server_socket.listen()

# list of sockets for select.select()
sockets_list = [server_socket]

# list of connected clients
clients = {}

print(f'Listening for connections on {server}:{port}...')

current_total_player = 0
game_id = 0
game_list = [CaptionThisGame(game_id)]

# receive command from the client
def receive_message(client_socket):
    try:
        message = client_socket.recv(2048)

        # if no data is present thefore assume client gracefully closed a connection
        if not len(message):
            return False 

        return message.decode('utf-8')
    except:
        return False

# Send message to all clients in the game 
def send_to_all(game_id, msg):
    for client_socket, data in clients.items():
        if data['gameId'] == game_id:
            # print(f"send new game object to {data['username']}")
            client_socket.send(msg)

# remove socket from sockets_list and clients
def remove_socket(client_socket):
    # remove from list of socket to be monitor
    sockets_list.remove(client_socket)
    # remove from list of clients 
    del clients[client_socket]

# Main function
while True: 
    # give this list of sockets for select.select() to monitor
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            try:
                # client should send a username right away, receive it
                username = receive_message(client_socket)

                # client disconnected before sending the username
                if username is False:
                    print("client disconnected before sending username")
                    continue


                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, username))

                # add this socket to the list to be monitor
                sockets_list.append(client_socket)

                # save username and unique id too!
                clients[client_socket] = {'id': str(uuid.uuid1().int), 'username': username}

                # add game object to this socket
                if current_total_player <= TOTAL_PLAYERS:
                    clients[client_socket]['gameId'] = game_id
                    current_total_player += 1

                    # start the game when full
                    if current_total_player >= TOTAL_PLAYERS:
                        game_list[game_id].ready = True
                        
                # Add client as player to the game with unique ID
                game_list[game_id].add_player(clients[client_socket]['id'], username)

                # send a game object to all clients in the game
                send_to_all(game_id, pickle.dumps(game_list[game_id]))

                print(f'Current game id = {game_list[game_id].gameId}')
                print(f'current total players: {current_total_player}')

                # initialize a new game for the next client
                if current_total_player >= TOTAL_PLAYERS:
                    current_total_player = 0
                    game_id += 1
                    # TODO: refractor this since its will be useless if there is no next client
                    game_list.append(CaptionThisGame(game_id))


            except socket.error as e:
                print(str(e))

        # existed socket is sending a message
        else:
            message_command = receive_message(notified_socket)

            # client disconnected, cleanup
            if message_command is False:
                print(f'Closed connection from {clients[notified_socket]["username"]}')

                # remove current client from the game
                game_list[clients[notified_socket]['gameId']].remove_player(clients[notified_socket]["id"])
                
                # Remove the game if there is no player 
                # TODO: take care of the hack that use game_list[gameId]
                if (len(game_list[clients[notified_socket]['gameId']].players) == 0) :
                    # Turn the game into None for now
                    game_list[clients[notified_socket]['gameId']] = None

                remove_socket(notified_socket)
                print(f"[*] Removing {notified_socket} from the server")

                # TODO: notify all clients about this removal
                continue
            
            # TODO: check if game still exist in memory

            # get client's info 
            info = clients[notified_socket]
            game = game_list[info['gameId']]

            # client wants to submit a caption text (msg: "c caption text")
            if message_command[0] == "c":
                caption_text = message_command[1:]
                game = game_list[info['gameId']]
                game.add_caption(info['id'], caption_text)
                
            # client wants to vote a caption (msg: "v player_id")
            elif message_command[0] == "v":
                player_id = message_command[1:]
                game = game_list[info['gameId']]
                game.vote_caption(player_id)

            # client must call caption_winner from the server in order for data to stay persistent across other clients
            elif message_command[0] == "f":
                game.caption_winner()

            # TODO: clients wants to reset the game
            elif message_command[0] == "r":
                game.reset()
                
            # send back an updated game object
            notified_socket.send(pickle.dumps(game))


    # handle any socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]

