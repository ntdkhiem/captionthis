import os
import sys

from kivy.app import App 
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen

import socket_client
# TODO: cache image locally
TOTAL_PLAYERS = 2

# The page for connecting to the server
class ConnectPage(GridLayout): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # create two columns
        self.cols = 2

        # Read settings from text file, or use empty strings
        if os.path.isfile("prev_details.txt"):
            with open("prev_details.txt","r") as f:
                d = f.read().split(",")
                prev_ip = d[0]
                prev_port = d[1]
                prev_username = d[2]
        else:
            prev_ip = ''
            prev_port = ''
            prev_username = ''

        # Server's address to connect to
        self.add_widget(Label(text="IP: "))
        self.ip = TextInput(text=prev_ip, multiline=False)
        self.add_widget(self.ip)
        # Server's port to connect to
        self.add_widget(Label(text='Port:'))
        self.port = TextInput(text=prev_port, multiline=False)
        self.add_widget(self.port)
        # Username to be play
        self.add_widget(Label(text='Username:'))
        self.username = TextInput(text=prev_username, multiline=False)
        self.add_widget(self.username)
        # Submit button
        self.add_widget(Label()) # take up the spot in column 1
        self.join = Button(text="Join")
        self.join.bind(on_press=self.join_button)
        self.add_widget(self.join)

    def join_button(self, instance):
        port = self.port.text
        ip = self.ip.text
        username = self.username.text
        with open("prev_details.txt","w") as f:
            f.write(f"{ip},{port},{username}")
            f.close()
        
        info = f"Joining {ip}:{port} as {username}"
        ct_app.wait_page.update_info(info)
        ct_app.screen_manager.current = 'Wait'
        # Connect to the server after switching to Wait page
        Clock.schedule_once(self.connect, 1)

    
    # connects to the server
    # second param is send by Clock which is useless
    def connect(self, _): 
        port = int(self.port.text)
        ip = self.ip.text
        username = self.username.text

        if not socket_client.connect(ip, port, username, show_error): 
            return 
        
        print("Start listening for responses...")
        socket_client.start_listening(ct_app.incoming_message_handler, show_error)

        info = f"Connecting..."
        ct_app.wait_page.update_info(info)

        # ct.screen_manager.current = 'Wait'
    

class WaitPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # create one column
        self.cols = 1

        self.message = Label(halign="center", valign="middle")

        # A hack to resize the font size when the widget gets resize
        self.message.bind(width=self.update_text_width)
        
        # add text widget to the layout 
        self.add_widget(self.message)

    # Update text widget with this new message
    def update_info(self, message):
        self.message.text = message

    # Called on label width update, so we can set text width properly - to 90% of label wid
    def update_text_width(self, *_):
        self.message.text_size = (self.message.width * 0.9, None)


class CaptionPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.rows = 2
        self.cols = 1

        # FIRST ROW - will be for viewing (image, time, number of captions) takes up 95% of the height of the screen 
        view_container = GridLayout(cols=2, height=Window.size[1] * 0.9, size_hint_y=None)
        # Image widget
        self.image = Image(source="images/Blank-Nut-Button.jpg")
        view_container.add_widget(self.image)

        # A container contains time and captions
        self.info_container = GridLayout(cols=1, rows=2)
        self.submissions = Label(halign="center", valign="middle", font_size=20)
        self.clock = Label(halign="center", valign="middle", text="60 seconds", font_size=20)
        self.info_container.add_widget(self.submissions)
        self.info_container.add_widget(self.clock)
        view_container.add_widget(self.info_container)
        self.add_widget(view_container)

        # SECOND ROW
        self.caption = TextInput(width=Window.size[0]*0.8, size_hint_x=None, multiline=False)
        self.send = Button(text="Send")
        self.send.bind(on_release=self.submit)

        # container for sending message
        submission_container = GridLayout(cols=2)
        submission_container.add_widget(self.caption)
        submission_container.add_widget(self.send)
        self.add_widget(submission_container)

    # TODO: could not update image's source
    def update_image(self, link):
        print(f"Got {link}")
        print(f"self.image: {self.image}")
        print(f"self.image.source: {self.image.source}")
        self.image.source = f"images/{link}"
        # self.image.norm_image_size
        print(f"self.image.source: {self.image.source}")
        # self.image.reload()

    def update_submission_count(self, submission_object):
        print("Updating submission count...")
        if not submission_object:
            submission_count = 0
        else:
            submission_count = len(submission_object.values())
        self.submissions.text = f"{submission_count} Caption(s)"

    def enable_submission_container(self):
        self.caption.disabled = False
        self.send.disabled = False

    def submit(self, instance):
        # print("Sending the caption to the server...")
        caption = self.caption.text

        # send to server
        socket_client.send(f"c {caption}")

        # clear field value
        self.caption.text = ''

        # disable the submission container to prevent extra submit
        self.caption.disabled = True
        self.send.disabled = True


