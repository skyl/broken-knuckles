# http://www.online-casinos.com/images/blackjack-chart.gif
# hrrm ...

basic_strategy_hard = {
    2: [None] + ["hit"] * 11,
    3: [None] + ["hit"] * 11,
    4: [None] + ["hit"] * 11,
    5: [None] + ["hit"] * 11,
    6: [None] + ["hit"] * 11,
    7: [None] + ["hit"] * 11,
    8: [None] + ["hit"] * 11,
    9: [None, "hit", "hit"] + ["double"] * 4 + ["hit"] * 4,
    10: [None, "hit"] + ["double"] * 8 + ["hit"],
    11: [None, "hit"] + ["double"] * 9,
    12: [None] + ["hit"] * 3 + ["stand"] * 3 + ["hit"] * 4,
    13: [None, "hit"] + ["stand"] * 5 + ["hit"] * 4,
    14: [None, "hit"] + ["stand"] * 5 + ["hit"] * 4,
    15: [None, "hit"] + ["stand"] * 5 + ["hit"] * 4,
    16: [None, "hit"] + ["stand"] * 5 + ["hit"] * 4,
    17: ["stand"] * 11,
    18: ["stand"] * 11,
    19: ["stand"] * 11,
    20: ["stand"] * 11,
    21: ["stand"] * 11,
}
basic_strategy_soft = {
    12: ["hit"] * 11,
    13: [None] + ["hit"] * 4 + ["double", "double"] + ["hit"] * 4,
    14: [None] + ["hit"] * 4 + ["double", "double"] + ["hit"] * 4,
    15: [None] + ["hit"] * 3 + ["double", "double", "double"] + ["hit"] * 4,
    16: [None] + ["hit"] * 3 + ["double", "double", "double"] + ["hit"] * 4,
    17: [None] + ["hit"] * 2 + ["double"] * 4 + ["hit"] * 4,
    18: [None] + ["hit", "stand"] + ["double"] * 4 + ["stand"] * 2 + ["hit"] * 2,
    19: ["stand"] * 11,
    20: ["stand"] * 11,
    21: ["stand"] * 11,
}
basic_strategy_split = {
    1: [True] * 11,
    2: [None] + [False] + [True] * 6 + [False] * 3,
    3: [None] + [False] + [True] * 6 + [False] * 3,
    4: [None] + [False] * 4 + [True] * 2 + [False] * 4,
    5: [False] * 11,
    6: [None] + [False] + [True] * 5 + [False] * 4,
    7: [None] + [False] + [True] * 6 + [False] * 3,
    8: [True] * 11,
    9: [None] + [False] + [True] * 5 + [False] + [True, True] + [False],
    10: [False] * 11,
}

