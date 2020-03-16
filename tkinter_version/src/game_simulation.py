from game import CaptionThisGame

game = CaptionThisGame('1', 3)

game.add_player('1', 'kevin')
game.add_player('2', 'katie')
game.add_player('3', 'kenny')
print("Added kevin, katie, kenny")
game.start_game()

# begin the game
while game.is_ready():
    if game.get_flag() == "reset":
        game.set_flag("caption")
    if game.get_flag() == "caption":
        print(f"[+] meme: {game.get_image()}")
        for player in game.players.keys():
            game.add_caption(player, input(f"{game.players.get(player)[0]}, please choose your caption > "))
        
        if game.all_players_submitted():
            game.set_flag("vote")
            
    if game.get_flag() == "vote":
        for player_id, caption in game.get_submitted_captions().items():
            print(f"{player_id}. {caption[0]}")
        
        for player in game.players.keys():
            vote_id = input(f"{game.players.get(player)[0]}, please vote for one caption > ")
            game.vote_caption(vote_id)

        if game.all_players_voted():
            game.set_flag("final")
    if game.get_flag() == "final":
        game.calculate_winners()
        print("-- Win captions -- ")
        print("\n".join(game.get_win_captions()))
        print("-- Winners --")
        print("\n".join(game.get_winners()))

        print("***Leaderboard***")
        for player_id, value in game.players.items():
            print(f"{player_id}) {value[0]} has {value[1]} points")
    
    input("Again?")
    game.reset()
