import tkinter as tk 


class VotePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.has_options = False

        display_container = tk.Frame(master=self)
        display_container.pack(fill="both", expand=True, side="top")
        display_container.rowconfigure(0, minsize=100, weight=1)
        display_container.columnconfigure(0, minsize=200, weight=1)

        choice_container = tk.Frame(master=display_container)
        choice_container.grid(row=0, column=0, sticky="nsew")
        choice_container.rowconfigure([0,1], minsize=50, weight=1)
        choice_container.columnconfigure(0, weight=1)

        self.image = tk.Label(master=choice_container, image=None, text="Image here...")
        self.image.grid(row=0, column=0, sticky="nsew")

        self.options_container = tk.Frame(master=choice_container)
        self.options_container.grid(row=1, column=0, sticky="nsew")
        self.options_container.rowconfigure([0,1], weight=1)
        self.options_container.columnconfigure([0,1], weight=1)

        opt_1 = tk.Button(master=self.options_container, text="1. abc", command=lambda: self.vote("1"))
        opt_1.grid(row=0, column=0, sticky="nsew")
        opt_2 = tk.Button(master=self.options_container, text="2. abc", command=lambda: self.vote("2"))
        opt_2.grid(row=0, column=1, sticky="nsew")
        opt_3 = tk.Button(master=self.options_container, text="3. abc", command=lambda: self.vote("3"))
        opt_3.grid(row=1, column=0, sticky="nsew")
        opt_4 = tk.Button(master=self.options_container, text="4. abc", command=lambda: self.vote("4"))
        opt_4.grid(row=1, column=1, sticky="nsew")

    def vote(self, player_id):
        print("Player id >>", player_id)

        # controller.send("vote", player_id)

        # disable all options