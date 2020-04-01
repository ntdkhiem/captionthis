import tkinter as tk
from src.utils.fonts import LARGE_FONT

class FinalPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        display_container = tk.Frame(master=self)
        display_container.pack(fill="both", expand=True)
        display_container.rowconfigure(0, minsize=100, weight=1)
        display_container.columnconfigure(0, weight=1)
        
        self.winner = tk.Label(master=display_container, text="{} is the unofficial meme lord!!", font=LARGE_FONT)
        self.winner.grid(row=0, column=0, sticky="nsew")

        btn_new_game = tk.Button(master=display_container, text="New Game", command=self.new_game)
        btn_new_game.grid(row=1, column=0, sticky="ew")

    def update_winner(self, winners):
        if len(winners) == 1:
            self.winner.configure(text=f"Congratulation! {winners[0]} is the meme lord. (unofficially)")
        else:
            self.winner.configure(text=f"Congratulation! {' and '.join(winners)} are the meme lord. (unofficially")

    def new_game(self):
        self.controller.send("new", "")
    
    def reset(self):
        self.winner.configure(text="")