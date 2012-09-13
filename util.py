def get_hard_soft(hand):
    hard = sum(hand)
    soft = hard if (1 not in hand) else hard + 10
    if soft > 21:
        soft = hard
    return hard, soft


def is_21(hand):
    if sum(hand) == 21:
        return True
    if (1 in hand) and (sum(hand) + 10 == 21):
        return True
    return False

