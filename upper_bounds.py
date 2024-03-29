from random import randint
from sys import maxsize

import networkx as nx

import tw_utils as util


def greedy(g, criterion):
    """Basic greedy heuristic that establishes an elimination ordering based on a given criterion"""
    ordering = []

    while len(ordering) != len(g.nodes):
        ordering.append(criterion.next())

    bound = max(len(x) for x in util.ordering_to_decomp(g, ordering)[0].values()) - 1
    bound = improve_scramble(g, ordering, bound=bound)
    bound = improve_swap(g, ordering, bound=bound)

    return bound, ordering


def improve_swap(g, ordering, rounds=500, bound=maxsize):
    """Tries to improve the bound of an elimination ordering by swapping random elements"""

    o = bound
    for _ in range(0, rounds):
        t1 = randint(0, len(ordering) - 1)
        t2 = randint(0, len(ordering) - 1)

        ordering[t1], ordering[t2] = ordering[t2], ordering[t1]

        result = max(len(x) for x in util.ordering_to_decomp(g, ordering)[0].values()) - 1

        if result > bound:
            ordering[t1], ordering[t2] = ordering[t2], ordering[t1]
        else:
            bound = result

    return bound


def improve_scramble(g, ordering, rounds=100, bound=maxsize, interval=15):
    """Tries to improve the bound by randomly scrambling the elements in an interval"""

    limit = len(ordering) - 1 - interval if len(ordering) > interval else 0
    interval = min(interval, len(ordering))

    for _ in range(0, rounds):
        index = randint(0, limit) if limit > 0 else 0

        old = ordering[index:index+interval]
        for c_i in range(0, interval-1):
            randindex = randint(0, interval - 1 - c_i) + index + c_i
            ordering[index + c_i], ordering[randindex] = ordering[randindex], ordering[index + c_i]

        result = max(len(x) for x in util.ordering_to_decomp(g, ordering)[0].values()) - 1

        # If the new bound is worse, restore
        if result > bound:
            for i in range(0, interval):
                ordering[index + i] = old[i]
        else:
            bound = result

    return bound


def greedy_min_degree(g_in):
    return greedy(g_in, MinDegreeCriterion(g_in))


# The idea here is to check if we can remove vertices from the bags. Initial tests show, that this is not possible
# which makes sense from the way that the decomposition is constructed from the ordering
def improve2(g_in, ordering):
    bags, tree, root = util.ordering_to_decomp(g_in, ordering)
    tree, bags = util.clean_tree(bags, tree, root)

    if not util.verify_decomposition(g_in, bags, tree):
        print("Invalid")

    removed = 0

    from collections import defaultdict
    covered = {x: defaultdict(set) for x in g_in.nodes}

    for u, v in g_in.edges:
        for k, b in bags.items():
            if u in b and v in b:
                covered[u][v].add(k)
                covered[v][u].add(k)

    import queue as qu

    for v in g_in.nodes:
        nbs = [k for k, b in bags.items() if v in b]
        g_sub = nx.induced_subgraph(tree, nbs)
        q = qu.Queue()

        # Add leafs
        for n in (x for x in g_sub.nodes if len(list(g_sub.successors(x))) + len(list(g_sub.predecessors(x))) == 1):
            q.put(n)

        # Proceed through graph
        while not q.empty():
            n = q.get()

            # Still relevant?
            if v in bags[n]:
                # Only one neighbor has vertex in bag?
                nbs = set(g_sub.predecessors(n)) | set(g_sub.successors(n))
                if len([x for x in nbs if v in bags[x]]) <= 1:
                    # No edge covered by only this bag?
                    if all(len(s) > 1 for s in covered[v].values() if n in s):
                        bags[n].remove(v)
                        removed += 1
                        for k, s in covered[v].items():
                            s.discard(n)
                            covered[k][v].discard(n)

    print(removed)
    return max(len(v) for v in bags.values()) - 1


class MinDegreeCriterion:
    """Always returns the vertex with lowest degree"""
    def __init__(self, g):
        self.g = g.copy()

        # q is a bucket queue
        self.max_degree = 0
        self.q = [set()]
        for k, v in ((n, len(g[n])) for n in g.nodes):
            if v > self.max_degree:
                for _ in range(0, v - self.max_degree):
                    self.q.append(set())
                self.max_degree = v

            self.q[v].add(k)

        self.cmin = 0

    def choose(self):
        # Choose min degree vertex
        return self.q[self.cmin].pop()

    def next(self):
        while len(self.q[self.cmin]) == 0:
            self.cmin += 1
            if self.cmin > self.max_degree:
                return None

        n = self.choose()

        # Eliminate
        nb = self.g[n]

        # First remove vertex
        self.g.remove_node(n)

        # Decrement degree of neighbors
        for u in nb:
            # Decrement, since degree will decrease after removing n
            self.update_degree(u, -1)

        # Introduce clique among neighbors
        for u, v in ((u, v) for u in nb for v in nb if u > v and u not in self.g[v]):
            self.g.add_edge(u, v)
            self.update_degree(u, 1)
            self.update_degree(v, 1)

        return n

    def update_degree(self, n, inc):
        dgn = len(self.g[n])
        dg = dgn - inc

        if dgn > self.max_degree:
            self.q.append(set())
            self.max_degree = dgn
        if dgn < self.cmin:
            self.cmin = dgn

        self.q[dg].remove(n)
        self.q[dgn].add(n)