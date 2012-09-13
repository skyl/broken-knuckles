from __future__ import print_function

import basic_strategy as bs
from util import get_hard_soft, is_21


class DummyPlayer(object):

    def __init__(self, hand, game, splits_left=None):
        self.game = game
        self.hand = hand
        self.debug = self.game.debug
        # allowed_splits is None if you can split infintely,
        # otherwise the max num of splits
        self.allowed_splits = game.allowed_splits
        if splits_left is None:
            self.splits_left = self.allowed_splits
        else:
            self.splits_left = splits_left
        self.can_double_after_split = game.can_double_after_split

    def play(self):

        if self.debug:
            print("DummyPlayer.play", self.hand)
        if is_21(self.hand):
            if self.debug:
                print("DummyPlayer, got 21")
            return

        move = self.get_move(self.hand)
        if self.debug:
            print("DummyPlayer to play", move)

        if move == "stand":
            return

        if move == "split":
            if self.debug:
                print("DummyPlayer to split with splits_left=", self.splits_left)
            self.splits_left -= 1
            hand0 = [self.hand[0]]
            hand1 = [self.hand[1]]
            hand0.append(self.game.get_card())
            hand1.append(self.game.get_card())
            if self.debug:
                print("DummyPlayer to play 2 hands", hand0, hand1)
                print("DummyPlayer now has splits_left=", self.splits_left)
            DummyPlayer(hand0, self.game, splits_left=self.splits_left).play()
            DummyPlayer(hand1, self.game, splits_left=self.splits_left).play()
            return

        if move == "double":
            self.hand.append(self.game.get_card())
            if self.debug:
                print("DummyPlayer doubled and ends with", self.hand)
            return

        while move == "hit":
            self.hand.append(self.game.get_card())
            if self.debug:
                print("DummyPlayer hit, now has", self.hand)
            if sum(self.hand) > 21:
                if self.debug:
                    print("DummyPlayer busted")
                return
            move = self.get_move(self.hand)

    def get_move(self, hand):
        # unfortunate duplication of Game.get_move FIXME
        dealershows = self.game.dealershows
        first = len(hand) == 2
        hard, soft = get_hard_soft(hand)
        can_split = first and (hand[0] == hand[1])

        if can_split and bool(self.splits_left):
            split = bs.basic_strategy_split[hand[0]][dealershows]
            if split:
                return "split"

        use_hard = hard == soft
        if use_hard:
            move = bs.basic_strategy_hard[hard][dealershows]
        else:
            move = bs.basic_strategy_soft[soft][dealershows]

        if self.allowed_splits is not None:
            has_not_split = self.allowed_splits == self.splits_left
        else:
            has_not_split = self.splits_left == -1

        can_double = first and (self.can_double_after_split or has_not_split)
        if not can_double and move == "double":
            move = "hit" if soft < 17 else "stand"

        return move

