import shortuuid
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit, send
import game


app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app)

TOTAL_PLAYERS = 2
TOTAL_GAMES = 3
DURATION_PER_CAPTION = 60
rooms = {}
room_id = shortuuid.uuid()
players_ingame = 0
threaded_timers = {}

connected_clients = {}


def new_game():
    global players_ingame, room_id
    players_ingame = 0
    room_id = shortuuid.uuid()  
    rooms[room_id] = game.CaptionThisGame(room_id, total_players=TOTAL_PLAYERS, total_games=TOTAL_GAMES, game_duration=DURATION_PER_CAPTION)

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("join")
def on_join(data):
    global players_ingame
    username = data["username"]
    connected_clients[request.sid] = {"id": shortuuid.uuid()}

    if players_ingame < TOTAL_PLAYERS:
        if not rooms:
            rooms[room_id] = game.CaptionThisGame(room_id, total_players=TOTAL_PLAYERS, total_games=TOTAL_GAMES, game_duration=DURATION_PER_CAPTION)
        
        connected_clients[request.sid]["roomId"] = room_id
        
        join_room(room=room_id)

        rooms[room_id].add_player(connected_clients[request.sid]["id"], username)
        
        players_ingame += 1

        if players_ingame == TOTAL_PLAYERS:
            rooms[room_id].start_game()

        send(rooms[room_id].to_json(), room=room_id)

    print(f"[+] accepted client {username}:{request.sid}...")
    
    if players_ingame == TOTAL_PLAYERS:
        new_game()


@socketio.on("caption")
def on_caption(data):
    player = connected_clients[request.sid]
    game = rooms[player["roomId"]]
    
    if game.get_flag() == "reset":
        game.set_flag("caption")

    game.add_caption(player["id"], data["msg"])
    
    if game.all_players_submitted():
        game.set_flag("vote")
    
    send(game.to_json(), room=player["roomId"])

@socketio.on("vote")
def on_vote(data):
    player = connected_clients[request.sid]
    game = rooms[player["roomId"]]

    game.vote_caption(data["id"])

    if game.all_players_voted():
        game.set_flag("win")
        game.calculate_winners()

    send(game.to_json(), room=player["roomId"])

@socketio.on("new")
def on_new(data):
    player = connected_clients[request.sid]
    game = rooms[player["roomId"]]

    game.reset(data["newGame"])

    send(game.to_json(), room=player["roomId"])

if __name__ == "__main__":
    socketio.run(app, debug=True)