#!/usr/bin/env python
from __future__ import division
import random
import logging

logging.basicConfig(level=logging.WARNING)

LOG = logging.getLogger()


PAYOUTS = {15: 50,
           16: 100,
           17: 200,
           18: 250,
           19: 300,
           20: 400}

M1_8 = range(1, 9)
M4_7 = range(4, 8)
PAYOUT = "PAYOUT"
MOVES = (M1_8, M4_7, PAYOUT)


def get_payout(value):
    return PAYOUTS.get(value, 0)

def possible_moves(current_value):
    if current_value > 20:
        return (PAYOUT,)
    elif current_value < 15:
        return (M1_8, M4_7)
    else:
        return (M1_8, M4_7, PAYOUT)


class memoize(object):

    def __init__(self, fn):
        self.cache = {}
        self.fn = fn

    def __call__(self, *args, **kwargs):
        arg_tuple = tuple(args)

        if arg_tuple not in self.cache:
            LOG.debug("Caching: %s", arg_tuple)
            self.cache[arg_tuple] = self.fn(*args, **kwargs)
        else:
            LOG.debug("Hit cache: %s", arg_tuple)
        return self.cache[arg_tuple]

@memoize
def next_move(current_value):
    return max(((move, expected_payout_for_move(current_value, move))
                for move in possible_moves(current_value)),
                key=lambda x: x[1])

def expected_payout_for_move(current_value, move_range):

    if move_range == PAYOUT or current_value > 20:
        return get_payout(current_value)

    payout_moves = [next_move(current_value + i) for i in move_range]

    return expected_value([payout for move, payout in payout_moves],
                          probability_fn=lambda x: 1 / len(move_range))


def identity(x):
    return x

def expected_value(items, probability_fn, value_fn=identity):
    return sum(value_fn(item) * probability_fn(item) for item in items)


def play_interactive():
    while True:
        try:
            cur_val = raw_input('Current value? ')
        except EOFError:
            return

        if cur_val.upper() == "Q":
            return
        try:
            cur_val = int(cur_val)
        except ValueError:
            continue
        print next_move(int(cur_val))


class StopPlaying(Exception):
    pass


def next_value(current_value, move):
    if current_value is None:
        return random.randint(1, 5)
    elif move == PAYOUT:
        raise StopPlaying()
    else:
        return current_value + random.choice(move)

def play_noninteractive(starting_value=None):
    '''Play a single quasar game; return the payout'''
    current_value = starting_value or random.randint(1, 5)

    while current_value <= 20:
        move, expected_payout = next_move(current_value)

        LOG.info("move = {}, current_value = {}, expected = {}".format(
            move,
            current_value,
            expected_payout))
        try:
            current_value = next_value(current_value, move)
        except StopPlaying():
            break

    return get_payout(current_value)

def play_n_games(n, ante=200, starting=0):
    current_cash = starting

    for i in xrange(n):
        current_cash -= ante

        payout = play_noninteractive()
        LOG.info("Won: %s", payout)

        current_cash += payout
    return current_cash


if __name__ == "__main__":
    play_interactive()