class VotePage(GridLayout): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2
        self.captions_dict = {}
        self.hasOptions = False

        # FIRST COLUMN - will contain image and all options to vote
        view_container = GridLayout(cols=1, rows=2, width=Window.size[0] * 0.8, size_hint_x=None)
        self.image = Image()
        self.options_container = GridLayout(cols=2, rows=2)
        # options_container.add_widget(Label(text="Option #1"))
        # options_container.add_widget(Label(text="Option #2"))
        # options_container.add_widget(Label(text="Option #3"))
        # options_container.add_widget(Label(text="Option #4"))
        
        view_container.add_widget(self.image)
        view_container.add_widget(self.options_container)
        self.add_widget(view_container)
        
        
        # SECOND COLUMN - will contain time counter and number of votes
        info_container = GridLayout(cols=1, rows=2)
        self.submissions = Label(halign="center", valign="middle", font_size=20)
        self.clock = Label(halign="center", valign="middle", text="30 seconds", font_size=20)
        info_container.add_widget(self.submissions)
        info_container.add_widget(self.clock)
        self.add_widget(info_container)

    def add_options(self, captions_dict):
        self.captions_dict = captions_dict
        for player_id, lst in captions_dict.items():
            btn = Button(text=lst[0])
            btn.bind(on_release=self.on_click)
            self.options_container.add_widget(btn)
        self.hasOptions = True

    def clear_options(self):
        self.hasOptions = False
        self.options_container.clear_widgets()

    def update_image(self, link):
        pass 

    def update_submission_count(self, votes):
        self.submissions.text = f"{votes} Vote(s)"

    # TODO: refractor this so that the button will always be unique
    def on_click(self, instance):
        print("sending a message")
        # find the voted caption's player 
        for player_id, lst in self.captions_dict.items():
            if instance.text == lst[0]:
                # send player_id to the server
                socket_client.send(f"v {player_id}")
        
        # TODO: disable all options
        



class FinalPage(GridLayout): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.rows = 3

        self.image = Label(height=Window.size[1] * 0.5, text="Image Here...", size_hint_y=None)
        self.caption = Label(size_hint_y=None)
        self.winner = Label()
        self.add_widget(self.image)
        self.add_widget(self.caption)
        self.add_widget(self.winner)

        # switch to leaderboard page after 5 seconds
        # print("scheduling switch_to_leaderboard in 5 seconds")
        # Clock.schedule_once(self.switch_to_leaderboard, 5)

    def update_image(self):
        pass 

    def update_caption(self, caption):
        self.caption.text = caption

    def update_winner(self, winners):
        msg = ', '.join(winners)
        self.winner.text = f"{msg} get 1 point."

    def switch_to_leaderboard(self, _):
        # print("Switching to Leadboard Page")
        # if not ct_app.screen_manager.has_screen('Leaderboard'):
        # initialize leadboard page
        ct_app.create_leaderboard_page()
        # print("switching now...")
        ct_app.screen_manager.current = 'Leaderboard'


