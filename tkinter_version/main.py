import tkinter as tk 
import pages
import socket_client

class CaptionThis(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.current_frame = ''

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
        
        self.show_frame("CaptionPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

        self.current_frame = page_name

    def connect(self, payload):
        '''Connect to the server then start to listen'''
        # # redirect client to wait page
        # info = "Joining {}:{} as {}".format(*payload.values())
        # self.frames["WaitPage"].update_info(info)
        # self.show_frame("WaitPage")

        # # connect to the server
        # if not socket_client.connect(**payload, error_callback=self.error_handler):
        #     return

        # socket_client.start_listen(self.server_message_handler, self.error_handler)

        self.frames["WaitPage"].update_info("Connecting...")
        self.show_frame("WaitPage")

    def server_message_handler(self, game):
        '''Handle responses from the server'''
        if not game.is_ready():
            info = f"Waiting for {game.players_left()} more players..."
            self.frames["WaitPage"].update_info(info)
        else:
            if game.get_flag() == "caption":
                if self.current_frame != "CaptionPage":
                    self.show_frame("CaptionPage")
                    self.current_frame = "CaptionPage"

                caption_page = self.frames["CaptionPage"]

                if not caption_page.has_image():
                    caption_page.create_image(game.get_image())

                caption_page.update_submission_count(game.get_caption_submissions())
            else:
                pass

    def error_handler(self, message):
        '''display error message to wait page and exit'''
        self.frames["WaitPage"].update_info(message)
        self.show_frame("WaitPage")
        self.after(10 * 1000, self.quit)
        

if __name__ == "__main__":
    app = CaptionThis()
    app.geometry("1280x720")
    app.mainloop()