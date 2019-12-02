# TODO: Try different contraction strategies, especially for GHTW it may be better


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
        d2 = 0

        while not self.q[self.cmin] and self.cmin <= self.max_degree:
            self.cmin += 1

        # The second lowest degree may give a better bound
        if self.q[self.cmin]:
            d2 = self.cmin

        return n, d, d2

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
    """Finds a minimum degree lower bound based on minors (MMD+)"""
    g = og.copy()
    bound = 0
    q = MinDegreeQueue(g)

    while len(g.nodes) > 1:
        v, d, d2 = q.next()

        bound = max(bound, d2)
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


def improve(go, bound):
    """Computes the bound-improved graph. I.e. if u and v are non-adjacent and share bound+1 neighbors, adds {u,v}"""

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
    """Tightens the mmd"""
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
        bound2 = mmd(g)

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
            bound2 = mmd(g)

        if bound2 > bound:
            bound += 1
            changed = True

    return bound