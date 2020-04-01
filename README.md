# Caption This
A simple caption game to find who is the meme lord! 

The game consists of 10 matches with a library of non-caption memes. 

Each player will create their own unique and creative caption for each meme then vote for the best caption among all. 

The winner will be determine after all matches and will *unofficially* be the memelord!

### How To Play
- Install requirements before start
```bash
pip install -r requirements.txt
```
- Input your Ip Address ([how to find!](https://www.posim.com/knowledgebase/finding-ip-address-windows/)) in `src/socket_server.py` line 6

- Start the server
```bash
python src\socket_server.py
```
- Play
```bash
python app.py
```

### Notes
- You can change things such as **total players**, **total matches**, **match's duration** in `src/socket_server.py`
- You can add more memes (without caption!) in `src/images`

### Warnings
- The server will forcefully close the game if there is only one player
- Any other errors will be display on the client's screen. 
