import tkinter as tk 

# custom packages
import pages

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
        
        self.show_frame("ConnectPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

        self.current_frame = page_name

    def connect(self, payload):
        '''Connect to the server then start to listen'''
        info = "Joining {}:{} as {}".format(*payload.values())
        self.frames["WaitPage"].update_info(info)
        self.show_frame("WaitPage")
        

if __name__ == "__main__":
    app = CaptionThis()
    app.geometry("1280x720")
    app.mainloop()