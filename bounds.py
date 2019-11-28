import networkx as nx
from sys import maxsize
from collections import deque
from random import randint

class MinDegreeQueue:
    def __init__(self, g):
        self.g = g
        self.degrees = {x: len(g[x]) for x in g.nodes}

        # q is a bucket queue
        self.max_degree = max(self.degrees.values())
        self.q = [set() for _ in range(0, self.max_degree + 1)]
        for k, v in self.degrees.items():
            self.q[v].add(k)

        self.cmin = 0

    def next(self):
        while not self.q[self.cmin]:
            self.cmin += 1

        n = self.q[self.cmin].pop()
        d = self.degrees.pop(n)

        return n, d

    def remove(self, n):
        for u in self.g[n]:
            self.change(u, -1)

    def change(self, n, amount):
        if n in self.degrees:
            dg = self.degrees[n]
            dn = dg + amount
            if dn > self.max_degree:
                for _ in range(self.max_degree, dn):
                    self.q.append(set())
                self.max_degree = dn

            self.degrees[n] += amount
            self.q[dg].remove(n)
            self.q[dn].add(n)

            if dn < self.cmin:
                self.cmin = dn

    def add_edge(self, u, v):
        self.change(u, 1)
        self.change(v, 1)

    def has_next(self):
        return len(self.degrees) > 0


def mmd(og):
    g = og.copy()
    bound = 0
    q = MinDegreeQueue(g)

    while len(g.nodes) > 1:
        v, d = q.next()

        bound = max(bound, d)
        nbs = set(g[v])

        # Select neighbor with minimum number of common neighbors
        _, tg = min((len(nbs & set(g[u])), u) for u in nbs)

        # Contract
        for u in nbs:
            if u != tg and u not in g[tg]:
                g.add_edge(u, tg)
                q.add_edge(u, tg)

        q.remove(v)
        g.remove_node(v)

    return bound

def mmdr(og):
    g = og.copy()
    bound = 0

    while len(g.nodes) > 1:
        d, v = min((len(g[x]), x) for x in g.nodes)
        bound = max(bound, d)

        nbs = set(g[v])

        # Select neighbor with minimum number of common neighbors
        _, tg = min((len(nbs & set(g[u])), u) for u in nbs)

        # Contract
        for u in g[tg]:
            if u != v and u not in g[v]:
                g.add_edge(u, v)

        g.remove_node(tg)

    return bound

def build_decomposition(go, ordering):
    g = go.copy()
    tw = 0
    #bags = {x: {x} for x in ordering}
    for n in ordering:
        # Last bag is just the node itself
        if len(g.nodes) > 1:
            tw = max(tw, len(g[n]))
            #bags[n] = set(g[n])
            #bags[n].add(n)

            for u in g[n]:
                for v in g[n]:
                    if u < v:
                        g.add_edge(u, v)
            g.remove_node(n)

    return tw

def greedy(go):
    g = go.copy()
    ordering = []
    q = MinDegreeQueue(g)

    # Define ordering based on min degree
    while q.has_next():
        n, d = q.next()

        ordering.append(n)
        q.remove(n)

        for u in g[n]:
            for v in g[n]:
                if u < v and v not in g[u]:
                    q.add_edge(u, v)
                    g.add_edge(u, v)

        g.remove_node(n)

    # Build decomposition
    bnd = build_decomposition(go, ordering)
    return improve_ub(go, ordering, bound=bnd)




def greedy_fi(go):
    g = go.copy()
    ordering = []

    while len(g.nodes) > 0:
        c_min = maxsize
        c_node = None

        for n in g.nodes:
            val = len(g[n])
            for u in g[n]:
                for v in g[n]:
                    if u < v and not g.has_edge(u, v):
                        val += 1

            if val < c_min:
                c_min = val
                c_node = n

        ordering.append(c_node)
        for u in g[c_node]:
            for v in g[c_node]:
                if u < v and v not in g[u]:
                    g.add_edge(u, v)

        g.remove_node(c_node)

    ps = {x: ordering.index(x) for x in ordering}
    g = go.copy()
    bags = {}
    for n in ordering:
        if len(g.nodes) == 1:
            bags[n] = {n}
        else:
            _, nb = min((ps[x], x) for x in g[n])
            bags[n] = set(g[nb])
            for u in g[n]:
                for v in g[n]:
                    if u < v:
                        g.add_edge(u, v)

    return max(len(x) for x in bags.values()) - 1


def improve(go, bound):
    g = go.copy()
    changed = True

    while changed:
        changed = False
        for n in g.nodes:
            if len(g[n]) > bound:
                nb = set(g[n])

                # build set of candidates, i. e. neighbors of neighbors
                nnb = set()
                for u in nb:
                    nnb.update(set(g[u]) - nb)

                for u in nnb:
                    if len(nb & set(g[u])) > bound:
                        g.add_edge(n, u)
                        changed = True

    return g


def lbn(go):
    bound = mmd(go)
    changed = True

    while changed:
        changed = False
        # Improve
        g = improve(go, bound)
        bound2 = mmd(g)

        if bound2 > bound:
            changed = True
            bound += 1

    return bound


def lbnp(go):
    changed = True
    bound = mmd(go)

    while changed:
        changed = False
        g = improve(go, bound)
        bound2 = mmdr(g)

        while bound2 <= bound and len(g.nodes) > 1:
            # Select minimum degree vertex
            _, c_v = min((len(g[x]), x) for x in g.nodes)
            nb = set(g[c_v])

            # Select neighbor with minimum number of common vertices
            _, c_nb = min((len(nb & set(g[x])), x) for x in nb)

            # Contract
            g.remove_node(c_v)
            for n in nb:
                if c_nb != n:
                    g.add_edge(c_nb, n)

            # Improve
            g = improve(g, bound)
            bound2 = mmdr(g)

        if bound2 > bound:
            bound += 1
            changed = True

    return bound


def improve_ub(go, ord, rounds=0, bound=maxsize):
    forbidden = deque(maxlen=min(len(ord)//2, 10))
    new_try = -1

    for _ in range(0, rounds):
        while new_try in forbidden:
            new_try = randint(0, len(ord)-2)

        forbidden.append(new_try)
        ord[new_try], ord[new_try+1] = ord[new_try+1], ord[new_try]

        result = build_decomposition(go, ord)

        if result > bound:
            ord[new_try], ord[new_try + 1] = ord[new_try + 1], ord[new_try]
        elif result < bound:
            bound = result

    return bound
