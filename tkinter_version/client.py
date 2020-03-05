import tkinter as tk 
import socket_client

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        container = tk.Frame(self)
        container.pack()
        lbl = tk.Label(text="Started...")
        lbl.pack()
        self.ent = tk.Entry()
        self.ent.insert(0, "Send: ")
        self.ent.pack()
        btn = tk.Button(text="send", command=self.send)
        btn.pack()
        socket_client.connect("10.0.0.113", 5000)
        socket_client.start_listen(self.listen)

    def send(self):
        msg = self.ent.get()
        socket_client.send(msg)

    def listen(self, msg):
        print(msg)

App().mainloop()