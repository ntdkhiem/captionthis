import tkinter as tk 
import functools
from utils.fonts import LARGE_FONT


class VotePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.has_options = False

        display_container = tk.Frame(master=self)
        display_container.pack(fill="both", expand=True, side="top")
        display_container.rowconfigure([0,1], minsize=50, weight=1)
        display_container.columnconfigure(0, weight=1)

        choice_container = tk.Frame(master=display_container)
        choice_container.grid(row=0, column=0, sticky="nsew")
        choice_container.rowconfigure(0, minsize=50, weight=1)
        choice_container.columnconfigure(0, minsize=70, weight=1)

        self.image = tk.Label(master=choice_container, image=None, text="Image here...")
        self.image.grid(row=0, column=0, sticky="nsew")

        info_container = tk.Frame(master=choice_container)
        info_container.grid(row=0, column=1, sticky="nsew")
        info_container.rowconfigure([0,1], weight=1)

        self.submitted_votes = tk.Label(master=info_container, text="0 vote", font=LARGE_FONT)
        self.submitted_votes.grid(row=0, column=0, sticky="nsew", padx=10)

        self.countdown = tk.Label(master=info_container, text="60 seconds", font=LARGE_FONT)
        self.countdown.grid(row=1, column=0, sticky="nsew", padx=10)

        self.options_container = tk.Frame(master=display_container)
        self.options_container.grid(row=1, column=0, sticky="nsew")
        self.options_container.rowconfigure([0,1], weight=1)
        self.options_container.columnconfigure([0,1], weight=1)

    def has_image(self):
        return self.image["image"]

    def upload_image(self, photo):
        self.image.configure(image=photo)
        self.image.image = photo

    def update_submission_count(self, total_votes):
        self.submitted_votes.configure(text=f"{total_votes} votes")

    def create_options(self, captions: dict) -> None:
        j = 0
        if not self.has_options:
            for i, (player_id, value) in enumerate(captions.items()):
                btn = tk.Button(master=self.options_container, text=value[0], command=functools.partial(self.vote, player_id))
                btn.grid(row=j, column=i % 2, sticky="nsew")
                if i % 2 == 1:
                    j += 1

            self.has_options = True

    # TODO: only vote for one id 
    def vote(self, player_id):
        print(f"Voting for {player_id}")
        self.controller.send("vote", player_id)

        # disable all options
        for child in self.options_container.winfo_children():
            child.configure(state="disabled")

    def reset(self):
        self.has_options = False

        for child in self.options_container.winfo_children():
            child.destroy()
