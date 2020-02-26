import os
import random

# TODO: Use lock 
class CaptionThisGame:

    def __init__(self, gameId):
        self.players = {}
        # self.players = {
        #   'UniqueID': ['kevin', 0]
        # }
        self.caption_texts = {}
        # self.captions_texts = {
        #   'UniqueID': ['caption_text', 0]
        # }
        self.total_votes = 0
        self.winners = []
        self.image = self.get_image()
        self.ready = False
        self.gameId = gameId
        # flag: wait, caption, vote, final to indicate when to switch page
        self.flag = 'wait'

    def is_ready(self): 
        return self.ready

    # def get_gameId(self):
    #     return self.gameId
    
    # Get random image from ./images
    # TODO: uncomment this
    def get_image(self):
        return random.choice(os.listdir('images'))
        # return 'image.jpg'

    def set_flag(self, id):
        self.flag = id

    def add_player(self, player_id, player_name):
        # print(f"Adding {player_name} to the game.")
        self.players[player_id] = [player_name, 0]

    # Assuming in Captioning Page: 
    # Add caption text to caption_texts
    def add_caption(self, playerId, caption_text):
        self.caption_texts[playerId] = [caption_text, 0]
            
    # If the length of caption_texts is equal to the length of players then assume everyone submitted
    def all_captions_submitted(self): 
        return True if len(self.caption_texts) == len(self.players) else False

    # upvote a caption text
    def vote_caption(self, player_id):
        self.total_votes += 1
        self.caption_texts[player_id][1] += 1
        # print(f"New vote. Current total: {self.total_votes}")

    # if total votes equal total players then assume everyone voted
    def all_captions_voted(self):
        return True if self.total_votes == len(self.players) else False

    # Return the player object with the most voted caption text
    def caption_winner(self):
        if not self.winners:
            winners_id = []
            most_votes = 0
            for player_id, value in self.caption_texts.items():
                # Get total votes in [caption, votes]
                if value[1] > most_votes:
                    winners_id = [player_id]
                    most_votes = value[1]
                elif value[1] == most_votes:
                    winners_id.append(player_id)
            
            # add bonus points to these winner
            for player in winners_id:
                self.players[player][1] += 1
                self.winners.append(self.players[player][0])

    def remove_player(self, player_id):
        del self.players[player_id]
        if self.caption_texts.get(player_id):
            del self.caption_texts[player_id]
        print(f'[*] Removing {player_id} from game_id={self.gameId}')


    def reset(self):
        if self.winners:
            self.caption_texts = {}
            self.total_votes = 0
            self.image = self.get_image()
            self.winners = []
