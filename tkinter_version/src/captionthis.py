import tkinter as tk 
import pages
from src import socket_client
from PIL import Image, ImageTk


class CaptionThis(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.current_frame = ''
        self.current_image = None

        # where I will stack and switch frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in pages.__all__:
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("ConnectPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        if self.current_frame != page_name:
            frame = self.frames[page_name]
            frame.tkraise()

            self.current_frame = page_name

    def connect(self, payload):
        '''Connect to the server then start to listen'''

        # connect to the server
        if not socket_client.connect(**payload, error_callback=self.error_handler):
            return

        socket_client.start_listen(self.server_message_handler, self.error_handler)
        
        # redirect client to wait page
        info = "Joining {}:{} as {}".format(*payload.values())
        self.frames["WaitPage"].update_info(info)
        self.show_frame("WaitPage")

    def send(self, cmd, msg):

        if cmd == "caption":
            socket_client.send(f"c {msg}")
        elif cmd == "vote":
            socket_client.send(f"v {msg}")
        elif cmd == "reset":
            socket_client.send(f"r")

    def server_message_handler(self, game):
        '''Handle responses from the server'''
        if not game.is_ready():
            info = f"Waiting for {game.get_players_left()} more players..."
            self.frames["WaitPage"].update_info(info)
        else:
            if game.get_flag() == "reset":
                self.reset()

            if game.get_flag() == "caption":
                self.show_frame("CaptionPage")

                caption_page = self.frames["CaptionPage"]

                if not caption_page.has_image():
                    caption_page.upload_image(self.create_image(game.get_image()))

                caption_page.update_submission_count(game.get_caption_submissions())
            
            elif game.get_flag() == "vote":
                self.show_frame("VotePage")
                
                vote_page = self.frames["VotePage"]
                
                if not vote_page.has_image():
                    vote_page.upload_image(self.create_image(game.get_image()))
                    
                if not vote_page.has_options():
                    vote_page.create_options(game.get_captions())
                    
                vote_page.update_submission_count(game.get_total_votes())
                
            elif game.get_flag() == "final":
                self.show_frame("FinalPage")
                
                final_page = self.frames["FinalPage"]
                
                final_page.display_caption(game.get_win_captions())
                
                final_page.display_winners(game.get_winners())
                
                # switch to leaderboard page in 5 seconds 
                self.after(5 * 1000, lambda: self.switch_to_leaderboard(game))
    
    def switch_to_leaderboard(self, game):
        self.frames["LeaderboardPage"].add_players(game.players)
        self.show_frame("LeaderboardPage")

    def create_image(self, source):
        if not self.current_image:
            image = Image.open(f"images\\{source}")
            photo = ImageTk.PhotoImage(image)
            self.current_image = photo
        return self.current_image

    def reset(self):
        for frame in self.frames.values():
            frame.reset()

    def error_handler(self, message):
        '''display error message to wait page and exit'''
        self.frames["WaitPage"].update_info(message)
        self.show_frame("WaitPage")
        # quit after 10 seconds
        self.after(10 * 1000, self.quit)
