import tkinter as tk 


class FinalPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        display_container = tk.Frame(master=self)
        display_container.pack(fill="both", expand=True)
        display_container.rowconfigure(0, minsize=30, weight=1)
        display_container.rowconfigure(1, minsize=50, weight=1)
        display_container.columnconfigure(0, weight=1)
        
        self.image = tk.Label(master=display_container, image=None, text="Image here...")
        self.image.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.win_captions = tk.Label(master=display_container, text="winning caption here...")
        self.win_captions.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        self.winners = tk.Label(master=display_container, text="player 4 get 1 point!")
        self.winners.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)

    def has_image(self):
        return self.image["image"]

    def upload_image(self, photo):
        self.image.configure(image=photo)
        self.image.image = photo

    def update_win_captions(self, captions):
        self.win_captions.configure(text="\n".join(captions))

    def update_winners(self, winners):
        players = " and ".join(winners)
        self.winners.configure(text=f"{players} gain 1 point")

    def reset(self):
        self.win_captions.configure(text="")
        self.winners.configure(text="")