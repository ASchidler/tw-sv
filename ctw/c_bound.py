from sys import maxsize

import tw_utils as util
import upper_bound_criteria as crit


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

    def __init__(self, g, reds):
        self.g = g
        self.reds = reds
        self.ordering = None

    def next(self):
        # since the normal method does not support backtracking, this is a little bit of a hack...
        if self.ordering is None:
            bound = 1
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

    bags = util.ordering_to_decomp(g, ordering)
    tw = max(len(x) for x in bags.values())
    c = max(len(x & reds) for x in bags.values())

    return tw, c


def min_degree(g, reds):
    return greedy(g, crit.MinDegreeCriterion(g), reds)


def min_c(g, reds):
    return greedy(g, MinCCriterion(g, reds), reds)


def c_bound_min_degree(g, reds, bound):
    try:
        return greedy(g, BoundedCCriterion(g, reds, bound),reds)
    except RuntimeError:
        return maxsize, maxsize


def incremental_c_min_degree(g, reds):
    return greedy(g, IncrementalCriterion(g, reds), reds)


def min_degree_min_c(g, reds):
    return greedy(g, MinDegreeCCriterion(g, reds), reds)


def twopass(g, reds):
    result = greedy(g, MinCCriterion(g, reds), reds)
    try:
        return greedy(g, BoundedCCriterion(g, reds, result[1]), reds)
    except RuntimeError:
        return result
