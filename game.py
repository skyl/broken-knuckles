from __future__ import print_function
import random

from functools import partial
from collections import defaultdict

from cards import get_shuffled
from dummy import DummyPlayer
from util import get_hard_soft, is_21
import basic_strategy as bs


class Game(object):
    def __init__(self, debug=False, allowed_splits=None,
                 can_double_after_split=True, num_decks=1,
                 penetration=.75,
                 dealer_hit_on_soft_17=False,
                 blackjack_pays=1.5,
                 count_off_list=[0],
                 one_card_after_split_aces=True,
                 num_other_players=0,
                 get_bet=None):
        self.debug = debug
        # allowed_splits is None for infinite splits
        # otherwise the number of splits
        self.allowed_splits = allowed_splits
        self.can_double_after_split = can_double_after_split
        self.num_decks = num_decks
        self.penetration = penetration
        self.dealer_hit_on_soft_17 = dealer_hit_on_soft_17
        self.blackjack_pays = blackjack_pays
        self.count_off_list = count_off_list
        self.one_card_after_split_aces = one_card_after_split_aces
        self.num_other_players = num_other_players
        if get_bet is not None:
            self.get_bet = get_bet.__get__(self, Game)

        self.player_money = 0
        self.money_trail = []
        self.bets = []  # only initial bets
        self.hands = []  # add if split
        self.deferred = []  # needed for eventual evaluation of split
        self.shuffle()

    @property
    def true_count(self):
        return self.count / (len(self.shoe) / 52.)

    @property
    def perceived_true_count(self):
        off = random.choice(self.count_off_list)
        pcount = self.count + off
        return pcount / (len(self.shoe) / 52. + random.random() / .75)

    @property
    def dealershows(self):
        return self.dealer_hand[0]

    @property
    def dealer_hidden(self):
        return self.dealer_hand[1]

    def shuffle(self):
        self.count = 0
        self.shoe = get_shuffled(self.num_decks)
        if self.debug:
            print("shuffled", self.shoe)

    def deal(self):
        self.dealer_hand = []
        self.player_hand = []
        self.other_players = [[] for i in range(self.num_other_players)]
        self.deal_others_one()
        self.player_hand.append(self.get_card())
        self.dealer_hand.append(self.get_card())
        self.deal_others_one()
        self.player_hand.append(self.get_card())
        self.dealer_hand.append(self.get_card(False))
        if self.debug:
            print("dealer=", self.dealer_hand)
            print("player=", self.player_hand)

    def deal_others_one(self):
        [hand.append(self.get_card()) for hand in self.other_players]

    def get_card(self, count=True):
        try:
            card = self.shoe.pop()
        except IndexError:
            # ran out of cards, reshuffle
            self.shuffle()
            card = self.shoe.pop()
        if not count:
            return card
        return self.count_card(card)

    def count_card(self, card):
        if card in [1, 10]:
            self.count -= 1
        elif card in range(2, 7):
            self.count += 1
        return card

    def play_dealer(self):
        hard, soft = get_hard_soft(self.dealer_hand)

        has_soft = soft != hard
        hit_if_less_than = 18 if (has_soft and self.dealer_hit_on_soft_17) else 17

        while soft < hit_if_less_than:
            self.dealer_hand.append(self.get_card())
            hard, soft = get_hard_soft(self.dealer_hand)
        if self.debug:
            print("dealer done", self.dealer_hand)
        return soft

    def eval_stand(self, hand, bet):
        hard, soft = get_hard_soft(hand)
        self.count_card(self.dealer_hidden)
        dealer_total = self.play_dealer()
        if self.debug:
            print("dealer has", dealer_total)
            print("player hand", hand)
        if dealer_total > 21:
            self.player_money += bet
            if self.debug:
                print("dealer busted. adding bet=", bet)
            return
        elif soft > dealer_total:
            self.player_money += bet
            if self.debug:
                print("player wins", bet)
            return
        elif soft == dealer_total:
            if self.debug:
                print("push")
            return
        else:
            self.player_money -= bet
            if self.debug:
                print("player loses", bet)
            return

    def evaluate_move(self, move, hand, bet):
        dh = self.dealer_hidden
        if move == "stand":

            if self.debug:
                hard, soft = get_hard_soft(hand)
                print("player stands at", soft)

            if self.hands:
                if self.debug:
                    print("MULTIPLE HANDS", self.hands)
                # wait until all hands are played before dealer plays
                self.deferred.append(partial(self.eval_stand, hand, bet))
                self.safe_remove(hand)
                return
            else:
                return self.eval_stand(hand, bet)

        if move == "hit":
            hand.append(self.get_card())
            hard, soft = get_hard_soft(hand)
            if self.debug:
                print("player hit, now has", hand)
            if hard > 21:
                self.safe_remove(hand)
                self.player_money -= bet
                self.count_card(dh)
                if self.debug:
                    print("player busted", hard, "loses", bet)
                if self.need_to_play_dealer():
                    self.play_dealer()
                return
            move = self.get_move(hand)
            self.evaluate_move(move, hand, bet)

        if move == "double":
            hand.append(self.get_card())
            hard, soft = get_hard_soft(hand)
            if self.debug:
                print("player doubles, now has", hand)
            if hard > 21:
                self.safe_remove(hand)
                self.player_money -= bet * 2
                self.count_card(dh)
                if self.debug:
                    print("player doubled and busted", hard, "loses", bet * 2)
                if self.need_to_play_dealer():
                    self.play_dealer()
                return
            self.evaluate_move("stand", hand, bet * 2)

    def need_to_play_dealer(self):
        """
        If other player have a non-blackjack, non-busted hand, dealer must play
        """
        if self.num_other_players == 0:
            return False

        for h in self.other_players:
            if not is_21(h) and sum(h) < 21:
                return True

            if is_21(h) and len(h) > 2:
                return True

        return False

    def get_move(self, hand):
        """Pass in hand b/c of split"""
        dealershows = self.dealershows
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
        # not quite sure about this. strategy says double
        # but, we can't double - we have split and not can_double_after_split.
        # or, we have more than 2 cards, so the time for doubling is over.
        # I think that means we hit ... always?
        # should this be configurable or is there a hard rule?
        if not can_double and move == "double":
            move = "hit"  # if soft < 17 else "stand"

        return move

    def get_bet(self):
        return 1

    def shuffle_if_penetration_exceeded(self):
        start = self.num_decks * 52
        to_play = self.num_decks * self.penetration * 52
        if len(self.shoe) < (start - to_play):
            self.shuffle()

    def set_splits_left(self):
        if self.allowed_splits is not None:
            self.splits_left = self.allowed_splits
        else:
            self.splits_left = -1

    def do_betting(self):
        bet = self.get_bet()
        if bet is None:
            if self.debug:
                print("LEAVING TABLE")
            self.shuffle()
            return
        self.bets.append(bet)
        return bet

    def play_hand(self):
        self.shuffle_if_penetration_exceeded()
        bet = self.do_betting()
        if bet is None:
            return
        self.set_splits_left()

        if self.debug:
            print("play_hand, count=", self.count)
            print("true=", self.true_count)
            print("bet", bet)

        self.deal()
        # for now, we will always put the other players
        # before the player of interest b/c
        # the dealer's actions are tied to the player of interest.
        self.do_other_players()
        self.do_hand(self.player_hand, bet)
        self.finish()
        self.money_trail.append(self.player_money)

    def do_other_players(self):
        for hand in self.other_players:
            DummyPlayer(hand, self).play()

    def safe_remove(self, hand):
        if hand not in self.hands:
            return
        if self.debug:
            print("removing", hand, "from", self.hands)
        self.hands.remove(hand)
        if not self.hands:
            if self.debug:
                print("EVAL deferreds in safe_remove")
            for f in self.deferred:
                f()
            self.deferred = []
            self.finish()

    def finish(self):
        if self.debug:
            print("MONEY", self.player_money)
            print("COUNT", self.count)
            print("TOTAL HANDS", len(self.bets))
            print()

    def do_hand(self, hand, bet, can_blackjack=True):
        if can_blackjack:
            if is_21(self.dealer_hand) and is_21(hand):
                self.count_card(self.dealer_hand[0])
                if self.debug:
                    print("DUAL BLACKJACK!")
                return
            elif is_21(hand):
                self.safe_remove(hand)
                self.player_money += bet * self.blackjack_pays
                self.count_card(self.dealer_hand[0])
                if self.debug:
                    print("PLAYER BLACKJACK!")
                    print("player wins = ", bet * self.blackjack_pays)
                if self.need_to_play_dealer():
                    self.play_dealer()
                return
            elif is_21(self.dealer_hand):
                self.safe_remove(hand)
                self.player_money -= bet
                self.count_card(self.dealer_hand[0])
                if self.debug:
                    print("DEALER BLACKJACK!")
                    print("player loses = ", bet)
                return

        move = self.get_move(hand)
        if move == "split":
            self.split_hand(hand, bet)
            return

        self.evaluate_move(move, hand, bet)

    def split_hand(self, hand, bet):
        #if self.allowed_splits is not None:
        # for infinite_splits we still count down from -1
        # so that we can know if we have split for can_double_after_split
        self.splits_left -= 1
        hand0 = [hand[0]]
        hand1 = [hand[1]]
        hand0.append(self.get_card())
        hand1.append(self.get_card())
        if hand in self.hands:
            self.hands.remove(hand)
        self.hands.extend([hand0, hand1])

        if self.debug:
          print("SPLIT", hand, hand0, hand1)

        if self.one_card_after_split_aces and hand[0] == 1:
            self.evaluate_move("stand", hand0, bet)
            self.evaluate_move("stand", hand1, bet)

        else:
            self.do_hand(hand0, bet, can_blackjack=False)
            self.do_hand(hand1, bet, can_blackjack=False)


    def play_shoes(self, num=1):
        start = self.num_decks * 52
        to_play = self.num_decks * self.penetration * 52

        for i in range(num):
            while len(self.shoe) > (start - to_play):
                self.play_hand()
            self.shuffle()

    @property
    def winnings_per_hand(self):
        return self.player_money / float(len(self.money_trail))

    def print_summary(self):
        print("final units", self.player_money)
        print("num hands", len(self.money_trail))
        print("winnings per hand", self.winnings_per_hand)
        #print(running_total
        print("min units=", min(self.money_trail))
        print("max units=", max(self.money_trail))
        print("Hours with 1 hand per minute=", len(self.money_trail) / 60)
        end = self.player_money
        print("$25 units=", end * 25)
        print("$5 units=", end * 5)