class LeaderboardPage(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2

        self.leaderboard_container = GridLayout(width=Window.size[0] * 0.9, size_hint_x=None, rows=5)
        self.leaderboard_container.add_widget(Label(text="Leaderboard", font_size=20))
        self.add_players()
        # leaderboard_container.add_widget(Label(text="5. Player 5"))
        self.next = Button(text="next game")
        self.next.bind(on_release=self.on_reset)
        self.add_widget(self.leaderboard_container)
        self.add_widget(self.next)

    def add_players(self):
        for id, value in ct_app.game_object.players.items():
            self.leaderboard_container.add_widget(Label(text=f"{value[0]}               {value[1]} point"))

    def clear_winners(self):
        self.leaderboard_container.clear_widgets()

    def on_reset(self, instance):
        socket_client.send("r")
        
class CaptionThisApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_object = None

    def build(self):

        self.screen_manager = ScreenManager()

        # Create a screen for ConnectPage then add to screenManager
        self.connect_page = ConnectPage()
        screen_connect = Screen(name='Connect')
        screen_connect.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen_connect)

        # Wait page
        self.wait_page = WaitPage()
        screen_wait = Screen(name='Wait')
        screen_wait.add_widget(self.wait_page)
        self.screen_manager.add_widget(screen_wait)
        
        return self.screen_manager
        # return CaptionPage()
        
    # Caption page
    def create_caption_page(self):
        self.caption_page = CaptionPage()
        screen_caption = Screen(name='Caption')
        screen_caption.add_widget(self.caption_page)
        self.screen_manager.add_widget(screen_caption)
    
    # Vote page
    def create_vote_page(self):
        self.vote_page = VotePage()
        screen_vote = Screen(name='Vote')
        screen_vote.add_widget(self.vote_page)
        self.screen_manager.add_widget(screen_vote)
    
    # Final page
    def create_final_page(self):
        self.final_page = FinalPage()
        screen_final = Screen(name='Final')
        screen_final.add_widget(self.final_page)
        self.screen_manager.add_widget(screen_final)
    
    # Leaderboard page
    def create_leaderboard_page(self):
        self.leaderboard_page = LeaderboardPage()
        # if screen_manager already have Leaderboard screen then reset and added this new object 
        if self.screen_manager.has_screen('Leaderboard'):
            self.screen_manager.get_screen('Leaderboard').clear_widgets()
            self.screen_manager.get_screen('Leaderboard').add_widget(self.leaderboard_page)
        else:
            screen_lead = Screen(name='Leaderboard')
            screen_lead.add_widget(self.leaderboard_page)
            self.screen_manager.add_widget(screen_lead)

        


    def incoming_message_handler(self, game_object):
        # print("Received message from the server")
        # if the game is not ready then update the game's total players
        if not game_object.is_ready():
            info = f"Waiting for {TOTAL_PLAYERS - len(game_object.players)} more player..."
            # print(info)
            self.wait_page.update_info(info)
        # the game is ready
        else:
            # print("Start the game...")
            if game_object.flag == 'reset':
                # enable submission container for Caption Page
                ct_app.caption_page.enable_submission_container()
                # clear options in Vote Page
                ct_app.vote_page.clear_options()
                # clear winners
                ct_app.leaderboard_page.clear_winners()
                # set the flag back to caption to begins the game
                game_object.set_flag('caption')

            # switch to caption page
            if game_object.flag == 'caption':
                # create caption page if not exist already
                if not self.screen_manager.has_screen('Caption'):
                    print("creating caption page...")
                    self.create_caption_page()

                # switch to caption screen if not already
                if not self.screen_manager.current == 'Caption':
                    self.screen_manager.current = 'Caption'

                caption_page = self.caption_page

                # update image if curren page does not have the image
                # TODO: Fix this
                # if not self.caption_page.image.source:
                caption_page.update_image(game_object.image)

                # Update submission count according to the game object
                caption_page.update_submission_count(game_object.caption_texts)
            
            # switch to vote page
            elif game_object.flag == 'vote':
                # create vote page if not exist already
                if not self.screen_manager.has_screen('Vote'):
                    print("creating vote page...")
                    self.create_vote_page()

                # switch to vote screen if not already
                if not self.screen_manager.current == 'Vote':
                    self.screen_manager.current = 'Vote'

                vote_page = self.vote_page

                # update image if curren page does not have the image
                vote_page.update_image(game_object.image)

                # add when the page doesn't have option buttons
                if not vote_page.hasOptions:
                    # Display captions as options
                    vote_page.add_options(game_object.caption_texts)

                # Update submission count according to the game object
                vote_page.update_submission_count(game_object.total_votes)

            # switch to final page
            elif game_object.flag == 'final':
                # create final page if not exist already
                if not self.screen_manager.has_screen('Final'):
                    print("creating final page...")
                    self.create_final_page()

                # switch to final screen if not already
                if not self.screen_manager.current == 'Final':
                    self.screen_manager.current = 'Final'

                final_page = self.final_page

                # display winning caption
                final_page.update_caption(game_object.winning_caption)

                # display winners
                final_page.update_winner(game_object.winners)

                print("Scheduling switch_to_leaderboard in 5 seconds.")
                Clock.schedule_once(final_page.switch_to_leaderboard, 5)

            self.game_object = game_object

# Error callback function, used by sockets client
# Updates info page with an error message, shows message and schedules exit in 10 seconds
def show_error(message):
    ct_app.wait_page.update_info(message)
    ct_app.screen_manager.current = 'Wait'
    Clock.schedule_once(sys.exit, 10)


if __name__ == "__main__":
    ct_app = CaptionThisApp()
    ct_app.run()
