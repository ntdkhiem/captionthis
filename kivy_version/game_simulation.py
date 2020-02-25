from game import CaptionThisGame

# Simulation
game = CaptionThisGame('234')

game.add_player('1', 'kevin')
game.add_player('2', 'katie')
game.add_player('3', 'kenny')
print("Added kevin, katie, kenny")
game.ready = True
# begin the game
while game.is_ready:
    print(f"[+] a chosen meme is > {game.image}")
    for player in game.players.keys():
        game.add_caption(player, input(f"{game.players.get(player)[0]}, please choose your caption > "))

    if (game.all_captions_submitted):
        for player_id, caption in game.caption_texts.items():
            print(f"{player_id}. {caption[0]}")
        
        for player in game.players.keys():
            vote_id = input(f"{game.players.get(player)[0]}, please vote for one caption > ")
            game.vote_caption(vote_id)
        
        if (game.all_captions_voted):
            print(f"Winners: { ', '.join(game.caption_winner()) }")

    print("***Leaderboard***")
    for player_id, value in game.players.items():
        print(f"{player_id}) {value[0]} has {value[1]} points")

    input("Again...?")
    game.reset()