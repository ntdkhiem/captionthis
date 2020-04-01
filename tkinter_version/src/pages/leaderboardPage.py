import tkinter as tk 
from src.utils.fonts import LARGE_FONT, SMALL_FONT

class LeaderboardPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        display_container = tk.Frame(master=self)
        display_container.pack(fill="both", expand=True)
        display_container.rowconfigure(1, weight=1)
        display_container.columnconfigure(0, weight=1)

        dashboard_container = tk.Frame(master=display_container)
        dashboard_container.grid(row=0, column=0, sticky="nsew")

        self.joined_players = tk.Label(master=dashboard_container, text="Joined players: {}", font=SMALL_FONT)
        self.joined_players.grid(row=0, column=0)

        self.played_games = tk.Label(master=dashboard_container, text="Games: {}/{}", font=SMALL_FONT)
        self.played_games.grid(row=0, column=1)

        self.players_container = tk.Frame(master=display_container)
        self.players_container.grid(row=1, column=0, sticky="ew")
        self.players_container.rowconfigure(0, weight=1)
        self.players_container.columnconfigure(0, weight=1)

        btn_next = tk.Button(master=display_container, text="Next", font=LARGE_FONT, command=self.on_reset)
        btn_next.grid(row=2, column=0, sticky="nsew")

        self.after(5 * 1000, self.reset)

    def add_players(self, players: dict):
        # sort from highest to lowest
        sorted_players = sorted(players, key=lambda x: players[x][1], reverse=True)
        
        for index, player_id in enumerate(sorted_players):
            player = players[player_id]
            lbl_player = tk.Label(master=self.players_container, text=f"{player[0]}\t{player[1]}")
            lbl_player.grid(row=index, column=0, sticky="ew")

    def update_dashboard(self, game):
        self.joined_players.configure(text=f"Joined Players: {len(game['players'])}/{game['total_players']}")
        self.played_games.configure(text=f"Games: {game['games_played']}/{game['total_games']}")

    def on_reset(self):
        self.controller.send("reset", None)
    
    def reset(self):
        for child in self.players_container.winfo_children():
            child.destroy()
        
        self.joined_players.configure(text="Joined Players: {}/{}")
        self.played_games.configure(text="Games: {}/{}")