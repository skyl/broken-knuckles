
`broken-knuckles` is a small library to evaluate different blackjack rules
and betting strategies.

Do not trust `broken knuckles`. Blackjack is a pile of special cases.
Find the flaws in `broken knuckles` and report them. Do not gamble; gambling is bad.
The best card counting strategies are risky in the short term and you can go
down (way down) for hours and hours playing the best strategy.
You will probably bankrupt yourself.


The class, `game.Game` is the basis. You instantiate a `Game` and simulate some hands.
The default betting is just 1 unit per hand regardless of count. You can replace this
betting strategy with the `get_bet` kwarg to game. Let's simulate
a game which pays 3:2 on blackjack and a game which pays 6:5.

Mostly, I have just been using the ipython notebook with pylab to run simulations.

You can enter the notebook, `ipython notebook --pylab inline`.

.. code_block:: pycon

    import pandas
    import game
    import betting
    reload(betting)
    reload(game)
    import pylab as pl

    g32 = game.Game(get_bet=betting.basic_kelly, blackjack_pays=1.5)
    g65 = game.Game(get_bet=betting.basic_kelly, blackjack_pays=6/5.)

    g32.play_shoes(10000)
    g65.play_shoes(10000)

    games = [
        g32,
        g65,
    ]
    num = min([len(i.money_trail) for i in games])
    df = pandas.DataFrame({
        "3/2": g32.money_trail[:num],
        "6/5": g65.money_trail[:num],
    })
    df.plot(title="BlackJack Pays, 3/2 vs 6/5")

    g32.print_summary()
    g65.print_summary()


Calling plot above may give you an image like this:

.. image:: https://s3.amazonaws.com/skyl/blackjackpays.png

And, the `print_summary` calls may print some stuff out like::

    final units 14302.0
    num hands 151635
    winnings per hand 0.0943185939922
    min units= -1223.0
    max units= 14760.0
    Hours with 1 hand per minute= 2527
    $25 units= 357550.0
    $5 units= 71510.0

Check out `game.Game.__init__` for the options to game.
As of the time of writing, the above code simulates:

* Infinte splits
* can double after split
* Only 1 card after split Aces
* 1 deck with 75% penetration
* perfect counting, perfect and undeviated basic strategy
* no other players at table
* dealer stands on soft 17

These can be changed with arguments to `Game`.

