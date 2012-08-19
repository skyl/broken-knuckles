from random import shuffle


def get_shuffled(numdecks=1, num_to_burn=0):
    """
    Caller sets count to 0.
    """

    ret = []
    for d in range(numdecks):
        for i in range(1, 10):
            ret.extend([i] * 4)

        ret.extend([10] * 16)

    shuffle(ret)
    for i in range(num_to_burn):
        ret.pop()
    return ret

