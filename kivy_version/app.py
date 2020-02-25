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
        print(ct_app.screen_manager.current)
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
        
        print("Start listening from the server...")
        socket_client.start_listening(incoming_message_handler, show_error)

        info = f"Waiting for 4 more player..."
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

        self.msg = TextInput(multiline=False)

        self.add_widget(self.msg)

        # Clock.schedule_once(self.switch_page, 5)
        # Clock.schedule_once(self.switch_page, 5)

    # Update text widget with this new message
    def update_info(self, message):
        self.message.text = message

    # Called on label width update, so we can set text width properly - to 90% of label wid
    def update_text_width(self, *_):
        self.message.text_size = (self.message.width * 0.9, None)

    # TODO: to be delete
    # def switch_page(self, _):
    #     ct_app.screen_manager.current = 'Caption'


class CaptionPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.rows = 2
        self.cols = 1

        # FIRST ROW - will be for viewing (image, time, number of captions) takes up 95% of the height of the screen 
        view_container = GridLayout(cols=2, height=Window.size[1] * 0.9, size_hint_y=None)
        # Image to be view takes 80% of the width of view_container
        # self.image = Label(width=Window.size[0]*0.8, halign="center", valign="middle", text="Image Here...", font_size=50)
        self.image = Image()
        view_container.add_widget(self.image)

        # A container contains time and captions
        info_container = GridLayout(cols=1, rows=2)
        self.submissions = Label(halign="center", valign="middle", font_size=20)
        self.clock = Label(halign="center", valign="middle", text="60 seconds", font_size=20)
        info_container.add_widget(self.submissions)
        info_container.add_widget(self.clock)
        view_container.add_widget(info_container)
        self.add_widget(view_container)

        # SECOND ROW
        # container for sending message
        submission_container = GridLayout(cols=2, size_hint_y=None)
        # takes up 80% of the width of submission_container
        self.caption = TextInput(width=Window.size[0]*0.8, size_hint_x=None, multiline=False, focus=True)
        self.send = Button(text="Send")
        self.send.bind(on_release=self.submit)
        submission_container.add_widget(self.caption)
        submission_container.add_widget(self.send)
        self.add_widget(submission_container)

    # TODO: could not update image's source
    # TODO: can't type in self.caption
    def update_image(self, link):
        print(f"Got {link}")
        self.image.source = f"images/{link}"

    def update_submission_count(self, total_submissions):
        if not total_submissions:
            total_submissions = 0
        self.submissions.text = f"{total_submissions} Caption(s)"

    def submit(self, instance):
        print("Sending the caption to the server...")
        caption = self.caption.text

        # send to server
        socket_client.send(caption)

        # clear field value
        self.caption.text = ''

        # disable the submission container to prevent extra submit
        self.caption.disabled = True


class VotePage(GridLayout): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2

        # FIRST COLUMN - will contain image and all options to vote
        view_container = GridLayout(cols=1, rows=2, width=Window.size[0] * 0.8, size_hint_x=None)
        self.image = Label(width=Window.size[0], text="Image Here...")
        options_container = GridLayout(cols=2, rows=2)
        options_container.add_widget(Label(text="Option #1"))
        options_container.add_widget(Label(text="Option #2"))
        options_container.add_widget(Label(text="Option #3"))
        options_container.add_widget(Label(text="Option #4"))
        
        view_container.add_widget(self.image)
        view_container.add_widget(options_container)
        self.add_widget(view_container)
        
        
        # SECOND COLUMN - will contain time counter and number of votes
        info_container = GridLayout(cols=1, rows=2)
        self.submissions = Label(halign="center", valign="middle", text="1 Vote(s)", font_size=20)
        self.clock = Label(halign="center", valign="middle", text="30 seconds", font_size=20)
        info_container.add_widget(self.submissions)
        info_container.add_widget(self.clock)
        self.add_widget(info_container)


class FinalPage(GridLayout): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.rows = 3

        self.image = Label(height=Window.size[1] * 0.5, text="Image Here...", size_hint_y=None)
        self.caption = Label(text="Winning caption here....", size_hint_y=None)
        self.winner = Label(text="{Player} gets 10 points!")
        self.add_widget(self.image)
        self.add_widget(self.caption)
        self.add_widget(self.winner)


class LeaderboardPage(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2

        leaderboard_container = GridLayout(width=Window.size[0] * 0.9, size_hint_x=None, rows=5)
        leaderboard_container.add_widget(Label(text="Leaderboard", font_size=20))
        leaderboard_container.add_widget(Label(text="1. Player 1"))
        leaderboard_container.add_widget(Label(text="2. Player 2"))
        leaderboard_container.add_widget(Label(text="3. Player 3"))
        leaderboard_container.add_widget(Label(text="4. Player 4"))
        # leaderboard_container.add_widget(Label(text="5. Player 5"))
        self.next = Button(text="-->", font_size=40)
        self.add_widget(leaderboard_container)
        self.add_widget(self.next)


class CaptionThisApp(App):
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
        
        # Caption page
        self.caption_page = CaptionPage()
        screen_caption = Screen(name='Caption')
        screen_caption.add_widget(self.caption_page)
        self.screen_manager.add_widget(screen_caption)
        
        # Vote page
        self.vote_page = VotePage()
        screen_vote = Screen(name='Vote')
        screen_vote.add_widget(self.vote_page)
        self.screen_manager.add_widget(screen_vote)
        
        # Final page
        self.final_page = FinalPage()
        screen_final = Screen(name='Final')
        screen_final.add_widget(self.final_page)
        self.screen_manager.add_widget(screen_final)
        
        # Leaderboard page
        self.leaderboard_page = LeaderboardPage()
        screen_lead = Screen(name='Leaderboard')
        screen_lead.add_widget(self.leaderboard_page)
        self.screen_manager.add_widget(screen_lead)

        return self.screen_manager
        # return CaptionPage()


def incoming_message_handler(game_object):
    # print("Received message from the server")
    # if the game is not ready then update the game's total players
    if not game_object.is_ready():
        info = f"Waiting for {TOTAL_PLAYERS - len(game_object.players)} more player..."
        # print(info)
        ct_app.wait_page.update_info(info)
    # the game is ready
    else:
        print("Start the game...")
        # switch to caption page
        if game_object.flag == 'caption':
            if not ct_app.screen_manager.current == 'Caption':
                ct_app.screen_manager.current = 'Caption'
            # update image if curren page does not have the image
            caption_page = ct_app.caption_page
            if not caption_page.image.source:
                caption_page.update_image(game_object.image)
            # TODO: update total submission according to the new game object
            caption_page.update_submission_count(game_object.caption_texts)


# Error callback function, used by sockets client
# Updates info page with an error message, shows message and schedules exit in 10 seconds
def show_error(message):
    ct_app.wait_page.update_info(message)
    ct_app.screen_manager.current = 'Wait'
    Clock.schedule_once(sys.exit, 10)


if __name__ == "__main__":
    ct_app = CaptionThisApp()
    ct_app.run()
