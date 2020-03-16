import os
import json
import tkinter as tk 

# custom packages
from utils.fonts import *


class ConnectPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        lbl_title = tk.Label(master=self, text="Caption This!", font=LARGE_FONT)
        lbl_title.pack(pady=10, padx=10)
        
        # get previous details to prefill
        if os.path.isfile("prev_details.txt"):
            with open("prev_details.txt","r") as f:
                data = json.load(f)
                prev_ip = data["ip"]
                prev_port = data["port"]
                prev_username = data["username"]
        else:
            prev_ip = ''
            prev_port = ''
            prev_username = ''

        # container
        fr_info = tk.Frame(master=self)
        fr_info.pack(fill="both")
        fr_info.rowconfigure([0,1,2,3], minsize=50, weight=1)
        fr_info.columnconfigure([0,1], minsize=80, weight=1)

        lbl_ip = tk.Label(master=fr_info, text="Ip Address: ")
        self.ent_ip = tk.Entry(master=fr_info, width=150)
        self.ent_ip.insert(tk.END, prev_ip)
        lbl_ip.grid(row=0, column=0, sticky="e", padx=10)
        self.ent_ip.grid(row=0, column=1, sticky="w", padx=10)

        lbl_port = tk.Label(master=fr_info, text="Port: ")
        self.ent_port = tk.Entry(master=fr_info, text=prev_port, width=150)
        self.ent_port.insert(tk.END, prev_port)
        lbl_port.grid(row=1, column=0, sticky="e", padx=10)
        self.ent_port.grid(row=1, column=1, sticky="w", padx=10)

        lbl_username = tk.Label(master=fr_info, text="Username: ")
        self.ent_username = tk.Entry(master=fr_info, text=prev_username, width=150)
        self.ent_username.insert(tk.END, prev_username)
        lbl_username.grid(row=2, column=0, sticky="e", padx=10)
        self.ent_username.grid(row=2, column=1, sticky="w", padx=10)

        btn_connect = tk.Button(master=self, text="connect", command=lambda: self.join())
        btn_connect.pack(ipadx=15, ipady=5)

    def join(self):
        '''save user's info into a file then call controller to connect to the server'''
        payload = {
            "ip": self.ent_ip.get(),
            "port": int(self.ent_port.get().strip()),
            "username": self.ent_username.get()
        }

        # there is an empty field
        if "" in payload.values():
            return
        
        with open("prev_details.txt", "w") as f:
            json.dump(payload, f)
        
        self.controller.connect(payload)

    def reset(self):
        return
