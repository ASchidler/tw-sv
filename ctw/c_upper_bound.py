from sys import maxsize

import tw_utils as util
import upper_bound_criteria as crit
from random import randint
import networkx as nx


class MinDegreeCCriterion(crit.MinDegreeCriterion):
    def __init__(self, g, reds):
        super().__init__(g)
        self.reds = reds

    def choose(self):
        min_c = (maxsize, maxsize, None)
        for n in self.q[self.cmin]:
            rval = 1 if n in self.reds else 0
            rval += len(set(self.g[n]) & self.reds)
            min_c = min(min_c, (rval, len(self.g[n]), n))
            if rval < min_c[0]:
                min_c = (rval, n)

        self.q[self.cmin].remove(min_c[2])
        return min_c[2]


class MinDegreeCFirstCriterion:
    def __init__(self, g, reds):
        self.g = g.copy()
        self.reds = set(reds)

    def next(self):
        min_c = (maxsize, maxsize, None)

        if self.reds:
            for n in self.reds:
                rval = 1 + len(set(self.g[n]) & self.reds)
                min_c = min(min_c, (rval, len(self.g[n]), n))
            self.reds.remove(min_c[2])
        else:
            for n in self.g:
                min_c = min(min_c, (0, len(self.g[n]), n))

        n = min_c[2]
        nbs = self.g[n]
        for u in nbs:
            for v in nbs:
                if u > v:
                    self.g.add_edge(u, v)
        self.g.remove_node(n)

        return n


class BoundedCCriterion(crit.MinDegreeCriterion):
    """Ensures that the c value stays below a given bound. May fail!"""
    def __init__(self, g, reds, limit):
        super().__init__(g)
        self.reds = reds
        self.limit = limit

    def choose(self):
        cval = self.cmin
        maxval = (-1, None)
        while True:
            for n in self.q[cval]:
                rval = 1 if n in self.reds else 0
                rval += len(set(self.g[n]) & self.reds)

                if self.limit >= rval > maxval[0]:
                    maxval = (rval, n)

            if maxval[0] > -1:
                self.q[cval].remove(maxval[1])
                return maxval[1]

            # Try to find the next bucket
            cval += 1
            while cval < len(self.q) and not self.q[cval]:
                cval += 1

            if cval > self.max_degree:
                raise RuntimeError(f"No decomposition for c={self.limit} found.")


class MinCCriterion:
    """Minimizes the c value in each iteration"""

    def __init__(self, g, reds):
        self.g = g.copy()
        self.reds = reds

    def next(self):
        # Quick implementation, may be easier to cache c-values
        min_c = (maxsize, None)
        for n in self.g.nodes:
            nbs = set(self.g[n])
            nbs.add(n)
            nbs &= self.reds

            # Minimize c first and degree second
            if len(nbs) < min_c[0] or (len(nbs) == min_c[0] and len(self.g[n]) < len(self.g[min_c[1]])):
                min_c = (len(nbs), n)

        n = min_c[1]
        nbs = self.g[n]
        for u in nbs:
            for v in nbs:
                if u > v:
                    self.g.add_edge(u, v)
        self.g.remove_node(n)

        return n


class IncrementalCriterion:
    """Tries to bound c, whenever it fails, it increments the bound and restarts"""

    def __init__(self, g, reds, lb):
        self.g = g
        self.reds = reds
        self.ordering = None
        self.lb = lb

    def next(self):
        # since the normal method does not support backtracking, this is a little bit of a hack...
        if self.ordering is None:
            bound = self.lb
            while True:
                try:
                    self.ordering = []
                    crit = BoundedCCriterion(self.g, self.reds, bound)
                    while len(self.ordering) != len(self.g.nodes):
                        self.ordering.append(crit.next())
                    break
                except RuntimeError:
                    bound += 1

            self.ordering.reverse()

        return self.ordering.pop()


def greedy(g, criterion, reds):
    ordering = []

    while len(ordering) != len(g.nodes):
        ordering.append(criterion.next())

    bags = util.ordering_to_decomp(g, ordering)[0]
    tw = max(len(x) for x in bags.values()) - 1
    c = max(len(x & reds) for x in bags.values())

    tw, c = improve_swap(g, ordering, reds, bound_tw=tw, bound_c=c)

    return tw, c, ordering


def min_degree(g, reds):
    return greedy(g, crit.MinDegreeCriterion(g), reds)


def min_c(g, reds):
    return greedy(g, MinDegreeCFirstCriterion(g, reds), reds)


def c_bound_min_degree(g, reds, bound):
    try:
        return greedy(g, BoundedCCriterion(g, reds, bound), reds)
    except RuntimeError:
        return maxsize, maxsize


def incremental_c_min_degree(g, reds, lb):
    return greedy(g, IncrementalCriterion(g, reds, lb), reds)


def min_degree_min_c(g, reds):
    return greedy(g, MinDegreeCCriterion(g, reds), reds)


def twopass(g, reds):
    result = greedy(g, MinCCriterion(g, reds), reds)
    try:
        return greedy(g, BoundedCCriterion(g, reds, result[1] - 1), reds)
    except RuntimeError:
        return result


def improve_swap(g, ordering, reds, rounds=500, bound_tw=maxsize, bound_c=maxsize):
    """Tries to improve the bound of an elimination ordering by swapping random elements"""

    for _ in range(0, rounds):
        t1 = randint(0, len(ordering) - 1)
        t2 = randint(0, len(ordering) - 1)

        ordering[t1], ordering[t2] = ordering[t2], ordering[t1]

        bags = util.ordering_to_decomp(g, ordering)[0].values()

        result_tw = max(len(x) for x in bags) - 1
        result_c = max(len(reds & x) for x in bags)

        if result_tw > bound_tw or result_c > bound_c:
            ordering[t1], ordering[t2] = ordering[t2], ordering[t1]
        else:
            bound_tw = result_tw
            bound_c = result_c

    return bound_tw, bound_c


def improve_scramble(g, ordering, reds, rounds=100, bound_tw=maxsize, bound_c=maxsize, interval=50):
    """Tries to improve the bound by randomly scrambling the elements in an interval"""

    # If interval is bigger than the length of the ordering, limit scope accordingly
    if len(ordering) < interval:
        limit = 0
        interval = len(ordering)
    else:
        limit = len(ordering) - 1 - interval

    for _ in range(0, rounds):
        index = randint(0, limit) if limit > 0 else 0

        old = ordering[index:index+interval]
        for c_i in range(0, interval-1):
            randindex = randint(0, interval - 1 - c_i) + index + c_i
            ordering[index + c_i], ordering[randindex] = ordering[randindex], ordering[index + c_i]

        bags = util.ordering_to_decomp(g, ordering)[0].values()

        result_tw = max(len(x) for x in bags) - 1
        result_c = max(len(reds & x) for x in bags)

        # If the new bound is worse, restore
        if result_tw > bound_tw or result_c > bound_c:
            for i in range(0, interval):
                ordering[index + i] = old[i]
        else:
            bound_tw = result_tw
            bound_c = result_c

    return bound_tw, bound_c