import tkinter as tk 
from src.utils.fonts import LARGE_FONT

class LeaderboardPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        display_container = tk.Frame(master=self)
        display_container.pack(fill="both", expand=True)
        display_container.rowconfigure(0, weight=1)
        display_container.columnconfigure(0, weight=1)

        self.players_container = tk.Frame(master=display_container)
        self.players_container.grid(row=0, column=0, sticky="ew")
        self.players_container.rowconfigure(0, weight=1)
        self.players_container.columnconfigure(0, weight=1)

        btn_next = tk.Button(master=display_container, text="Next", font=LARGE_FONT, command=self.on_reset)
        btn_next.grid(row=1, column=0, sticky="nsew")

        self.after(5 * 1000, self.reset)

    def add_players(self, players: dict):
        # sort from highest to lowest
        sorted_players = sorted(players, key=lambda x: players[x][1], reverse=True)
        
        for index, player_id in enumerate(sorted_players):
            player = players[player_id]
            lbl_player = tk.Label(master=self.players_container, text=f"{player[0]}\t{player[1]}")
            lbl_player.grid(row=index, column=0, sticky="ew")

    def on_reset(self):
        self.controller.send("reset", None)
    
    def reset(self):
        for child in self.players_container.winfo_children():
            child.destroy()