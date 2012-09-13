import unittest
#import sys
from cStringIO import StringIO

import game
import betting
import dummy

test_one_deck_shoe = [
    10, 6, 6, 1, 6, 9, 10, 8, 10, 4, 10, 10, 5, 2, 10, 9, 7, 6, 4, 10, 10, 1,
    5, 4, 3, 10, 8, 5, 7, 10, 1, 10, 5, 9, 3, 7, 10, 3, 2, 10, 7, 10, 4, 2, 9,
    10, 8, 10, 2, 3, 1, 8
]

stdout = StringIO()
def fake_print(*args):
    #print args
    s = " ".join(str(a) for a in args) + "\n"
    stdout.write(s)

setattr(game, "print", fake_print)
setattr(dummy, "print", fake_print)


class TestDefaultGame(unittest.TestCase):

    def setUp(self):
        #self.stdout = sys.stdout
        #sys.stdout = StringIO()

        self.game = game.Game(True)
        self.game.shoe = test_one_deck_shoe[:]

    def tearDown(self):
        #sys.stdout = self.stdout
        pass

    def test_default_game_init(self):
        # maybe we don't really want to verify this ...
        # maybe better to setup the game expliticly
        # and allow the default params to change. hrm.
        self.assert_(self.game.debug)
        self.assert_(self.game.allowed_splits is None)
        self.assert_(self.game.can_double_after_split)
        self.assert_(self.game.num_decks == 1)
        self.assert_(self.game.penetration == .75)
        self.assert_(self.game.dealer_hit_on_soft_17 == False)
        self.assert_(self.game.blackjack_pays == 1.5)
        self.assert_(self.game.count_off_list == [0])
        self.assert_(self.game.one_card_after_split_aces)
        self.assert_(self.game.num_other_players == 0)
        # get_bet just returns 1
        # stuff that tracks the action over hands
        self.assert_(self.game.player_money == 0)
        self.assert_(self.game.money_trail == [])
        self.assert_(self.game.bets == [])
        self.assert_(self.game.hands == [])
        # for splits
        self.assert_(self.game.deferred == [])

    def test_deal(self):
        self.game.deal()
        self.assert_(self.game.other_players == [])
        self.assertEqual(self.game.dealer_hand, [1, 2])
        self.assertEqual(self.game.player_hand,  [8, 3])
        self.assertEqual(self.game.count, 0)

    def test_get_card(self):
        self.game.get_card()
        self.assertEqual(self.game.count, 0)
        self.game.get_card()
        self.assertEqual(self.game.count, -1)
        self.game.get_card()
        self.game.get_card()
        self.assertEqual(self.game.count, 1)
        self.game.shoe = []
        card = self.game.get_card()
        self.game.shoe.append(card)
        self.assertEqual(card, self.game.get_card())

    def test_true_count(self):
        [self.game.get_card() for i in range(4)]
        self.assertEqual(self.game.count, 1.0)
        left = len(self.game.shoe)
        true_count = 1.0 / (left / 52.)
        #print true_count
        #print self.game.count
        #print len(self.game.shoe)
        #print 52.
        #true_count = 1.0 / len(self.game.shoe) / 52
        self.assertEqual(self.game.true_count, true_count)

    def test_perceived_true_count(self):
        # TODO, mock this and make better assertions ..
        # also clean up the actual implementation
        self.game.perceived_true_count

    def test_get_move_basic(self):
        self.game.deal()
        self.game.set_splits_left()
        self.assertEqual(self.game.dealershows, 1)
        move = self.game.get_move([8, 3])
        self.assertEqual(move, "hit")

    def test_get_move_can_split_but_does_not(self):
        self.game.dealer_hand = [10, 10]
        self.game.splits_left = -1
        move = self.game.get_move([10, 10])
        self.assertEqual(move, "stand")

    def test_get_move_split(self):
        self.game.dealer_hand = [6, 10]
        self.game.splits_left = -1
        move = self.game.get_move([8, 8])
        self.assertEqual(move, "split")

    def test_get_move_soft_no_split(self):
        self.game.dealer_hand = [6, 10]
        self.game.splits_left = -1
        move = self.game.get_move([1, 5])
        self.assertEqual(move, "double")

    def test_get_move_want_to_double_but_cant(self):
        # TODO, see comment in code.
        self.game.dealer_hand = [6, 10]
        self.game.splits_left = -1
        move = self.game.get_move([1, 2, 3])
        self.assertEqual(move, "hit")

    def test_get_move_cant_double_after_split_has_split_so_hit(self):
        self.game.dealer_hand = [6, 10]
        self.game.allowed_splits = 1
        self.game.splits_left = 0
        self.game.can_double_after_split = False
        move = self.game.get_move([1, 5])
        self.assertEqual(move, "hit")

    def test_get_bet_default(self):
        self.game.count = 99999999
        self.assertEqual(self.game.get_bet(), 1)
        self.game.count = -9999999
        self.assertEqual(self.game.get_bet(), 1)

    def test_shuffle_if_penetration_exceeded(self):
        length = len(self.game.shoe)
        top_ten = self.game.shoe[-10:]

        self.game.shuffle_if_penetration_exceeded()
        self.assertEqual(length, len(self.game.shoe))
        self.assertEqual(top_ten, self.game.shoe[-10:])
        self.game.shoe = [10, 8, 7]
        self.game.shuffle_if_penetration_exceeded()
        self.assertNotEqual(len(self.game.shoe), 3)
        self.assert_(len(self.game.shoe), 52)

    def test_set_splits_left(self):
        self.game.allowed_splits = None
        self.game.set_splits_left()
        self.assertEqual(self.game.splits_left, -1)
        self.game.allowed_splits = 3
        self.game.set_splits_left()
        self.assertEqual(self.game.splits_left, 3)

    def test_do_betting_default(self):
        self.game.do_betting()
        self.assertEqual(self.game.bets, [1])

    def test_do_betting_wong_out(self):
        self.game = game.Game(True, get_bet=betting.kelly_wong_out)
        self.game.shoe = [1, 2, 3, 4]
        self.game.count = -999
        self.game.do_betting()
        self.assertEqual(self.game.bets, [])
        self.assertEqual(len(self.game.shoe), 52)

    def test_play_hand(self):
        self.assertEqual(self.game.player_money, 0)
        self.assertEqual(len(self.game.shoe), 52)

        self.game.play_hand()
        self.assertEqual(len(self.game.shoe), 46)
        self.assertEqual(self.game.dealer_hand, [1, 2, 8])
        self.assertEqual(self.game.player_hand, [8, 3, 10])
        self.assertEqual(self.game.player_money, 0)
        self.assertEqual(self.game.money_trail, [0])

        self.game.play_hand()
        self.assertEqual(len(self.game.shoe), 41)
        self.assertEqual(self.game.dealer_hand, [9, 4])
        self.assertEqual(self.game.player_hand, [10, 2, 10])
        self.assertEqual(self.game.player_money, -1)
        self.assertEqual(self.game.money_trail, [0, -1])

    def test_play_hand_wong_out(self):
        self.game = game.Game(True, get_bet=betting.kelly_wong_out)
        self.game.count = -999
        self.game.play_hand()
        self.assertEqual(self.game.bets, [])
        self.assertEqual(len(self.game.shoe), 52)

    def test_do_other_players(self):
        self.game.other_players = [[10, 10]]
        self.game.dealer_hand = [6, 10]
        self.game.do_other_players()
        self.assertEqual(len(self.game.shoe), 52)

    def test_do_hand_dual_blackjack(self):
        self.assertEqual(self.game.player_money, 0)
        self.game.dealer_hand = [10, 1]
        self.game.do_hand([1, 10], 1)
        self.assertEqual(self.game.player_money, 0)

    def test_do_hand_player_blackjack(self):
        self.assertEqual(self.game.player_money, 0)
        self.game.dealer_hand = [10, 2]
        self.game.do_hand([1, 10], 1)
        self.assertEqual(self.game.player_money, 1.5)
        self.assertEqual(self.game.dealer_hand, [10, 2])

    def test_do_hand_player_blackjack_play_dealer(self):
        self.assertEqual(self.game.player_money, 0)
        self.game.num_other_players = 1
        self.game.other_players = [[10, 10]]
        self.game.dealer_hand = [10, 2]
        self.game.do_hand([1, 10], 1)
        self.assertEqual(self.game.player_money, 1.5)
        self.assertEqual(self.game.dealer_hand, [10, 2, 8])

    def test_do_hand_dealer_blackjack(self):
        self.assertEqual(self.game.player_money, 0)
        self.game.dealer_hand = [10, 1]
        self.game.do_hand([10, 10], 1)
        self.assertEqual(self.game.player_money, -1)
        self.assertEqual(self.game.dealer_hand, [10, 1])

    def test_do_hand_split(self):
        self.assertEqual(self.game.player_money, 0)
        self.game.allowed_splits = None
        self.game.splits_left = -1
        self.game.shoe = [10, 10, 10]
        self.game.dealer_hand = [6, 10]
        self.game.do_hand([8, 8], 1)
        self.assertEqual(self.game.player_money, 2)
        self.assertEqual(self.game.dealer_hand, [6, 10, 10])

    def test_do_hand_hits(self):
        # hit does not enter do_hand while loop,
        # evaluate_move is recursive itself.
        self.assertEqual(self.game.player_money, 0)
        self.game.allowed_splits = None
        self.game.splits_left = -1
        self.game.shoe = [10, 6, 2, 2]
        self.game.dealer_hand = [6, 10]
        self.game.do_hand([2, 3], 1)
        self.assertEqual(self.game.player_money, 1)
        self.assertEqual(self.game.dealer_hand, [6, 10, 10])

    def test_do_hand_evaluate_move_stand(self):
        # hit does not enter do_hand while loop,
        # evaluate_move is recursive itself.
        self.assertEqual(self.game.player_money, 0)
        self.game.allowed_splits = None
        self.game.splits_left = -1
        self.game.shoe = [2]
        self.game.dealer_hand = [6, 10]
        self.game.do_hand([10, 10], 1)
        self.assertEqual(self.game.player_money, 1)
        self.assertEqual(self.game.dealer_hand, [6, 10, 2])

    def test_resplit_hands(self):
        # [8, 8] -> [8, 8] [8, 1]
        # -> [8, 1] [8, 3] [8, 2]
        # double [8, 3, 10]
        # double [8, 2, 8]
        # stand [8, 1]
        # dealer busts at [6, 10, 10]
        self.game.dealer_hand = [6, 10]
        self.game.allowed_splits = None
        self.game.set_splits_left()
        self.game.hands = [[8,8]]
        self.game.split_hand([8, 8], 1)
        self.assertEqual(self.game.player_money, 5)
        self.assertEqual(self.game.dealer_hand, [6, 10, 10])
        self.assertEqual(self.game.hands, [])
        self.assertEqual(len(self.game.shoe), 52 - 7)

    def test_split_aces_hit_once(self):

        self.assertEqual(self.game.player_money, 0)
        self.game.allowed_splits = None
        self.game.splits_left = -1
        self.game.dealer_hand = [10, 10]
        self.game.shoe = [3, 3]
        self.game.split_hand([1, 1], 1)
        self.assertEqual(self.game.player_money, -2)

    def test_do_hand(self):
        #print self.game.shoe
        #self.game.debug = True
        self.game.deal()
        self.game.set_splits_left()
        self.game.do_hand(self.game.player_hand, 1)

    # eval_stand changes player_money, is this right?
    # yes, on split, each hand has the original bet.
    def test_eval_stand_dealer_busts(self):
        self.assertEqual(self.game.player_money, 0)
        self.game.deal()
        self.game.dealer_hand = [10, 6]
        self.game.shoe = [10, 10, 10, 10, 10]
        self.game.eval_stand([5, 5, 5, 5], 1)
        self.assertEqual(self.game.player_money, 1)

    def test_eval_stand_player_wins(self):
        self.assertEqual(self.game.player_money, 0)
        self.game.deal()
        self.game.dealer_hand = [10, 9]
        self.game.eval_stand([10, 10], 1)
        self.assertEqual(self.game.player_money, 1)

    def test_eval_stand_push(self):
        self.assertEqual(self.game.player_money, 0)
        self.game.deal()
        self.game.dealer_hand = [10, 5, 4]
        self.game.eval_stand([10, 9], 1)
        self.assertEqual(self.game.player_money, 0)

    def test_eval_stand_dealer_wins(self):
        self.assertEqual(self.game.player_money, 0)
        self.game.deal()
        self.game.dealer_hand = [10, 10]
        self.game.eval_stand([10, 9], 1)
        self.assertEqual(self.game.player_money, -1)

    def test_evaluate_move_split_hands(self):
        self.assertEqual(self.game.deferred, [])
        self.assertEqual(self.game.player_money, 0)

        self.game.shoe = [1]
        self.game.dealer_hand = [10, 6]
        self.game.hands = [[10, 10], [10, 8]]

        self.game.evaluate_move("stand", [10, 10], 1)
        self.assertEqual(len(self.game.deferred), 1)
        self.assertEqual(self.game.hands, [[10, 8]])
        self.assertEqual(self.game.player_money, 0)
        self.assertEqual(self.game.dealer_hand, [10, 6])

        self.game.evaluate_move("stand", [10, 8], 1)
        self.assertEqual(len(self.game.deferred), 0)
        self.assertEqual(self.game.hands, [])
        self.assertEqual(self.game.player_money, 2)
        self.assertEqual(self.game.dealer_hand, [10, 6, 1])

    def test_evaluate_move_hit_and_bust(self):
        self.assertEqual(self.game.player_money, 0)

        self.game.shoe = [10]
        self.game.dealer_hand = [10, 2]
        self.game.player_hand = [10, 3]
        self.game.evaluate_move("hit", [10, 3], 1)
        self.assertEqual(self.game.player_money, -1)
        self.assertEqual(self.game.dealer_hand, [10, 2])

    def test_evaluate_move_hit_and_bust_play_dealer_for_other_21(self):
        self.assertEqual(self.game.player_money, 0)

        self.game.num_other_players = 1
        self.game.other_players = [[10, 3, 8]]
        self.game.shoe = [10, 10]
        self.game.dealer_hand = [10, 2]
        self.game.player_hand = [10, 3]
        self.game.evaluate_move("hit", [10, 3], 1)
        self.assertEqual(self.game.player_money, -1)
        self.assertEqual(self.game.dealer_hand, [10, 2, 10])

    def test_evaluate_move_hit_and_bust_dont_play_dealer_other_blackjack(self):
        self.assertEqual(self.game.player_money, 0)

        self.game.num_other_players = 1
        self.game.other_players = [[10, 1]]
        self.game.shoe = [10, 10]
        self.game.dealer_hand = [10, 2]
        self.game.player_hand = [10, 3]
        self.game.evaluate_move("hit", [10, 3], 1)
        self.assertEqual(self.game.player_money, -1)
        self.assertEqual(self.game.dealer_hand, [10, 2])

    def test_evaluate_move_hit_and_bust_dont_play_dealer_other_lt_21(self):
        self.assertEqual(self.game.player_money, 0)

        self.game.num_other_players = 1
        self.game.other_players = [[10, 3, 3, 3]]
        self.game.shoe = [10, 10]
        self.game.dealer_hand = [10, 2]
        self.game.player_hand = [10, 3]
        self.game.evaluate_move("hit", [10, 3], 1)
        self.assertEqual(self.game.player_money, -1)
        self.assertEqual(self.game.dealer_hand, [10, 2, 10])

    def test_evaluate_move_double_and_win(self):
        self.assertEqual(self.game.player_money, 0)
        self.game.shoe = [8, 10]
        self.game.dealer_hand = [10, 2]
        self.game.player_hand = [8, 3]
        self.game.evaluate_move("double", [8, 3], 1)
        self.assertEqual(self.game.dealer_hand, [10, 2, 8])
        self.assertEqual(self.game.player_money, 2)

    def test_evaluate_move_double_and_bust(self):
        self.assertEqual(self.game.player_money, 0)
        self.game.shoe = [8, 10]
        self.game.dealer_hand = [6, 10]
        self.game.player_hand = [8, 4]
        self.game.evaluate_move("double", [8, 4], 1)
        self.assertEqual(self.game.dealer_hand, [6, 10])
        self.assertEqual(self.game.player_money, -2)

    def test_evaluate_move_double_bust_play_dealer(self):
        self.assertEqual(self.game.player_money, 0)
        self.game.num_other_players = 1
        self.game.other_players = [[10, 3, 3, 3]]
        self.game.shoe = [8, 10]
        self.game.dealer_hand = [6, 10]
        self.game.player_hand = [8, 4]
        self.game.evaluate_move("double", [8, 4], 1)
        self.assertEqual(self.game.dealer_hand, [6, 10, 8])
        self.assertEqual(self.game.player_money, -2)

    def test_play_shoes(self):
        self.game.play_shoes(5)
        self.assert_(len(self.game.money_trail) > 10)
        # TODO, what else to assert?

    def test_print_summary(self):
        self.game.play_shoes()
        self.game.print_summary()


if __name__ == "__main__":
    unittest.main()

