

def basic_kelly(game):
    #if game.true_count < -4:
    #    return None
    if game.true_count <= 1:
        bet = 1
    elif game.true_count < 2:
        bet = 2
    elif game.true_count < 3:
        bet = 5
    elif game.true_count < 4:
        bet = 7
    elif game.true_count < 5:
        bet = 10
    else:
        bet = 20
    return bet


