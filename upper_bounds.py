from sys import maxsize
from collections import deque
from random import randint
import upper_bound_criteria as cr

import tw_utils as util


def greedy(g, criterion):
    ordering = []

    while len(ordering) != len(g.nodes):
        ordering.append(criterion.next())

    bound = max(len(x) for x in util.ordering_to_decomp(g, ordering).values()) - 1
    return improve_ub(g, ordering, bound=bound)


def improve_ub(g_in, ord, rounds=0, bound=maxsize):
    g = g_in.copy()
    forbidden = deque(maxlen=min(len(ord)//2, 10))
    new_try = -1

    for _ in range(0, rounds):
        while new_try in forbidden:
            new_try = randint(0, len(ord)-2)

        forbidden.append(new_try)
        ord[new_try], ord[new_try+1] = ord[new_try+1], ord[new_try]

        result = max(len(x) for x in util.ordering_to_decomp(g, ord)) - 1

        if result > bound:
            ord[new_try], ord[new_try + 1] = ord[new_try + 1], ord[new_try]
        elif result < bound:
            bound = result

    return bound


def greedy_min_degree(g_in):
    return greedy(g_in, cr.MinDegreeCriterion(g_in))
